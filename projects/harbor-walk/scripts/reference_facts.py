"""Read headers/retained inventories only; never launch the reference executable."""
from pathlib import Path
import json,hashlib,collections,re
ROOT=Path(__file__).resolve().parents[1];EX=Path('/workspace/work/reference-extracted/Windows');E=ROOT/'evidence'
b=(EX/'GirlFishing/Binaries/Win64/GirlFishing-Win64-Shipping.exe').read_bytes()
markers=[]
for s in ['Unreal Engine 5.6.1','++UE5+Release-5.6','++UE5+Release-5.6-CL-44394996']:
 v=s.encode('utf-16le');i=b.find(v);markers.append({'file':'Windows/GirlFishing/Binaries/Win64/GirlFishing-Win64-Shipping.exe','encoding':'UTF-16LE','text':s,'byte_offset':i,'verified':i>=0})
lines=(E/'retoc-paths.txt').read_text().splitlines();paths=[]
for l in lines:
 m=re.match(r'GirlFishing-Windows\s+(\w+)\s+(\w+)\s+(\d+)\s+(.+)',l)
 if m:paths.append({'chunk':m[1],'kind':m[2],'uncompressed_chunk_bytes':int(m[3]),'path':m[4]})
facts={'exe_bytes':len(b),'exe_sha256':hashlib.sha256(b).hexdigest(),'engine_markers':markers,'chunk_kinds':dict(collections.Counter(p['kind'] for p in paths)),'chunk_count':len(paths),'project_paths':sum('/GirlFishing/Content/' in p['path'] for p in paths),'claims_limit':'Names and manifests establish asset presence only, not decoded topology or algorithms.','selected_paths':[p for p in paths if any(x in p['path'] for x in ['Skeleton','PhysicsAsset','BS_Idle_Walk_Run','ABP_Unarmed','xBP/','xUI/UI_','xUI/WBP_Aim'])]}
(E/'reference-facts.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in facts.items() if k!='selected_paths'},indent=2))
