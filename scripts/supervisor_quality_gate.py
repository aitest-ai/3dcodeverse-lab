#!/usr/bin/env python3
"""Fail-closed two-layer quality supervision for 3DCodeVerse GLB releases.

Technical tests automatically check GLB map plumbing and actual render files.
Artistic acceptance is a separately authored, model-hash-bound visual review.
No pixel heuristic is marketed as reliable artistic judgement.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import pathlib
import statistics
import struct
import sys
from PIL import Image, ImageStat

CRITERIA = (
    "bear_anatomy_and_silhouette",
    "face_and_expression",
    "salmon_shape_and_bite",
    "carving_detail_and_wood",
    "paws_and_limbs",
    "multi_view_presentation",
)
MIN_PER_CRITERION = 3.0
MIN_MEAN = 4.0

def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def glb_info(path: pathlib.Path) -> dict:
    with path.open("rb") as f:
        h = f.read(20)
        if len(h) < 20:
            raise ValueError("short glb")
        magic, version, total, chunk_len, chunk_type = struct.unpack("<IIIII", h)
        if (magic,version) != (0x46546c67,2) or total != path.stat().st_size or chunk_type != 0x4E4F534A:
            raise ValueError("not valid glTF 2.0 GLB container")
        data = json.loads(f.read(chunk_len))
    materials = data.get("materials",[])
    pbr = [m for m in materials if m.get("normalTexture") and
        m.get("pbrMetallicRoughness",{}).get("baseColorTexture") and
        m.get("pbrMetallicRoughness",{}).get("metallicRoughnessTexture")]
    ao = [m for m in pbr if m.get("occlusionTexture")]
    return {"mesh_count":len(data.get("meshes",[])),
        "material_count":len(materials),"texture_count":len(data.get("textures",[])),
        "embedded_image_count":len([i for i in data.get("images",[]) if "bufferView" in i]),
        "pbr_material_count":len(pbr),"ao_material_count":len(ao)}

def image_info(path: pathlib.Path) -> dict:
    with Image.open(path) as im:
        rgb = im.convert("RGB")
        stat = ImageStat.Stat(rgb)
        entropy = rgb.entropy()
        width,height = rgb.size
        return {"width":width,"height":height,
            "entropy":round(entropy,3),
            "mean_rgb":[round(v,1) for v in stat.mean],
            "std_rgb":[round(v,1) for v in stat.stddev]}

def audit(model: pathlib.Path, hero: pathlib.Path, side: pathlib.Path, review_path: pathlib.Path, allow_untextured_sculpt: bool = False) -> dict:
    technical=[]
    def gate(name, ok, details):
        technical.append({"name":name,"passed":bool(ok),"details":details})

    model_digest=sha256(model); hero_digest=sha256(hero); side_digest=sha256(side)
    try:
        info=glb_info(model)
        gate("valid_glb_2",True,info)
        gate("genuine_pbr_channels_or_raw_sculpt",allow_untextured_sculpt or bool(info["pbr_material_count"] and info["ao_material_count"] and
            info["embedded_image_count"]>=3),info)
    except Exception as exc:
        info={"error":str(exc)}
        gate("valid_glb_2",False,info)
        gate("genuine_pbr_channels_or_raw_sculpt",False,info)

    images={}
    for key,path in (("hero",hero),("side",side)):
        try:
            images[key]=image_info(path)
            im=images[key]
            gate("render_"+key, im["width"]>=640 and im["height"]>=480 and
                im["entropy"]>=3.2 and max(im["std_rgb"])>12, im)
        except Exception as exc:
            gate("render_"+key,False,{"error":str(exc)})

    model_key={"model_sha256":model_digest,
        "hero_sha256":hero_digest,"side_sha256":side_digest}
    try:
        review=json.loads(review_path.read_text(encoding="utf-8"))
    except Exception as exc:
        review={"review_status":"unreviewed","error":str(exc)}

    tied = all(review.get(k)==v for k,v in model_key.items())
    gate("review_hashes_match_exact_assets",tied,{
        "expected":model_key,
        "review_sha_match":{k:review.get(k)==v for k,v in model_key.items()}})

    items=review.get("criteria",{})
    scores={}
    notes={}
    for name in CRITERIA:
        item=items.get(name,{})
        score=item.get("score")
        if type(score) not in (int,float) or not math.isfinite(score) or not 0<=score<=5:
            score=None
        scores[name]=score
        notes[name]=item.get("reason","No reviewer comment")

    scored=all(v is not None for v in scores.values())
    average=statistics.mean(scores.values()) if scored else None
    blockers=[d for d in review.get("defects",[]) if d.get("severity") in ("blocker","critical")]
    visual_pass=(tied and review.get("review_status")=="approved" and scored and
        average>=MIN_MEAN and min(scores.values())>=MIN_PER_CRITERION and not blockers)
    gate("reviewed_artistic_quality",visual_pass,{
        "status":review.get("review_status"),"mean":average,
        "scores":scores,"minimum_each":MIN_PER_CRITERION,"minimum_mean":MIN_MEAN,
        "blocker_count":len(blockers),"note":"Requires visually inspected reviewer judgement, not image-statistic aesthetics."
    })
    approved=all(t["passed"] for t in technical)
    return {"schema":"3dcodeverse-art-supervision/v1","decision":"APPROVED" if approved else "REJECTED",
        "model":str(model),"review_file":str(review_path),"asset_hashes":model_key,
        "technical_gates":technical,"visual_review":{"status":review.get("review_status"),
            "scores":scores,"average":average,"notes":notes,
            "defects":review.get("defects",[]),"reviewer":review.get("reviewer"),
            "improvement_tasks":review.get("improvement_tasks",[])},
        "rule":"Only model-linked human/AI-vision inspections can approve shape/material aesthetics. Never equate technical GLB success with artistic acceptance."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--model",type=pathlib.Path,required=True)
    p.add_argument("--hero",type=pathlib.Path,required=True)
    p.add_argument("--side",type=pathlib.Path,required=True)
    p.add_argument("--review",type=pathlib.Path,required=True)
    p.add_argument("--report",type=pathlib.Path,required=True)
    p.add_argument("--allow-untextured-sculpt",action="store_true",help="For upstream raw geometry candidates ONLY; still needs visual approval.")
    a=p.parse_args()
    report=audit(a.model,a.hero,a.side,a.review,a.allow_untextured_sculpt)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SUPERVISOR_RESULT",report["decision"],file=sys.stderr)
    for item in report["technical_gates"]:
        print(("PASS" if item["passed"] else "FAIL")+" "+item["name"],file=sys.stderr)
    if report["decision"]!="APPROVED":
        print("ARTWORK NOT APPROVED: keeping the candidate out of release.",file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    sys.exit(main())
