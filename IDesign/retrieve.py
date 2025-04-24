
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence

import faiss                      
import numpy as np
import torch
from huggingface_hub import hf_hub_download
from torch import nn
from torch.nn import functional as F
from transformers import (
    AutoModel,
    AutoProcessor,
    SiglipModel,
    SiglipProcessor,
)
import objaverse 


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DTYPE = torch.float16 if torch.cuda.is_available() else torch.bfloat16
TOP_K = 5  
OBJAVERSE_HF_REPO = "OpenShape/openshape-objaverse-embeddings"
EMB_DIR = Path("OpenShape-Embeddings")
INDEX_PATH = Path("objaverse.index")
LOG_LEVEL = logging.INFO

#   * SigLIP 2: multilingual, SOTA retrieval
#   * EVA‑02‑CLIP: highest open‑source zero‑shot ImageNet score, but larger
MODEL_NAME = os.getenv("VL_MODEL", "google/siglip2-so400m-patch14-384")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)


def preprocess(text: str) -> str:
    """Basic prompt cleaning: drop numerals, replace underscores."""
    return re.sub(r"\d", "", text).replace("_", " ").strip()


def load_embeddings() -> tuple[np.ndarray, List[str]]:
    """Download Objaverse embeddings (vectors + UIDs) once and memory‑map them."""
    logging.info("Loading Objaverse embeddings …")
    deser_path = hf_hub_download(
        OBJAVERSE_HF_REPO,
        "objaverse.pt",
        repo_type="dataset",
        local_dir=str(EMB_DIR),
    )
    blob = torch.load(deser_path, map_location="cpu")
    feats: torch.Tensor = blob["feats"]  # [N, D]
    uids: List[str] = blob["us"]
    feats32 = F.normalize(feats.float(), dim=-1).numpy()
    logging.info("Loaded %d embeddings of size %d.", *feats32.shape)
    return feats32, uids


def build_or_load_faiss(feats: np.ndarray) -> faiss.IndexFlatIP:
    """Create a FAISS index on disk or load an existing one."""
    if INDEX_PATH.exists():
        logging.info("Reading FAISS index from %s", INDEX_PATH)
        index = faiss.read_index(str(INDEX_PATH))
    else:
        logging.info("Building FAISS index … this can take a few minutes")
        index = faiss.IndexFlatIP(feats.shape[1])
        index.add(feats)
        faiss.write_index(index, str(INDEX_PATH))
        logging.info("Index written to %s", INDEX_PATH)
    return index


@torch.inference_mode()
def load_vl_encoder(model_name: str = MODEL_NAME):
    """Load VL encoder & processor on the correct device / dtype."""
    logging.info("Loading vision‑language model %s", model_name)
    processor = AutoProcessor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(
        model_name,
        torch_dtype=DTYPE,
        device_map="auto",  
    )
    model = model.to(DEVICE).eval()
    return model, processor


def encode_text(text: str, model, processor) -> torch.Tensor:
    """Return an L2‑normalized embedding [1, D] on CPU."""
    inputs = processor(text=[text], padding=True, return_tensors="pt").to(DEVICE)
    emb = model.get_text_features(**inputs)
    emb = F.normalize(emb, dim=-1).cpu()
    return emb


def retrieve(
    text_emb: torch.Tensor,
    index: faiss.IndexFlatIP,
    meta: Dict[str, Dict[str, Any]],
    uids: Sequence[str],
    k: int = TOP_K,
    sim_th: float = 0.0,
    filter_fn: Callable[[Dict[str, Any]], bool] | None = None,
) -> List[Dict[str, Any]]:
    """Search the FAISS index and return up to *k* meta records above *sim_th*."""
    scores, idxs = index.search(text_emb.numpy().astype("float32"), k * 5)  # oversample
    results: List[Dict[str, Any]] = []
    for score, idx in zip(scores[0], idxs[0]):
        if score < sim_th:
            continue
        uid = uids[idx]
        m = meta.get(uid)
        if m and (filter_fn is None or filter_fn(m)):
            results.append(dict(m, sim=float(score)))
            if len(results) == k:
                break
    return results


def main(scene_graph_path: str = "scene_graph.json") -> None:  # noqa: C901
    logging.info("Device: %s", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

    meta_path = hf_hub_download(
        OBJAVERSE_HF_REPO,
        "objaverse_meta.json",
        repo_type="dataset",
        local_dir=str(EMB_DIR),
    )
    with open(meta_path, "r", encoding="utf-8") as fh:
        meta = {x["u"]: x for x in json.load(fh)["entries"]}

    feats, uids = load_embeddings()
    index = build_or_load_faiss(feats)
    model, processor = load_vl_encoder()

    # Load scene graph
    with open(scene_graph_path, "r", encoding="utf-8") as fh:
        scene_objects: List[Dict[str, Any]] = json.load(fh)
    logging.info("Processing %d scene objects", len(scene_objects))

    def filter_fn(m: Dict[str, Any]) -> bool:
        return 0 <= m["faces"] <= 35_000_000 and 0 <= m["anims"] <= 563

    for obj in scene_objects:
        try:
            style = obj["style"]
            material = obj["material"]
            color = obj["color"]
        except KeyError:
            logging.warning("Skipping object without style/material/color: %s", obj)
            continue

        prompt = preprocess(f"A {style} {color} {obj['new_object_id']} with {material} material, high quality")
        logging.info("Query: '%s'", prompt)

        text_emb = encode_text(prompt, model, processor)
        candidates = retrieve(text_emb, index, meta, uids, k=1, sim_th=0.1, filter_fn=filter_fn)
        if not candidates:
            logging.warning("No match found for %s", obj["new_object_id"])
            continue
        best = candidates[0]
        logging.info("Best match: %s (sim=%.3f)", best["u"], best["sim"])

        obj_files = objaverse.load_objects(uids=[best["u"]])
        dest_dir = Path.cwd() / "Assets13"
        dest_dir.mkdir(exist_ok=True)
        dest_glb = dest_dir / f"{obj['new_object_id']}.glb"
        shutil.move(obj_files[best["u"]], dest_glb)
        logging.info("Saved to %s", dest_glb)

    logging.info("Done.")


if __name__ == "__main__":
    scene_graph = sys.argv[1] if len(sys.argv) > 1 else "scene_graph.json"
    main(scene_graph)
