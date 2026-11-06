"""Freeze explicit float32 local TRS text. Run only for inspected authoring output."""
import hashlib,json,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from v05.overlay import read
D=R/'motion-v15';D.mkdir(exist_ok=True);doc,_=read(R/'library-v14/horse-brown-walk-smooth-review/0.1.0/model.glb');lock={}
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
for name in ['RestartWalk','WalkTurnLeft','WalkTurnRight']:
 dst=D/(name+'.json');assert not dst.exists(),'Refuse overwrite'
 c=json.loads((R/'work/v15/authoring'/('horse-brown-'+name+'-curves.json')).read_text());tracks=[]
 for node in c['frames'][0]:
  track={'node':int(node),'name':doc['nodes'][int(node)]['name']}
  for prop in ['translation','rotation','scale']:
   values=[[f32(x) for x in f[node][prop]] for f in c['frames']]
   track[prop]={'constant':values[0]} if all(v==values[0] for v in values) else {'values':values}
  tracks.append(track)
 dst.write_text(json.dumps({'schema':1,'source':'v14 native Walk and StandStopped; no foreign skeleton','units':'native glTF local TRS; display calibration exactly once','clips':[{'name':name,'times':c['times'],'nodes':tracks}]},separators=(',',':'))+'\n')
 lock[name]=hashlib.sha256(dst.read_bytes()).hexdigest();print(name,dst.stat().st_size,lock[name])
(D/'curves.lock.json').write_text(json.dumps(lock,indent=2)+'\n')
