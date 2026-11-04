#!/usr/bin/env python3
"""Lossless glTF packaging + inventory. Never retarget or resize a model."""
import base64,copy,hashlib,json,struct,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def read_model(p):
 b=p.read_bytes()
 if b[:4]==b'glTF':
  n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);o=20+n;bin=b[o+8:] if o<len(b) else b'';return d,bin,b
 d=json.loads(b);assert len(d['buffers'])==1 and d['buffers'][0]['uri'].startswith('data:');bin=base64.b64decode(d['buffers'][0]['uri'].split(',',1)[1]);return d,bin,None

def package(d,bin):
 d=copy.deepcopy(d);d['buffers']=[{'byteLength':len(bin)}];j=json.dumps(d,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*((-len(j))%4);bin+=b'\0'*((-len(bin))%4);return struct.pack('<III',0x46546C67,2,28+len(j)+len(bin))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(bin),0x004e4942)+bin

def save(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() and p.read_bytes()!=b:raise RuntimeError(f'Refuse overwrite: {p}')
 p.write_bytes(b)
def jsave(p,d):save(p,(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def build():
 reg=json.loads((R/'library-v04/intake.json').read_text());out=[]
 for e in reg['entries']:
  src=R/e['source'];d,bin,raw=read_model(src);assert sha(src.read_bytes())==e['source_sha256'];b=raw or package(d,bin);dest=R/'library-v04'/e['id']/e['version'];save(dest/'model.glb',b)
  nodes=d.get('nodes',[]);parents={c:i for i,n in enumerate(nodes) for c in n.get('children',[])};joints=sorted(set(j for sk in d.get('skins',[]) for j in sk['joints']))
  vrm=d.get('extensions',{}).get('VRM');semantic={}
  if vrm:
   assert vrm['meta']['licenseName']=='CC0';semantic={b['bone']:nodes[b['node']].get('name',str(b['node'])) for b in vrm['humanoid']['humanBones']}
  elif e['family']=='kaykit-adventurers':
   semantic={'root':'root','hips':'hips','spine':'spine','chest':'chest','head':'head'}
   for side,s in [('Left','l'),('Right','r')]:
    for k,v in [('UpperArm','upperarm'),('LowerArm','lowerarm'),('Hand','hand'),('UpperLeg','upperleg'),('LowerLeg','lowerleg'),('Foot','foot'),('Toes','toes')]:semantic[side[0].lower()+side[1:]+k]=v+'.'+s
  else:
   semantic={'body':'Body','back':'Back','chest':'Torso','head':'Head'}
   for s in ['L','R']:
    for k in ['FrontUpperLeg','FrontLowerLeg','BackLeg','BackUpperLeg','BackLowerLeg']:semantic[k+'.'+s]=k+'.'+s
  names={n.get('name') for n in nodes};semantic={k:v for k,v in semantic.items() if v in names}
  clips=[]
  for a in d.get('animations',[]):
   maximum=max(d['accessors'][s['input']].get('max',[0])[0] for s in a['samplers']);minimum=min(d['accessors'][s['input']].get('min',[0])[0] for s in a['samplers']);clips.append({'name':a.get('name',''), 'duration_s':maximum-minimum,'channels':len(a['channels']),'source':'original-native-animation','art_approved':False})
  textures=[]
  for i,im in enumerate(d.get('images',[])):
   assert 'uri' not in im,'Unpinned external image';bv=d['bufferViews'][im['bufferView']];data=bin[bv.get('byteOffset',0):bv.get('byteOffset',0)+bv['byteLength']];ext='png' if im['mimeType']=='image/png' else 'jpg';name=f'textures/{i:02d}.{ext}';save(dest/name,data);dim=list(struct.unpack('>II',data[16:24])) if ext=='png' else None;textures.append({'file':name,'sha256':sha(data),'bytes':len(data),'dimensions':dim,'resized':False})
  profile={'schema_version':1,'asset_id':e['id'],'version':e['version'],'model_sha256':sha(b),'family':e['family'],'format_coordinate_system':'glTF right-handed Y-up; meters by specification; source author scale not normalized','forward_axis':'VRM0 -Z, viewer rotates Y by pi' if vrm else 'to be confirmed in browser; source untouched','reference_pose':'source node transforms and inverse bind matrices preserved byte-for-byte','semantic_bones':semantic,'node_hierarchy':[{'index':i,'name':n.get('name',''),'parent':parents.get(i),'children':n.get('children',[]),'translation':n.get('translation',[0,0,0]),'rotation_xyzw':n.get('rotation',[0,0,0,1]),'scale':n.get('scale',[1,1,1]),'matrix':n.get('matrix')} for i,n in enumerate(nodes)],'joint_indices':joints,'skins':d.get('skins',[]),'bone_lengths_note':'See Blender editor report for native rest heads/tails/lengths; no common-length normalization. glTF joints may include IK controls.','root_motion':'Unmodified source animation channels; per-clip displacement/contact calibration NOT TESTED.','retargeting':'NONE; humanoid and quadruped semantic families must be adapted independently.','vrm_humanoid':vrm.get('humanoid') if vrm else None,'vrm_meta':vrm.get('meta') if vrm else None,'clips':clips,'textures':textures,'art_approved':False,'game_ready':False}
  editor_path=R/'evidence-v04'/f"{e['id']}-editor.json"
  if editor_path.exists():
   editor=json.loads(editor_path.read_text());profile['editable_master_sha256']=editor['master_sha256'];profile['native_blender_rest_rigs']=editor['rigs'];lengths={b['name']:b['length'] for rig in editor['rigs'] for b in rig['bones']};reference=max(lengths.values()) if lengths else 1;profile['bone_length_ratios']={n:v/reference for n,v in lengths.items()};profile['bone_length_ratio_reference']='longest native Blender rest bone, including source controls; not character height or common target skeleton';profile['forward_axis']='glTF -Z (VRM0); viewer Y rotation pi' if vrm else 'glTF +Z, checked in browser front views; no rest-axis conversion';profile['reference_pose']='Original reference matrices retained; native Blender rest matrices/heads/tails included. No target pose normalization.'
  jsave(dest/'skeleton-profile.json',profile)
  item={**e,'model':{'url':'../'+str((dest/'model.glb').relative_to(R)),'sha256':sha(b),'bytes':len(b)},'profile':'../'+str((dest/'skeleton-profile.json').relative_to(R)),'profile_sha256':sha((dest/'skeleton-profile.json').read_bytes()),'renderer':'vrm0-mtoon' if vrm else 'gltf-pbr','clips':clips,'bones':len(joints),'textures':textures,'display_yaw':math.pi if vrm else 0,'status':'candidate-native-motion' if clips else 'appearance-only-no-animation','modifications':['Lossless data-URI glTF → binary GLB packaging'] if raw is None else ['None: runtime GLB container byte-identical to downloaded GLB/VRM'],'validation':{'structure':'pass; evidence-v04/structure-qa.json' if (R/'evidence-v04/structure-qa.json').exists() else 'pending','blender_editable':editor['status'] if editor_path.exists() else 'pending','browser':'native-render-and-clip-sampling-pass; see evidence-v04/browser-all-clips.json' if (R/'evidence-v04/browser-all-clips.json').exists() else 'pending','human_art':'not-tested','physical_mobile':'not-tested','engine_gameplay':'not-tested'}}
  
  if e['editable']['original_blend_available']:save(dest/'model.blend',(R/e['editable']['path']).read_bytes())
  jsave(dest/'asset_manifest.json',{**item,'schema_version':1,'asset_id':e['id'],'model_file':'model.glb','source_file':'model.blend','clips':[c['name'] for c in clips],'min_animation_count':len(clips),'requirements':{'skins':True,'animated':bool(clips),'visual_review':True}});jsave(dest/'report.json',{'status':'SOURCE_PRESERVED_REVIEW_CANDIDATE','validation':item['validation'],'original_bytes_preserved':True,'texture_resized':False,'art_approved':False,'game_ready':False,'limitations':e['warning']});out.append(item)
 jsave(R/'library-v04/catalog.json',{'schema_version':1,'version':'0.4.0','entries':out,'source_lock':'../sources-v04/SOURCE_FILES.sha256','legacy_studio':'../web-v03/','policy':'Source-native review candidates; no inferred art approval, no automatic map replacement.'})
 print('built',len(out),'models;',sum(len(x['clips']) for x in out),'native clips;',sum(bool(x['clips']) for x in out),'animated assets')
if __name__=='__main__':build()
