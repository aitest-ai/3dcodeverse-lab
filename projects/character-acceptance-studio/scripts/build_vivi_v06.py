"""Refine v0.1.0 in a new v0.2.0 candidate; preserve the original geometry; turn twist/settling is separately audited."""
import bpy,json,os,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture,pose_basis,bake_actions
from v06.motion_overlay import MotionOverlay
from v06.refine import relaxed_fingers,skirt_clearance,FINGER_POSES,CLOTH_EASE_M_PER_RAD,turn_heading_twist,turn_settle
BASE=R/'library-v05/vroid-vivi-motion-review/0.1.0';ORIGINAL=R/'library-v04/vroid-vivi/1.0.0/model.glb';OUT=Path(os.environ.get('STUDIO_V06_OUT',str(R/'work/v06-build'))).resolve()/'vroid-vivi-motion-review'/'0.2.0';OUT.mkdir(parents=True,exist_ok=True)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for row in json.loads((BASE/'files.json').read_text())['files']:
 if row['file'] in ['model.blend','model.glb']:assert h(BASE/row['file'])==row['sha256'],'Base version changed'
bpy.ops.wm.open_mainfile(filepath=str(BASE/'model.blend'));rig=bpy.data.objects['Armature'];root=bpy.data.objects['StudioRootMotion_v05'];capture=Capture(rig,ORIGINAL);overlay=MotionOverlay(BASE/'model.glb');baked={};audit={};sc=bpy.context.scene
allowed={i for i,n in enumerate(overlay.doc['nodes']) if any(part in n.get('name','') for part in ['_Index','_Middle','_Ring','_Little','_Thumb']) or n.get('name') in ['J_Sec_L_SkirtFront0','J_Sec_R_SkirtFront0']}
idle=None;idle_z=None
for name in ['Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight']:
 for ob in [rig,root]:
  for tr in ob.animation_data.nla_tracks:tr.mute=True
  a=bpy.data.actions[name if ob==rig else name+'_Root'];ob.animation_data.action=a
  if a.slots:ob.animation_data.action_slot=a.slots[0]
 N=round(rig.animation_data.action.frame_range[1]);D=N/60;frames=[];poses=[];maxease=0
 for i in range(N+1):
  sc.frame_set(i)
  if name=='Idle' and i==0:idle=pose_basis(rig);idle_z=root.location.z
  turn_heading_twist(rig,root,name);turn_settle(rig,root,name,i/60,D,idle,idle_z);relaxed_fingers(rig,name,i/60,D);ease=skirt_clearance(rig,root,name);maxease=max(maxease,max(ease.values(),default=0));frames.append(capture.frame(root.matrix_world));poses.append({'bones':pose_basis(rig),'root':{'p':list(root.location),'q':list(root.rotation_quaternion),'s':list(root.scale)}})
 overlay.patch(name,frames,set(capture.map)|{capture.wrapper} if name.startswith('Turn') else allowed);baked[name]=poses;audit[name]={'duration_s':D,'frames':N+1,'maximum_front_support_translation_m':maxease};print(name,'complete','max support ease',maxease,flush=True)
sha=overlay.save(OUT/'model.glb');bake_actions(rig,root,baked,60);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True)
meta={'asset_id':'vroid-vivi-motion-review','version':'0.2.0','base_model':str((BASE/'model.glb').relative_to(R)),'base_model_sha256':h(BASE/'model.glb'),'base_mother':str((BASE/'model.blend').relative_to(R)),'base_mother_sha256':h(BASE/'model.blend'),'original_geometry':str(ORIGINAL.relative_to(R)),'original_geometry_sha256':h(ORIGINAL),'model_sha256':sha,'mother_sha256':h(OUT/'model.blend'),'original_binary_prefix_bytes':overlay.prefix_bytes,'original_binary_prefix_sha256':overlay.prefix_sha256,'finger_angles_radians':FINGER_POSES,'finger_factors':{'Index':.88,'Middle':1,'Ring':1.08,'Little':1.15,'Thumb':.55},'skirt_front_ease_m_per_radian':CLOTH_EASE_M_PER_RAD,'turn_correction':'Heading-aware axial twist on upper arms, thighs and shins, preserving joint/foot world positions; final 15% settles to exact Idle in turned root frame. Contact drift is independently measured.','scope':'Run-only front-support translation based on native thigh pitch; original topology, skin weights, textures and rest rig unchanged. Not a cloth simulation or full-body collision approval.','changed_channels':overlay.changed,'clips':audit,'art_approved':False,'game_ready':False};(OUT/'adaptation.json').write_text(json.dumps(meta,indent=2)+'\n');print('V06_COMPLETE',sha,flush=True)
