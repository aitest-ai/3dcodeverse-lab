"""Face v8 prototype: official MPFB head plus real fitted accessories, hair audition and materials.
Never transfer face vertices onto an unrelated pre-rigged neutral avatar.
"""
import os,sys,json,math,importlib
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree
ID=os.getenv("FACE_ID","you")
assert ID in ("you","boss")
OUT=Path(os.getenv("FACE_OUT","outputs/face_v8")).resolve()
HAIR_CHOICE=os.getenv("FACE_HAIR_CHOICE","short02")
TAG=ID+"_v8_"+(HAIR_CHOICE if ID=="boss" else "main")
OUT.mkdir(parents=True,exist_ok=True)
ASSETS=Path(os.environ["MAKEHUMAN_ASSET_ROOT"]).resolve()
assert ASSETS.is_dir()
PROFILES={
 "you":{"gender":.95,"age":.48,"weight":.39,"muscle":.56,"height":.53,"proportions":.52},
 "boss":{"gender":.0,"age":.87,"weight":.72,"muscle":.30,"height":.42,"proportions":.45}}
def need(filename):
    matches=list(ASSETS.rglob(filename))
    if not matches:raise RuntimeError("Missing original licensed MakeHuman asset: "+filename)
    return str(matches[0])
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.preferences.addon_enable(module="bl_ext.local_mpfb.mpfb")
import bl_ext.local_mpfb.mpfb
def service(suffix,name):
    names=[x for x in sys.modules if x.endswith(suffix)]
    assert len(names)==1,(suffix,names)
    return getattr(importlib.import_module(names[0]),name)
HumanService=service("mpfb.services.humanservice","HumanService")
TargetService=service("mpfb.services.targetservice","TargetService")
macro=TargetService.get_default_macro_info_dict()
macro.update(PROFILES[ID])
macro["race"]={"asian":.78,"caucasian":.17,"african":.05}
body=HumanService.create_human(mask_helpers=True,extra_vertex_groups=True,
                               feet_on_ground=True,scale=.1,macro_detail_dict=macro)
assert body.type=="MESH" and len(body.data.vertices)==19158
body.name="TrueMPFBBody_"+ID
# Face identity: applied before the skeleton and accessories are fitted.
FACE_PROFILES={
 "you":[("head-square",.55),("head-scale-horiz-decr",.25),("chin-width-incr",.52),("chin-prominent-incr",.40),("nose-scale-depth-incr",.35),("nose-width1-decr",.30),("mouth-scale-horiz-incr",.27),("l-eye-scale-decr",.18),("r-eye-scale-decr",.18)],
 "boss":[("head-round",.55),("head-scale-horiz-incr",.29),("chin-height-decr",.37),("nose-width1-incr",.48),("nose-point-width-incr",.36),("mouth-scale-horiz-decr",.29),("l-eye-scale-incr",.22),("r-eye-scale-incr",.22),("l-cheek-volume-incr",.62),("r-cheek-volume-incr",.62),
         ("head-age-incr",.52),("l-eye-bag-incr",.38),("r-eye-bag-incr",.38),
         ("mouth-laugh-lines-out",.46),("eyebrows-angle-down",.18)]}
face_stack=[{"target":name,"value":weight} for name,weight in FACE_PROFILES[ID]]
missing=[t["target"] for t in face_stack if TargetService.target_full_path(t["target"]) is None]
if missing:raise RuntimeError("Missing MPFB face targets: "+str(missing))
TargetService.bulk_load_targets(body,face_stack)
bpy.context.view_layer.update()
print("V8_FACE_IDENTITY",ID,json.dumps(face_stack))
# A unique rig fitted AFTER that particular body is created and morphed.
rig=HumanService.add_builtin_rig(body,"game_engine")
assert rig and rig.type=="ARMATURE"
rig.name="RootRig_"+ID
# Attach to the genuine morphed body while all MPFB target keys still exist.
# Asset positions, rigging, and skin must be fitted together as a unit.
# Prefer original age-related licensed skin maps if the asset pack contains them.
# Always keep original CC0 provenance; use procedural adjustment only as detail.
skin_files=sorted({p.name for p in ASSETS.rglob("*.mhmat")})
print("V8_SKIN_CATALOG",json.dumps([x for x in skin_files if "asian" in x]))
skin_name="old_asian_female.mhmat" if ID=="boss" else "young_asian_male.mhmat"
if skin_name not in skin_files:raise RuntimeError("Original MakeHuman age-appropriate Asian skin absent: "+skin_name)
skin=need(skin_name)
HumanService.set_character_skin(skin,body,skin_type="GAMEENGINE")
def warm_skin(obj,age):
    used=[]
    for mat in obj.data.materials:
        if mat is None or not mat.use_nodes:continue
        tree=mat.node_tree
        for bs in list(tree.nodes):
            if bs.type!="BSDF_PRINCIPLED":continue
            used.append(mat.name)
            col=bs.inputs.get("Base Color")
            tint=(.89,.80,.75,1) if age else (.92,.84,.80,1)
            if col and col.is_linked:
                old=col.links[0].from_socket
                tree.links.remove(col.links[0])
                mix=tree.nodes.new("ShaderNodeMixRGB")
                mix.name="NaturalSkinWarmth";mix.blend_type="MULTIPLY"
                mix.inputs[0].default_value=1
                mix.inputs[2].default_value=tint
                tree.links.new(old,mix.inputs[1])
                tree.links.new(mix.outputs[0],col)
            elif col:
                orig=col.default_value
                col.default_value=tuple(orig[i]*tint[i] for i in range(3))+(1,)
            rough=bs.inputs.get("Roughness")
            if rough and not rough.is_linked:rough.default_value=.67 if age else .57
            normal=bs.inputs.get("Normal")
            if normal and not normal.is_linked:
                micro=tree.nodes.new("ShaderNodeTexNoise")
                micro.name="SubtleSkinPores";micro.inputs["Scale"].default_value=240
                micro.inputs["Detail"].default_value=2
                bump=tree.nodes.new("ShaderNodeBump")
                bump.name="VerySubtleSkinBump"
                bump.inputs["Strength"].default_value=.08 if age else .04
                bump.inputs["Distance"].default_value=.0006
                tree.links.new(micro.outputs["Fac"],bump.inputs["Height"])
                tree.links.new(bump.outputs["Normal"],normal)
    return used
skin_materials=warm_skin(body,ID=="boss")
attached=[]
for filename,category in [
 ("high-poly.mhclo","Eyes"),
 ("eyebrow001.mhclo","Eyebrows"),
 ("eyelashes01.mhclo","Eyelashes"),
 ("teeth_base.mhclo","Teeth"),
 ("tongue01.mhclo","Tongue")]:
    asset=HumanService.add_mhclo_asset(need(filename),body,asset_type=category,
                      subdiv_levels=0,material_type="GAMEENGINE")
    if asset is None:raise RuntimeError("MPFB failed to fit "+filename)
    attached.append(asset)
# Add headwear on the SAME MPFB mesh so original MHCLO metadata does the
# vertex fitting, instead of creating artificial shell-shaped hairstyles.
haircatalog=sorted({p.name for p in ASSETS.rglob("*.mhclo") if any(
  w in p.name.lower() for w in ("short","bob","hair","crop","buzz","long"))})
print("FACE_V3_HAIR_CATALOG",json.dumps(haircatalog))
preferred=(("short01.mhclo","short02.mhclo") if ID=="you"
           else (HAIR_CHOICE+".mhclo",))
found=next((p for name in preferred for p in ASSETS.rglob(name)),None)
if found is None:
    raise RuntimeError("Official CC0 head hair assets unavailable: "+str(haircatalog))
hair=HumanService.add_mhclo_asset(str(found),body,asset_type="Hair",
                   subdiv_levels=0,material_type="GAMEENGINE")
if hair is None:raise RuntimeError("Could not apply scalp-fitted hair "+str(found))
hair.name="HairFitted_"+ID
# The source "system" hair material is platinum or over-bright. Tint boss
# into a dark brown with natural original texture variation, not flat paint.
if ID=="boss":
    for mat in hair.data.materials:
        if not mat or not mat.use_nodes:continue
        tree=mat.node_tree
        for node in list(tree.nodes):
            if node.type!="BSDF_PRINCIPLED":continue
            inp=node.inputs.get("Base Color")
            if not inp:continue
            if inp.is_linked:
                prev=inp.links[0].from_socket
                tree.links.remove(inp.links[0])
                mul=tree.nodes.new("ShaderNodeMixRGB")
                mul.name="TaiwanDarkHairTextureTint"
                mul.blend_type="MULTIPLY"
                mul.inputs[0].default_value=1.0
                mul.inputs[2].default_value=(.26,.22,.20,1)
                tree.links.new(prev,mul.inputs[1])
                tree.links.new(mul.outputs[0],inp)
            else:
                old=inp.default_value
                inp.default_value=(old[0]*.26,old[1]*.22,old[2]*.20,1)
attached.append(hair)
print("FACE_V3_HAIR_ATTACHED",ID,found.name)
# Real independent, auto-fitted official CC0 MakeHuman top and pants.
OUTFITS={
 "you":[("namuhekam_male_polo_shirt.mhclo","Shirts 01","namuhekam"),("cortu_cargo_pants.mhclo","Pants 01","Cortu")],
 "boss":[("toigo_fisherman_sweater.mhclo","Shirts 01","MargaretToigo"),("toigo_wool_pants.mhclo","Pants 01","MargaretToigo")]}
garment_items=[];garment_files=[]
for filename,pack,author in OUTFITS[ID]:
    source=need(filename)
    ob=HumanService.add_mhclo_asset(source,body,asset_type="Clothes",subdiv_levels=0,material_type="GAMEENGINE")
    if ob is None:raise RuntimeError("CC0 garment failed: "+filename)
    ob.name="OpenSourceCloth_"+ID+"_"+Path(filename).stem
    attached.append(ob);garment_items.append(ob)
    garment_files.append({"file":filename,"pack":pack,"author":author,"license":"CC0","mesh":ob.name,"vertices":len(ob.data.vertices)})
print("V8_REAL_OPEN_CLOTHING",ID,json.dumps(garment_files))
clothes=garment_items[0]
garmentpath=Path(need(OUTFITS[ID][0][0]))
shoes_path=next((p for name in ("shoes03.mhclo","shoes02.mhclo","shoes01.mhclo")
                 for p in ASSETS.rglob(name)),None)
if shoes_path is None:raise RuntimeError("CC0 footwear missing")
shoes=HumanService.add_mhclo_asset(str(shoes_path),body,asset_type="Clothes",
                      subdiv_levels=0,material_type="GAMEENGINE")
if shoes is None:raise RuntimeError("CC0 shoes could not be fitted")
attached.append(shoes)
print("FACE_V8_SHOES",ID,shoes_path.name)
# Morph geometry is visibly real, not merely shape key weights in Blender.
TargetService.bake_targets(body)
for mod in tuple(body.modifiers):
    if mod.type=="MASK":body.modifiers.remove(mod)
bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table();bm.verts.index_update()
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index>=13380],context="VERTS")
bm.to_mesh(body.data);bm.free();body.data.update()
assert len(body.data.vertices)==13380
assert all(m.type!="MASK" for m in body.modifiers)
# Reproject independently skinned tops/pants away from body skin.
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
body_bvh=BVHTree.FromObject(body,deps)
b2w=body.matrix_world.copy();w2b=b2w.inverted()
normal_transform=b2w.to_3x3().inverted().transposed()
clearance=.010
fit_count=0;initial_negative=0;greatest_offset=0.0;garment_fit=[]
for item in garment_items:
    w2c=item.matrix_world.inverted()
    corrected=0
    for vertex in item.data.vertices:
        world=item.matrix_world@vertex.co
        nearest,norm,index,d=body_bvh.find_nearest(w2b@world)
        if nearest is None:continue
        surface=b2w@nearest
        n=normal_transform@norm
        if n.length<1e-8:continue
        n.normalize()
        signed=(world-surface).dot(n);delta=(world-surface).length
        if delta>.055 or signed<-.05:continue
        if signed<0:initial_negative+=1
        if signed<clearance:
            dist=clearance-signed
            vertex.co=w2c@(world+n*dist)
            corrected+=1
            greatest_offset=max(greatest_offset,dist)
    item.data.update()
    garment_fit.append({"mesh":item.name,"corrected":corrected})
    fit_count+=corrected
print("V8_CLOTHING_FITTING",ID,json.dumps(garment_fit))
if fit_count<10:raise RuntimeError("CC0 garment fitting did not apply")

# All fitted eyes/teeth remain independent and are not altered by artificial
# per-object "face width" interpolation. Preserve their original materials.
bpy.context.view_layer.update()
Z=[(body.matrix_world@v.co).z for v in body.data.vertices]
top=max(Z);height=max(Z)-min(Z)
headcenter=top-.14
# Limit all source texture images to 512px and pack in the BLEND.
texture_dimensions=[]
for im in bpy.data.images:
    if not im.has_data or im.source!="FILE":continue
    if im.size[0]>512 or im.size[1]>512:
        im.scale(min(512,im.size[0]),min(512,im.size[1]))
    texture_dimensions.append([im.name,*list(im.size)])
scene=bpy.context.scene
scene.render.engine="CYCLES";scene.cycles.samples=28
scene.cycles.device="CPU"
scene.render.resolution_x=520;scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.15,.18,.21,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.56
camera_data=bpy.data.cameras.new("QA_FaceCamera")
camera=bpy.data.objects.new("QA_FaceCamera",camera_data)
scene.collection.objects.link(camera);scene.camera=camera
camera_data.type="ORTHO"
for name,xyz,power in (("Key",(3,-4,4),440),("Fill",(-3,-3,3),260),("Rim",(-2,3,4),260)):
    light=bpy.data.lights.new(name,"AREA");obj=bpy.data.objects.new(name,light)
    scene.collection.objects.link(obj);obj.location=xyz
    obj.rotation_euler=(Vector((0,0,1.15))-obj.location).to_track_quat("-Z","Y").to_euler()
    light.energy=power;light.size=3.3
views={
 "face":((0,-3,headcenter),(0,0,headcenter),.50),
 "side":((3,0,headcenter),(0,0,headcenter),.57),
 "threequarter":((2,-3,headcenter),(0,0,headcenter),.53),
 "front":((0,-4.5,height*.52),(0,0,height*.52),height*1.28)}
for view,(pos,target,scale) in views.items():
    camera.location=pos
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera_data.ortho_scale=scale
    scene.render.filepath=str(OUT/(TAG+"_"+view+".png"))
    bpy.ops.render.render(write_still=True)
# Export a real 3D test asset with original MPFB game-engine skeleton,
# ORIGINAL fitted eye/teeth/hair/clothes objects, and skinning.
# Only the manually selected hero/boss candidates are enabled by CI.
glb_path=None
if os.environ.get("FACE_EXPORT_GLB")=="1":
    import struct
    rig["character_id"]=ID
    rig["author"]="aitest-ai MPFB face QA pilot"
    rig["provenance"]="MPFB 2.0 + original MakeHuman CC0 system asset pack"
    rig["review"]="STRUCTURE_ONLY_ART_AND_EXPRESSIONS_PENDING"
    bpy.ops.object.select_all(action="DESELECT")
    for meshobj in [body,rig,*attached]:
        meshobj.select_set(True)
    bpy.context.view_layer.objects.active=rig
    glb_path=OUT/(TAG+".glb")
    bpy.ops.export_scene.gltf(filepath=str(glb_path),export_format="GLB",
                use_selection=True,export_skins=True,
                export_animations=False,export_morph=True,
                export_morph_normal=False,export_cameras=False,
                export_lights=False,export_extras=True)
    if glb_path.stat().st_size<200000:
        raise RuntimeError("3D pilot unexpectedly small")
    with glb_path.open("rb") as fh:
        magic,ver,size=struct.unpack("<4sII",fh.read(12))
        jsonlen,chunk=struct.unpack("<I4s",fh.read(8))
        assert magic==b"glTF" and ver==2 and size==glb_path.stat().st_size and chunk==b"JSON"
        gltf=json.loads(fh.read(jsonlen))
    assert len(gltf.get("skins",[]))>=1,"Missing animated skeleton"
    print("FACE_V8_GLB_PILOT",ID,glb_path.stat().st_size,
          "skins",len(gltf["skins"]),"meshes",len(gltf.get("meshes",[])))

# This pilot isn't claiming the export-ready expressions are complete;
# actual faces must pass visual review BEFORE the full GLB pipeline is enabled.
report={"character":ID,"status":"FACE_ONLY_PILOT_REQUIRES_VISUAL_APPROVAL",
        "source":"MPFB2 official phenotype and attached CC0 system face assets",
        "phenotype":macro,"body_vertices":len(body.data.vertices),
        "head_top_m":top,"height_m":height,"bones":len(rig.data.bones),
        "attached_original_face_assets":[x.name for x in attached],
        "hair_asset":found.name,
        "garment_asset":garmentpath.name if garmentpath else None,
        "textures":texture_dimensions,
        "views":[TAG+"_"+x+".png" for x in views],
        "skin_asset":skin_name,"skin_materials":skin_materials,
        "shoe_asset":shoes_path.name,"output_tag":TAG,
        "personal_face_targets":face_stack,
        "separate_open_source_garments":garment_files,
        "garment_fit":garment_fit,
        "pilot_glb":glb_path.name if glb_path else None,
        "pilot_glb_bytes":glb_path.stat().st_size if glb_path else None,
        "cloth_skin_fitting":{"reprojected":fit_count,"under_skin_before":initial_negative,
        "maximum_correction_m":greatest_offset,"clearance_m":clearance},
        "note":"Face-only QA; no proof yet of acceptable art, expressions, garments or final license metadata."}
(OUT/(TAG+"_report.json")).write_text(json.dumps(report,indent=2,ensure_ascii=False))
print("FACE_V8_PILOT",json.dumps(report))
