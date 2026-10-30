#!/usr/bin/env python3
"""Safe, dependency-free cross-agent horse submission checker.

This checks manifest provenance and (when provided) the real GLB.
It deliberately does not execute any submitted Blender source or download
unknown third-party URLs. A passing result is STRUCTURE_ONLY, not final art
or legal approval. Use a human-reviewed PR before publication.
"""
from __future__ import annotations
import argparse,hashlib,json,re,struct,sys
from pathlib import Path
VALID_LICENSES={"CC0-1.0","CC-BY-4.0","CC-BY-3.0","original-private"}
def fail(reason):
    raise ValueError(reason)

def audit(manifest_path:Path,glb_path:Path|None):
    item=json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in ("asset_id","version","creator","license","license_url",
                "source_url","model_file","model_sha256","build","quality"):
        if key not in item:fail("Missing manifest field "+key)
    ident=item["asset_id"]
    if not isinstance(ident,str) or not re.fullmatch("[a-z][a-z0-9-]{2,62}",ident):
        fail("asset_id must be lowercase kebab-case, 3-63 characters")
    if not re.fullmatch(r"\d+\.\d+\.\d+",str(item["version"])):
        fail("version must be semver major.minor.patch")
    if item["license"] not in VALID_LICENSES:
        fail("Unknown/incompatible redistributable license; request owner review")
    for field in ("source_url","license_url"):
        if not str(item[field]).startswith("https://"):fail(field+" must have HTTPS provenance")
    if item.get("redistribution_allowed") is not True:
        fail("No explicit permission to redistribute")
    if not item.get("creator") or item["creator"].startswith("Your AI"):
        fail("Creator placeholder is not attribution")
    if "example." in item["source_url"]:fail("Source URL still a placeholder")
    if item.get("status") not in ("candidate_pending_review","in_review"):
        fail("Submitted model status must be pending review")
    if not re.fullmatch("[0-9a-f]{64}",str(item["model_sha256"])):
        fail("Pinned SHA256 missing or invalid")
    if int(item.get("schema_version",0))!=1:fail("Unsupported manifest schema")
    if item["license"].startswith("CC-BY") and (not item.get("attribution") or "omit" in item["attribution"].lower()):
        fail("CC BY attribution must identify the original creator")
    if "run_id" not in item["build"] or "artifact_name" not in item["build"]:
        fail("Build must specify Actions run_id and artifact_name for verification")
    if not re.fullmatch("[a-zA-Z0-9_-]{3,128}",str(item["build"]["artifact_name"])):
        fail("Unsafe artifact_name")
    p=Path(str(item["model_file"]))
    if p.name!=str(p) or p.suffix.lower()!=".glb":
        fail("model_file must be a safe local basename ending .glb")
    if not isinstance(item.get("quality"),dict):
        fail("Missing quality metadata")
    result={"asset_id":ident,"version":item["version"],"license":item["license"],
            "status":"METADATA_PASS_BINARY_NOT_TESTED"}
    if glb_path is not None:
        with glb_path.open("rb") as file:
            raw=file.read()
        actual_sha=hashlib.sha256(raw).hexdigest()
        if actual_sha!=item["model_sha256"]:fail("SHA256 mismatch: actual "+actual_sha)
        if len(raw)<200 or raw[:4]!=b"glTF":fail("Not GLB")
        magic,version,total=struct.unpack_from("<4sII",raw,0)
        if magic!=b"glTF" or version!=2 or total!=len(raw):
            fail("GLB header or length invalid")
        length,typ=struct.unpack_from("<I4s",raw,12)
        if typ!=b"JSON":fail("No GLB JSON chunk")
        gltf=json.loads(raw[20:20+length])
        clips={a.get("name","") for a in gltf.get("animations",[])}
        expected=item.get("required_clips",["Idle","Walk","Gallop"])
        if item.get("asset_type")=="animated_horse":
            for clip in expected:
                if clip not in clips:fail("Missing animated clip "+str(clip))
            skins=gltf.get("skins",[])
            if not skins or max(len(s.get("joints",[])) for s in skins)<20:
                fail("Missing meaningful horse rig")
            prims=[p for m in gltf.get("meshes",[]) for p in m.get("primitives",[])]
            if not any("JOINTS_0" in p.get("attributes",{}) and "WEIGHTS_0" in p.get("attributes",{}) for p in prims):
                fail("No deforming skin weights in GLB")
        result.update({"status":"STRUCTURE_PASS_HUMAN_REVIEW_REQUIRED","sha256":actual_sha,
                       "file_bytes":len(raw),"mesh_count":len(gltf.get("meshes",[])),
                       "animation_clips":sorted(clips),
                       "skins":len(gltf.get("skins",[])),
                       "images":len(gltf.get("images",[]))})
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest",type=Path)
    ap.add_argument("--glb",type=Path,help="Local GLB for full structural and hash verification")
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    try:
        result=audit(args.manifest,args.glb)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
        print("HORSE_SUBMISSION_QA",json.dumps(result,ensure_ascii=False))
    except (ValueError,OSError,KeyError,TypeError) as e:
        print("HORSE_SUBMISSION_REJECTED",str(e),file=sys.stderr)
        sys.exit(1)
