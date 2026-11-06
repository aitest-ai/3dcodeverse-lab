"""Exact v14 A and new locomotion B; both remain unapproved review candidates."""
import copy,hashlib,json,os,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.overlay import read
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OUT=Path(os.environ.get('STUDIO_V15_OUT',str(R/'library-v15'))).resolve()
old=json.loads((R/'library-v14/catalog.json').read_text());entries=[]
for key in ['horse-brown','horse-white']:
    F=OUT/(key+'-locomotion-review')/'0.1.0'
    if not (F/'adaptation.json').exists():continue
    source=next(e for e in old['entries'] if e['asset_id']==key+'-walk-smooth-review')
    A=copy.deepcopy(source);B=copy.deepcopy(source);m=json.loads((F/'adaptation.json').read_text());doc,_=read(F/'model.glb')
    baseline=source['id'];corrected=m['asset_id']+'@0.1.0'
    A.update(variant='baseline',name=('棕馬' if key=='horse-brown' else '白馬')+' · v14 既有版本',pair_baseline=baseline,pair_corrected=corrected,warning='原封保留的 v14 步行候選。沒有再起步與行進轉向對應動畫。人工自然度尚未驗收。')
    B.update(asset_id=m['asset_id'],id=corrected,variant='corrected',name=('棕馬' if key=='horse-brown' else '白馬')+' · 再起步／轉向候選',pair_baseline=baseline,pair_corrected=corrected,warning='新增再起步與行進左右轉向；指令於完整片段邊界執行。人工自然度、真實平衡與遊戲驗收未完成。')
    B['model']={'url':'../'+str((F/'model.glb').relative_to(R)),'sha256':m['model_sha256'],'bytes':(F/'model.glb').stat().st_size}
    B['editable']={'path':str((F/'model.blend').relative_to(R)),'sha256':m['mother_sha256'],'description':'21 rig actions + 6 paired root actions; 3 new rig/root pairs only.'}
    B['modifications']=['Preserved all 18 v14 GLB clips, 21 native actions and source geometry/textures.','Added RestartWalk from StandStopped plus ±15 degree walking turns on native skeleton.','World-locked planned hoof patches, fixed link lengths; no physical balance claim.']
    B['locomotion']=m['locomotion']
    for name,spec in m['locomotion']['clips'].items():
        B['root_clips'][name]={'start':{'x':0,'z':0,'yaw':0},'end':spec['root_end']}
        B['phase_ranges'][name]=[0,spec['duration']]
    B['clips']=[a['name'] for a in doc['animations']]
    profile=json.loads((R/source['profile'].removeprefix('../')).read_text())
    profile.update(profile_version='0.15.0',asset_id=B['asset_id'],model_sha256=m['model_sha256'],editable_master_sha256=m['mother_sha256'],source_editable_master_sha256=m['source_mother_sha256'],source_profile=source['profile'],adaptation=m)
    profile['editable_description']='50 native bones; 21 rig actions + 6 paired root actions. Original 21 actions preserved.'
    for name,spec in m['locomotion']['clips'].items():
        profile['clips'].append({'name':name,'duration_s':spec['duration'],'first_key_s':0,'last_key_s':spec['duration'],'status':'unapproved-v15-candidate'})
        profile['root_motion'][name]={'paired_action':name+'_Root','start':{'x':0,'z':0,'yaw':0},'end_metres':spec['root_end'],'native_units':'apply calibrated display scale once','finite':True}
    profile['root_motion']['controller']=m['locomotion']['controller']
    profile['root_motion']['turn_yaw_convention']=m['locomotion']['turn_yaw_convention']
    (F/'skeleton-profile.json').write_text(json.dumps(profile,indent=2)+'\n');B['profile']='../'+str((F/'skeleton-profile.json').relative_to(R));B['profile_sha256']=sha(F/'skeleton-profile.json')
    (F/'asset_manifest.json').write_text(json.dumps({'schema_version':1,'asset_id':B['asset_id'],'format':'glTF 2.0 GLB','model_file':'model.glb','source_file':'model.blend','clips':[a['name'] for a in doc['animations']],'min_animation_count':21,'requirements':{'skins':True,'animated':True,'visual_review':True},'license_note':'Quaternius CC0; aitest-ai original modifications; THIRD_PARTY_V15.md'},indent=2)+'\n')
    (F/'report.json').write_text(json.dumps({'status':'review-candidate','art_approved':False,'game_ready':False,'model_sha256':m['model_sha256'],'known_limitations':[B['warning'],'same body in two colors','queued clip-boundary control; no emergency interruption']},indent=2)+'\n')
    entries.extend([A,B])
(OUT/'catalog.json').write_text(json.dumps({'version':'0.15.0','entries':entries},indent=2)+'\n');print('V15_CATALOG',len(entries))
