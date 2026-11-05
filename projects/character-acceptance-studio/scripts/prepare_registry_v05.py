"""Promote verified build output into a NEW review version. Refuses overwriting existing version folders."""
import hashlib,json,shutil,sys,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.overlay import read
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
old=json.loads((R/'library-v04/catalog.json').read_text())['entries'];entries=[]
for prior,newid,key in [('vroid-vivi','vroid-vivi-motion-review','vivi'),('quaternius-shibainu','quaternius-shibainu-grounded-review','shiba')]:
 src=R/'work/v05-build'/newid/'0.1.0';dest=R/'library-v05'/newid/'0.1.0'
 if dest.exists():raise RuntimeError('Version already exists: '+str(dest))
 dest.mkdir(parents=True)
 for f in ['model.glb','baseline.glb','model.blend','adaptation.json','motion-audit.json']:shutil.copy2(src/f,dest/f)
 base=next(x for x in old if x['id']==prior);meta=json.loads((dest/'adaptation.json').read_text());doc,bin=read(dest/'model.glb');audit=json.loads((dest/'motion-audit.json').read_text());profile=json.loads((R/'library-v04'/prior/'1.0.0/skeleton-profile.json').read_text());clips=[]
 for a in doc['animations']:
  times=[doc['accessors'][s['input']] for s in a['samplers']];clips.append({'name':a['name'],'duration_s':max(x['max'][0] for x in times),'channels':len(a['channels']),'status':'corrected-candidate' if a['name'] in audit['clips'] else 'source-only-unreviewed'})
 parents={c:i for i,n in enumerate(doc['nodes']) for c in n.get('children',[])};profile.update(asset_id=newid,version='0.1.0',model_sha256=h(dest/'model.glb'),editable_master_sha256=h(dest/'model.blend'),forward_axis='glTF +Z via root wrapper; Blender -Y',format_coordinate_system='glTF right-handed +Y up, meters; native bone lengths retained under explicit common root transform',clips=clips,node_hierarchy=[{'index':i,'parent':parents.get(i),**n} for i,n in enumerate(doc['nodes'])],reference_pose='Native rest matrices unchanged; skin rest derived from inverseBindMatrices, not posed default nodes.',root_motion={'node':'StudioRootMotion_v05','translation':'baked world meters +Y up','heading':'baked quaternion','loop_rule':'Advance root XZ by end-start per Walk/Run/Gallop loop; turn/start/stop intended as one-shot clips.','source_axes':'Vivi original -Z rotated Y pi; Shiba native +Z','uniform_scale':meta.get('scale',1)},retargeting=meta,editable_note='New baked FK working copy; runtime weights synchronized from original GLB (duplicate VRM influences summed; animal native master retained separately). Native length ratios are unchanged; controls are included in reference lengths.')
 write(dest/'skeleton-profile.json',profile)
 before_profile={**profile,'asset_id':newid+'-before','model_sha256':h(dest/'baseline.glb'),'variant':'intermediate before correction; correction mother and rebuild recipe supplied'};write(dest/'baseline-profile.json',before_profile)
 if key=='vivi':
  contacts={k:{'all':ids,'sets':meta['contact_sets'][k]} for k,ids in meta['foot_vertex_ids'].items()};maps=[{'mesh_name':'Bodybaked','indices':{str(i):i for ids in meta['foot_vertex_ids'].values() for i in ids}}]
 else:
  contacts={k:{'all':p['ids'],'sets':{'flat':p['flat']}} for k,p in meta['paws'].items()};maps=[{'mesh_name':m['mesh_name'],'indices':{str(i):j for j,i in enumerate(m['native_ids'])}} for m in meta['vertex_maps']]
 for filename,label in [('baseline.glb','適配初稿' if key=='vivi' else '原生動作重烘焙'),('model.glb','接地修正候選')]:
  e=dict(base);before=filename=='baseline.glb';e.update(id=newid+'-before' if before else newid,asset_id=newid+'-before' if before else newid,version='0.1.0',name=('Vivi' if key=='vivi' else '柴犬')+' · '+label,variant='before' if before else 'corrected',display_yaw=0,default_clip='Walk',pair_baseline=newid+'-before',pair_corrected=newid,clips=clips,contact_sets=contacts,vertex_maps=maps,model={'url':'../'+str((dest/filename).relative_to(R)),'sha256':h(dest/filename),'bytes':(dest/filename).stat().st_size},profile='../'+str((dest/('baseline-profile.json' if before else 'skeleton-profile.json')).relative_to(R)),profile_sha256=h(dest/('baseline-profile.json' if before else 'skeleton-profile.json')),editable={'kind':'baked-FK-correction-working-copy','path':str((dest/'model.blend').relative_to(R)),'note':'B 修正母檔；A 由保留的來源與 build 腳本重建。原生輸入母檔另附。'},license='CC0-1.0 inputs; project-authored motion/adaptation contributions',modifications=meta,warning='未經人工美術核准；A 為流程初稿，B 為修正候選。'+('裙襬使用骨骼烘焙；不是布料模擬，手部鬆緊仍需美術檢視。' if key=='vivi' else '只修正 Idle／Walk／Gallop；其餘 9 段保留原動畫，未作接地驗收。'))
  entries.append(e)
 write(dest/'asset_manifest.json',{'schema_version':1,'asset_id':newid,'version':'0.1.0','model_file':'model.glb','source_file':'model.blend','sha256':h(dest/'model.glb'),'unit':'meter','clips':[c['name'] for c in clips],'min_animation_count':len(clips),'requirements':{'skins':True,'animated':True,'visual_review':True},'source':base['source_url'],'license_note':'See THIRD_PARTY_V05.md; source CC0 grants retained, project corrections not newly dedicated CC0.','art_approved':False,'game_ready':False})
 write(dest/'report.json',{'generation':'Blender 5.2.3 LTS background; CPU only; no desktop GUI/GPU claim','corrected_clips':list(audit['clips']),'runtime_geometry_material_skin_vrm_bytes':'unchanged source prefix','editable_weight_sync':meta['editable_weight_sync'],'browser_evidence':'../../../evidence-v05/browser-contacts.json','art_approved':False,'game_ready':False})
 write(dest/'files.json',{'files':[{'file':p.name,'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(dest.iterdir()) if p.is_file()]})
write(R/'library-v05/catalog.json',{'schema_version':1,'version':'0.5.0','entries':entries})
print('Registered two new immutable review candidates and their before/after pairs')
