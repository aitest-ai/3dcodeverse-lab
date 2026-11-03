import sys,json,struct,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'/'blender5'))
from verify_glb_v84 import verify_document,verify_file

nodes=[{'name':'MechaRig','children':[1,2,3]},
       {'name':'weapon_socket.R','children':[4]},
       {'name':'PrimaryCannon_energy_bore'},
       {'name':'PrimaryCannon_outer_barrel'},
       {'name':'MuzzleTip_R'}]
doc={'asset':{'version':'2.0'},'nodes':nodes,
     'skins':[{'joints':list(range(15))}],
     'animations':[{'name':n} for n in ['Idle','Run','Fire','Dodge','Punch','Hit']]}
assert verify_document(doc)['anchor_attached_to_socket']
wrong=json.loads(json.dumps(doc));wrong['nodes'][1]['children']=[];wrong['nodes'][0]['children'].append(4)
try:verify_document(wrong);raise AssertionError('Misparented marker accepted')
except ValueError:pass
wrong2=json.loads(json.dumps(doc));wrong2['skins'][0]['joints']=[0,1]
try:verify_document(wrong2);raise AssertionError('Missing original bones accepted')
except ValueError:pass
s=json.dumps(doc,separators=(',',':')).encode();s+=b' '*((4-len(s)%4)%4)
blob=struct.pack('<4sII',b'glTF',2,20+len(s))+struct.pack('<I4s',len(s),b'JSON')+s
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'candidate.glb';p.write_bytes(blob)
 assert verify_file(p)['animation_count']==6
print('PASS v8.4 GLB ancestry, 15-bone skin, 6 animation clips')
