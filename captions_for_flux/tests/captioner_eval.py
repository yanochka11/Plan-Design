# -*- coding: utf-8 -*-
"""
InternVL caption evaluator – clearance‑free

Per‑scene metrics
-----------------
objects_correct     – caption objects found in GT
location_correct    – objects whose qualitative location matches
length_correct      – objects whose length is within --dim_tol
width_correct       – objects whose width  is within --dim_tol
room_ratio_correct  – 1 if room aspect ratio is within --room_ratio_tol else 0
"""
from __future__ import annotations

import argparse, json, re
from pathlib import Path
from typing  import Dict, List, Optional, Tuple

# ───────────────────────────── class names ──────────────────────────────
CLASSES = [
    "tv stand","bar counter","bench","bookshelf","cabinet","chair","chair-bed",
    "coffee table","desk","dining table","fireplace","floor lamp","floor plant",
    "floor vase","kitchen island","modular kitchen","ottoman","rocking chair",
    "rug","shelves","side table","sideboard","sofa","stool","wardrobe",
    "armchair","window","door","shelf",
]
STANDARD_CLASSES: List[str] = []
for c in CLASSES:
    s = re.sub(r"[^a-z0-9]+", "_", c.lower()).strip("_")
    STANDARD_CLASSES.append(s)
    if s.endswith("s"): STANDARD_CLASSES.append(s[:-1])   # singular form

def standardise(txt: str) -> str:
    txt = re.sub(r"[^a-z0-9]+", "_", txt.lower())
    return re.sub(r"_+", "_", txt).strip("_")

def base_name(n: str) -> str:
    n = standardise(n)
    n = re.sub(r"_\d+$", "", n)
    return n[:-1] if n.endswith("s") else n

# ───────────────────────────── regexes ──────────────────────────────────
OBJ_HEADER_RE = re.compile(r"^\s*\d+\.\s*\*\*(?P<name>[^*]+?)\*\*", re.I)
LOCATION_RE   = re.compile(r"Location:\s*(?P<loc>.+)",               re.I)
NUM_RE        = re.compile(r"~?([\d.]+)\s*meters?",                 re.I)
ROOM_SIZE_RE1 = re.compile(
    r"Approximately\s*(?P<w>[\d.]+)\s*(?:meters?|m)?\s*(?:by|x|×)\s*"
    r"(?P<h>[\d.]+)\s*(?:meters?|m)?", re.I)
ROOM_SIZE_RE2 = re.compile(r"Estimated (?:Overall )?Room Size.*?([\d.]+).*?(\d[\d.]*)", re.I)

# ───────────────────────────── containers ──────────────────────────────
class ParsedObject:
    __slots__ = ("name","raw_location","length","width")
    def __init__(self, raw_name: str):
        raw_name = re.sub(r"\s*\(.*?\)","", raw_name)     # strip "(4)"
        self.name  : str            = standardise(raw_name)
        self.raw_location: Optional[str] = None
        self.length: Optional[float]    = None
        self.width : Optional[float]    = None

class CaptionData:
    def __init__(self):
        self.objects   : Dict[str, ParsedObject]       = {}
        self.room_dims : Optional[Tuple[float,float]] = None

# ─────────────────────────── parse helpers ─────────────────────────────
def parse_dims(line: str) -> Tuple[Optional[float], Optional[float]]:
    if "dimension" not in line.lower(): return None, None
    nums = [float(n) for n in NUM_RE.findall(line)]
    if not nums: return None, None
    if "diameter" in line.lower(): return nums[0], nums[0]
    if len(nums)==1:
        if re.search(r"long", line, re.I): return nums[0], None
        if re.search(r"wide|deep", line, re.I): return None, nums[0]
        return nums[0], None
    nums.sort(reverse=True)
    return nums[0], nums[1]

# ─────────────────────────── caption parser ────────────────────────────
def parse_caption(path: Path) -> CaptionData:
    cd = CaptionData(); current: List[ParsedObject] = []

    for raw in path.read_text("utf-8").splitlines():
        line = raw.strip()

        # object header ----------------------------------------------------
        if m := OBJ_HEADER_RE.match(line):
            current = []
            for nm in re.split(r"\s*(?:and|,)\s*", m.group("name")):
                nm = nm.strip();  0
                if not nm: continue
                mult = re.search(r"\((\d+)\)", nm)
                k, base = (int(mult.group(1)), re.sub(r"\s*\(\d+\)","", nm).strip()) if mult else (1, nm)
                for i in range(1, k+1):
                    obj = ParsedObject(f"{base}_{i}" if k>1 else base)
                    cd.objects[obj.name] = obj
                    current.append(obj)
            continue

        # room dimensions --------------------------------------------------
        if rs := (ROOM_SIZE_RE1.search(line) or ROOM_SIZE_RE2.search(line)):
            cd.room_dims = (
                (float(rs.group("w")), float(rs.group("h")))
                if "w" in rs.groupdict()
                else (float(rs.group(1)), float(rs.group(2)))
            )

        if not current: continue

        # location & dimensions -------------------------------------------
        if loc := LOCATION_RE.search(line):
            txt = loc.group("loc").strip().lower()
            for o in current: o.raw_location = txt

        L, W = parse_dims(line)
        if L is not None or W is not None:
            for o in current:
                if L is not None: o.length = L
                if W is not None: o.width  = W
    return cd

# ─────────────────────────── ground‑truth loader ───────────────────────
def load_gt(p: Path) -> Tuple[Dict[str,dict],Tuple[float,float,float]]:
    data = json.loads(p.read_text("utf-8"))
    room = next(e["room_dimensions"] for e in data if "room_dimensions" in e)
    objs = {standardise(e["new_object_id"]): e for e in data if "new_object_id" in e}
    return objs, tuple(room)  # type: ignore

# ─────────────────────────── spatial helpers ───────────────────────────
def classify_loc(x:float,y:float,W:float,H:float,t:float)->str:
    if x<=t*W and y<=t*H:               return "top left corner"
    if x<=t*W and y>=(1-t)*H:           return "bottom left corner"
    if x>=(1-t)*W and y<=t*H:           return "top right corner"
    if x>=(1-t)*W and y>=(1-t)*H:       return "bottom right corner"
    lab=[]
    if x<=t*W:      lab.append("left wall")
    elif x>=(1-t)*W:lab.append("right wall")
    if y<=t*H:      lab.append("top wall")
    elif y>=(1-t)*H:lab.append("bottom wall")
    return " and ".join(lab) if lab else "center"

_LOC_SYNONYMS = {"back wall":"top wall","front wall":"bottom wall","centre":"center"}
def loc_matches(desc:Optional[str],label:str)->bool:
    if not desc: return False
    d = desc.lower()
    for k,v in _LOC_SYNONYMS.items(): d = d.replace(k,v)
    if label in d: return True
    if "corner" in label: return all(w in d for w in label.split())
    if "wall"   in label: return all(w in d for w in label.split() if w!="and")
    return False

# ─────────────────────────── object matching ───────────────────────────
def choose_gt(cn:str, co:ParsedObject, gt:Dict[str,dict], W:float, H:float, t:float)->Optional[str]:
    if cn in gt: return cn
    for cls in STANDARD_CLASSES:
        if cls in cn:
            cand = [g for g in gt if cls in g]
            if cand:
                if co.raw_location:
                    for g in cand:
                        if classify_loc(gt[g]["position"]["x"],gt[g]["position"]["y"],W,H,t) in co.raw_location:
                            return g
                return cand[0]
    bn = base_name(cn)
    cand = [g for g in gt if base_name(g)==bn]
    if cand:
        if co.raw_location:
            for g in cand:
                if classify_loc(gt[g]["position"]["x"],gt[g]["position"]["y"],W,H,t) in co.raw_location:
                    return g
        return cand[0]
    for g in gt:
        sg = standardise(g)
        if bn in sg or sg in bn: return g
    return None

# ─────────────────────────── eval 1 scene ──────────────────────────────
def eval_scene(cd:CaptionData, gt:Dict[str,dict], dims:Tuple[float,float,float],
               *, wall_tol:float, ratio_tol:float, dim_tol:float)->Dict[str,int]:
    W,H,_ = dims
    m = {k:0 for k in (
        "total_gt","objects_correct","location_correct",
        "length_checked","length_correct","width_checked","width_correct","room_ratio_correct")}
    m["total_gt"] = len(gt)

    name_map = {}
    for cn,co in cd.objects.items():
        gid = choose_gt(cn,co,gt,W,H,wall_tol)
        if gid: name_map[cn]=gid
    m["objects_correct"] = len(name_map)

    # location & sizes
    for cn,gid in name_map.items():
        if loc_matches(cd.objects[cn].raw_location,
                       classify_loc(gt[gid]["position"]["x"],gt[gid]["position"]["y"],W,H,wall_tol)):
            m["location_correct"] += 1
        po = cd.objects[cn]
        gs = gt[gid]["size_in_meters"]
        gL,gW = max(gs["length"],gs["width"]), min(gs["length"],gs["width"])
        if po.length is not None:
            m["length_checked"] += 1
            if abs(po.length-gL)<=dim_tol or abs(po.length-gW)<=dim_tol:
                m["length_correct"] += 1
        if po.width is not None:
            m["width_checked"] += 1
            if abs(po.width-gW)<=dim_tol or abs(po.width-gL)<=dim_tol:
                m["width_correct"] += 1

    # room aspect ratio
    if cd.room_dims and min(cd.room_dims)>0 and min(W,H)>0:
        r_desc = max(cd.room_dims)/min(cd.room_dims)
        r_gt   = max(W,H)/min(W,H)
        if abs(r_desc-r_gt) <= ratio_tol:
            m["room_ratio_correct"] = 1
    return m

# ─────────────────────────── reporting ────────────────────────────────
def safe_div(num:int, den:int)->str:
    return f"{num}/{den or 1}"

def make_table(scenes:Dict[str,Dict[str,int]])->str:
    hdr = ["Scene","Objects_recognised","Objects_locations","Objects_length","Objects_width","RoomRatio"]
    col_w = [max(len(h), 10) for h in hdr]
    rows  : List[List[str]] = []

    for sid, m in sorted(scenes.items(), key=lambda x: int(x[0])):
        row = [
            sid,
            safe_div(m["objects_correct"],  m["total_gt"]),
            safe_div(m["location_correct"], m["objects_correct"]),
            safe_div(m["length_correct"],   m["length_checked"]),
            safe_div(m["width_correct"],    m["width_checked"]),
            str(m["room_ratio_correct"]),
        ]
        rows.append(row)
        for i,v in enumerate(row): col_w[i] = max(col_w[i], len(v))

    fmt = "  ".join(f"{{:<{w}}}" for w in col_w)
    return "\n".join([fmt.format(*hdr),
                      fmt.format(*("-"*w for w in col_w)),
                      *[fmt.format(*r) for r in rows]])

# ─────────────────────────── main ──────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser("InternVL caption evaluator (no clearance)")
    ap.add_argument("--text_dir",       type=Path, required=True)
    ap.add_argument("--json_dir",       type=Path, required=True)
    ap.add_argument("--out",            type=Path, default=Path("final_metrics.txt"))
    ap.add_argument("--wall_tol",       type=float, default=0.5)
    ap.add_argument("--dim_tol",        type=float, default=0.5)
    ap.add_argument("--room_ratio_tol", type=float, default=0.5)
    args = ap.parse_args()

    scenes: Dict[str,Dict[str,int]] = {}
    agg    = dict.fromkeys([
        "objects_correct","total_gt","location_correct",
        "length_correct","length_checked","width_correct",
        "width_checked","room_ratio_correct"], 0)

    for txt in sorted(args.text_dir.glob("*.txt")):
        sid = txt.stem
        gt_files = list(args.json_dir.glob(f"{sid}_*_3d.json"))
        if not gt_files:
            print(f"[WARN] No GT for {sid}"); continue
        cd   = parse_caption(txt)
        gt,d = load_gt(gt_files[0])
        m    = eval_scene(cd,gt,d,
                          wall_tol=args.wall_tol,
                          ratio_tol=args.room_ratio_tol,
                          dim_tol=args.dim_tol)
        scenes[sid] = m
        for k in agg: agg[k] += m[k]

    def safe_div(num: int, den: int) -> str:
        """return 'a/b' (den==0 ⇒ '0/0')"""
        return f"{num}/{den or 1}"
    
    def safe_pct(num: int, den: int) -> str:
        """return percentage string or 'n/a' when denominator is 0"""
        return f"{(100 * num / den):5.1f}%" if den else "n/a"
    
    # table & summary -----------------------------------------------------
    report = make_table(scenes)
    
    summary = (
        "\n  Final metrics  \n"
        f"Objects recognised        : {safe_div(agg['objects_correct'], agg['total_gt'])}"
        f"  ({safe_pct(agg['objects_correct'], agg['total_gt'])})\n"
        f"Correct object locations  : {safe_div(agg['location_correct'], agg['objects_correct'])}"
        f"  ({safe_pct(agg['location_correct'], agg['objects_correct'])})\n"
        f"Objects length        : {safe_div(agg['length_correct'], agg['length_checked'])}"
        f"  ({safe_pct(agg['length_correct'], agg['length_checked'])})\n"
        f"Objects width          : {safe_div(agg['width_correct'],  agg['width_checked'])}"
        f"  ({safe_pct(agg['width_correct'],  agg['width_checked'])})\n"
        f"Room ratio correct        : {safe_div(agg['room_ratio_correct'], len(scenes))}"
        f"  ({safe_pct(agg['room_ratio_correct'], len(scenes))})\n"
    )
    
    args.out.write_text(report + summary, "utf-8")
    print(report + summary)
    print(f"\nMetrics saved to {args.out}")

if __name__ == "__main__":
    main()
