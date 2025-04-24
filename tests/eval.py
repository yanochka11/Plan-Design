#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unittest
from itertools import combinations
from pathlib import Path
from typing import List, Sequence, Tuple

ACCEPTED_CLASSES = [
    "tv stand", "bar counter", "bench", "bookshelf", "cabinet", "chair",
    "chair-bed", "coffee table", "desk", "dining table", "fireplace",
    "floor lamp", "floor plant", "floor vase", "kitchen island",
    "modular kitchen", "ottoman", "rocking chair", "rug", "shelves",
    "side table", "sideboard", "sofa", "stool", "wardrobe", "armchair",
    "window",
]
SEATING_CLASSES = [
    "bench", "chair", "chair-bed", "sofa", "armchair", "stool", "ottoman", "rocking chair"]
PRIMARY_FURNITURE_CLASSES = [
    "sofa", "tv stand", "fireplace", "modular kitchen",
    "sideboard",
]
LIGHT_CLASSES = ["floor lamp"]

SEAT_DIST_LIMIT = 10.0    #pairs ≥ this are disconnected
CLEARANCE_LIMIT = 0.4    #edge gap < this -> blocked circulation

_CRIT_COLS = ["B1", "B2", "B3", "G1", "G2", "G3", "P4"]

def load_design(path: Path) -> List[dict]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def normalise_name(raw: str) -> str:
    name = raw.lower().strip().replace("_", " ")
    tokens = name.split()
    clean_tokens: list[str] = []
    for token in tokens:
        # strip trailing non‑letter/non‑hyphen chars
        token = re.sub(r'[^a-z\-]+$', '', token)
        if not re.search(r'[a-z\-]', token):
            break                # stop at first non‑name token
        clean_tokens.append(token)
    return " ".join(clean_tokens)


def accepted(o: dict) -> bool:
    return normalise_name(o.get("new_object_id", "")) in ACCEPTED_CLASSES


def centre(o: dict) -> Tuple[float, float]:
    p = o["position"]
    return p["x"], p["y"]


def dist(a: Sequence[float], b: Sequence[float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def bbox(o: dict) -> Tuple[float, float, float, float]:
    x, y = o["position"]["x"], o["position"]["y"]
    L, W = o["size_in_meters"]["length"], o["size_in_meters"]["width"]
    if o.get("rotation_z", 0) % 180 == 90:
        L, W = W, L
    return (x - L / 2, y - W / 2, x + L / 2, y + W / 2)


def overlap(a: Tuple[float, float, float, float],
            b: Tuple[float, float, float, float]) -> bool:
    return min(a[2], b[2]) > max(a[0], b[0]) and \
           min(a[3], b[3]) > max(a[1], b[1])


def _edge_gap(boxA: Tuple[float, float, float, float],
              boxB: Tuple[float, float, float, float]) -> float:
    gap_x = max(boxB[0] - boxA[2], boxA[0] - boxB[2], 0)
    gap_y = max(boxB[1] - boxA[3], boxA[1] - boxB[3], 0)
    return math.hypot(gap_x, gap_y)


def B1(seating: List[dict]) -> bool:
    if len(seating) < 3:
        return True
    return any(
        _edge_gap(bbox(a), bbox(b)) >= SEAT_DIST_LIMIT
        for a, b in combinations(seating, 2)
    )

def B2(primary: List[dict]) -> bool:
    for a, b in combinations(primary, 2):
        na, nb = normalise_name(a["new_object_id"]), normalise_name(b["new_object_id"])

        if na == nb:
            continue

        gap = _edge_gap(bbox(a), bbox(b))
        if gap <= 0:          
            continue
        if gap < CLEARANCE_LIMIT:
            return True      
    return False


def B3(furn: List[dict], arch: List[dict]) -> bool:
    for f in furn:
        if "rug" in normalise_name(f["new_object_id"]):
            continue
        if any(overlap(bbox(f), bbox(a)) for a in arch):
            return True
    return False


G1 = lambda seating: not B1(seating)
G2 = lambda primary: not B2(primary)  
G3 = lambda furn, arch: not B3(furn, arch)
P1, P2, P3 = G1, G2, G3               
P4 = lambda lights: len(lights) >= 1  


def classify(path: Path):
    data = load_design(path)

    objs = [o for o in data[1:] if accepted(o)]
    seating = [o for o in objs if normalise_name(o["new_object_id"]) in SEATING_CLASSES]
    primary = [o for o in objs if normalise_name(o["new_object_id"]) in PRIMARY_FURNITURE_CLASSES]
    arch    = [o for o in objs if normalise_name(o["new_object_id"]) in ACCEPTED_CLASSES]
    lights  = [o for o in objs if normalise_name(o["new_object_id"]) in LIGHT_CLASSES]
    furn    = [o for o in objs if o not in arch]

    res = {
        "B1": B1(seating), "B2": B2(primary), "B3": B3(furn, arch),
        "G1": G1(seating), "G2": G2(primary), "G3": G3(furn, arch),
        "P1": G1(seating), "P2": G2(primary), "P3": G3(furn, arch),
        "P4": P4(lights),
    }

    if any(res[k] for k in ("B1", "B2", "B3")):
        label = "bad design"
    elif all(res[k] for k in ("G1", "G2", "G3")):
        label = "perfect design" if res["P4"] else "good design"
    else:
        label = "good design"

    return label, res

crit_B1, crit_B2, crit_B3 = B1, B2, B3
crit_G1, crit_G2, crit_G3 = G1, G2, G3
crit_P4 = P4
classify_design = classify


def build_table(folder: Path):
    header = "\t".join(["File"] + _CRIT_COLS + ["Final"])
    rows: List[str] = [header]
    counts = {"bad design": 0, "good design": 0, "perfect design": 0}

    for fp in sorted(folder.glob("*.json")):
        try:
            label, r = classify(fp)
            counts[label] += 1
            rows.append(
                f"{fp.name}\t"
                f"{int(r['B1'])}\t{int(r['B2'])}\t{int(r['B3'])}\t"
                f"{int(r['G1'])}\t{int(r['G2'])}\t{int(r['G3'])}\t"
                f"{int(r['P4'])}\t{label}"
            )
        except Exception as exc:
            rows.append(f"{fp.name}\tERROR\t{exc}")

    rows += ["", "# counts"]
    for lbl in ("bad design", "good design", "perfect design"):
        rows.append(f"{lbl}\t{counts[lbl]}")
    return rows, counts


def main(argv: List[str] | None = None):
    p = argparse.ArgumentParser(
        description="Evaluate interior‑layout JSON files"
    )
    p.add_argument("--data", type=Path, required=True,
                   help="Folder with *.json layouts")
    p.add_argument("--out", type=Path, default=Path("design_evaluation.tsv"),
                   help="Destination TSV file")
    args = p.parse_args(argv)

    if not args.data.exists():
        sys.exit(f"{args.data} does not exist")

    lines, counts = build_table(args.data)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")

    print(args.out.resolve())
    for lbl in ("bad design", "good design", "perfect design"):
        print(f"{lbl:<16} {counts[lbl]}")

if __name__ == "__main__":
    if any(a in ("-m", "-t", "--test", "test", "unittest") for a in sys.argv[1:]):
        unittest.main(argv=[sys.argv[0]])
    else:
        main()
