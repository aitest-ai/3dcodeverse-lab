"""Refine Run hand shape on each native rig; patch only finger and upper-arm rotation tracks.

No new geometry, cross-rig quaternion transfer, or new motion source. Existing
rest, skin, clothes, textures, leg, root and six other clips stay unchanged.
"""
import bpy,sys,os,json,math,hashlib
from pathlib import Path
from mathutils import Quaternion
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture,bone_world,set_world,set_q,vertices
from v06.motion_overlay import MotionOverlay
from v06.geometry_guard import geometry_signature
from v07.regions import native_regions
from v06.collision import crossings
OUT=Path(os.environ.get('STUDIO_V16_OUT',str(R/'work/v16-build')))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def activate(rig,root,name):
 for o in [rig,root]:
  for tr in o.animation_data.nla_tracks:tr.mute=True
  a=bpy.data.actions[name if o==rig else name+'_Root'];o.animation_data.action=a
  if a.slots:o.animation_data.action_slot=a.slots[0]

for key,basepath,version in [('vivi','library-v07/vroid-vivi-motion-review/0.3.0','0.4.0'),('vita','library-v08/vroid-vita-motion-review/0.2.0','0.3.0')]:
 base=R/basepath;meta=json.loads((base/'adaptation.json').read_text());original=R/'library-v04'/('vroid-'+key)/'1.0.0/model.glb';dest=OUT/('vroid-'+key+'-motion-review')/version
 if dest.exists():raise RuntimeError('Refuse to overwrite candidate '+str(dest))
 dest.mkdir(parents=True)
 assert sha(base/'model.glb')==meta['model_sha256'] and sha(base/'model.blend')==meta['mother_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(base/'model.blend'));rig=bpy.data.objects['Armature'];root=bpy.data.objects['StudioRootMotion_v05'];body=bpy.data.objects['Body'];scene=bpy.context.scene;signature=geometry_signature();activate(rig,root,'Run')
 capture=Capture(rig,original);overlay=MotionOverlay(base/'model.glb');regions=native_regions(body,rig)
 finger_names=['J_Bip_'+s+'_'+d+str(i) for s in ['L','R'] for d in ['Index','Middle','Ring','Little','Thumb'] for i in range(1,4)]
 assert all(n in rig.pose.bones for n in finger_names)
 assert len(finger_names)==30
 changed_names=finger_names+['J_Bip_L_UpperArm','J_Bip_R_UpperArm'];clearance=json.loads((R/'scripts/v16/hand-clearance.json').read_text())['characters'][key]['abduction_degrees'];nodes={i for i,n in capture.map.items() if n in changed_names};profile={};frames=[];poses=[];audit=[]
 for side in ['L','R']:
  pre='J_Bip_'+side+'_';rest=lambda part:rig.data.bones[pre+part].matrix_local
  along=rest('Middle1').translation-rest('Hand').translation;across=rest('Index1').translation-rest('Little1').translation;palm=along.cross(across).normalized()
  if palm.z>0:palm=-palm
  profile[side]={'palm_normal_rig_rest':list(palm),'palm_width_m':across.length,'digits':{}}
  for digit,factor in [('Index',.88),('Middle',1),('Ring',1.08),('Little',1.15),('Thumb',.55)]:
   # The source PIP skin folds through itself under larger flexion. Increase
   # MCP curl, retain the tested PIP range; do not hide intersections or resize.
   angles=[math.degrees(a*.67*factor) for a in [.45,.65,.33]] if digit=='Thumb' else [40*factor,25*factor,12*factor]
   direction=(rest(digit+'2').translation-rest(digit+'1').translation).normalized();axis=direction.cross(palm).normalized()
   profile[side]['digits'][digit]={'flexion_degrees':angles,'hinge_axis_rig_rest':list(axis)}
 N=round(rig.animation_data.action.frame_range[1]);assert N==42 and scene.render.fps==60
 for i in range(N+1):
  scene.frame_set(i)
  for side,sign in [('L',1),('R',-1)]:
   n='J_Bip_'+side+'_UpperArm';set_q(rig,n,Quaternion((0,-1,0),math.radians(clearance[side][i%42])*sign)@bone_world(rig,n).to_quaternion())
  for side in ['L','R']:
   pre='J_Bip_'+side+'_';hand=rig.data.bones[pre+'Hand'].matrix_local;delta=bone_world(rig,pre+'Hand')@hand.inverted()
   for digit,settings in profile[side]['digits'].items():
    # Reset all three native phalanges first. Never add another curl to a baked curl.
    for j in range(1,4):set_world(rig,pre+digit+str(j),delta@rig.data.bones[pre+digit+str(j)].matrix_local)
    from mathutils import Vector
    axis=delta.to_quaternion()@Vector(settings['hinge_axis_rig_rest'])
    for j,degrees in enumerate(settings['flexion_degrees'],1):
     n=pre+digit+str(j);set_q(rig,n,Quaternion(axis,math.radians(degrees))@bone_world(rig,n).to_quaternion())
  frames.append(capture.frame(root.matrix_world));poses.append({n:list(rig.pose.bones[n].rotation_quaternion) for n in changed_names})
  vs=vertices(body);counts={s:len(crossings(vs,regions['hand_triangles'][s])) for s in ['L','R']};clothcounts={s:len(crossings(vs,regions['hand_triangles'][s],regions['cloth_triangles'])) for s in ['L','R']};audit.append({'time_s':i/60,'hand_skin_crossings':counts,'hand_skirt_crossings':clothcounts})
 assert all(max(row['hand_skin_crossings'].values())==0 and max(row['hand_skirt_crossings'].values())==0 for row in audit), 'Rejected hand-skin intersections'
 overlay.patch('Run',frames,nodes,properties=('rotation',),threshold=0)
 # Replace only the existing Run target quaternion curve values. All other
 # native action data is retained, including root curves and reference poses.
 action=rig.animation_data.action
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     name=next((n for n in changed_names if fc.data_path=='pose.bones["'+n+'"].rotation_quaternion'),None)
     if name is None:continue
     assert len(fc.keyframe_points)==N+1
     qs=[poses[i][name][:] for i in range(N+1)]
     for i in range(1,len(qs)):
      if sum(a*b for a,b in zip(qs[i-1],qs[i]))<0:qs[i]=[-x for x in qs[i]]
     for i,kp in enumerate(fc.keyframe_points):kp.co.y=qs[i][fc.array_index];kp.interpolation='LINEAR'
     fc.update()
 scene.frame_set(0);assert geometry_signature()==signature
 modelsha=overlay.save(dest/'model.glb');bpy.ops.wm.save_as_mainfile(filepath=str(dest/'model.blend'),compress=True)
 write(dest/'hand-fit.json',{'method':'Native-rest phalange flexion with independent palm frame and thumb settings; no scaling or bone-length edits. Run only.','characters_are_distinct_bodies':True,'hands':profile,'upper_arm_clearance_degrees':clearance,'art_approved':False})
 write(dest/'collision-regions.json',regions)
 write(dest/'motion-audit.json',{'fps':60,'clip':'Run','samples':audit,'maximum_hand_skin_crossings':{s:max(a['hand_skin_crossings'][s] for a in audit) for s in ['L','R']},'collision_scope':'proper hand-skin and hand-skirt triangle crossings; nails excluded; not containment/thickness/full-body validation'})
 write(dest/'adaptation.json',{'asset_id':'vroid-'+key+'-motion-review','version':version,'base_model':basepath+'/model.glb','base_model_sha256':sha(base/'model.glb'),'base_mother':basepath+'/model.blend','base_mother_sha256':sha(base/'model.blend'),'original_geometry':str(original.relative_to(R)),'original_geometry_sha256':sha(original),'model_sha256':modelsha,'mother_sha256':sha(dest/'model.blend'),'geometry_signature':signature,'preserved_binary_prefix_bytes':overlay.prefix_bytes,'preserved_binary_prefix_sha256':overlay.prefix_sha256,'changed_clips':['Run'],'preserved_clips':['Idle','Walk','Start','Stop','TurnLeft','TurnRight'],'changed_channels':overlay.changed,'preserved':'all non-target channels, roots, leg motions, geometry, topology, UVs, weights, rest bones, materials and texture bytes','motion_source':'project-authored procedural gait from the pinned prior candidate, not mocap or trained AI','blender_version':bpy.app.version_string,'art_approved':False,'game_ready':False})
 print('V16_BUILT',key,modelsha,'hand crossings',audit[0]['hand_skin_crossings'],flush=True)
