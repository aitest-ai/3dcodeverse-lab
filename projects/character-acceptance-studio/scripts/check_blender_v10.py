"""Cold-open complete candidate masters and generate native-body surface probes + true offline CPU renders."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.blender_utils import vertices
E=R/'evidence-v10';W=R/'work/v10-cold';W.mkdir(exist_ok=True);(E/'blender').mkdir(exist_ok=True);reports=[]
for key in ['horse-brown','horse-white']:
 F=R/'library-v10'/(key+'-grounded-review')/'0.1.0';meta=json.loads((F/'adaptation.json').read_text());assert hashlib.sha256((F/'model.blend').read_bytes()).hexdigest()==meta['mother_sha256'];bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'));rig=bpy.data.objects['AnimalArmature'];body=bpy.data.objects['Horse'];scale=meta['display_calibration']['scale'];offset=meta['display_calibration']['offset_y'];clips={}
 assert len(rig.data.bones)==50 and len(bpy.data.actions)==13
 for name in ['Walk','Gallop']:
  rig.animation_data.action=bpy.data.actions[name]
  if rig.animation_data.action.slots:rig.animation_data.action_slot=rig.animation_data.action.slots[0]
  D=float(rig.animation_data.action.frame_range[1])/24;poses=[]
  for phase in [0,.125,.5,.875,1]:
   f=D*phase*24;bpy.context.scene.frame_set(int(f),subframe=f%1);poses.append({'phase':phase,'time_s':D*phase,'body':[[v.x*scale,v.z*scale+offset,-v.y*scale] for v in vertices(body)]})
  clips[name]=poses
 (W/(key+'.json')).write_text(json.dumps(clips));reports.append({'source_id':key,'model_sha256':meta['model_sha256'],'mother_sha256':meta['mother_sha256'],'bones':50,'editable_actions':13,'probes_per_clip':5,'native_body_vertices':len(body.data.vertices),'world_sliding':'not-tested'})
 # Transient render scene; candidate mother is never saved after adding cameras/ground.
 if bpy.data.objects.get('Icosphere'):bpy.data.objects['Icosphere'].hide_render=True
 rig.animation_data.action=bpy.data.actions['Gallop']
 if rig.animation_data.action.slots:rig.animation_data.action_slot=rig.animation_data.action.slots[0]
 bpy.context.scene.frame_set(3);scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.resolution_x=640;scene.render.resolution_y=480;scene.render.resolution_percentage=100;scene.world.color=(.28,.28,.28)
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-offset/scale));plane=bpy.context.object;mat=bpy.data.materials.new('v10 verification floor');mat.diffuse_color=(.37,.43,.39,1);plane.data.materials.append(mat)
 for pos,power,size in [((3,-4,9),1800,6),((-4,4,7),1200,5)]:
  data=bpy.data.lights.new('v10 area','AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new('v10 area',data);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
 camera=bpy.data.objects.new('v10 camera',bpy.data.cameras.new('v10 camera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=10.6;points=vertices(body)+vertices(bpy.data.objects['ManeTail_IndividualWisps']);lo=Vector(tuple(min(v[j] for v in points) for j in range(3)));hi=Vector(tuple(max(v[j] for v in points) for j in range(3)));lo.z=min(lo.z,-offset/scale);center=(lo+hi)/2
 for view,pos in [('front',(0,-12,2.5)),('side',(12,0,2.5)),('back',(0,12,2.5))]:
  camera.location=center+Vector((14 if view=='side' else 0,-14 if view=='front' else 14 if view=='back' else 0,.45));camera.data.ortho_scale=max(hi.y-lo.y if view=='side' else hi.x-lo.x,(hi.z-lo.z)*640/480)*1.16;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(E/'blender'/(key+'-'+view+'.png'));bpy.ops.render.render(write_still=True)
 print('COLD_AND_RENDER',key,flush=True)
(E/'blender-cold.json').write_text(json.dumps({'renderer':'Blender 5.2.3 Cycles CPU, 12 samples, 640x480; three still views per horse at Gallop 0.125s; not offline animation/art approval','entries':reports},indent=2)+'\n')
