#!/usr/bin/env python3
"""V29: 本機騎姿接觸證據量測；不修改遊戲、也不核准道路。"""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, struct, sys
from collections import defaultdict

ACTOR_SHA="4dab76c398f4c30c3aa62ef88e389b28974018c01fd271c08bf029d840d263d1"
BIKE_SHA="7cb53e92247cf081354c1551b91ae812aab56be7c07748ed00764f0d2c844ece"
SCHEMA="setouchi.pose_contact.capture.v1"
PAIRS={
 "left_hand_to_grip":("rider_hand_left","bike_grip_left"),
 "right_hand_to_grip":("rider_hand_right","bike_grip_right"),
 "left_foot_to_pedal":("rider_foot_left","bike_pedal_left"),
 "right_foot_to_pedal":("rider_foot_right","bike_pedal_right"),
}
PHASES=("straight","turn","start_stop")
def require(ok,msg):
 if not ok: raise ValueError(msg)
def sha256(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def inspect_glb(path, expected, label):
 path=pathlib.Path(path)
 require(path.is_file(),f"{label} GLB 不存在")
 require(sha256(path)==expected,f"{label} SHA256 不符")
 with path.open("rb") as f:
  header=f.read(20)
  require(len(header)==20,f"{label} GLB 標頭太短")
  magic,version,total,n,chunk=struct.unpack("<4sIIII",header)
  require(magic==b"glTF" and version==2 and total==path.stat().st_size,f"{label} GLB 格式不符")
  require(chunk==0x4e4f534a and n<=40_000_000,"GLB JSON 區段錯誤")
  data=json.loads(f.read(n).decode("utf8").rstrip(" \0"))
 return {"label":label,"sha256_verified":True,
         "nodes_count":len(data.get("nodes",[])),
         "meshes_count":len(data.get("meshes",[])),
         "animation_clip_names":[str(a.get("name","")) for a in data.get("animations",[])],
         "node_name_candidates":[str(n.get("name","")) for n in data.get("nodes",[])
                 if any(s in str(n.get("name","")).lower() for s in ("hand","wrist","foot","ankle","grip","pedal","crank"))][:80]}
def vec(value,label):
 require(isinstance(value,list) and len(value)==3,f"{label} 須為世界座標 [x,y,z]")
 require(all(isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v)
         and abs(v)<1_000_000 for v in value),f"{label} 無效／無限值")
 return tuple(float(v) for v in value)
def quantile(vals,q):
 v=sorted(vals);x=(len(v)-1)*q;a=math.floor(x);b=math.ceil(x)
 return v[a] if a==b else v[a]*(b-x)+v[b]*(x-a)
def stats(vals):
 return {"samples":len(vals),"median_mm":round(quantile(vals,.5),3),
         "p95_mm":round(quantile(vals,.95),3),"max_mm":round(max(vals),3)}
def analyse_capture(d,verified_glbs=False):
 require(isinstance(d,dict) and d.get("schema")==SCHEMA,"V29 JSON schema 不符")
 require(d.get("source") in ("synthetic","runtime_capture"),"來源型別不符")
 require(d.get("coordinate_system")=="THREE_WORLD_METERS","須同一 Three.js 世界座標")
 require(d.get("player_animation")=="Cycle","需為原版 Cycle 動畫")
 a=d.get("asset_sha256",{})
 require(isinstance(a,dict) and a.get("actor_glb")==ACTOR_SHA and a.get("bike_glb")==BIKE_SHA,
         "原始人車 SHA256 不符")
 env=d.get("environment",{})
 require(isinstance(env,dict),"環境記錄缺失")
 real=d["source"]=="runtime_capture"
 if real:
  require(env.get("webgl2") is True and env.get("capture_method")=="live_scene_world_matrices"
          and isinstance(env.get("browser"),str) and len(env["browser"].strip())>=3,
          "真實騎姿必須實際 WebGL2 世界座標；不可由 DOM 冒充")
 frames=d.get("frames",[])
 require(isinstance(frames,list) and 3<=len(frames)<=30000,"須有 3~30000 幀")
 distances={k:[] for k in PAIRS}
 by_phase=defaultdict(lambda:{k:[] for k in PAIRS})
 phases=[];times=[]
 for i,f in enumerate(frames):
  require(isinstance(f,dict),"frame 必須是物件")
  t=f.get("t_s")
  require(isinstance(t,(int,float)) and not isinstance(t,bool) and math.isfinite(t)
          and t>=0 and (not times or t>times[-1]),"t_s 必須是嚴格遞增的有限正值")
  times.append(float(t))
  phase=f.get("phase")
  require(phase in PHASES,"phase 須明確標記 straight/turn/start_stop")
  if phase not in phases:phases.append(phase)
  markers=f.get("markers",{})
  require(isinstance(markers,dict),"markers 缺失")
  for key,(aa,bb) in PAIRS.items():
   p=vec(markers.get(aa),f"frame {i} {aa}")
   q=vec(markers.get(bb),f"frame {i} {bb}")
   mm=math.dist(p,q)*1000
   distances[key].append(mm);by_phase[phase][key].append(mm)
 sufficient=len(frames)>=30 and "straight" in phases and "turn" in phases and times[-1]-times[0]>=2
 status=("SYNTHETIC_UNIT_TEST_ONLY" if not real else
         "REAL_CAPTURE_INSUFFICIENT_FRAMES_NOT_APPROVED" if not sufficient else
         "REAL_CAPTURE_GLBS_UNVERIFIED_NOT_APPROVED" if not verified_glbs else
         "REAL_CAPTURE_SHA_VERIFIED_MANUAL_REVIEW_REQUIRED")
 return {"schema":"setouchi.pose_contact.report.v1","version":"V29",
         "status":status,"source_type":d["source"],
         "glb_bytes_sha_verified_in_this_run":bool(verified_glbs),
         "frame_count":len(frames),"duration_s":round(times[-1]-times[0],4),
         "phases_present":phases,
         "distances_mm":{k:stats(v) for k,v in distances.items()},
         "by_phase_mm":{ph:{k:stats(v) for k,v in sub.items()} for ph,sub in by_phase.items()},
         "review_only":{"actor_looks_correct":None,"hands_grip_accepted_by_human":None,
          "feet_pedals_accepted_by_human":None,"camera_verified_in_webgl2":None,
          "real_road_surface_verified":False,"legal_bicycle_road_access_verified":False,
          "collision_verified":False,"rideable_route_approved":False,
          "main_or_website_modified":False},
         "limitations":"Distance math only; original WebGL2 poses, bike transforms and real road conditions remain unverified."}
def main(argv=None):
 p=argparse.ArgumentParser(description="V29 local pose-contact QA, no gameplay modifications")
 p.add_argument("--capture",type=pathlib.Path)
 p.add_argument("--actor-glb",type=pathlib.Path)
 p.add_argument("--bike-glb",type=pathlib.Path)
 p.add_argument("--output",type=pathlib.Path)
 args=p.parse_args(argv)
 try:
  require(bool(args.actor_glb)==bool(args.bike_glb),"原人物/單車須同時提供")
  require(bool(args.capture) or bool(args.actor_glb),"至少提供 capture 或兩個 GLB")
  glbs=[inspect_glb(args.actor_glb,ACTOR_SHA,"actor"),inspect_glb(args.bike_glb,BIKE_SHA,"bike")] if args.actor_glb else []
  if glbs:require("Cycle" in glbs[0]["animation_clip_names"],"原人物不存在 Cycle 動畫")
  if args.capture:
   report=analyse_capture(json.loads(args.capture.read_text(encoding="utf8")),bool(glbs))
   if glbs:report["glb_structure_inspected_locally"]=glbs
  else:
   report={"schema":"setouchi.pose_contact.report.v1","version":"V29",
           "status":"SOURCE_GLBS_INSPECTED_NO_LIVE_POSE_CAPTURE",
           "glb_structure_inspected_locally":glbs,"rideable_route_approved":False}
  out=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
  if args.output:
   args.output.parent.mkdir(parents=True,exist_ok=True)
   args.output.write_text(out,encoding="utf8")
  print(out,end="")
  return 0
 except (ValueError,OSError,json.JSONDecodeError) as e:
  print("V29 安全檢查拒絕："+str(e),file=sys.stderr)
  return 2
if __name__=="__main__":raise SystemExit(main())
