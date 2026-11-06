"""Export edited Run finger/upper-arm rotations to a NEW candidate; refuse silently lost edits.
Example: blender -b -t 4 --python export_hands_v16.py -- --character vivi --output new.glb
"""
import bpy,sys,argparse,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture
from v06.motion_overlay import MotionOverlay
from v06.geometry_guard import geometry_signature
FINGERS=['J_Bip_'+s+'_'+d+str(i) for s in ['L','R'] for d in ['Index','Middle','Ring','Little','Thumb'] for i in range(1,4)]
FINGERS += ['J_Bip_L_UpperArm','J_Bip_R_UpperArm']
def activate(rig,root,name):
 for ob in [rig,root]:
  for tr in ob.animation_data.nla_tracks:tr.mute=True
  a=bpy.data.actions[name if ob==rig else name+'_Root'];ob.animation_data.action=a
  if a.slots:ob.animation_data.action_slot=a.slots[0]
def other_animation_signature():
 data=[]
 for a in sorted(bpy.data.actions,key=lambda a:a.name):
  for layer in a.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      if a.name=='Run' and fc.data_path in {'pose.bones["'+n+'"].rotation_quaternion' for n in FINGERS}:continue
      data.append((a.name,fc.data_path,fc.array_index,[(list(k.co),k.interpolation) for k in fc.keyframe_points]))
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
def setup_signature():
 data=[]
 for ob in sorted(bpy.data.objects,key=lambda o:o.name):
  if ob.constraints or (ob.type=='ARMATURE' and any(p.constraints for p in ob.pose.bones)) or (ob.animation_data and ob.animation_data.drivers):raise RuntimeError('Constrained/driven edits need a full bake and a new export pipeline')
  mods=[]
  for m in ob.modifiers:
   props={}
   for p in m.bl_rna.properties:
    if p.is_readonly or p.identifier=='rna_type':continue
    v=getattr(m,p.identifier)
    if p.type in ['BOOLEAN','INT','FLOAT','STRING','ENUM']:props[p.identifier]=list(v) if getattr(p,'is_array',False) else sorted(v) if isinstance(v,set) else v
    elif p.type=='POINTER':props[p.identifier]=getattr(v,'name',None)
   mods.append((m.name,m.type,props))
  data.append((ob.name,ob.type,ob.parent.name if ob.parent else None,mods))
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
def export(key,mother,dst):
 ver={'vivi':'0.4.0','vita':'0.3.0'}[key];folder=R/'library-v16'/('vroid-'+key+'-motion-review')/ver;meta=json.loads((folder/'adaptation.json').read_text())
 if dst.exists():raise RuntimeError('Refuse overwrite '+str(dst))
 bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'));geom=geometry_signature();other=other_animation_signature();setup=setup_signature()
 if mother:
  bpy.ops.wm.open_mainfile(filepath=str(mother))
  if geometry_signature()!=geom or other_animation_signature()!=other or setup_signature()!=setup:raise RuntimeError('This exporter accepts Run finger/upper-arm rotations only. Geometry/rest/weights/textures, modifiers, parents or other motion changed: use a new full-asset export pipeline.')
 rig=bpy.data.objects['Armature'];root=bpy.data.objects['StudioRootMotion_v05'];activate(rig,root,'Run');scene=bpy.context.scene
 if scene.render.fps!=60 or scene.render.fps_base!=1 or tuple(rig.animation_data.action.frame_range)!=(0.,42.):raise RuntimeError('Changed timeline requires a new motion export pipeline')
 capture=Capture(rig,R/meta['original_geometry']);overlay=MotionOverlay(R/meta['base_model']);frames=[]
 for i in range(43):scene.frame_set(i);frames.append(capture.frame(root.matrix_world))
 overlay.patch('Run',frames,{i for i,n in capture.map.items() if n in FINGERS},properties=('rotation',),threshold=0);dst.parent.mkdir(parents=True,exist_ok=True);sha=overlay.save(dst)
 return {'file':str(dst),'sha256':sha,'art_approved':False,'game_ready':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--character',choices=['vivi','vita'],required=True);p.add_argument('--mother',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);print(json.dumps(export(a.character,a.mother,a.output.resolve())))
