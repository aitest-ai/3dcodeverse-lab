#!/usr/bin/env python3
"""Structural acceptance of animated horse GLBs with stdlib, not aesthetic approval."""
import json
import struct
import sys
from pathlib import Path

def inspect(folder):
    folder=Path(folder)
    manifest=json.loads((folder/"asset_manifest.json").read_text(encoding="utf-8"))
    source_report=json.loads((folder/"report.json").read_text(encoding="utf-8"))
    p=folder/manifest["model_file"]
    with p.open("rb") as stream:
        magic,version,size=struct.unpack("<4sII",stream.read(12))
        if magic!=b"glTF" or version!=2 or size!=p.stat().st_size:
            raise RuntimeError("Invalid GLB header")
        length,kind=struct.unpack("<I4s",stream.read(8))
        if kind!=b"JSON":raise RuntimeError("GLB lacks JSON chunk")
        doc=json.loads(stream.read(length))
    meshes=doc.get("meshes",[])
    animations=[a.get("name","") for a in doc.get("animations",[])]
    skins=doc.get("skins",[])
    prims=[primitive for m in meshes for primitive in m.get("primitives",[])]
    if not meshes or not skins:raise RuntimeError("Horse must contain rigged mesh and skin")
    if len(animations)<4:
        raise RuntimeError("Horse GLB lost most animations: "+str(animations))
    if not any("JOINTS_0" in p.get("attributes",{}) and "WEIGHTS_0" in p.get("attributes",{}) for p in prims):
        raise RuntimeError("Horse mesh weights/indices not exported")
    if source_report["source_rig_bones"]<15:raise RuntimeError("No true quadruped skeleton")
    if len(animations)!=source_report["source_animation_count"]:
        raise RuntimeError("Exported animations do not match imported source clips: "+str(animations))
    views=["front","side","back","isometric","motion_a","motion_b"]
    for name in views:
        png=folder/("preview_"+name+".png")
        if not png.exists() or png.stat().st_size<3000:
            raise RuntimeError("Missing real Blender preview "+str(png))
    report={"asset_id":manifest["asset_id"],"status":"STRUCTURE_PASS_visual_anatomy_review_required",
            "source_animation_count":source_report["source_animation_count"],
            "exported_animation_count":len(animations),"animations":animations,
            "mesh_count":len(meshes),"skin_count":len(skins),
            "source_bone_count":source_report["source_rig_bones"],
            "glb_bytes":p.stat().st_size,
            "visual_review_required":True}
    (folder/"validation.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

if __name__=="__main__":inspect(sys.argv[1])
