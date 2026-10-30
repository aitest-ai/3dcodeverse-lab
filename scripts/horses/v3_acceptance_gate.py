#!/usr/bin/env python3
"""Game-ready V3 horse candidate acceptance gate.

This is a structural + provenance gate, NOT an automatic artistic score.
Reviewers must inspect Blender renders and independently sign off animation
contact and anatomy before promoting a model. Never trust a claimed license
unless a recorded source page has been verified by a reviewer.
"""
from pathlib import Path
import argparse,hashlib,json,struct

def glb(path):
    blob=path.read_bytes()
    if len(blob)<1000:raise ValueError("GLB unexpectedly small")
    magic,version,total=struct.unpack_from("<4sII",blob,0)
    if magic!=b"glTF" or version!=2 or total!=len(blob):raise ValueError("Invalid GLB v2")
    n,kind=struct.unpack_from("<I4s",blob,12)
    if kind!=b"JSON":raise ValueError("No GLB JSON chunk")
    return json.loads(blob[20:20+n]),hashlib.sha256(blob).hexdigest(),len(blob)

def run(model,source_info=None):
    path=Path(model)
    data,sha,size=glb(path)
    meshes=data.get("meshes",[])
    skins=data.get("skins",[])
    anim=data.get("animations",[])
    textures=data.get("images",[])
    mats=data.get("materials",[])
    accessors=data.get("accessors",[])
    prims=[p for m in meshes for p in m.get("primitives",[])]
    tri=sum(accessors[p["indices"]]["count"]//3 for p in prims if "indices" in p and p["indices"]<len(accessors))
    names={a.get("name","").lower() for a in anim}
    bones=max([len(s.get("joints",[])) for s in skins],default=0)
    weighted=any("JOINTS_0" in p.get("attributes",{}) and "WEIGHTS_0" in p.get("attributes",{}) for p in prims)
    uv=any("TEXCOORD_0" in p.get("attributes",{}) for p in prims)
    has_normal=any("normalTexture" in m for m in mats)
    has_albedo=any("baseColorTexture" in m.get("pbrMetallicRoughness",{}) for m in mats)
    reasons=[]
    if tri<18000:reasons.append("NO_HIGH_DETAIL_SOURCE: fewer than 18,000 polygons")
    if not skins or not weighted or bones<35:reasons.append("NO_ANIMATABLE_SKIN: need proper quadruped bone weights and 35+ joints")
    for expected in ("gallop","walk","idle"):
        if not any(expected in n for n in names):reasons.append("MISSING_ACTION:"+expected)
    if not uv or len(textures)<2 or not has_albedo or not has_normal:
        reasons.append("MISSING_PBR_TEXTURE_SET: must have UVs, albedo, normal and >=2 embedded images")
    meta=source_info or {}
    if meta.get("source_license_verified_by_human") is not True:
        reasons.append("SOURCE_LICENSE_NOT_HUMAN_VERIFIED")
    if meta.get("source_sha256_verified") is not True:
        reasons.append("SOURCE_SHA256_NOT_VERIFIED")
    if meta.get("anatomy_approved_by_human") is not True:
        reasons.append("HORSE_ANATOMY_NOT_VISUALLY_APPROVED")
    if meta.get("full_gallop_motion_approved_by_human") is not True:
        reasons.append("GALLOP_GAIT_AND_CONTACT_NOT_VISUALLY_APPROVED")
    result={
        "schema_version":1,"input":path.name,"sha256":sha,"bytes":size,
        "triangle_count":tri,"meshes":len(meshes),"skins":len(skins),
        "largest_skin_joints":bones,"animations":len(anim),
        "named_clips":sorted(names),"images":len(textures),"materials":len(mats),
        "has_uv":uv,"has_weights":weighted,"has_albedo_texture":has_albedo,
        "has_normal_texture":has_normal,"status":"V3_APPROVED" if not reasons else "V3_REJECTED_OR_PENDING",
        "blockers":reasons,
        "note":"Visual quality cannot be proven by triangle count; every approval requires actual model render review."
    }
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("model")
    p.add_argument("--source",help="Source/provenance JSON with independent human signoff")
    p.add_argument("--output",help="Output JSON path")
    args=p.parse_args()
    info=json.loads(Path(args.source).read_text()) if args.source else None
    result=run(args.model,info)
    if args.output:Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))
