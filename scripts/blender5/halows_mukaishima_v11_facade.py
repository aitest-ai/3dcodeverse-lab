"""Halows V11: source-locked V10 site plus photo-guided facade and baked PBR-albedo work.

This file deliberately executes only the geometry portion of the exact V10 parent.
The V10 output/render section is NOT run. V10 and all previous assets stay immutable.
"""
import bpy, math, hashlib, json, random, glob
from pathlib import Path

PARENT=Path(__file__).parent/"halows_mukaishima_v10_entryground.py"
raw=PARENT.read_bytes()
actual_git_blob=hashlib.sha1(("blob %d\0"%len(raw)).encode()+raw).hexdigest()
expected_git_blob="1d88a09b92024aacbe2e3b7c11b40bb2d659153b"
if actual_git_blob!=expected_git_blob:
    raise RuntimeError("V10 source changed; refusing unreviewed V11 rebuild: "+actual_git_blob)
source=raw.decode("utf-8")
marker="\nblend=OUT/f\"{ID}.blend\""
if source.count(marker)!=1: raise RuntimeError("Unexpected V10 build/export boundary")
prefix=source.split(marker)[0].replace(
    'ID="halows-mukaishima-v10-entryground"',
    'ID="halows-mukaishima-v11-facade"')
exec(compile(prefix,str(PARENT),"exec"),globals())
if ID!="halows-mukaishima-v11-facade": raise RuntimeError("V11 ID substitution failed")

# Everything produced above is the georeferenced V10 baseline with unchanged
# OSM/GSI site lock. V11 only adjusts proposed facade details and materials.
already={o.as_pointer() for o in bpy.context.scene.objects}
def remove_named(name):
    ob=bpy.data.objects.get(name)
    if ob: bpy.data.objects.remove(ob,do_unlink=True)

for prefix_name in ("red","disc","joint","front_joint_","tower_rib_v08_","rib"):
    for obj in list(bpy.context.scene.objects):
        nm=obj.name
        if prefix_name=="red" and not nm.startswith("red"): continue
        if prefix_name=="disc" and not nm.startswith("disc"): continue
        if prefix_name=="joint" and not nm.startswith("joint"): continue
        if prefix_name=="front_joint_" and not nm.startswith("front_joint_"): continue
        if prefix_name=="tower_rib_v08_" and not nm.startswith("tower_rib_v08_"): continue
        if prefix_name=="rib" and not nm.startswith("rib"): continue
        remove_named(nm)
remove_named("HALOWS_word"); remove_named("HALOWS_24H")

# The V10 dark seams were too regular and read like severe cracks in close-ups.
SH.diffuse_color=(.57,.44,.41,1)
SH.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.57,.44,.41,1)
arch=bpy.data.objects.get("arch")
if arch and arch.type=="CURVE": arch.data.bevel_depth=.105

# Distinctive front red panels + green roundels, then Japanese name; the west
# facing sign uses the English name. Scales/letter shapes are photo-informed
# proposals, NOT a licensed corporate logo mesh or measured as-built survey.
WARM_TILE=mat("V11_mortar_low_contrast",(.62,.47,.43,1),.97)
SIGN_JOINT=mat("V11_sign_panel_seams",(.80,.77,.70,1),.95)
SIGN_MOLD=mat("V11_arched_infill_cream",(.79,.755,.68,1),.88)
ALUMINUM=mat("V11_satin_aluminium",(.49,.51,.50,1),.28,.40)

for sign_index,dx in enumerate((-2.14,2.14)):
    cube("V11_front_redpanel_%d"%sign_index,(TX+dx,EF-.33,10.85),
         (1.20,.13,1.71),R,.032)
    cyl("V11_front_green_dot_%d"%sign_index,
        (TX+dx+.46,EF-.47,10.82),.31,.13,SG,rot=(math.pi/2,0,0))

# Lower tower masonry: approximate modest grout, only on solid visible piers.
pier_w=(TW-OPEN_W)/2
for side in (-1,1):
    px=TX+side*(OPEN_W/2+pier_w/2)
    for j in range(15):
        cube("V11_pier_grout_%s_%02d"%(side,j),
             (px,EF-.049,.46+j*.45),(pier_w-.10,.016,.013),WARM_TILE)
for i in range(11):
    x=TX-TW/2+.62+i*.87
    cube("V11_sign_seam_%02d"%i,
         (x,EF-.053,(TT+TB)/2),(.013,.015,TT-TB-.34),SIGN_JOINT)

# Light warm arch infill makes the feature in the historic exterior photo read
# as built architecture rather than a bright floating white tube. This is NOT
# an interior panorama; the material only expresses a facade inset.
a0=[]
for i in range(49):
    theta=math.pi-i*math.pi/48
    a0.append((TX+3.17*math.cos(theta),EF-.23,4.83+1.49*math.sin(theta)))
a0.append((TX-3.17,EF-.23,4.83))
me=bpy.data.meshes.new("V11_arch_infill_mesh")
me.from_pydata(a0,[],[tuple(range(len(a0)))])
me.update()
obj=bpy.data.objects.new("V11_arch_recess_noninterior",me)
bpy.context.collection.objects.link(obj); me.materials.append(SIGN_MOLD)

# Front sliding-door hardware. Exact mechanics and entry dimensions are unknown.
cube("V11_sliding_track_upper",(TX,EF-.31,2.83),(4.74,.08,.065),ALUMINUM,.007)
cube("V11_sliding_track_lower",(TX,EF-.31,.19),(4.74,.08,.055),ALUMINUM,.007)
cube("V11_sliding_sash_center",(TX,EF-.34,1.47),(.06,.09,2.49),ALUMINUM)
for sd in (-1,1):
    cube("V11_door_handle_%s"%sd,
         (TX+sd*.44,EF-.38,1.26),(.045,.065,.36),ALUMINUM,.008)
    cube("V11_entry_bumper_%s"%sd,
         (TX+sd*2.23,EF-.34,.55),(.07,.065,.89),ALUMINUM,.006)

UNDER=mat("V11_canopy_soffit",(.68,.68,.62,1),.88)
cube("V11_canopy_underside",(0,F-2.25,2.905),(L-1.66,3.98,.06),UNDER,.02)

# Historic 2017 official photo supports signage on two planes, but not exact
# glyph geometry. We bake original lettering to meshes from the open Noto CJK
# typeface at build time; no font files are bundled in the deliverable.
fonts=glob.glob("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
fonts+=glob.glob("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc")
if not fonts: raise RuntimeError("Noto CJK font unavailable; do not ship tofu signage")
font=bpy.data.fonts.load(fonts[0])
def signed_text(n,text,location,size,face="front",horizontal_scale=1.0):
    rot=(math.pi/2,0,0) if face=="front" else (math.pi/2,0,-math.pi/2)
    bpy.ops.object.text_add(location=location,rotation=rot)
    ob=bpy.context.object; ob.name=n; ob.data.font=font; ob.data.body=text
    ob.data.size=size; ob.data.align_x="CENTER"; ob.data.align_y="CENTER"
    ob.data.extrude=.023; ob.data.bevel_depth=.006
    ob.data.materials.append(SG)
    bpy.ops.object.convert(target="MESH")
    ob.scale.x=horizontal_scale
    return ob
signed_text("V11_kanji_sign","ハローズ",
            (TX,EF-.52,8.57),1.12,"front",1.02)
SIDE_X=TX-TW/2-.16
for i,dy in enumerate((-.98,.98)):
    cube("V11_west_redpanel_%d"%i,
         (SIDE_X,BZ+dy,10.84),(.13,.75,1.52),R,.03)
    cyl("V11_west_green_dot_%d"%i,
        (SIDE_X-.15,BZ+dy-.23,10.8),.27,.12,SG,rot=(0,math.pi/2,0))
signed_text("V11_english_sign","HALOWS",
            (SIDE_X-.21,BZ,8.52),.70,"west",.73)

# Rotate only newly modeled local-building objects into the same ENU frame as
# all V10 objects. No updates to OSM positions or geodetic data.
new_objs=[o for o in bpy.context.scene.objects if o.as_pointer() not in already]
for ob in new_objs:
    x,y,z=ob.location
    ob.location=(ca*x-sa*y,sa*x+ca*y,z)
    ob.rotation_euler.z+=HEAD

# Artist-authored reproducible, copyright-clean color textures. Packed into
# Blender and embedded in GLB; no Halows photograph is copied into any texture.
TEXTURES=[]
def generate_albedo(name,base,seed,is_paver=False):
    rng=random.Random(seed)
    dim=256
    image=bpy.data.images.new(name,width=dim,height=dim,alpha=True)
    px=[]
    for y in range(dim):
        for x in range(dim):
            u=x/dim; v=y/dim
            grain=(rng.random()-.5)*.043
            low=(math.sin(19.5*u+9.4*v)+math.sin(8.7*u-16.8*v))*.006
            grout=0.0
            if is_paver:
                row=int(v*5)
                bx=(12*u+(.5 if row%2 else 0.))%1.
                by=(v*5)%1.
                if bx<.020 or by<.020: grout=-.031
            px.extend((max(.025,min(.95,base[0]+grain+low+grout)),
                       max(.025,min(.95,base[1]+grain+low+grout)),
                       max(.025,min(.95,base[2]+grain+low+grout)),1.0))
    image.pixels.foreach_set(px)
    path=OUT/(name+".png")
    image.filepath_raw=str(path.resolve()); image.file_format="PNG"
    image.save(); image.pack()
    TEXTURES.append(path)
    return image

asphalt=generate_albedo("V11_procedural_asphalt",(.157,.163,.169),433)
pavers=generate_albedo("V11_procedural_apron_pavers",(.495,.354,.292),919,True)
def apply_image(material,image):
    nodes=material.node_tree.nodes
    tex=nodes.new("ShaderNodeTexImage"); tex.image=image; tex.extension="REPEAT"
    material.node_tree.links.new(tex.outputs["Color"],
       nodes["Principled BSDF"].inputs["Base Color"])
for material in (A,ROAD,SERVICE): apply_image(material,asphalt)
apply_image(P,pavers)

def planar_uv(mesh_obj,unit=3.0):
    mesh=mesh_obj.data
    uv=mesh.uv_layers.active or mesh.uv_layers.new(name="V11_tile_meters")
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            point=mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv=(point.x/unit,point.y/unit)
for name,tile in (("parking",3.4),("customer_apron",2.2),
                  ("rear_loading_pad",2.8)):
    ob=bpy.data.objects.get(name)
    if ob: planar_uv(ob,tile)
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name.startswith("OSM_road_"):
        planar_uv(ob,3.4)

# Render the actual model: five V10 views stay geometrically identical; add two
# V11 close-ups for honest real-image comparison of sign and ground.
bpy.context.scene["asset_id"]=ID
bpy.context.scene["v11_source_sha1"]=expected_git_blob
bpy.context.scene["photo_basis"]="https://www.halows.com/stores/detail/77"
bpy.context.scene["font_license"]="Noto CJK SIL OFL, converted to mesh, font not redistributed"
bpy.context.scene["route_accepted"]=False
blend=OUT/(ID+".blend"); glb=OUT/(ID+".glb")
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
bpy.ops.export_scene.gltf(filepath=str(glb.resolve()),export_format="GLB",
                           export_apply=True,export_animations=False)

sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=1400; sc.render.resolution_y=900
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.42,.55,.69,1)
bg.inputs["Strength"].default_value=.55
sc.view_settings.view_transform="AgX"; sc.view_settings.exposure=0.0
bpy.ops.object.light_add(type="SUN",location=(-80,-100,120)); bpy.context.object.data.energy=2.0
bpy.ops.object.light_add(type="AREA",location=(12,-40,50))
bpy.context.object.data.energy=4800
bpy.context.object.data.shape="DISK"; bpy.context.object.data.size=44
bpy.ops.object.light_add(type="AREA",location=(-30,20,44))
bpy.context.object.data.energy=2100
bpy.context.object.data.shape="DISK"; bpy.context.object.data.size=35
bpy.ops.object.camera_add(); cam=bpy.context.object; sc.camera=cam
def look(target):
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
shots=[
 ("site_aerial",(-115,-125,92),(0,-10,1.5),45),
 ("route317_arrival",(92,-92,8),(5,-18,3.0),42),
 ("forecourt",(-45,-82,7),(4,-16,3.2),40),
 ("north_overview",(-90,105,62),(0,-5,2.0),48),
 ("entry_eye",(ca*(TX+3)-sa*(F-17),sa*(TX+3)+ca*(F-17),1.68),
             (ca*TX-sa*(F-.2),sa*TX+ca*(F-.2),2.15),38),
 ("tower_identity",(ca*(TX-7)-sa*(EF-25),sa*(TX-7)+ca*(EF-25),10),
             (ca*TX-sa*EF,sa*TX+ca*EF,9.25),48),
 ("apron_detail",(ca*(TX-12)-sa*(F-18),sa*(TX-12)+ca*(F-18),3.7),
             (ca*(TX-11)-sa*(F-4),sa*(TX-11)+ca*(F-4),.10),43)
]
imgs=[]
for name,pos,target,lens in shots:
    cam.location=pos; look(target); cam.data.lens=lens
    p=OUT/(ID+"_"+name+".png")
    sc.render.filepath=str(p.resolve())
    bpy.ops.render.render(write_still=True)
    imgs.append(p)
bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))

def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for piece in iter(lambda:f.read(1<<20),b""): h.update(piece)
    return h.hexdigest()
(OUT/"site_lock.json").write_text(json.dumps(SITE,ensure_ascii=False,indent=2))
manifest={
 "schema_version":1,"asset_id":ID,
 "source_file":blend.name,"model_file":glb.name,
 "status":"V11_PHOTO_GUIDED_FACADE_CANDIDATE_NOT_RUNTIME_INTEGRATED",
 "source_parent_git_blob":actual_git_blob,
 "origin_wgs84":SITE["origin_wgs84"],
 "blender_version":bpy.app.version_string,"textures_origin":"authored_procedural",
 "font_asset_shipped":False,"browser_tested":False,"android_tested":False,
 "georeferenced":True,"clips":[],"requirements":{"skins":False},
 "min_animation_count":0,"files":{},
 "estimated":["front/side sign relief and glyph proportions",
              "glass door tracks and entry hardware","arch inset facade",
              "paved apron joint rhythm and asphalt surface microstructure",
              "existing V09 store pad height and 18m grading"],
 "not_approved":["current door coordinates","parking manoeuvre route",
                 "pedestrian/cycle legal access","browser and Android"]
}
for p in [blend,glb,*imgs,*TEXTURES,OUT/"site_lock.json"]:
    manifest["files"][p.name]={"bytes":p.stat().st_size,"sha256":digest(p)}
(OUT/"asset_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
report={
 "status":"PASS_BUILD_EXPORT_RENDER_FACADE_ONLY",
 "source_site_asset_id":SITE["asset_id"],
 "parent_git_blob":actual_git_blob,
 "osm_building_way":"661155704",
 "store_pad_elevation_m":PAD,"grading_feather_m":18.0,
 "views":[name for name,_,_,_ in shots],
 "new_geometry_object_count":len(new_objs),
 "baked_texture_images":[p.name for p in TEXTURES],
 "no_copyrighted_photographs_bundled":True,
 "font_is_only_authoring_input":True,
 "route_accepted":False,"runtime_integrated":False,
 "browser_tested":False,"android_tested":False,
 "limitations":SITE["integration_limits"]+[
  "Official storefront photo is historic; current appearance may differ.",
  "Facade details are approximations; no unverified store interior is modeled.",
  "No bicycle route built across unverified Route 377/317/store access.",
  "No full runtime collision, avatar, ferry, browser or Android playtest."
 ]
}
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print("V11_BUILD_COMPLETE",len(imgs),len(new_objs),glb.stat().st_size)
