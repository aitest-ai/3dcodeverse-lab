"""Exact v13 A and newly smoothed B; both remain unapproved review candidates."""
import copy,hashlib,json,os,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.overlay import read
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OUT=Path(os.environ.get('STUDIO_V14_OUT',str(R/'library-v14'))).resolve()
old=json.loads((R/'library-v13/catalog.json').read_text());entries=[]
for key in ['horse-brown','horse-white']:
    F=OUT/(key+'-walk-smooth-review')/'0.1.0'
    if not (F/'adaptation.json').exists():continue
    source=next(e for e in old['entries'] if e['asset_id']==key+'-walk-transition-review')
    A=copy.deepcopy(source);B=copy.deepcopy(source);m=json.loads((F/'adaptation.json').read_text());doc,_=read(F/'model.glb')
    baseline=source['id'];corrected=m['asset_id']+'@0.1.0'
    A.update(variant='baseline',name=('棕馬' if key=='horse-brown' else '白馬')+' · v13 鎖蹄版本',pair_baseline=baseline,pair_corrected=corrected,warning='原封保留的 v13 候選；接地檢查通過，但步行接縫仍有局部速度跳變。人工自然度尚未驗收。')
    B.update(asset_id=m['asset_id'],id=corrected,variant='corrected',name=('棕馬' if key=='horse-brown' else '白馬')+' · 接縫修正候選',pair_baseline=baseline,pair_corrected=corrected,warning='原生步行接縫平順候選；線性烘焙仍有有限速度差，人工自然度、真實平衡與遊戲驗收未完成。')
    B['model']={'url':'../'+str((F/'model.glb').relative_to(R)),'sha256':m['model_sha256'],'bytes':(F/'model.glb').stat().st_size}
    B['editable']={'path':str((F/'model.blend').relative_to(R)),'sha256':m['mother_sha256'],'description':'18 rig actions + 3 original paired root actions; only WalkWorld/StartWalk/StopWalk body curves replaced.'}
    B['modifications']=['Native Walk wrap TRS Hermite bridge over the last/first 1.5% with original seam pose retained, before fixed-length contact IK.','240 Hz body bake, 2400 Hz locally near the wrap for WalkWorld/StartWalk/StopWalk; 15 other clips and all root tracks preserved exactly.','No new anatomy, textures, body lowering, stride, contact schedule or speed.']
    profile=json.loads((R/source['profile'].removeprefix('../')).read_text())
    profile.update(profile_version='0.14.0',asset_id=B['asset_id'],model_sha256=m['model_sha256'],editable_master_sha256=m['mother_sha256'],source_editable_master_sha256=m['source_mother_sha256'],source_profile=source['profile'],adaptation=m)
    (F/'skeleton-profile.json').write_text(json.dumps(profile,indent=2)+'\n');B['profile']='../'+str((F/'skeleton-profile.json').relative_to(R));B['profile_sha256']=sha(F/'skeleton-profile.json')
    (F/'asset_manifest.json').write_text(json.dumps({'schema_version':1,'asset_id':B['asset_id'],'format':'glTF 2.0 GLB','model_file':'model.glb','source_file':'model.blend','clips':[a['name'] for a in doc['animations']],'min_animation_count':18,'requirements':{'skins':True,'animated':True,'visual_review':True},'license_note':'Quaternius CC0; aitest-ai original modifications; THIRD_PARTY_V14.md'},indent=2)+'\n')
    (F/'report.json').write_text(json.dumps({'status':'review-candidate','art_approved':False,'game_ready':False,'model_sha256':m['model_sha256'],'known_limitations':[B['warning'],'same body in two colors','finite straight trip; no interruptible controller']},indent=2)+'\n')
    entries.extend([A,B])
(OUT/'catalog.json').write_text(json.dumps({'version':'0.14.0','entries':entries},indent=2)+'\n');print('V14_CATALOG',len(entries))
