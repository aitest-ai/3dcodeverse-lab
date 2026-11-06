"""Phase-dependent Run elbow flexion on native rigs; only two forearm rotations change."""
import bpy,sys,os,json,math,hashlib
from pathlib import Path
from mathutils import Quaternion
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture,bone_world,set_q,vertices
from v06.motion_overlay import MotionOverlay
from v06.geometry_guard import geometry_signature
from v06.collision import crossings
from v17.sleeves import fit
from v17.morph import append as append_morph
OUT=Path(os.environ.get('STUDIO_V17_OUT',str(R/'work/v17-build')))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def activate(rig,root):
 for ob in [rig,root]:
  for tr in ob.animation_data.nla_tracks:tr.mute=True
  a=bpy.data.actions['Run' if ob==rig else 'Run_Root'];ob.animation_data.action=a
  if a.slots:ob.animation_data.action_slot=a.slots[0]
def arm_regions(body):
 me=body.data;me.calc_loop_triangles();weighted=lambda v,keys:sum(g.weight for g in v.groups if any(k in body.vertex_groups[g.group].name for k in keys))
 result={}
 for s in ['L','R']:
  keys=['J_Bip_'+s+'_'+p for p in ['UpperArm','LowerArm','Shoulder','Hand']];ids={v.index for v in me.vertices if weighted(v,keys)>.5};skin=[];cloth=[]
  for t in me.loop_triangles:
   if not all(i in ids for i in t.vertices):continue
   (skin if t.material_index==0 else cloth).append(list(t.vertices))
  result[s]={'skin_triangles':skin,'sleeve_triangles':cloth}
 return result
for key,prev,ver in [('vivi','0.4.0','0.5.0'),('vita','0.3.0','0.4.0')]:
 if key not in os.environ.get('STUDIO_V17_CHARACTERS','vivi,vita').split(','):continue
 center,amplitude=(80,12) if key=='vivi' else (74,6)
 base=R/'inputs-v17/library-v16'/('vroid-'+key+'-motion-review')/prev;meta=json.loads((base/'adaptation.json').read_text());original=R/meta['original_geometry'];dest=OUT/('vroid-'+key+'-motion-review')/ver
 if dest.exists():raise RuntimeError('Refuse overwrite '+str(dest))
 dest.mkdir(parents=True);assert sha(base/'model.glb')==meta['model_sha256'] and sha(base/'model.blend')==meta['mother_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(base/'model.blend'));rig=bpy.data.objects['Armature'];root=bpy.data.objects['StudioRootMotion_v05'];body=bpy.data.objects['Body'];scene=bpy.context.scene;signature=geometry_signature();activate(rig,root)
 capture=Capture(rig,original);overlay=MotionOverlay(base/'model.glb');names=['J_Bip_L_LowerArm','J_Bip_R_LowerArm'];nodes={i for i,n in capture.map.items() if n in names};regions=json.loads((base/'collision-regions.json').read_text());regions['arms']=arm_regions(body);frames=[];poses=[];audit=[]
 skin_triangles=[t for part in regions['arms'].values() for t in part['skin_triangles']];regions['baseline_arm_skin_pairs_120hz']=[]
 for sample in range(85):
  frame=sample/2;scene.frame_set(math.floor(frame),subframe=frame%1);regions['baseline_arm_skin_pairs_120hz'].append(crossings(vertices(body),skin_triangles))
 for i in range(43):
  scene.frame_set(i);joints={}
  for side,sign in [('L',1),('R',-1)]:
   U,E,H=[bone_world(rig,'J_Bip_'+side+'_'+p).translation.copy() for p in ['UpperArm','LowerArm','Hand']];upper=(E-U).normalized();fore=(H-E).normalized();flex=math.degrees(upper.angle(fore));target=center-amplitude*sign*math.cos(math.tau*i/42);axis=upper.cross(fore).normalized();name='J_Bip_'+side+'_LowerArm';set_q(rig,name,Quaternion(axis,math.radians(target-flex))@bone_world(rig,name).to_quaternion());joints[side]={'before_flexion_degrees':flex,'target_flexion_degrees':target,'hinge_axis_world':list(axis)}
  frames.append(capture.frame(root.matrix_world));poses.append({n:list(rig.pose.bones[n].rotation_quaternion) for n in names});vs=vertices(body)
  audit.append({'time_s':i/60,'elbows':joints,'hand_skin_crossings':{s:len(crossings(vs,regions['hand_triangles'][s])) for s in ['L','R']},'hand_skirt_crossings':{s:len(crossings(vs,regions['hand_triangles'][s],regions['cloth_triangles'])) for s in ['L','R']},'sleeve_skin_crossings':{s:len(crossings(vs,regions['arms'][s]['skin_triangles'],regions['arms'][s]['sleeve_triangles'])) for s in ['L','R']}})
 assert all(max(x['hand_skin_crossings'].values())==max(x['hand_skirt_crossings'].values())==0 for x in audit),'New hand/garment crossings'
 overlay.patch('Run',frames,nodes,properties=('rotation',),threshold=0)
 for layer in rig.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     name=next((n for n in names if fc.data_path=='pose.bones["'+n+'"].rotation_quaternion'),None)
     if name is None:continue
     qs=[p[name][:] for p in poses];assert len(fc.keyframe_points)==43
     for j in range(1,43):
      if sum(a*b for a,b in zip(qs[j-1],qs[j]))<0:qs[j]=[-x for x in qs[j]]
     for j,kp in enumerate(fc.keyframe_points):kp.co.y=qs[j][fc.array_index];kp.interpolation='LINEAR'
     fc.update()
 scene.frame_set(0);assert geometry_signature()==signature
 corrective=fit(body,rig,regions);morph=append_morph(overlay,body,[1]*43);scene.frame_set(0);new_signature=geometry_signature()
 modelsha=overlay.save(dest/'model.glb');bpy.ops.wm.save_as_mainfile(filepath=str(dest/'model.blend'),compress=True)
 write(dest/'pose-corrective.json',corrective);write(dest/'collision-regions.json',regions);write(dest/'motion-audit.json',{'fps':60,'clip':'Run','before_sleeve_corrective_samples':audit,'final_sleeve_checks':corrective['checks_60hz'],'limits':'proper triangle crossings; not solid containment, thickness or human art approval'})
 write(dest/'arm-fit.json',{'native_semantics':{s:{p:'J_Bip_'+s+'_'+p for p in ['UpperArm','LowerArm','Hand']} for s in ['L','R']},'method':'Native world-space anatomical hinge derived from upper-arm and forearm directions; only local forearm quaternion tracks baked. No cross-rig quaternion copying.','target_flexion_degrees':'center - amplitude * side_sign * cos(2*pi*phase), left +1, right -1','center':center,'amplitude':amplitude,'minimum':center-amplitude,'maximum':center+amplitude,'period_seconds':.7,'sleeve_corrective':'Run-only native shape key; source base geometry and six other runtime surfaces retained','retained':'V16 finger pose, wrist local motion, shoulder/upper-arm clothing clearance, bone lengths, lower body and six other clips','art_approved':False})
 write(dest/'adaptation.json',{'asset_id':'vroid-'+key+'-motion-review','version':ver,'base_model':str((base/'model.glb').relative_to(R)),'base_model_sha256':sha(base/'model.glb'),'base_mother':str((base/'model.blend').relative_to(R)),'base_mother_sha256':sha(base/'model.blend'),'original_geometry':str(original.relative_to(R)),'original_geometry_sha256':sha(original),'model_sha256':modelsha,'mother_sha256':sha(dest/'model.blend'),'source_geometry_signature':signature,'geometry_signature':new_signature,'sleeve_morph':morph,'preserved_binary_prefix_bytes':overlay.prefix_bytes,'preserved_binary_prefix_sha256':overlay.prefix_sha256,'changed_clips':['Run'],'preserved_clips':['Idle','Walk','Start','Stop','TurnLeft','TurnRight'],'changed_channels':overlay.changed,'preserved':'all non-target channels, root, legs, fingers, upper-arm clearance, native geometry, rest, weights, UVs, materials, textures','motion_source':'project-authored procedural Run refinement on pinned V16, not mocap or trained AI','blender_version':bpy.app.version_string,'art_approved':False,'game_ready':False})
 print('V17_BUILT',key,modelsha,'prefit maximum sleeve/skin crossings',max(v for x in audit for v in x['sleeve_skin_crossings'].values()),flush=True)
