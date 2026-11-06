"""Authoring-only: freeze inspected native TRS samples to explicit float32 text."""
import hashlib,json,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from v05.overlay import read
src=R/'work/v14/pilot3/horse-brown-curves.json';dst=R/'motion-v14/horse-smooth-curves.json'
if dst.exists():raise RuntimeError('Refuse replacing a reviewed recipe')
doc,_=read(R/'library-v13/horse-brown-walk-transition-review/0.1.0/model.glb')
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
clips=[]
for name,c in json.loads(src.read_text()).items():
    tracks=[]
    for node in c['frames'][0]:
        track={'node':int(node),'name':doc['nodes'][int(node)]['name']}
        for prop in ['translation','rotation','scale']:
            values=[[f32(x) for x in frame[node][prop]] for frame in c['frames']]
            track[prop]={'constant':values[0]} if all(v==values[0] for v in values) else {'values':values}
        tracks.append(track)
    clips.append({'name':name,'times':c['times'],'nodes':tracks})
dst.write_text(json.dumps({'schema':1,'native_source':'v13 complete editable mother; original Walk, not foreign motion','method':'1.5% cyclic native TRS Hermite bridge with original seam-pose constraint before contact IK, 240 Hz body-only bake with local 2400 Hz wrap samples','units':'native local glTF TRS; apply documented display calibration once','clips':clips},separators=(',',':'))+'\n')
print(hashlib.sha256(dst.read_bytes()).hexdigest(),dst.stat().st_size)
