"""Register two reviewed candidates and two explicitly uncorrected comparisons."""
import copy, hashlib, json, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.overlay import read
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((R/'library-v12/catalog.json').read_text());entries=[]
for key in ['horse-brown','horse-white']:
    template=next(e for e in old['entries'] if e['asset_id']==key+'-walk-support-review')
    baseline=key+'-transition-baseline@0.1.0';corrected=key+'-walk-transition-review@0.1.0'
    for suffix,variant in [('transition-baseline','baseline'),('walk-transition-review','corrected')]:
        F=R/'library-v13'/(key+'-'+suffix)/'0.1.0'
        if not (F/'adaptation.json').exists():continue
        m=json.loads((F/'adaptation.json').read_text());doc,_=read(F/'model.glb');e=copy.deepcopy(template)
        e.update(asset_id=m['asset_id'],id=m['asset_id']+'@0.1.0',variant=variant,name=('棕馬' if key=='horse-brown' else '白馬')+(' · 未鎖蹄試驗' if variant=='baseline' else ' · 起停鎖蹄候選'),default_clip='StartWalk',pair_baseline=baseline,pair_corrected=corrected,transition=m['transition'],walk_plan=m['walk_plan'])
        e['clips']=[{'name':a['name'],'duration':max(doc['accessors'][s['input']].get('max',[0])[0] for s in a['samplers'])} for a in doc['animations']]
        e['model']={'url':'../'+str((F/'model.glb').relative_to(R)),'sha256':m['model_sha256'],'bytes':(F/'model.glb').stat().st_size}
        e['editable']={'path':str((F/'model.blend').relative_to(R)),'sha256':m['mother_sha256'],'description':'Complete 18 rig actions + 3 paired travel-root actions. Original 14 rig clips preserved.'}
        e['warning']='未修正對照試驗；僅混合姿勢與根位移，預期腳滑／穿地。不是 v12 已有動作，也不可當正式模板。' if variant=='baseline' else '有限直線起停候選；全程重播會重置起點。動態平衡、人工自然度及任意時刻中斷控制尚未驗收。'
        e['modifications']=['Preserve all fourteen v12 GLB clips and all original scene/binary data.','Add StandReady, StartWalk, StopWalk, StandStopped with finite acceleration/deceleration.','A is an explicit uncorrected comparison experiment; B solves fixed world hoof anchors.']
        profile=json.loads((R/template['profile'].removeprefix('../')).read_text())
        profile.update(profile_version='0.13.0',asset_id=e['asset_id'],model_sha256=m['model_sha256'],editable_master_sha256=m['mother_sha256'],source_editable_master_sha256=m['source_mother_sha256'],source_profile=template['profile'],adaptation=m)
        for name in ['StartWalk','StopWalk']:
            profile.setdefault('root_motion',{})[name]={'native_wrapper':'StudioTravelRoot_v11','paired_action':name+'_Root','unit':'native; apply calibrated uniform scale once','finite':True}
            e['root_clips'][name]={'start':{'x':0,'z':0,'yaw':0},'end':{'x':0,'z':2*m['walk_plan']['candidate_stride_m'],'yaw':0}}
        (F/'skeleton-profile.json').write_text(json.dumps(profile,indent=2)+'\n');e['profile']='../'+str((F/'skeleton-profile.json').relative_to(R));e['profile_sha256']=sha(F/'skeleton-profile.json')
        (F/'asset_manifest.json').write_text(json.dumps({'schema_version':1,'asset_id':e['asset_id'],'format':'glTF 2.0 GLB','model_file':'model.glb','source_file':'model.blend','clips':[c['name'] for c in e['clips']],'min_animation_count':18,'requirements':{'skins':True,'animated':True,'visual_review':True},'license_note':'Quaternius CC0; aitest-ai original modifications; THIRD_PARTY_V13.md'},indent=2)+'\n')
        (F/'report.json').write_text(json.dumps({'status':'uncorrected-comparison-only' if variant=='baseline' else 'review-candidate','art_approved':False,'game_ready':False,'model_sha256':m['model_sha256'],'known_limitations':[e['warning'],'same body in two colors','no human, mobile, game, physical balance or full collision certification']},indent=2)+'\n')
        entries.append(e)
(R/'library-v13/catalog.json').write_text(json.dumps({'version':'0.13.0','entries':entries},indent=2)+'\n');print('V13_CATALOG',len(entries))
