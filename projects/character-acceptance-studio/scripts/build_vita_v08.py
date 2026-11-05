"""Append native Vita transitions to frozen v0.1.0. Existing three clips and geometry stay byte-identical."""
import bpy,sys,json,hashlib,os,math,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import pose_basis,bake_actions,Capture,restore_basis,bone_world
from v07.overlay import ClipOverlay
from v07.rig import Legs,skirt
from v07.regions import native_regions
from v06.refine import relaxed_fingers,turn_heading_twist,turn_settle
BASE=R/'library-v07/vroid-vita-motion-review/0.1.0';OUT=Path(os.environ.get('STUDIO_V08_OUT',str(R/'work/v08-build'))).resolve()/'vroid-vita-motion-review/0.2.0';OUT.mkdir(parents=True,exist_ok=True)
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta=json.loads((BASE/'adaptation.json').read_text())
assert h(BASE/'model.glb')==meta['model_sha256'] and h(BASE/'model.blend')==meta['mother_sha256']
bpy.ops.wm.open_mainfile(filepath=str(BASE/'model.blend'));oldrig=bpy.data.objects['Armature'];oldroot=bpy.data.objects['StudioRootMotion_v05'];baked={}
for name in ['Idle','Walk','Run']:
 for ob in [oldrig,oldroot]:
  for tr in ob.animation_data.nla_tracks:tr.mute=True
  a=bpy.data.actions[name if ob==oldrig else name+'_Root'];ob.animation_data.action=a
  if a.slots:ob.animation_data.action_slot=a.slots[0]
 poses=[]
 for i in range(round(oldrig.animation_data.action.frame_range[1])+1):
  bpy.context.scene.frame_set(i);poses.append({'bones':pose_basis(oldrig),'root':{'p':list(oldroot.location),'q':list(oldroot.rotation_quaternion),'s':list(oldroot.scale)}})
 baked[name]=poses
# Independent working copy initialized from original Vita rest rig and Harbor world reference.
from v08.vita_setup import *
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
legs=Legs(rig,body,root,footids,sets,{s:list(q) for s,q in flat.items()});overlay=ClipOverlay(BASE/'model.glb');audit={};idle=baked['Idle'][0];idle_z=idle['root']['p'][2]
for name in ['Start','Stop','TurnLeft','TurnRight']:
 D=planner.duration[name];N=round(D*60);frames=[];poses=[];rows=[]
 for i in range(N+1):
  t=i/60;sc.frame_set(i);plan=planner.sample(name,t);base(name,t,plan)
  if name in ['Start','Stop']:
   blend=plan['walk_blend'];ratio=.99+( .96+.02*math.cos(4*math.pi*(plan['phase']-.30))-.99)*blend
   legs.pelvis(plan['phase'],center=ratio,amplitude=0)
  solved=legs.correct(plan)
  turn_heading_twist(rig,root,name)
  skirt(rig,rest_world,plan,0);relaxed_fingers(rig,name,t,D)
  # Idle is already finger/garment-corrected: settle after those edits, never apply them twice.
  turn_settle(rig,root,name,t,D,idle['bones'],idle_z)
  frames.append(capture.frame(root.matrix_world));poses.append({'bones':pose_basis(rig),'root':{'p':list(root.location),'q':list(root.rotation_quaternion),'s':list(root.scale)}})
  rows.append({'t':t,'root':list(root.location),'heading':plan['yaw'],**solved,**legs.audit(plan)})
 overlay.replace_clip(name,[i/60 for i in range(N+1)],frames);baked[name]=poses;audit[name]={'duration_s':D,'samples':rows};print('Vita v08',name,'complete',flush=True)
sha=overlay.save(OUT/'model.glb');regions=native_regions(body,rig);bake_actions(rig,root,baked,60);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True)
def write(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
write('collision-regions.json',regions);write('motion-audit.json',{'fps':60,'clips':audit,'unchanged_clips':['Idle','Walk','Run']})
meta.update(version='0.2.0',base_model=str((BASE/'model.glb').relative_to(R)),base_model_sha256=h(BASE/'model.glb'),base_mother=str((BASE/'model.blend').relative_to(R)),base_mother_sha256=h(BASE/'model.blend'),model_sha256=sha,mother_sha256=h(OUT/'model.blend'),original_binary_prefix_bytes=overlay.prefix_bytes,original_binary_prefix_sha256=overlay.prefix_sha256,changed_clips=list(audit),unchanged_clips=['Idle','Walk','Run'],walk_stride_m=planner.strides['Walk'],walk_period_s=planner.periods['Walk'],turn_correction='Heading-aware axial twist; final 15% settles to exact corrected native Idle pose including fingers and skirt.',transition_pelvis='Blend native Idle 0.99 ratio to the frozen Walk 0.96 + 0.02*cos(4pi*(phase-0.30)) envelope using planner walk_blend.',art_approved=False,game_ready=False)
for k in ['baseline_sha256','baseline_mother_sha256','baseline_status']:meta.pop(k,None)
write('adaptation.json',meta);print('V08_COMPLETE',sha,flush=True)
