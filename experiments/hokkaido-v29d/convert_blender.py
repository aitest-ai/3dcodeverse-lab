"""Convert generated v29d MANIFOLD 3D geometry into actual Blender GLB.
No 2D image generation or image-plane meshes. Surfaces come from the two
reference-outline SDF fields, and are full closed 3D meshes.
"""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
root=Path("candidate").resolve()
assert (root/"v29d_bear_head.ply").is_file()
assert (root/"v29d_salmon.ply").is_file()
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
def m(name,color):
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*color,1.)
    mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value=(*color,1.)
    bsdf.inputs["Roughness"].default_value=.91
    return mat
bearmat=m("V29D_BEAR_NEUTRAL_CARVED_WALNUT",(.18,.091,.047))
fishmat=m("V29D_SALMON_NEUTRAL_WOOD",(.43,.25,.11))
nosemat=m("V29D_DARK_WOOD_ENDGRAIN",(.063,.032,.015))
for stem,material,name in [
 ("v29d_bear_head",bearmat,"V29D_ORIGINAL_SILHOUETTE_BEAR_HEAD"),
 ("v29d_salmon",fishmat,"V29D_ORIGINAL_SILHOUETTE_SALMON")]:
    prior=set(bpy.data.objects.keys())
    bpy.ops.wm.ply_import(filepath=str(root/(stem+".ply")))
    newest=[o for o in bpy.data.objects if o.name not in prior and o.type=="MESH"]
    assert len(newest)==1,(stem,len(newest))
    ob=newest[0]
    ob.name=name
    ob.data.materials.clear()
    ob.data.materials.append(material)
    for poly in ob.data.polygons:poly.use_smooth=True
# Real small triangular nose carved from same forward tip region, no buttons.
verts=[(-2.793,-.088,1.252),(-2.793,.088,1.252),(-2.807,0,1.165),
       (-2.712,-.095,1.259),(-2.712,.095,1.259),(-2.717,0,1.166)]
faces=[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]
md=bpy.data.meshes.new("HandcutNoseMesh")
md.from_pydata(verts,[],faces);md.update()
nose=bpy.data.objects.new("V29D_TRIANGULAR_NOSE_ENDGRAIN",md)
bpy.context.collection.objects.link(nose);nose.data.materials.append(nosemat)
bevel=nose.modifiers.new("GentlyCarvedNose","BEVEL")
bevel.width=.012;bevel.segments=2
bpy.ops.object.select_all(action="DESELECT")
nose.select_set(True);bpy.context.view_layer.objects.active=nose
bpy.ops.object.modifier_apply(modifier=bevel.name)
for p in nose.data.polygons:p.use_smooth=True
# Rotate axes so output matches entire v25-28 bear project's orientation.
world=Matrix.Translation(Vector((0,0,-.06))) @ Matrix.Rotation(math.pi/2,4,"Z")
for ob in bpy.data.objects:
    ob.matrix_world=world @ ob.matrix_world
dest=root/"v29d_silhouette_real.blender.glb"
bpy.ops.export_scene.gltf(filepath=str(dest),export_format="GLB",
                          export_apply=True,export_yup=True)
assert dest.exists() and dest.stat().st_size>250000
print("V29D_REAL_BLENDER_GLB",dest,dest.stat().st_size,flush=True)
