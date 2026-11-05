"""New Vivi 0.3 candidate: Run pelvis envelope + native-length foot IK, preserving all six other GLB clips."""
import bpy,json,sys,os,hashlib,math
from pathlib import Path
from mathutils import Matrix,Quaternion
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import *
from v07.rig import Legs,skirt,bn
from v07.overlay import ClipOverlay
from gait_plan_v02 import Planner
BASE=R/'library-v06/vroid-vivi-motion-review/0.2.0';ORIGINAL=R/'library-v04/vroid-vivi/1.0.0/model.glb';CALIB=R/'library-v05/vroid-vivi-motion-review/0.1.0/adaptation.json';OUT=Path(os.environ.get('STUDIO_V07_OUT',str(R/'work/v07-build'))).resolve()/'vroid-vivi-motion-review'/'0.3.0';OUT.mkdir(parents=True,exist_ok=True);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base=json.loads((BASE/'adaptation.json').read_text());assert h(BASE/'model.glb')==base['model_sha256'] and h(BASE/'model.blend')==base['mother_sha256']
bpy.ops.wm.open_mainfile(filepath=str(BASE/'model.blend'));rig=bpy.data.objects['Armature'];root=bpy.data.objects['StudioRootMotion_v05'];body=bpy.data.objects['Body'];sc=bpy.context.scene

def action(name):
 for o in [rig,root]:
  for tr in o.animation_data.nla_tracks:tr.mute=True
  a=bpy.data.actions[name if o==rig else name+'_Root'];o.animation_data.action=a
  if a.slots:o.animation_data.action_slot=a.slots[0]
action('Idle');sc.frame_set(0);cal=json.loads(CALIB.read_text());legs=Legs(rig,body,root,cal['foot_vertex_ids'],cal['contact_sets'],cal['flat_foot_world_quaternions']);rest={b.name:Quaternion((0,0,1),math.pi).to_matrix().to_4x4()@rig.matrix_local@b.matrix_local for b in rig.data.bones};capture=Capture(rig,ORIGINAL);overlay=ClipOverlay(BASE/'model.glb');planner=Planner(legs.leg,.075,4/3,.7);planner.strides={'Walk':cal['walk_stride_m'],'Run':cal['run_stride_m']};baked={};audit={};baseline=[]
for name in ['Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight']:
 action(name);oldN=round(rig.animation_data.action.frame_range[1]);N=42 if name=='Run' else oldN;frames=[];poses=[];rows=[]
 for i in range(N+1):
  pos=i*oldN/N;sc.frame_set(math.floor(pos),subframe=pos-math.floor(pos));solve={}
  if name=='Run':
   plan=planner.sample(name,i/60);before=legs.audit(plan);baseline.append(before);ratio=legs.pelvis(plan['phase']);solve=legs.correct(plan);skirt(rig,rest,plan,.07);row=legs.audit(plan);rows.append({'t':i/60,'root':list(root.location),'heading':0,'requested_leg_height_ratio':ratio,**solve,**row})
  frames.append(capture.frame(root.matrix_world));poses.append({'bones':pose_basis(rig),'root':{'p':list(root.location),'q':list(root.rotation_quaternion),'s':list(root.scale)}})
 if name=='Run':overlay.replace_clip(name,[i/60 for i in range(N+1)],frames);audit[name]={'duration_s':N/60,'samples':rows}
 baked[name]=poses;print(name,'captured',flush=True)
sha=overlay.save(OUT/'model.glb');bake_actions(rig,root,baked,60);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True)
meta={'asset_id':'vroid-vivi-motion-review','version':'0.3.0','base_model':str((BASE/'model.glb').relative_to(R)),'base_model_sha256':h(BASE/'model.glb'),'base_mother':str((BASE/'model.blend').relative_to(R)),'base_mother_sha256':h(BASE/'model.blend'),'original_geometry':str(ORIGINAL.relative_to(R)),'original_geometry_sha256':h(ORIGINAL),'contact_calibration':str(CALIB.relative_to(R)),'contact_calibration_sha256':h(CALIB),'model_sha256':sha,'mother_sha256':h(OUT/'model.blend'),'preserved_binary_prefix_bytes':overlay.prefix_bytes,'changed_clips':['Run'],'preserved_clips':['Idle','Walk','Start','Stop','TurnLeft','TurnRight'],'run_period_s':.7,'run_speed_m_s':cal['run_stride_m']/.7,'pelvis_ratio_center':.94,'pelvis_ratio_amplitude':.01,'source_motion':'project-authored previous candidate, not mocap/trained AI','contact_sets':cal['contact_sets'],'foot_vertex_ids':cal['foot_vertex_ids'],'art_approved':False,'game_ready':False};(OUT/'adaptation.json').write_text(json.dumps(meta,indent=2)+'\n');(OUT/'motion-audit.json').write_text(json.dumps({'fps':60,'clips':audit,'baseline_run_phase_matched':baseline},indent=2)+'\n');print('V07_VIVI',sha,flush=True)
