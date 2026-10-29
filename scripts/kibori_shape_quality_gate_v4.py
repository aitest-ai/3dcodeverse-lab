#!/usr/bin/env python3
"""Fail-closed shape-first 3D asset approval. Requires visual approval tied to exact GLB/renders."""
import argparse,hashlib,json,struct,sys
from pathlib import Path
from PIL import Image
CRITERIA=["bear_silhouette","head_muzzle","jaw_fish_contact","paw_anatomy","carved_surface","view_consistency"]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def audit(folder):
 def no(reason):return {"approved":False,"reason":reason}
 root=Path(folder);model=root/"candidate.glb";hero=root/"hero.png";side=root/"side.png";review=root/"shape_review.json"
 try:
  if not all(p.is_file() for p in (model,hero,side,review)):return no("missing model, two views or visual review")
  d=model.read_bytes()
  if len(d)<256 or d[:4]!=b"glTF" or struct.unpack_from("<I",d,4)[0]!=2 or struct.unpack_from("<I",d,8)[0]!=len(d):return no("invalid GLB 2.0")
  size,typ=struct.unpack_from("<II",d,12)
  if typ!=0x4e4f534a or size<20 or size+20>len(d):return no("invalid GLB JSON")
  obj=json.loads(d[20:20+size])
  if not obj.get("meshes"):return no("GLB missing mesh")
  for path in (hero,side):
   with Image.open(path) as im:
    im.verify()
   with Image.open(path) as im:
    if im.width<640 or im.height<480:return no("insufficient render resolution")
  report=json.loads(review.read_text())
  for key,path in (("model_sha256",model),("hero_sha256",hero),("side_sha256",side)):
   if report.get(key)!=sha(path):return no("review hash mismatch: "+key)
  if report.get("permission_verified") is not True:return no("source permission not established")
  if report.get("review_status")!="APPROVED":return no("visual review not approved")
  if report.get("blocking_defects"):return no("blocking defects remain")
  scores=[report.get("scores",{}).get(k,0) for k in CRITERIA]
  if any(not isinstance(x,(int,float)) or x<3.5 or x>5 for x in scores):return no("criterion score below 3.5")
  if sum(scores)/len(scores)<4.2:return no("mean score below 4.2")
  return {"approved":True,"model_sha256":sha(model),"scores":dict(zip(CRITERIA,scores))}
 except Exception as exc:return no(str(exc)[:400])
if __name__=="__main__":
 parser=argparse.ArgumentParser();parser.add_argument("folder");a=parser.parse_args()
 result=audit(a.folder);print(json.dumps(result,ensure_ascii=False));sys.exit(0 if result["approved"] else 2)
