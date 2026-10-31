"""Read/diagnose the actual V31 output; do not call this a production edit."""
from pathlib import Path
import os,json
import bpy
from mathutils import Vector
root=Path('input/prior').resolve();out=Path('outputs/probe').resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'shui.blend'))
scene=bpy.context.scene;scene.frame_set(0);bpy.context.view_layer.update()
shirt=bpy.data.objects['OpenSourceCloth_shui_namuhekam_male_polo_shirt']
report={'modifiers':[{'name':m.name,'type':m.type,'render':m.show_render,'viewport':m.show_viewport} for m in shirt.modifiers],
 'attributes':[{'name':a.name,'type':a.data_type,'domain':a.domain} for a in shirt.data.attributes],
 'has_custom_normals':shirt.data.has_custom_normals,'vertices':len(shirt.data.vertices),'faces':len(shirt.data.polygons)}
scene.render.engine='CYCLES';scene.cycles.samples=20;scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';camera=scene.camera
camera.location=(0,3,.9);target=Vector((0,-.01,.9));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=.49

def render(name):
 scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
render('as_delivered')
shirt.data.normals_split_custom_set([(0.,0.,0.)]*len(shirt.data.loops));shirt.data.update()
render('automatic_normals')
bs=next(n for n in shirt.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
for link in list(bs.inputs['Normal'].links):shirt.data.materials[0].node_tree.links.remove(link)
render('automatic_normals_no_normal_map')
for link in list(bs.inputs['Base Color'].links):shirt.data.materials[0].node_tree.links.remove(link)
bs.inputs['Base Color'].default_value=(.3,.3,.3,1)
render('flat_gray_no_textures')
(out/'diagnostic.json').write_text(json.dumps(report,indent=2));print('V31_HEM_DIAGNOSTIC',json.dumps(report),flush=True)
