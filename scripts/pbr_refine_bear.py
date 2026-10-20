"""Add reusable, GLB-compatible walnut PBR channels to a 3DCodeVerse GLB.
Based on verified UV / PBR guidance from MIT skills vendored in this repository.
Python script runs inside Blender 5.2; no AI image generator or external assets.
"""
import bpy, sys, os, math, json, pathlib, argparse
import numpy as np
from mathutils import Vector

argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
p=argparse.ArgumentParser()
p.add_argument("--source",required=True)
p.add_argument("--output",required=True)
p.add_argument("--res",type=int,default=2048)
args=p.parse_args(argv)
assert args.res in (1024,2048,4096)
out=pathlib.Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(pathlib.Path(args.source).resolve()))
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
bear=next((o for o in meshes if "Kuma_Handcarved_OnePiece" in o.name),None)
assert bear is not None,"No bear mesh in source GLB"
assert len(bear.data.uv_layers)>=1,"Bear lacks UV"
uv=bear.data.uv_layers.active
coords=np.array([tuple(v.uv) for v in uv.data],dtype=np.float32)
valid=bool(np.isfinite(coords).all())
inside=float(np.mean(np.all((coords>=-.001)&(coords<=1.001),axis=1)))
assert valid and inside>.99,f"UV values invalid or outside 0..1: {inside}"
print("UV_VALIDATION",bear.name,len(bear.data.polygons),inside,flush=True)

res=args.res
u=(np.arange(res,dtype=np.float32)+.5)/res
v=(np.arange(res,dtype=np.float32)+.5)/res
U,V=np.meshgrid(u,v)
# Hand-carved walnut: restrained long-grain variation and low-frequency figure.
warp=.018*np.sin(2*np.pi*(V*4.6+U*1.8))+.009*np.sin(2*np.pi*(V*9.3-U*3))
grain=np.sin(2*np.pi*(U*47+warp*27+.6*np.sin(2*np.pi*V*1.3)))
fine=np.sin(2*np.pi*(U*147+5*warp+V*13))
slow=np.sin(2*np.pi*(U*7+V*.33+.065*np.sin(8*V)))
veins=np.maximum(0,np.sin(2*np.pi*(U*14.4+warp*8)))**3
value=np.clip(.92+.065*grain+.025*fine+.038*slow-.037*veins,.70,1.1)
color=np.stack([np.clip(.265*value,0,1),np.clip(.136*value,0,1),np.clip(.067*value,0,1)],axis=-1)
height=.35*grain+.15*fine+.24*slow+.16*veins
hy,hx=np.gradient(height)
nx=-hx*4.5;ny=-hy*4.5;nz=np.ones_like(nx)
norm=np.sqrt(nx*nx+ny*ny+nz*nz)
normal=np.stack([.5+.5*nx/norm,.5+.5*ny/norm,.5+.5*nz/norm],axis=-1)
rough=np.clip(.78+.075*slow+.065*grain+.037*fine,.62,.94)
ao=np.clip(.94-.06*veins-.025*np.maximum(0,slow),.78,1)
orm=np.stack([ao,rough,np.zeros_like(ao)],axis=-1)

def make_image(name,array,space,file):
    alpha=np.ones((res,res,1),dtype=np.float32)
    rgba=np.concatenate((np.clip(array,0,1),alpha),axis=-1)
    img=bpy.data.images.new(name,width=res,height=res,alpha=True)
    img.colorspace_settings.name=space
    img.pixels.foreach_set(rgba.ravel())
    img.file_format='PNG';img.filepath_raw=str(out/file);img.save()
    img.pack()
    return img

albedo=make_image('Wood_BaseColor_sRGB',color,'sRGB','wood_basecolor.png')
normal_img=make_image('Wood_Normal_OpenGL_Yplus',normal,'Non-Color','wood_normal.png')
orm_img=make_image('Wood_ORM_AO_Rough_Metal',orm,'Non-Color','wood_orm.png')
mat=bpy.data.materials.new('Hokkaido_HandCarved_Walnut_PBR')
mat.use_nodes=True
n=mat.node_tree.nodes;l=mat.node_tree.links
bs=n.get('Principled BSDF')
bs.inputs['Metallic'].default_value=0
bs.inputs['Roughness'].default_value=.78
def imnode(name,img,location):
    obj=n.new('ShaderNodeTexImage');obj.name=name;obj.image=img;obj.location=location;return obj
c=imnode('BaseColor',albedo,(-650,150))
l.new(c.outputs['Color'],bs.inputs['Base Color'])
tex_n=imnode('Normal_OpenGL',normal_img,(-650,-140))
nmap=n.new('ShaderNodeNormalMap');nmap.location=(-380,-140);nmap.inputs['Strength'].default_value=.35
l.new(tex_n.outputs['Color'],nmap.inputs['Color']);l.new(nmap.outputs['Normal'],bs.inputs['Normal'])
tex_r=imnode('ORM',orm_img,(-650,-425))
split=n.new('ShaderNodeSeparateColor');split.location=(-380,-425)
l.new(tex_r.outputs['Color'],split.inputs['Color'])
l.new(split.outputs['Green'],bs.inputs['Roughness'])
l.new(split.outputs['Blue'],bs.inputs['Metallic'])
# glTF exporter recognizes this group name & input convention for AO.
grp=bpy.data.node_groups.get('glTF Material Output')
if grp is None:
    grp=bpy.data.node_groups.new('glTF Material Output','ShaderNodeTree')
    grp.interface.new_socket(name='Occlusion',in_out='INPUT',socket_type='NodeSocketFloat')
occ=n.new('ShaderNodeGroup');occ.node_tree=grp;occ.location=(-120,-540)
l.new(split.outputs['Red'],occ.inputs['Occlusion'])

# Apply PBR only to original bear mesh; maintain fish and eye materials.
bear.data.materials.clear()
bear.data.materials.append(mat)
for poly in bear.data.polygons: poly.material_index=0
path=out/'hokkaido_bear_pbr.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_texcoords=True,export_normals=True,export_materials='EXPORT')
assert path.exists() and path.stat().st_size>100000
qa={'source':args.source,'output':str(path),'resolution':res,'bear_mesh':bear.name,
'bear_faces':len(bear.data.polygons),'mesh_count':len(meshes),'uv_valid':valid,'uv_inside_0_1_ratio':inside,
'color_space':{'basecolor':'sRGB','normal':'Non-Color','orm':'Non-Color'},
'normal_map':'OpenGL +Y','orm':'R=AO G=Roughness B=Metallic',
'note':'Postprocessed official 3DCodeVerse-built GLB in Blender; upstream skills used as guidance, not as executed 3DCodeVerse AI agents.'}
(out/'qa_uv_pbr.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False))
print('PBR_EXPORT_OK',path.stat().st_size,qa,flush=True)

# Independent material render in Blender: same actual imported model + PBR, no image generation.
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=12
scene.render.resolution_x=680;scene.render.resolution_y=600;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.color=(0.65,0.65,0.65)
mins=Vector((min((o.matrix_world@Vector(v)).x for o in meshes for v in o.bound_box),min((o.matrix_world@Vector(v)).y for o in meshes for v in o.bound_box),min((o.matrix_world@Vector(v)).z for o in meshes for v in o.bound_box)))
maxs=Vector((max((o.matrix_world@Vector(v)).x for o in meshes for v in o.bound_box),max((o.matrix_world@Vector(v)).y for o in meshes for v in o.bound_box),max((o.matrix_world@Vector(v)).z for o in meshes for v in o.bound_box)))
center=(mins+maxs)/2
radius=(maxs-mins).length*.75
bpy.ops.object.camera_add(location=center+Vector((radius*.70,-radius*1.0,radius*.45)))
camera=bpy.context.object;camera.name='PBR_Preview_Camera';scene.camera=camera
camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=radius*2.05
for loc,power,size in [((3,-4,6),900,5),((-4,-2,3),500,4),((1,5,5),800,5)]:
    bpy.ops.object.light_add(type='AREA',location=center+Vector(loc))
    light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size
for label,offset in [('three_quarter',(0.70,-1.0,.45)),('side',(1.15,0,.40))]:
    camera.location=center+Vector(offset)*radius
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/('preview_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
print('PBR_RENDER_OK',flush=True)
