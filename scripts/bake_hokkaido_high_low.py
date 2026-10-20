"""Bake *measured* original-sculpt detail into a decimated, newly unwrapped bear.
Three real Blender Cycles bakes: high->low tangent normals, high->low
procedural-wood albedo, and low-geometry AO. Exports a genuine PBR GLB.
This is not an AI image generator or 3DCodeVerse autonomous agent.
"""
import bpy, argparse, sys, json, pathlib, math, numpy as np
from mathutils import Vector

argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
parser=argparse.ArgumentParser()
parser.add_argument('--source',required=True)
parser.add_argument('--out',required=True)
parser.add_argument('--resolution',type=int,default=1024)
parser.add_argument('--target-triangles',type=int,default=28000)
args=parser.parse_args(argv)
assert args.resolution in (512,1024,2048)
dst=pathlib.Path(args.out).resolve();dst.mkdir(parents=True,exist_ok=True)
src=pathlib.Path(args.source).resolve()
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(src))
original=[o for o in bpy.data.objects if o.type=='MESH']
hi=next((o for o in original if 'Kuma_Handcarved_OnePiece' in o.name),None)
if hi is None: raise RuntimeError('Source 3DCodeVerse GLB has no named bear body')
source_faces=len(hi.data.polygons)
lo=hi.copy();lo.data=hi.data.copy()
lo.name='Kuma_Baked_UV_Lowpoly';bpy.context.collection.objects.link(lo)
lo.matrix_world=hi.matrix_world.copy()
for o in bpy.context.selected_objects:o.select_set(False)
lo.hide_set(False);lo.select_set(True);bpy.context.view_layer.objects.active=lo
dec=lo.modifiers.new('Preserve_Silhouette_Decimate','DECIMATE')
dec.ratio=min(1.0,args.target_triangles/max(source_faces,1))
bpy.ops.object.modifier_apply(modifier=dec.name)
print('LOWPOLY',source_faces,len(lo.data.polygons),flush=True)
# UV remap after decimation: never reuse the stretched pseudo-cylindrical UV.
lo.data.uv_layers.clear()
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(island_margin=0.012)
bpy.ops.object.mode_set(mode='OBJECT')
uv=lo.data.uv_layers.active
assert uv is not None and len(uv.data)==len(lo.data.loops)
co=np.empty(len(uv.data)*2,dtype=np.float32)
uv.data.foreach_get('uv',co)
xy=co.reshape(-1,2)
in01=np.mean(np.all((xy>=-0.0001)&(xy<=1.0001),axis=1))
finite=bool(np.isfinite(xy).all())
assert finite and in01>0.999,'UV coordinate coverage failed'
print('NEW_UV',len(lo.data.uv_layers),in01,flush=True)

# Mark nonzero UV triangles and approximate world-space texel density spread.
lo.data.calc_loop_triangles()
areas2=[];ratios=[]
for t in lo.data.loop_triangles:
    ids=np.array(t.loops)
    a,b,c=xy[ids]
    uv_area=abs(float(np.cross(b-a,c-a)))*.5
    if uv_area>1e-11 and t.area>1e-10:
        areas2.append(uv_area);ratios.append(math.sqrt(uv_area/t.area))
tri_coverage=len(areas2)/max(1,len(lo.data.loop_triangles))
assert tri_coverage>.995,f'Degenerate UVs: {tri_coverage}'
ratio=np.percentile(ratios,[10,50,90])
density_spread=float(ratio[2]/max(ratio[0],1e-9))
print('UV_DENSITY_P10_P50_P90',ratio.tolist(),'spread',density_spread,flush=True)

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=12
scene.render.bake.use_clear=True
scene.render.bake.margin=12
scene.render.bake.use_selected_to_active=True
scene.render.bake.max_ray_distance=.06

# High-poly sculpt is the actual 3DCodeVerse geometry.
# Use 3D Object coordinates for wood grain so the texture does not depend
# on old UVs or project unrealistic stripes onto the bear's face.
wood=bpy.data.materials.new('Highpoly_Wood_For_Color_Bake')
wood.use_nodes=True
nodes=wood.node_tree.nodes;links=wood.node_tree.links
bs=nodes.get('Principled BSDF')
coord=nodes.new('ShaderNodeTexCoord')
n=nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=4.2
n.inputs['Detail'].default_value=4
wave=nodes.new('ShaderNodeTexWave');wave.wave_type='BANDS'
wave.bands_direction='X';wave.inputs['Scale'].default_value=21.0
wave.inputs['Distortion'].default_value=3.0
wave.inputs['Detail'].default_value=3.0
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.18
ramp.color_ramp.elements[0].color=(.085,.039,.019,1)
ramp.color_ramp.elements[1].position=.86
ramp.color_ramp.elements[1].color=(.235,.120,.059,1)
ramp.color_ramp.elements.new(.49).color=(.155,.072,.034,1)
links.new(coord.outputs['Generated'],n.inputs['Vector'])
links.new(coord.outputs['Generated'],wave.inputs['Vector'])
links.new(n.outputs['Fac'],wave.inputs['Distortion'])
links.new(wave.outputs['Fac'],ramp.inputs['Fac'])
links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
hi.data.materials.clear();hi.data.materials.append(wood)
for poly in hi.data.polygons:poly.material_index=0

lowmat=bpy.data.materials.new('Hokkaido_Genuine_Baked_Wood_PBR')
lowmat.use_nodes=True
lo.data.materials.clear();lo.data.materials.append(lowmat)
for face in lo.data.polygons:face.material_index=0
nt=lowmat.node_tree
bs_low=nt.nodes.get('Principled BSDF')
res=args.resolution
def img_bake(name,color,space):
    image=bpy.data.images.new(name,width=res,height=res,alpha=False)
    image.generated_color=color
    image.colorspace_settings.name=space
    node=nt.nodes.new('ShaderNodeTexImage');node.image=image
    nt.nodes.active=node
    return image,node

def choose_bake(selected_to_active):
    bpy.ops.object.select_all(action='DESELECT')
    hi.hide_set(False)
    hi.select_set(selected_to_active)
    lo.select_set(True)
    bpy.context.view_layer.objects.active=lo
    scene.render.bake.use_selected_to_active=selected_to_active

def save_map(img,name):
    img.filepath_raw=str(dst/name);img.file_format='PNG'
    img.save()
    return img

# Selected-to-active NORMAL: compare original 112k+ sculpt to new 28k UV mesh.
normal,node_normal=img_bake('TRUE_HighToLow_Normal',(0.5,0.5,1,1),'Non-Color')
choose_bake(True)
bpy.ops.object.bake(type='NORMAL',normal_space='TANGENT')
save_map(normal,'baked_tangent_normal.png')
print('BAKED_HIGH_TO_LOW_NORMAL',flush=True)
# DIFFUSE Color: original high-poly surface procedural grain projected to the NEW UV.
base,node_base=img_bake('True_Baked_Wood_Albedo',(0.13,0.07,0.04,1),'sRGB')
choose_bake(True)
bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'})
save_map(base,'baked_wood_basecolor.png')
print('BAKED_WOOD_DIFFUSE',flush=True)
# Real Cycles AO from visible low-poly carved body (not fake noise).
hi.hide_render=True
hi.hide_set(True)
ao,node_ao=img_bake('TRUE_Baked_Lowpoly_AO',(1,1,1,1),'Non-Color')
choose_bake(False)
bpy.ops.object.bake(type='AO')
save_map(ao,'baked_geometry_ao.png')
print('BAKED_GEOMETRY_AO',flush=True)

def rgba_flat(image):
    ar=np.empty(res*res*4,dtype=np.float32)
    image.pixels.foreach_get(ar)
    return ar.reshape(res,res,4)
ao_a=rgba_flat(ao)[:,:,0]
base_a=rgba_flat(base)
brightness=np.clip(base_a[:,:,:3].mean(axis=2),0,1)
rough=np.clip(.71+(.15-brightness)*.37+(1-ao_a)*.10,.61,.88)
orm_a=np.empty((res,res,4),dtype=np.float32)
orm_a[:,:,0]=ao_a
orm_a[:,:,1]=rough
orm_a[:,:,2]=0.0
orm_a[:,:,3]=1.0
orm=bpy.data.images.new('Baked_AO_Roughness_Metallic',width=res,height=res,alpha=True)
orm.colorspace_settings.name='Non-Color'
orm.pixels.foreach_set(orm_a.ravel())
save_map(orm,'baked_orm.png')

# Final physically-based material; ensure glTF exporter recognizes all channels.
for node in list(nt.nodes):
    if node.type=='TEX_IMAGE' and node not in (node_base,node_normal):
        nt.nodes.remove(node)
links=nt.links
links.new(node_base.outputs['Color'],bs_low.inputs['Base Color'])
bs_low.inputs['Metallic'].default_value=0.
normal_node=nt.nodes.new('ShaderNodeNormalMap')
normal_node.space='TANGENT'
normal_node.inputs['Strength'].default_value=1.0
links.new(node_normal.outputs['Color'],normal_node.inputs['Color'])
links.new(normal_node.outputs['Normal'],bs_low.inputs['Normal'])
node_orm=nt.nodes.new('ShaderNodeTexImage');node_orm.image=orm
separate=nt.nodes.new('ShaderNodeSeparateColor')
links.new(node_orm.outputs['Color'],separate.inputs['Color'])
links.new(separate.outputs['Green'],bs_low.inputs['Roughness'])
links.new(separate.outputs['Blue'],bs_low.inputs['Metallic'])
glgrp=bpy.data.node_groups.get('glTF Material Output')
if not glgrp:
    glgrp=bpy.data.node_groups.new('glTF Material Output','ShaderNodeTree')
    glgrp.interface.new_socket(name='Occlusion',in_out='INPUT',socket_type='NodeSocketFloat')
node_grp=nt.nodes.new('ShaderNodeGroup');node_grp.node_tree=glgrp
links.new(separate.outputs['Red'],node_grp.inputs['Occlusion'])
for image in (base,normal,orm):image.pack()
bpy.data.objects.remove(hi,do_unlink=True)
# Save the actual new GLB before adding studio lighting or floor.
glb=dst/'hokkaido_bear_high_low_baked.glb'
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_texcoords=True,export_normals=True,export_materials='EXPORT')
assert glb.stat().st_size>100000

qa={'source':str(src),'target_triangles':args.target_triangles,
'high_faces':source_faces,'low_faces':len(lo.data.polygons),
'uv_coordinate_valid':finite,'uv_coordinate_in_0_1':float(in01),
'nondegenerate_uv_triangle_ratio':tri_coverage,'uv_density_p10_med_p90':ratio.tolist(),
'uv_density_spread_p90_over_p10':density_spread,'resolution':res,
'normal':'Blender Cycles high-to-low tangent-space NORMAL selected-to-active',
'base_color':'Blender Cycles high-to-low DIFFUSE COLOR from 3D wood shader',
'ao':'Blender Cycles self AO from decimated body',
'roughness':'derived from physically baked albedo and AO (not baked from high)',
'other_parts':'original GLB fish and eyes preserved, texture workflow targets bear torso',
'glb_bytes':glb.stat().st_size}
(dst/'bake_qa.json').write_text(json.dumps(qa,indent=2))
print('COMPLETE_BAKE',json.dumps(qa),flush=True)

# Real Blender camera output, not an image generation preview.
for other in original:
    if other is not hi and other.name in bpy.data.objects: other.hide_render=False
lo.hide_render=False
meshes=[o for o in bpy.data.objects if o.type=='MESH']
coordinates=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
mins=Vector(tuple(min(v[i] for v in coordinates) for i in range(3)))
maxs=Vector(tuple(max(v[i] for v in coordinates) for i in range(3)))
center=(mins+maxs)*.5
span=(maxs-mins).length
scene.render.resolution_x=900;scene.render.resolution_y=700
scene.render.resolution_percentage=100
scene.cycles.samples=16
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background')
if bg:bg.inputs['Color'].default_value=(.67,.70,.75,1)
bpy.ops.object.camera_add()
cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=span*1.00
scene.camera=cam
for pos,power in [((3,-4,6),1300),((-4,-1,4),700),((1,4,5),850)]:
    bpy.ops.object.light_add(type='AREA',location=center+Vector(pos))
    light=bpy.context.object;light.data.energy=power;light.data.size=5
for name,d in [('hero',(.7,-1.0,.45)),('side',(1,0,.33))]:
    cam.location=center+Vector(d)*span*.95
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(dst/('bake_preview_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
print('RENDER_COMPLETE',flush=True)
