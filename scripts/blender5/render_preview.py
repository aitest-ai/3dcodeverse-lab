"""Render review images for an asset .blend (headless, Cycles CPU so it works on GitHub Actions without a GPU).
Usage: blender -b outputs/<asset_id>.blend --python scripts/blender5/render_preview.py -- <out_dir> <clip:frame:view> ...
views: front | back | side | three.   Default: front/side/back of the first frame of the Idle action.
"""
import bpy, sys, math, os
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = argv[0] if argv else "outputs/preview"
os.makedirs(out, exist_ok=True)
specs = argv[1:] or ["Idle:1:front", "Idle:1:side", "Idle:1:back"]
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24; sc.cycles.use_denoising = False
sc.render.resolution_x = 420; sc.render.resolution_y = 520; sc.render.film_transparent = False
w = bpy.data.worlds.new("w"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.74, 0.88, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
sc.world = w
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0)); fl = bpy.context.object
m = bpy.data.materials.new("floor"); m.use_nodes = True; m.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.35, 0.42, 0.3, 1); fl.data.materials.append(m)
sun = bpy.data.lights.new("sun", 'SUN'); sun.energy = 3.2; so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
cam = bpy.data.cameras.new("cam"); cam.lens = 70; co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
rig.animation_data_create()
VIEW = {"front": (0, -1), "back": (0, 1), "side": (1, 0), "three": (0.7, -0.7)}
for spec in specs:
    clip, frame, view = spec.split(":")
    rig.animation_data.action = bpy.data.actions[clip]
    sc.frame_set(int(frame))
    dx, dy = VIEW[view]; d = 5.0
    co.location = (dx * d, dy * d, 0.78); direction = Vector((0, 0, 0.7)) - co.location
    co.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(out, "%s_%s_%s.png" % (clip, frame, view))
    bpy.ops.render.render(write_still=True)
print("PREVIEW_DONE")
