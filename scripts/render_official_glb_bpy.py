"""Render ACTUAL official 3DCodeVerse-built GLB with Blender Cycles.

This is a model render, not an AI-generated promotional picture.
Input is the GLB from official Harness spatial build; source geometry is unchanged.
Used when the upstream render_views host cannot run without Puppeteer.
"""
import bpy, math, pathlib, sys
from mathutils import Vector

if '--' not in sys.argv:
    raise SystemExit('Expected -- <source.glb> <output_dir>')
argv=sys.argv[sys.argv.index('--')+1:]
assert len(argv)==2,argv
source=pathlib.Path(argv[0]).resolve()
out=pathlib.Path(argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes=[o for o in bpy.data.objects if o.type=='MESH']
if not meshes:
    raise RuntimeError('GLB has no 3D geometry')
corners=[o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
mn=Vector(tuple(min(c[i] for c in corners) for i in range(3)))
mx=Vector(tuple(max(c[i] for c in corners) for i in range(3)))
center=(mn+mx)/2
dims=mx-mn
span=max(dims.x,dims.y,dims.z)

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=20
scene.cycles.use_denoising=True
scene.render.resolution_x=960
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False

world=bpy.data.worlds.new('Neutral Studio World') if scene.world is None else scene.world
scene.world=world
world.use_nodes=True
background=world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value=(.72,.75,.79,1.0)
background.inputs['Strength'].default_value=.7

# Render-only floor, never exported back into the model.
bpy.ops.mesh.primitive_plane_add(size=150,location=(center.x,center.y,mn.z-.04))
floor=bpy.context.object
floor.name='RENDER_ONLY_FLOOR'
mat=bpy.data.materials.new('MatteNeutralStudio')
mat.diffuse_color=(.78,.79,.81,1.0)
floor.data.materials.append(mat)
for offset,power,size in [((3,-4,7),1200,5),((-5,-1,4),800,4),((1,5,6),1400,5)]:
    bpy.ops.object.light_add(type='AREA',location=center+Vector(offset))
    light=bpy.context.object
    light.data.energy=power
    light.data.size=size

bpy.ops.object.camera_add()
cam=bpy.context.object
cam.name='3DCodeVerse Real GLB Multi-angle Camera'
cam.data.type='ORTHO'
cam.data.ortho_scale=span*1.32
scene.camera=cam

# These names preserve downstream supervisor/collector expectations.
angles=[
    ('view_top.png',(.1,-.35,1.65)),
    ('view_front.png',(.05,-1.35,.25)),
    ('view_back_left_high.png',(-1.2,.95,.58)),
    ('view_front_right_high.png',(.9,-1.25,.59)),
]
for filename,vec in angles:
    cam.location=center+Vector(vec)*span*1.12
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/filename)
    bpy.ops.render.render(write_still=True)
    p=out/filename
    if not p.exists() or p.stat().st_size<12000:
        raise RuntimeError(f'Invalid genuine 3D render: {p}')
    print('REAL_GLB_RENDER_OK',filename,p.stat().st_size,flush=True)
print('ALL_FOUR_TRUE_3D_VIEWS_RENDERED',source,flush=True)
