import bpy,math,os,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'evidence/character';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/harbor-courier.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
for t in rig.animation_data.nla_tracks:t.mute=True
rig.animation_data.action=bpy.data.actions['Idle'];bpy.context.scene.frame_set(12)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=False;sc.render.resolution_x=700;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.world.color=(.35,.35,.35)
for loc,power,size in [((3,-4,5),500,4),((-3,-1,3),350,3),((0,4,4),700,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.name='Preview ground';mat=bpy.data.materials.new('Warm paper');mat.diffuse_color=(.65,.67,.59,1);floor.data.materials.append(mat);floor.location.z=-.025
bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam
for name,loc,target,lens in [('front',(0,-4,1.1),(0,0,.94),60),('side',(4,0,1.1),(0,0,.94),60),('back',(0,4,1.1),(0,0,.94),60),('face',(.08,-1.05,1.69),(0,-.01,1.65),70)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;sc.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
