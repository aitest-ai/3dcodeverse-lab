"""Face v14 prototype: official MPFB head plus real fitted accessories, hair audition and materials.
Never transfer face vertices onto an unrelated pre-rigged neutral avatar.
"""
import os,sys,json,math,importlib
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree
ID=os.getenv("FACE_ID","you")
assert ID in ("you","boss","uncle","jie")
OUT=Path(os.getenv("FACE_OUT","outputs/face_v14")).resolve()
HAIR_CHOICE=os.getenv("FACE_HAIR_CHOICE","short02")
TAG=ID+"_v14_"+(HAIR_CHOICE if ID=="boss" else "main")
OUT.mkdir(parents=True,exist_ok=True)
ASSETS=Path(os.environ["MAKEHUMAN_ASSET_ROOT"]).resolve()
assert ASSETS.is_dir()
PROFILES={
 "you":{"gender":.95,"age":.48,"weight":.39,"muscle":.56,"height":.53,"proportions":.52},
 "boss":{"gender":.0,"age":.82,"weight":.69,"muscle":.33,"height":.44,"proportions":.45},
 "uncle":{"gender":.99,"age":.94,"weight":.77,"muscle":.32,"height":.47,"proportions":.51},
 "jie":{"gender":.99,"age":.46,"weight":.34,"muscle":.58,"height":.60,"proportions":.56}}
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
 "boss":[("head-round",.55),("head-scale-horiz-incr",.29),("chin-height-decr",.37),("nose-width1-incr",.48),("nose-point-width-incr",.36),("mouth-scale-horiz-decr",.29),("l-eye-scale-incr",.22),("r-eye-scale-incr",.22),("l-cheek-volume-incr",.53),("r-cheek-volume-incr",.53),
         ("head-age-incr",.37),("l-eye-bag-incr",.22),("r-eye-bag-incr",.19),
         ("mouth-laugh-lines-out",.26)],
 "uncle":[("head-square",.82),("head-scale-horiz-incr",.42),("chin-prominent-incr",.56),("chin-width-incr",.66),("nose-width1-incr",.69),("nose-scale-depth-incr",.58),("mouth-scale-horiz-incr",.35),("l-eye-scale-decr",.32),("r-eye-scale-decr",.32),("l-cheek-volume-incr",.47),("r-cheek-volume-incr",.43),
          ("head-age-incr",.40),("l-eye-bag-incr",.28),("r-eye-bag-incr",.22),
          ("mouth-laugh-lines-out",.24)],
 "jie":[("head-scale-horiz-decr",.40),("chin-height-incr",.16),("chin-width-decr",.35),
         ("nose-width1-decr",.36),("nose-scale-depth-decr",.10),
         ("mouth-scale-horiz-decr",.06),("l-eye-scale-incr",.13),
         ("r-eye-scale-incr",.11),("head-round",.18),
         ("l-cheek-volume-decr",.18),("r-cheek-volume-decr",.15)]}
face_stack=[{"target":name,"value":weight} for name,weight in FACE_PROFILES[ID]]
missing=[t["target"] for t in face_stack if TargetService.target_full_path(t["target"]) is None]
if missing:raise RuntimeError("Missing MPFB face targets: "+str(missing))
TargetService.bulk_load_targets(body,face_stack)
bpy.context.view_layer.update()
print("V14_FACE_IDENTITY",ID,json.dumps(face_stack))
# A unique rig fitted AFTER that particular body is created and morphed.
rig=HumanService.add_builtin_rig(body,"game_engine")
assert rig and rig.type=="ARMATURE"
rig.name="RootRig_"+ID
# Attach to the genuine morphed body while all MPFB target keys still exist.
# Asset positions, rigging, and skin must be fitted together as a unit.
# Prefer original age-related licensed skin maps if the asset pack contains them.
# Always keep original CC0 provenance; use procedural adjustment only as detail.
skin_files=sorted({p.name for p in ASSETS.rglob("*.mhmat")})
print("V14_SKIN_CATALOG",json.dumps([x for x in skin_files if "asian" in x]))
skin_name={"you":"young_asian_male.mhmat","boss":"middleage_asian_female.mhmat","uncle":"old_asian_male.mhmat","jie":"young_asian_male.mhmat"}[ID]
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
            if rough and not rough.is_linked:rough.default_value=.75 if age else .70
            spec=bs.inputs.get("Specular IOR Level")
            if spec and not spec.is_linked:spec.default_value=.32
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
skin_materials=warm_skin(body,ID in ("boss","uncle"))
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
preferred={
 "you":("short01.mhclo","short02.mhclo"),
 "boss":(HAIR_CHOICE+".mhclo",),
 "uncle":("short04.mhclo","short03.mhclo"),
 "jie":("short02.mhclo","short01.mhclo")}[ID]
found=next((p for name in preferred for p in ASSETS.rglob(name)),None)
if found is None:
    raise RuntimeError("Official CC0 head hair assets unavailable: "+str(haircatalog))
hair=HumanService.add_mhclo_asset(str(found),body,asset_type="Hair",
                   subdiv_levels=0,material_type="GAMEENGINE")
if hair is None:raise RuntimeError("Could not apply scalp-fitted hair "+str(found))
hair.name="HairFitted_"+ID
# The source "system" hair material is platinum or over-bright. Tint boss
# into a dark brown with natural original texture variation, not flat paint.
if ID in ("boss","uncle","jie"):
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
                mul.inputs[2].default_value=({"boss":(.28,.25,.24,1), "uncle":(.40,.39,.37,1), "jie":(.11,.12,.13,1)}[ID])
                tree.links.new(prev,mul.inputs[1])
                tree.links.new(mul.outputs[0],inp)
            else:
                old=inp.default_value
                factor={"boss":(.28,.25,.24), "uncle":(.40,.39,.37), "jie":(.11,.12,.13)}[ID]
                inp.default_value=tuple(old[k]*factor[k] for k in range(3))+(1,)
attached.append(hair)
print("FACE_V3_HAIR_ATTACHED",ID,found.name)
# Real independent, auto-fitted official CC0 MakeHuman top and pants.
OUTFITS={
 "you":[("namuhekam_male_polo_shirt.mhclo","Shirts 01","namuhekam"),("cortu_cargo_pants.mhclo","Pants 01","Cortu")],
 "boss":[("toigo_fisherman_sweater.mhclo","Shirts 01","MargaretToigo"),("toigo_wool_pants.mhclo","Pants 01","MargaretToigo")],
 "uncle":[("toigo_basic_tucked_t-shirt.mhclo","Shirts 01","MargaretToigo"),("toigo_wool_pants.mhclo","Pants 01","MargaretToigo")],
 "jie":[("toigo_basic_tucked_t-shirt.mhclo","Shirts 01","MargaretToigo"),("cortu_cargo_pants.mhclo","Pants 01","Cortu")]}
garment_items=[];garment_files=[]
for filename,pack,author in OUTFITS[ID]:
    source=need(filename)
    ob=HumanService.add_mhclo_asset(source,body,asset_type="Clothes",subdiv_levels=0,material_type="GAMEENGINE")
    if ob is None:raise RuntimeError("CC0 garment failed: "+filename)
    ob.name="OpenSourceCloth_"+ID+"_"+Path(filename).stem

    # Preserve the genuine MHCLO materials, changing only tint/roughness.
    # A real different knit/jersey silhouette remains visible, not a fake cube.
    top_colour={"you":(.52,.55,.55), "boss":(.88,.83,.76),
                "uncle":(.25,.33,.37), "jie":(.16,.48,.34)}[ID]
    pant_colour={"you":(.43,.43,.43),"boss":(.51,.49,.46),
                 "uncle":(.41,.39,.37),"jie":(.31,.33,.33)}[ID]
    tint=top_colour if len(garment_items)==0 else pant_colour
    for midx,original_mat in enumerate(tuple(ob.data.materials)):
        if original_mat is None:continue
        mat=original_mat.copy()
        ob.data.materials[midx]=mat
        if not mat.use_nodes:continue
        for bs in mat.node_tree.nodes:
            if bs.type!="BSDF_PRINCIPLED":continue
            input_colour=bs.inputs.get("Base Color")
            if not input_colour:continue
            if input_colour.is_linked:
                from_socket=input_colour.links[0].from_socket
                mat.node_tree.links.remove(input_colour.links[0])
                mx=mat.node_tree.nodes.new("ShaderNodeMixRGB")
                mx.blend_type="MULTIPLY";mx.inputs[0].default_value=.80
                mx.inputs[2].default_value=(*tint,1)
                mat.node_tree.links.new(from_socket,mx.inputs[1])
                mat.node_tree.links.new(mx.outputs[0],input_colour)
            else:
                old=input_colour.default_value
                input_colour.default_value=tuple(old[k]*tint[k] for k in range(3))+(1,)
            rough=bs.inputs.get("Roughness")
            if rough and not rough.is_linked:rough.default_value=.86
    print("V14_CC0_GARMENT_TINT",ID,filename,tint)
    attached.append(ob);garment_items.append(ob)
    garment_files.append({"file":filename,"pack":pack,"author":author,"license":"CC0","mesh":ob.name,"vertices":len(ob.data.vertices)})
print("V14_REAL_OPEN_CLOTHING",ID,json.dumps(garment_files))
clothes=garment_items[0]
garmentpath=Path(need(OUTFITS[ID][0][0]))
shoes_path=next((p for name in ("shoes03.mhclo","shoes02.mhclo","shoes01.mhclo")
                 for p in ASSETS.rglob(name)),None)
if shoes_path is None:raise RuntimeError("CC0 footwear missing")
shoes=HumanService.add_mhclo_asset(str(shoes_path),body,asset_type="Clothes",
                      subdiv_levels=0,material_type="GAMEENGINE")
if shoes is None:raise RuntimeError("CC0 shoes could not be fitted")
attached.append(shoes)
print("FACE_V14_SHOES",ID,shoes_path.name)
# Morph geometry is visibly real, not merely shape key weights in Blender.
TargetService.bake_targets(body)
# Official MPFB method interpolates 3D target deltas to ORIGINAL fitted MHCLO
# teeth, tongue, eyes, eyelashes, eyebrows, clothing, and hair. Unlike V13,
# preserve helpers until this propagation has finished.
sys.path.insert(0,str(Path(__file__).resolve().parent))
from add_arkit_faceunits_full import attach_faceunits,FACE_MORPHS
FaceService=service("mpfb.services.faceservice","FaceService")
ExportService=service("mpfb.services.exportservice","ExportService")
assert len(body.data.vertices)==19158
faceunit_metrics=attach_faceunits(body,os.environ["FACEUNITS_ROOT"],TargetService)
assert set(body.data.shape_keys.key_blocks.keys())==set(["Basis",*FACE_MORPHS.values()])
# FaceService correctly interpolates original MHCLO geometry, but its built-in
# resolver searches only MPFB registered asset roots. These CC0 files have been
# unpacked to MAKEHUMAN_ASSET_ROOT without registering them as an MPFB library.
# Adapt *only file lookup*, never the official shape interpolation algorithm.
ClothesService=service("mpfb.services.clothesservice","ClothesService")
GeneralObjectProperties=service("mpfb.entities.objectproperties","GeneralObjectProperties")
_original_mhclo_resolver=ClothesService.find_clothes_absolute_path
externally_resolved={}
def _qa_mhclo_resolver(clothes_obj):
    original=_original_mhclo_resolver(clothes_obj)
    if original is not None:
        externally_resolved[clothes_obj.name]=original
        return original
    source=GeneralObjectProperties.get_value("asset_source", entity_reference=clothes_obj)
    if not source:
        raise RuntimeError("Cannot prove source MHCLO for "+clothes_obj.name)
    filename=Path(str(source)).name
    if not filename.lower().endswith(".mhclo"):
        raise RuntimeError("Unrecognized MHCLO source "+str(source))
    matches=sorted({str(p.resolve()) for p in ASSETS.rglob(filename) if p.is_file()})
    if len(matches)!=1:
        raise RuntimeError("Ambiguous or absent original MHCLO "+filename+" "+repr(matches))
    externally_resolved[clothes_obj.name]=matches[0]
    return matches[0]
ClothesService.find_clothes_absolute_path=staticmethod(_qa_mhclo_resolver)
try:
    FaceService.interpolate_targets(body)
finally:
    ClothesService.find_clothes_absolute_path=staticmethod(_original_mhclo_resolver)
print("V14_ORIGINAL_CC0_ASSET_RESOLVER_AUDIT",json.dumps(externally_resolved))
asset_expression_keys_before={}
for ob in attached:
    names=[] if ob.data.shape_keys is None else list(ob.data.shape_keys.key_blocks.keys())[1:]
    asset_expression_keys_before[ob.name]=names
print("V14_CHILD_TARGETS_AFTER_OFFICIAL_INTERPOLATION",json.dumps(asset_expression_keys_before))
if not any("jawOpen" in keys for name,keys in asset_expression_keys_before.items()
           if "teeth" in name.lower() or "tongue" in name.lower()):
    raise RuntimeError("MPFB official interpolation did not move original teeth or tongue MHCLO: "+
                       json.dumps(asset_expression_keys_before))
# ExportService preserves shape keys when it physically deletes 5,778 helpers.
ExportService.bake_modifiers_remove_helpers(
    body,bake_masks=False,bake_subdiv=False,remove_helpers=True,also_proxy=False)
for mod in tuple(body.modifiers):
    if mod.type=="MASK":body.modifiers.remove(mod)
assert len(body.data.vertices)==13380,"Official deletion did not leave correct true human body"
assert set(body.data.shape_keys.key_blocks.keys())==set(["Basis",*FACE_MORPHS.values()])
# Rename game-friendly mouthOpen alias on BODY and EVERY child fitted mesh.
# All other 9 names exactly match original ARKit source data.
for ob in [body,*attached]:
    if ob.type=="MESH" and ob.data.shape_keys:
        if "jawOpen" in ob.data.shape_keys.key_blocks:
            ob.data.shape_keys.key_blocks["jawOpen"].name="mouthOpen"
asset_expression_keys_after={}
for ob in attached:
    names=[] if ob.data.shape_keys is None else list(ob.data.shape_keys.key_blocks.keys())[1:]
    asset_expression_keys_after[ob.name]=names
assert set(body.data.shape_keys.key_blocks.keys())==set(["Basis",*FACE_MORPHS.keys()])
assert all(m.type!="MASK" for m in body.modifiers)
print("V14_TRUE_HELPERS_REMOVED_CHILD_MORPHS_PRESERVED",ID,json.dumps(asset_expression_keys_after))

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
    # Smooth shading uses existing geometry and does not invent a new outline.
    for polygon in item.data.polygons: polygon.use_smooth=True
    garment_fit.append({"mesh":item.name,"corrected":corrected})
    fit_count+=corrected
print("V14_CLOTHING_FITTING",ID,json.dumps(garment_fit))
# Detect any structural weakness in the clothing topology before exporting.
hem_diagnostic={}
for gm in garment_items:
    from collections import Counter
    edges=Counter()
    for poly in gm.data.polygons:
        vs=list(poly.vertices)
        for i,v in enumerate(vs):
            key=tuple(sorted((v,vs[(i+1)%len(vs)])))
            edges[key]+=1
    boundary=sum(count==1 for count in edges.values())
    hem_diagnostic[gm.name]={"vertices":len(gm.data.vertices),
                              "faces":len(gm.data.polygons),
                              "boundary_edges":boundary}
print("V14_WARDROBE_TOPOLOGY_QA",ID,json.dumps(hem_diagnostic))

if fit_count<10:raise RuntimeError("CC0 garment fitting did not apply")

# Waistband fitting: in earlier tests the original T-shirt hem and cargo
# waistband exposed a horizontal stripe of bare skin. Stretching the T-shirt
# *destroyed* its lower polygon boundary. Instead keep the original fitted
# original shirt and extend the waistband a little upward, smoothly across
# the existing original trousers geometry while keeping UVs and skin weights.
waistband_repair={"character":ID,"moved_vertices":0,"height_m":0.0}
if ID=="jie":
    jersey,trousers=garment_items
    sh=jersey.matrix_world
    hem=min((sh@v.co).z for v in jersey.data.vertices)
    pw=trousers.matrix_world.copy()
    wp=pw.inverted()
    pants_top=max((pw@v.co).z for v in trousers.data.vertices)
    rise=min(.075,max(0.0,hem+.060-pants_top))
    moved=0
    for vertex in trousers.data.vertices:
        world=pw@vertex.co
        t=(pants_top-world.z)/.18
        if t>=1:continue
        candidate=world.copy()
        candidate.z+=rise*(1-t)**2
        nearest,normal,index,distance=body_bvh.find_nearest(w2b@candidate)
        if nearest is not None and distance<.065:
            outside=normal_transform@normal
            if outside.length>1e-9:
                outside.normalize()
                off=(candidate-(b2w@nearest)).dot(outside)
                if off<.010:candidate+=outside*(.010-off)
        vertex.co=wp@candidate
        moved+=1
    trousers.data.update()
    waistband_repair={"character":ID,"moved_vertices":moved,"height_m":rise,
                        "shirt_hem_z_m":hem,"old_trouser_top_z_m":pants_top,
                        "new_trouser_top_z_m":max((pw@v.co).z for v in trousers.data.vertices)}
    if moved<10 or rise<.02:
        raise RuntimeError("No real cargo waistband correction was made: "+str(waistband_repair))
    print("V14_NATIVE_CARGO_WAISTBAND_REPAIR",json.dumps(waistband_repair))

# Clothing hem overlaps: remove only the topmost wool-trouser polygons
# fully hidden by the knitted sweater. This prevents jagged black belt islands
# while preserving the lower trouser surface and its skinned weights.
waist_cleaned=0
if ID=="boss":
    top_garment,pant_garment=garment_items
    hem=min((top_garment.matrix_world@v.co).z for v in top_garment.data.vertices)
    limit=hem+.006
    mesh=bmesh.new();mesh.from_mesh(pant_garment.data)
    bad=[]
    for face in mesh.faces:
        zvals=[(pant_garment.matrix_world@v.co).z for v in face.verts]
        if min(zvals)>limit:
            bad.append(face)
    waist_cleaned=len(bad)
    if bad:
        bmesh.ops.delete(mesh,geom=bad,context="FACES")
        mesh.to_mesh(pant_garment.data)
    mesh.free()
    pant_garment.data.update()
    print("V14_WAIST_CLEANUP",ID,hem,waist_cleaned)

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
# Show actual facial movements using the final Blender mesh, not AI images.
# These are evidence only; manual QA must still reject broken teeth/eyelids.
expression_previews=[]
if ID in ("you","boss"):
    presets={
      "expression_smile":{"mouthSmileLeft":.80,"mouthSmileRight":.80},
      "expression_mouthOpen":{"mouthOpen":.82},
      "expression_blink":{"eyeBlinkLeft":.95,"eyeBlinkRight":.95},
    }
    # Drive the exact same faceunit on fitted teeth/tongue/eyelashes, not just
    # body skin, so mouth and blink preview shows real accessory tracking.
    keyobjects=[ob for ob in [body,*attached]
                if ob.type=="MESH" and ob.data.shape_keys]
    for pose,weights in presets.items():
        for ob in keyobjects:
            for key in FACE_MORPHS:
                if key in ob.data.shape_keys.key_blocks:ob.data.shape_keys.key_blocks[key].value=0.0
            for key,val in weights.items():
                if key in ob.data.shape_keys.key_blocks:ob.data.shape_keys.key_blocks[key].value=val
        bpy.context.view_layer.update()
        camera.location=(0,-3,headcenter)
        camera.rotation_euler=(Vector((0,0,headcenter))-camera.location).to_track_quat("-Z","Y").to_euler()
        camera_data.ortho_scale=.50
        name=TAG+"_"+pose+".png"
        scene.render.filepath=str(OUT/name)
        bpy.ops.render.render(write_still=True)
        expression_previews.append(name)
        print("REAL_FACE_EXPR_RENDERED",ID,pose,weights)
for ob in [body,*attached]:
    if ob.type=="MESH" and ob.data.shape_keys:
        for key in FACE_MORPHS:
            if key in ob.data.shape_keys.key_blocks:
                ob.data.shape_keys.key_blocks[key].value=0.0
bpy.context.view_layer.update()

# Export a real 3D test asset with original MPFB game-engine skeleton,
# ORIGINAL fitted eye/teeth/hair/clothes objects, and skinning.
# Only the manually selected hero/boss candidates are enabled by CI.
glb_path=None
if os.environ.get("FACE_EXPORT_GLB")=="1":
    import struct
    rig["character_id"]=ID
    rig["author"]="aitest-ai MPFB face QA pilot"
    rig["provenance"]="MPFB 2.0 + original MakeHuman CC0 system asset pack"
    rig["review"]="REAL_10_ARKIT_STYLE_KEYS_ART_ANIMATION_PENDING"
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
    print("FACE_V14_GLB_PILOT",ID,glb_path.stat().st_size,
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
        "face_identity_slider_count":len(face_stack),
        "face_profile_gender_age":[macro["gender"],macro["age"]],
        "separate_open_source_garments":garment_files,
        "garment_fit":garment_fit,
        "wardrobe_topology_qa":hem_diagnostic,
        "waistband_repair":waistband_repair,
        "faceunit_assets":"Official Faceunits 01 Mika Suominen CC0",
        "arkit_style_shape_keys":faceunit_metrics,
        "fitted_face_accessory_keys_before_renaming":asset_expression_keys_before,
        "original_mhclo_resolved_paths":externally_resolved,
        "fitted_face_accessory_keys_after_renaming":asset_expression_keys_after,
        "expression_previews":expression_previews,
        "overlap_hidden_trouser_faces_removed":waist_cleaned,
        "pilot_glb":glb_path.name if glb_path else None,
        "pilot_glb_bytes":glb_path.stat().st_size if glb_path else None,
        "cloth_skin_fitting":{"reprojected":fit_count,"under_skin_before":initial_negative,
        "maximum_correction_m":greatest_offset,"clearance_m":clearance},
        "note":"V14 uses official MPFB FaceService.interpolate_targets to propagate real CC0 expression targets onto original fitted MHCLO teeth/tongue/eyelash meshes before helper deletion. Manual mouth interior and blink art QA still mandatory."}
(OUT/(TAG+"_report.json")).write_text(json.dumps(report,indent=2,ensure_ascii=False))
print("FACE_V14_PILOT",json.dumps(report))
