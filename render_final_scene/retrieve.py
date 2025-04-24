import os
import sys
import json
import re
import shutil
import multiprocessing

import torch
from torch.nn import functional as F
import openshape
import objaverse
from huggingface_hub import hf_hub_download
from transformers import CLIPModel, CLIPProcessor

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

torch.set_grad_enabled(False)
pc_encoder = openshape.load_pc_encoder("openshape-pointbert-vitg14-rgb")

print("Loading OpenShape embeddings.")
emb_dir = "OpenShape-Embeddings"

meta_fp = hf_hub_download(
    repo_id="OpenShape/openshape-objaverse-embeddings",
    filename="objaverse_meta.json",
    repo_type="dataset",
    local_dir=emb_dir,
    token=True
)
with open(meta_fp, "r") as f:
    meta = {e["u"]: e for e in json.load(f)["entries"]}

emb_fp = hf_hub_download(
    repo_id="OpenShape/openshape-objaverse-embeddings",
    filename="objaverse.pt",
    repo_type="dataset",
    local_dir=emb_dir,
    token=True
)
data = torch.load(emb_fp, map_location="cpu")
us, feats = data["us"], data["feats"]

def preprocess(text: str) -> str:
    #Remove digits and underscores, normalize spaces.
    clean = re.sub(r"\d+", "", text)
    return clean.replace("_", " ").strip()

def move_glb(files: dict, dest_dir: str, obj_id: str):
    #Move only .glb files
    os.makedirs(dest_dir, exist_ok=True)

    for uid, path in files.items():
        if not path.lower().endswith(".glb"):
            continue
        target = os.path.join(dest_dir, f"{obj_id}.glb")
        try:
            shutil.move(path, target)
            print(f"Moved {path} → {target}")
        except Exception as e:
            print(f"Failed moving {path}: {e}")

def get_clip_model(
    model_name: str = "laion/CLIP-ViT-bigG-14-laion2B-39B-b160k",
):
    print(f"Loading CLIP model '{model_name}'…")
    model = CLIPModel.from_pretrained(
        model_name,
        torch_dtype=(torch.float16 if device.type == "cuda" else torch.float32),
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    processor = CLIPProcessor.from_pretrained(model_name)
    proj_dim = model.config.projection_dim
    assert proj_dim == feats.shape[1], (
        f"CLIP proj_dim={proj_dim} but embeddings have dim={feats.shape[1]}"
    )
    return model, processor

def retrieve_top(
    text_emb: torch.Tensor,
    top_k: int = 1,
    threshold: float = 0.1,
    filter_fn=None):
    
    # Return top-k nearest objects from OpenShape embeddings.
    emb = text_emb.cpu().float()
    emb = F.normalize(emb, dim=-1).squeeze(0)

    sims = []
    for chunk in torch.split(feats, 10240, dim=0):
        chunk_f32 = chunk.float()           # ensure float32
        chunk_f32 = F.normalize(chunk_f32, dim=-1)
        sims.append(emb @ chunk_f32.T)

    sim_all = torch.cat(sims)
    vals, idxs = torch.sort(sim_all, descending=True)

    results = []
    for val, idx in zip(vals, idxs):
        if val < threshold:
            break
        uid = us[idx]
        info = meta.get(uid)
        if info and (filter_fn is None or filter_fn(info)):
            results.append({**info, "sim": float(val)})
            if len(results) >= top_k:
                break
    return results

def obj_filter():
    return lambda m: True

if __name__ == "__main__":
    clip_model, clip_processor = get_clip_model()

    # Load scene graph JSON
    scene_json = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "/home/jovyan/shares/SR006.nfs2/Kulichenko/Design_Iana/dataset_furn_100/13_jpg.rf.c31d51e36d3972bde3189d04c529d2d1_3d.json"
    )
    print(f"Reading scene graph: {scene_json}")
    with open(scene_json, "r") as jf:
        scene_data = json.load(jf)

    objects = [o for o in scene_data if "new_object_id" in o]
    print(f"Found {len(objects)} objects to process.")

    for obj in objects:
        oid      = obj["new_object_id"]
        color    = obj.get("color", "brown")
        material = obj.get("material", "wood")
        style    = obj.get("style", "Modern")

        prompt = (
            f"A {oid} with {color} color and {material} material "
            f"in {style} style, high quality"
        )
        text = preprocess(prompt)
        print(f"\nObject {oid}: '{text}'")

        tokens = clip_processor(
            text=[text], return_tensors="pt", truncation=True, max_length=77
        )
        tokens = {k: v.to(device) for k, v in tokens.items()}
        with torch.no_grad():
            text_emb = clip_model.get_text_features(**tokens)

        retrieved = retrieve_top(
            text_emb, top_k=1, threshold=0.1, filter_fn=obj_filter()
        )
        if not retrieved:
            print(f"No results for {oid}")
            continue
        best = retrieved[0]
        print(f"Retrieved: {best.get('name','')} (sim={best['sim']:.3f})")

        # Download and move the .glb file
        objs = objaverse.load_objects(
            uids=[best["u"]],
            download_processes=multiprocessing.cpu_count()
        )
        dest = os.path.join(os.getcwd(), "Assets13", oid)
        move_glb(objs, dest, oid)
