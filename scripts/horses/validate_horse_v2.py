"""Horse V2 GLB audit against preserved 13-clip Quaternius source.
Geometry count, armature, animation names, PBR factor and file integrity.
"""
import json
import struct
import sys
from pathlib import Path

old=Path(sys.argv[1]);new=Path(sys.argv[2])
def parse(path):
    data=path.read_bytes()
    magic,version,size=struct.unpack_from("<4sII",data,0)
    assert magic==b"glTF" and version==2 and size==len(data),(path,"bad GLB")
    n,kind=struct.unpack_from("<I4s",data,12)
    assert kind==b"JSON"
    return json.loads(data[20:20+n])
old_doc=parse(old)
new_doc=parse(new)
old_names={a.get("name") for a in old_doc.get("animations",[])}
new_names={a.get("name") for a in new_doc.get("animations",[])}
if len(old_names)!=13 or old_names!=new_names:
    raise RuntimeError("V2 lost or renamed animation clips: "+str((old_names,new_names)))
skins=new_doc.get("skins",[])
if len(skins)!=1 or len(skins[0].get("joints",[]))<45:
    raise RuntimeError("V2 lost quadruped skin")
old_tris=sum(old_doc["accessors"][p["indices"]]["count"]//3
            for m in old_doc.get("meshes",[]) for p in m.get("primitives",[])
            if "indices" in p)
new_tris=sum(new_doc["accessors"][p["indices"]]["count"]//3
            for m in new_doc.get("meshes",[]) for p in m.get("primitives",[])
            if "indices" in p)
if new_tris < old_tris*2:
    raise RuntimeError("Actual GLB polygon complexity did not increase enough: "+str((old_tris,new_tris)))
prims=[p for m in new_doc.get("meshes",[]) for p in m.get("primitives",[])]
if not any("JOINTS_0" in p.get("attributes",{}) and "WEIGHTS_0" in p.get("attributes",{})
           for p in prims):
    raise RuntimeError("No GLB skin weights after surface subdivision")
mat=new_doc.get("materials",[])
if len(mat)<7:raise RuntimeError("Horse materials missing")
pbr={m.get("name",""):m.get("pbrMetallicRoughness",{}) for m in mat}
if "Main" not in pbr or pbr["Main"].get("roughnessFactor",1)>=.5:
    raise RuntimeError("Coat material gloss upgrade missing from actual GLB")
folder=new.parent
for name in ("side","front","back","isometric"):
    pic=folder/("V2_"+name+".png")
    if not pic.is_file() or pic.stat().st_size<10000:
        raise RuntimeError("Blender rendered image missing: "+str(pic))
result={
 "status":"STRUCTURAL_PASS_VISUAL_REVIEW_REQUIRED",
 "source_triangle_count":old_tris,
 "v2_triangle_count":new_tris,
 "triangle_multiplier":round(new_tris/max(1,old_tris),2),
 "skin_count":len(skins),
 "joint_count":len(skins[0]["joints"]),
 "original_actions":len(old_names),
 "v2_actions":len(new_names),
 "preserved_animation_names":sorted(new_names),
 "material_count":len(mat),
 "v2_coat_roughness":pbr["Main"].get("roughnessFactor"),
 "visual_review":"Required for silhouette, hoof anatomy, gait and hair"
}
(folder/"v2_validation.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
print("HORSE_V2_GLB_AUDIT",json.dumps(result,ensure_ascii=False),flush=True)
