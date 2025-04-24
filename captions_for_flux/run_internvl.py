#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, math, warnings
from pathlib import Path
from typing import Dict, List

import torch
from PIL import Image
import torchvision.transforms as T
from torchvision.transforms.functional import InterpolationMode
from transformers import AutoModel, AutoTokenizer, modeling_utils
from huggingface_hub import login
from accelerate import Accelerator

warnings.filterwarnings("ignore", category=FutureWarning)
modeling_utils.caching_allocator_warmup = lambda *_, **__: None

MODEL_NAME = "OpenGVLab/InternVL2_5-78B-MPO"
IMAGE_EXT  = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

CLASSES = [
    "TV stand","bar counter","bench","bookshelf","cabinet","chair","chair-bed",
    "coffee table","desk","dining table","fireplace","floor lamp","floor plant",
    "floor vase","kitchen island","modular kitchen","ottoman","rocking chair",
    "rug","shelves","side table","sideboard","sofa","stool","wardrobe",
    "armchair","window"
]
PROMPT = (
    "<image>\n"
    "Please describe this room beginning with the statement: 'This is a top-down view from the center of the living room.'\n"
    f"Identify and describe **all** items in the following classes: {', '.join(CLASSES)}.\n"
    "If an item appears multiple times (e.g., 3 sofas, 2 windows), number them: "
    "sofa_1, sofa_2, sofa_3 … window_1, window_2, etc.\n\n"
    "Please provide:\n"
    "1. Items location (e.g., against which wall, in a corner, center of the room).\n"
    "2. Approximate dimensions (e.g., a sofa ~2 meters long, a table ~1×0.6 meters).\n"
    "3. Distances or clearances (e.g., 0.8 meters between sofa and table).\n"
    "4. Orientation and angles (e.g., which direction it faces, how it's rotated).\n"
    "5. Style of the room (e.g., modern, minimalist, classic), including colors and materials.\n"
    "6. Estimated overall room size in meters.\n"
    "7. Location of windows and doors.\n\n"
    "Keep the description concise and clear, suitable for manual sketching."
)

MEAN, STD = (0.485,0.456,0.406), (0.229,0.224,0.225)
_transform = T.Compose([
    T.Lambda(lambda im: im.convert("RGB")),
    T.Resize((448,448), interpolation=InterpolationMode.BICUBIC),
    T.ToTensor(), T.Normalize(MEAN, STD)
])

def _tiles(img: Image.Image, tile=448, max_tiles=12) -> List[Image.Image]:
    w,h,ar = img.width, img.height, img.width/img.height
    grids = sorted({(i,j) for n in range(1,max_tiles+1)
                    for i in range(1,n+1) for j in range(1,n+1)
                    if 1<=i*j<=max_tiles}, key=lambda g:g[0]*g[1])
    gw,gh = min(grids, key=lambda g: abs(ar-g[0]/g[1]))
    rs = img.resize((tile*gw, tile*gh))
    out = [rs.crop((x*tile,y*tile,(x+1)*tile,(y+1)*tile))
           for y in range(gh) for x in range(gw)]
    if len(out)!=1: out.append(img.resize((tile,tile)))
    return out

def load_pixels(path: Path) -> torch.Tensor:
    img = Image.open(path).convert("RGB")
    return torch.stack([_transform(t) for t in _tiles(img)])

def device_map() -> Dict[str,int]:
    layers, gpus = 80, torch.cuda.device_count()
    assert gpus>=8, "need 8 GPUs for 78B checkpoint"
    per = math.ceil(layers/(gpus-0.5))
    per_gpu = [per]*gpus; per_gpu[0]=math.ceil(per_gpu[0]*0.5)
    d, idx = {}, 0
    for g,nl in enumerate(per_gpu):
        for _ in range(nl):
            if idx>=layers: break
            d[f"language_model.model.layers.{idx}"] = g; idx+=1
    for k in ["vision_model","mlp1",
              "language_model.model.tok_embeddings",
              "language_model.model.embed_tokens",
              "language_model.model.rotary_emb",
              "language_model.output",
              "language_model.model.norm",
              "language_model.lm_head",
              f"language_model.model.layers.{layers-1}"]:
        d[k] = 0
    return d

def main():
    Accelerator() 

    login(token=os.getenv("HF_TOKEN"), add_to_git_credential=False)

    in_dir  = Path("/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/captions/input_images")
    out_dir = Path("/home/jovyan/shares/SR008.fs2/iana_kulichenko/Experiments/captions/output_prompts_2")
    out_dir.mkdir(parents=True, exist_ok=True)

    imgs = sorted(p for p in in_dir.iterdir() if p.suffix.lower() in IMAGE_EXT)
    if not imgs:
        print(f"[INFO] No images in {in_dir}")
        return
    print(f"[INFO] Found {len(imgs)} images")

    print("[INFO] Loading InternVL‑78B … (first run may take minutes)")
    model = AutoModel.from_pretrained(
        MODEL_NAME, torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True, use_flash_attn=True,
        trust_remote_code=True, device_map=device_map()
    ).eval()
    tok = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False,
                                        trust_remote_code=True)

    gen_cfg = dict(max_new_tokens=1024, do_sample=True, temperature=0.2)

    for p in imgs:
        print("→", p.name)
        try:
            px = load_pixels(p).to("cuda:0", dtype=torch.bfloat16)
            txt = model.chat(tok, px, PROMPT, gen_cfg)
            (out_dir/f"{p.stem}.txt").write_text(txt, encoding="utf-8")
        except Exception as e:
            print(f"[ERR] {p.name}: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted")
