"""Freeze Vita 0.2.0 and derive each asset's own root motion directly from its pinned GLB."""
import json,hashlib,shutil,math,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v06.motion_overlay import MotionOverlay
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
F=R/'library-v08/vroid-vita-motion-review/0.2.0';S=R/'work/v08-build/vroid-vita-motion-review/0.2.0'
if F.exists():raise RuntimeError('Refuse overwrite of version folder')
F.mkdir(parents=True)
for name in ['model.glb','model.blend','adaptation.json','motion-audit.json','collision-regions.json']:shutil.copy2(S/name,F/name)
meta=json.loads((F/'adaptation.json').read_text());old=json.loads((R/'library-v07/catalog.json').read_text());a=json.loads(json.dumps(next(e for e in old['entries'] if e['asset_id']=='vroid-vita-motion-review')));b=json.loads(json.dumps(a));a.update(name='Vita · 前版 0.1（3 段動作）',variant='before',pair_baseline=a['id'],pair_corrected='vroid-vita-motion-review@0.2.0',default_clip='Idle',warning='前版只有 Idle／Walk／Run，這三段在新版精確保留。新增片段無前版動畫可比較。')
b.update(id='vroid-vita-motion-review@0.2.0',version='0.2.0',name='Vita · 起停與轉身候選',pair_baseline=a['id'],pair_corrected='vroid-vita-motion-review@0.2.0',default_clip='Start',modifications=meta,warning='新增起步、停步、左右轉身；使用原生骨架與各自步幅。人工美術與完整衣物碰撞未核准。')
doc=MotionOverlay(F/'model.glb').doc;clips=[{'name':c['name'],'duration_s':max(doc['accessors'][s['input']]['max'][0] for s in c['samplers']),'channels':len(c['channels']),'status':'candidate; not art-approved'} for c in doc['animations']];profile=json.loads((R/a['profile'].removeprefix('../')).read_text());profile.update(version='0.2.0',model_sha256=h(F/'model.glb'),editable_master_sha256=h(F/'model.blend'),clips=clips,retargeting=meta);write(F/'skeleton-profile.json',profile)
b.update(clips=clips,model={'url':'../'+str((F/'model.glb').relative_to(R)),'bytes':(F/'model.glb').stat().st_size,'sha256':h(F/'model.glb')},profile='../'+str((F/'skeleton-profile.json').relative_to(R)),profile_sha256=h(F/'skeleton-profile.json'),editable={'kind':'native FK baked working copy','path':str((F/'model.blend').relative_to(R)),'sha256':h(F/'model.blend'),'note':'此版本自己的母檔，需 Vita Sources ZIP。'})
entries=[a,b]+[e for e in old['entries'] if e['asset_id']=='vroid-vivi-motion-review']
for e in entries:
 o=MotionOverlay(R/e['model']['url'].removeprefix('../'));node=next(i for i,n in enumerate(o.doc['nodes']) if n.get('name')=='StudioRootMotion_v05');plans={}
 for clip in o.doc['animations']:
  tracks={c['target']['path']:o.values(clip['samplers'][c['sampler']]['output']) for c in clip['channels'] if c['target']['node']==node};duration=max(o.doc['accessors'][s['input']]['max'][0] for s in clip['samplers']);p,q=tracks['translation'],tracks['rotation'];heading0=2*math.atan2(q[0][1],q[0][3]);endyaw=2*math.atan2(q[-1][1],q[-1][3])-heading0;endyaw=math.atan2(math.sin(endyaw),math.cos(endyaw));plans[clip['name']]={'duration':duration,'start':{'x':p[0][0],'z':p[0][2],'yaw':0},'end':{'x':p[-1][0],'z':p[-1][2],'yaw':endyaw}}
 e['root_clips']=plans
write(R/'library-v08/catalog.json',{'schema_version':1,'version':'0.8.0','entries':entries,'root_motion_policy':'Per entry derived from its own pinned GLB; no global shared stride.'})
write(F/'asset_manifest.json',{'schema_version':1,'asset_id':b['asset_id'],'version':b['version'],'model_file':'model.glb','source_file':'model.blend','sha256':h(F/'model.glb'),'unit':'meter','clips':[c['name'] for c in clips],'min_animation_count':7,'requirements':{'skins':True,'animated':True,'visual_review':True},'source':b['source_url'],'license_note':'CC0 upstream; project-authored motions. See THIRD_PARTY_V08.md.','art_approved':False,'game_ready':False})
write(F/'report.json',{'generation':'Blender 5.2.3 LTS background CPU','native_joints':155,'geometry_weights_materials_textures':'unchanged','evidence':'../../../evidence-v08/','human_art':'not-tested','art_approved':False,'game_ready':False});write(F/'files.json',{'files':[{'file':p.name,'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(F.iterdir())]});print('V08_REGISTRY_FROZEN')
