"""Polish a REAL MakeHuman MPFB GLB from a verified GitHub Actions artifact.

No source pack re-download. Keeps skin weights and embedded CC0 textures.
Creates 3 differentiated hairstyle lengths, material tint and simple strands.
This is a genuine Blender GLB editing pipeline, not an AI concept image.
"""
import bpy
import json
import math
import os
import sys
from pathlib import Path
from mathutils import Vector

STYLE = os.getenv("HUMAN_STYLE", "studio")
if STYLE not in ("studio", "street", "sport"):
    raise ValueError("Style must be studio, street, or sport")
INPUT = Path(os.environ.get("BASE_GLB", "inputs/baseline/human_mpfb_blender5.glb")).resolve()
OUT = Path(os.environ.get("ASSET_OUT", "outputs/human_" + STYLE)).resolve()
OUT.mkdir(parents=True, exist_ok=True)
if not INPUT.is_file(): raise FileNotFoundError(INPUT)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(INPUT))
scene=bpy.context.scene
mesh_objects=[o for o in scene.objects if o.type=="MESH"]
rigs=[o for o in scene.objects if o.type=="ARMATURE"]
if len(rigs)!=1: raise RuntimeError("Expected one MakeHuman rig, got "+str(len(rigs)))
rig=rigs[0]
def pick(fragment):
    found=[o for o in mesh_objects if o.name.lower()==fragment.lower()] or [o for o in mesh_objects if fragment in o.name.lower()]
    if len(found)!=1: raise RuntimeError("Missing/ambiguous source mesh "+fragment+" "+str([o.name for o in found]))
    return found[0]
body=pick("Human_Body_MakeHumanTopology")
hair=pick(".long01")
clothes=pick(".female_casualsuit01")
shoes=pick(".shoes01")
original_names=[o.name for o in mesh_objects]

# Keep each copied character visually distinct without destroying existing
# skinning or source image textures. Material tint is a pure Blender PBR node.
def tint_material(original, name, rgb):
    result=original.copy()
    result.name=name
    result.use_nodes=True
    bsdf=next((n for n in result.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
    if bsdf is None: raise RuntimeError("No Principled BSDF in "+original.name)
    input_color=bsdf.inputs["Base Color"]
    links=list(input_color.links)
    if links:
        link=links[0]
        result.node_tree.links.remove(link)
        mix=result.node_tree.nodes.new("ShaderNodeMixRGB")
        mix.blend_type="MULTIPLY"
        mix.inputs[0].default_value=1.0
        mix.inputs[2].default_value=(*rgb,1.0)
        result.node_tree.links.new(link.from_socket,mix.inputs[1])
        result.node_tree.links.new(mix.outputs[0],input_color)
    else:
        input_color.default_value=(*rgb,1.0)
    bsdf.inputs["Roughness"].default_value=.73 if name.startswith("Cloth") else .42
    return result

# The real MPFB garment contains the shirt AND trousers in one skinned mesh.
# Split by face average vertex height without touching geometry or weights.
color_table={
 "studio":{"upper":(.65,.70,.76),"lower":(.20,.24,.31),"shoe":(.28,.21,.17),"hair":(.43,.27,.19)},
 "street":{"upper":(.67,.80,.71),"lower":(.38,.47,.64),"shoe":(.41,.31,.22),"hair":(.64,.40,.29)},
 "sport":{"upper":(.76,.40,.38),"lower":(.17,.22,.28),"shoe":(.27,.27,.29),"hair":(.23,.16,.13)},
}
colors=color_table[STYLE]
base_garment=clothes.data.materials[0]
lower=tint_material(base_garment,"Cloth_Pants_"+STYLE,colors["lower"])
upper=tint_material(base_garment,"Cloth_Shirt_"+STYLE,colors["upper"])
clothes.data.materials.clear()
clothes.data.materials.append(lower)
clothes.data.materials.append(upper)
zvals=[(clothes.matrix_world @ v.co).z for v in clothes.data.vertices]
for poly in clothes.data.polygons:
    z=sum(zvals[i] for i in poly.vertices)/len(poly.vertices)
    poly.material_index=1 if z>0.91 else 0

original_shoe=shoes.data.materials[0]
shoes.data.materials.clear()
shoes.data.materials.append(tint_material(original_shoe,"Leather_"+STYLE,colors["shoe"]))

# Retain original high-resolution MakeHuman hair cap and rig weights. Shorten
# the opaque hair mass instead of placing procedural strands over a long board.
# Shader tint preserves original per-pixel hair texture.
original_hair=hair.data.materials[0]
hair.data.materials.clear()
hair.data.materials.append(tint_material(original_hair,"Hair_Base_"+STYLE,colors["hair"]))
cutoff={"studio":1.28,"street":1.08,"sport":1.47}[STYLE]
world=hair.matrix_world
old_verts=len(hair.data.vertices)
import bmesh
bm=bmesh.new()
bm.from_mesh(hair.data)
bm.verts.ensure_lookup_table()
trimmed=[v for v in bm.verts if (world @ v.co).z < cutoff]
if trimmed:bmesh.ops.delete(bm,geom=trimmed,context="VERTS")
bm.to_mesh(hair.data)
bm.free()
hair.data.update()
print("HAIR_TRIM",STYLE,old_verts,len(hair.data.vertices),cutoff)
if len(hair.data.vertices)<300:
    raise RuntimeError("Hair became too sparse after style trim")

# Independent thin spline locks to soften harsh straight hair-sheet edges.
# Each strand is created in world-space then converted to a skinned mesh;
# rigid head-bone skinning keeps the locks attached in GLB game engines.
head_candidates=[bone.name for bone in rig.data.bones if "head" in bone.name.lower()]
if not head_candidates:raise RuntimeError("No head bone in rig")
head_bone=head_candidates[0]
def make_strands():
    curve=bpy.data.curves.new("HairFiberSet_"+STYLE,"CURVE")
    curve.dimensions="3D"
    curve.resolution_u=4
    curve.bevel_depth=.0016 if STYLE!="sport" else .0023
    curve.bevel_resolution=1
    curve.use_fill_caps=True
    # Hair on crown from z~1.72 to neck; no fur or free-floating blobs.
    count=110 if STYLE!="sport" else 80
    length={"studio":.32,"street":.48,"sport":.17}[STYLE]
    for i in range(count):
        theta=2*math.pi*(i/count)
        # strands from the top/side with varying hairline coverage
        latitude=.38+.38*((i*19)%13)/12
        radius=.085*math.sin(latitude*math.pi/2)
        x=radius*math.cos(theta)
        y=.013+radius*math.sin(theta)
        start_z=1.71+.058*math.cos(latitude)
        sp=curve.splines.new("POLY")
        sp.points.add(5)
        for j,p in enumerate(sp.points):
            t=j/5
            drift=(.008+.034*t*t)
            py=y+(.015*t if STYLE=="street" else -.008*t)
            p.co=(x+(1 if x>=0 else -1)*drift*t,py,start_z-length*t,1)
    obj=bpy.data.objects.new("HairStrands_"+STYLE,curve)
    scene.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.convert(target="MESH")
    new=bpy.context.object
    new.data.materials.append(tint_material(original_hair,"Hair_Fibers_"+STYLE,colors["hair"]))
    # Geometry is in world coordinates; rig skinning transform uses rest bind.
    vg=new.vertex_groups.new(name=head_bone)
    vg.add(list(range(len(new.data.vertices))),1.0,"REPLACE")
    modifier=new.modifiers.new("HeadRig","ARMATURE")
    modifier.object=rig
    return new
new_hair=make_strands()

# Studio collar and sport sleeve seams are intentionally restrained:
# adjust fabric tones on source (deforming) mesh, not fake rigid costume boxes.
# The original pants/shirt UVs continue to carry their real texture maps.
studio=STYLE=="studio"
if studio:
    # Small pinned fabric collar, modeled as thin wedges in front of chest.
    for side in (-1,1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(side*.13,-.125,1.39))
        ob=bpy.context.object
        ob.name="CollarFold_"+str(side)
        ob.scale=(.075,.014,.11)
        ob.rotation_euler[1]=side*.22
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
        mat=bpy.data.materials.new("Collar_OffWhite")
        mat.diffuse_color=(.78,.80,.77,1)
        mat.use_nodes=True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.78,.80,.77,1)
        ob.data.materials.append(mat)
        # Attachment to torso with an armature modifier; fitted location
        # is approximate and must be checked in close-up.
        torso=next((b.name for b in rig.data.bones if "spine" in b.name.lower()),None)
        if torso:
            vg=ob.vertex_groups.new(name=torso)
            vg.add(list(range(len(ob.data.vertices))),1.0,"REPLACE")
            mod=ob.modifiers.new("SkinnedCollar","ARMATURE")
            mod.object=rig

# Export selected rig, all original rigged meshes plus explicitly added meshes.
bpy.context.view_layer.update()
before=max((body.matrix_world@v.co).z for v in body.data.vertices)-min((body.matrix_world@v.co).z for v in body.data.vertices)
if not 1<before<2.4:raise RuntimeError("Unexpected human height "+str(before))
outblend=OUT/("human_"+STYLE+".blend")
bpy.ops.wm.save_as_mainfile(filepath=str(outblend))
bpy.ops.object.select_all(action="DESELECT")
rig.select_set(True)
for obj in scene.objects:
    if obj.type=="MESH" and obj.name!="QA_ground":obj.select_set(True)
bpy.context.view_layer.objects.active=rig
glb=OUT/("human_"+STYLE+".glb")
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
    use_selection=True,export_animations=False,export_skins=True)
if not glb.exists() or glb.stat().st_size<1000000:raise RuntimeError("GLB export failed")

manifest={"schema_version":1,"asset_id":"human_"+STYLE,
 "style":STYLE,"model_file":glb.name,"source_file":outblend.name,
 "format":"glTF 2.0 GLB","unit":"meter",
 "requirements":{"skins":True,"animated":False,"visual_review":True},
 "clips":[],"min_animation_count":0,
 "source":"MPFB CC0 character base from verified GitHub Actions 2026-10-30, source run #15",
 "original_source":"https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html",
 "license_note":"Derived from MakeHuman CC0 system asset pack; procedurally edited material tint, hair and optional collar. Verify source copyright metadata before redistribution.",
 "quality_status":"PROCEDURAL_STYLE_PREVIEW_REQUIRES_FIT_AND_ANIMATION_QA"}
(OUT/"asset_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")

# Six viewpoints with material-aware Cycles CPU.
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=12
scene.render.resolution_x=520
scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.42,.48,.54,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.7
cam_data=bpy.data.cameras.new("QA_Ortho")
cam=bpy.data.objects.new("QA_Ortho",cam_data)
scene.collection.objects.link(cam)
scene.camera=cam
cam_data.type="ORTHO"
def lamp(name,pos,power,size):
    l=bpy.data.lights.new(name,"AREA")
    o=bpy.data.objects.new(name,l)
    scene.collection.objects.link(o)
    o.location=pos
    o.rotation_euler=(Vector((0,0,1.2))-o.location).to_track_quat("-Z","Y").to_euler()
    l.energy=power;l.size=size
lamp("Key",(3,-4,4),590,3.5)
lamp("Fill",(-3,-3,2.8),390,4)
lamp("Rim",(-2,3.5,3.5),510,3)
views={
 "front":((0,-5,1.15),(0,0,.90),2.3),
 "side":((5,0,1.15),(0,0,.90),2.3),
 "back":((0,5,1.15),(0,0,.90),2.3),
 "isometric":((4,-4,2.2),(0,0,.95),2.3),
 "face":((0,-4,1.57),(0,0,1.53),.7),
 "outfit":((2,-4.0,1.20),(0,0,1.04),1.25)}
for name,(pos,target,scale) in views.items():
    cam.location=pos
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam_data.ortho_scale=scale
    dest=OUT/("preview_"+name+".png")
    scene.render.filepath=str(dest)
    bpy.ops.render.render(write_still=True)
    if not dest.exists() or dest.stat().st_size<10000:raise RuntimeError("Missing render "+str(dest))

report={"style":STYLE,"source_mesh_count":len(original_names),
 "hair_source_vertices":old_verts,"hair_remaining_vertices":len(hair.data.vertices),
 "hair_new_strand_mesh_vertices":len(new_hair.data.vertices),
 "height_m":round(before,4),"bone_count":len(rig.data.bones),
 "source_texture_images":len(bpy.data.images),"glb_bytes":glb.stat().st_size,
 "render_views":list(views),"qa_status":"RENDERS_GENERATED_MANUAL_REVIEW_PENDING"}
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("CHARACTER_POSTPROCESS_OK",json.dumps(report))
