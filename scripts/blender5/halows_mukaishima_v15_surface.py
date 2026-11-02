"""Halows V15: reviewable surface and architectural-scale refinement.

Strictly source-locked V14 geometry. No inventing ferry-to-store cycle access.
Creates true Blender 5.2.3 BLEND, GLB, textures, and same-view renders.
"""
import bpy,math,hashlib,json,random
from pathlib import Path
from mathutils import Vector
PARENT=Path(__file__).parent/"halows_mukaishima_v14_forecourt.py"
raw=PARENT.read_bytes()
git_blob=hashlib.sha1(("blob %d\0"%len(raw)).encode()+raw).hexdigest()
EXPECTED="7876eef919cdc0620daeb1e0478259ee06dde06b"
if git_blob!=EXPECTED:
    raise RuntimeError("V14 immutable source lock mismatch: "+git_blob)
s=raw.decode("utf-8")
marker='\nblend=OUT/(ID+".blend"); glb=OUT/(ID+".glb")'
if s.count(marker)!=1: raise RuntimeError("V14 authoring boundary changed")
prefix=s.split(marker)[0].replace(
 'ID="halows-mukaishima-v14-forecourt"',
 'ID="halows-mukaishima-v15-surface"').replace(
 'if ID!="halows-mukaishima-v14-forecourt"',
 'if ID!="halows-mukaishima-v15-surface"')
exec(compile(prefix,str(PARENT),"exec"),globals())
# V14 prefix reuses git_blob internally for V11; restore our V14 provenance.
git_blob=EXPECTED
if ID!="halows-mukaishima-v15-surface":
    raise RuntimeError("V15 asset identity mismatch")
preexisting={ob.name for ob in bpy.context.scene.objects}

# V14 already models the correct dimensions/site. Preserve it and add
# restrained roof-envelope / asphalt / glazing details at correct scale.
# Site photo is a historic visual reference only; these are not surveyed.
ROOF_JOINT=mat("V15_roof_joint_warm_grey",(.39,.425,.43,1),.96)
SOFT_FASCIA=mat("V15_fascia_shadow",(.105,.22,.195,1),.74)
WINDOW_SILL=mat("V15_glazing_sill",(.34,.425,.425,1),.48,.23)
PAVE_TRIM=mat("V15_pavement_join_lowcontrast",(.39,.375,.35,1),.92)
PALE_PINK=mat("V15_pale_pink_facade",(.695,.56,.54,1),.91)
DARK_POST=mat("V15_post_foot_satin",(.295,.335,.32,1),.78,.12)

# Flat roofs stay flat: no invented dormers or fake HVAC modules.
# Gentle 5cm relief in repeated cap seams removes the unbroken toy-like lid.
for i in range(1,9):
    x=-L/2+i*L/9
    building_aligned_box("V15_roof_seam_%02d"%i,(x,0,H+.165),
                         (.028,D-1.5,.012),ROOF_JOINT)
for x,name in [(-L/2+.32,"west"),(L/2-.32,"east")]:
    building_aligned_box("V15_roof_edge_base_"+name,(x,0,H+.015),
                         (.075,D-1.4,.055),PAVE_TRIM)
# Controlled signs of roof drainage: no claim to real as-built gutters.
for y,name in [(F+.21,"front"),(D/2-.28,"rear")]:
    building_aligned_box("V15_roof_edge_reveal_"+name,(0,y,H+.10),
                         (L-.85,.07,.036),ROOF_JOINT)

# Large bare upper facade reads like a smooth polygon. Add finely spaced
# horizontal relief at existing fascia without inventing new windows.
for z in [3.78,4.68,5.29]:
    building_aligned_box("V15_front_wall_line_%03d"%int(z*100),
                         (0,F-.203,z),(L-.82,.026,.014),PALE_PINK)
for x in [-L/2+.8+i*(L-1.6)/15 for i in range(16)]:
    building_aligned_box("V15_front_wall_panel_%02d"%int((x+L/2)*10),
                         (x,F-.205,4.53),(.013,.02,1.37),PALE_PINK)

# The photo shows a dark-green line and a continuous storefront underneath.
# Avoid inappropriate bright plastic glare; preserve original glass gaps.
building_aligned_box("V15_fascia_lower_reveal",
                     (0,F-4.30,3.00),(L-1.6,.065,.055),SOFT_FASCIA)
for idx,x in enumerate([-L/2+2+i*(L-4)/11 for i in range(12)]):
    if abs(x-TX)<TW/2+1.2: continue
    building_aligned_box("V15_glazing_lower_sill_%02d"%idx,
                         (x,F-.22,.265),(2.25,.038,.036),WINDOW_SILL)

# Replace V11 original asphalt texture on parking lot with a gently mottled
# 512px reproducible material. Don't add fictitious crossings or cycle arrows.
TEX_NEW=[]
def baked_albedo(name,base,seed,dim=512,roof=False):
    rng=random.Random(seed); vals=[]
    for y in range(dim):
        for x in range(dim):
            low=.0027*(math.sin(x*.033+y*.014)+math.sin(x*.007-y*.024))
            fleck=(rng.random()-.5)*.018
            if roof: low*=.55; fleck*=.5
            change=low+fleck
            vals.extend([max(.015,min(.95,c+change)) for c in base]+[1.0])
    im=bpy.data.images.new(name,width=dim,height=dim,alpha=True)
    im.pixels.foreach_set(vals)
    p=OUT/(name+".png");im.filepath_raw=str(p.resolve());im.file_format="PNG"
    im.save();im.pack();TEX_NEW.append(p)
    return im
asphalt=baked_albedo("V15_asphalt_subtle_mottle",(.151,.161,.173),751)
def image_material(label,im,r=.95):
    ma=mat(label,(.4,.4,.4,1),r)
    tex=ma.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image=im;tex.extension="REPEAT"
    ma.node_tree.links.new(tex.outputs["Color"],
        ma.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    return ma
asphalt_m=image_material("V15_asphalt_micro_mottle",asphalt,.97)
obj=bpy.data.objects.get("parking")
if obj and obj.type=="MESH":
    obj.data.materials.clear();obj.data.materials.append(asphalt_m)
    planar_uv(obj,9.0)
# A measured curb-cut isn't present. Only trim the join already introduced
# by V14 with texture-consistent low contrast: no crossing or route created.
for x in (-16,16):
    building_aligned_box("V15_apron_outer_joint_%d"%x,
                         (x,F-6.45,.12),(.042,.095,.025),PAVE_TRIM)
# Give representative bollards a restrained base without affecting routing.
for i,x in enumerate([TX-3.5+j*(7/6) for j in range(7)]):
    ob=cyl("V15_bollard_socket_%02d"%i,(x,F-5,.037),.11,.068,DARK_POST)
    px,py,pz=ob.location
    ob.location=(ca*px-sa*py,sa*px+ca*py,pz)

# Geometry-only comparison: all original 7 V14 view names preserved.
# Render changes of actual generated geometry, never recycle earlier pngs.
new_names=sorted({ob.name for ob in bpy.context.scene.objects}-preexisting)
bpy.context.scene["asset_id"]=ID
bpy.context.scene["v15_source_v14_git_blob"]=git_blob
bpy.context.scene["route_accepted"]=False
bpy.context.scene["ferry_to_store_connected"]=False
bpy.context.scene["current_2026_site_surveyed"]=False
bpy.context.scene["v06_runtime_integrated"]=False
blend=OUT/(ID+".blend");glb=OUT/(ID+".glb")
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
bpy.ops.export_scene.gltf(filepath=str(glb.resolve()),
                           export_format="GLB",export_apply=True,
                           export_animations=False)

sc=bpy.context.scene;sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=1400;sc.render.resolution_y=900
sc.render.resolution_percentage=100;sc.render.image_settings.file_format="PNG"
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.54,.67,.79,1)
bg.inputs["Strength"].default_value=.72
sc.view_settings.view_transform="AgX";sc.view_settings.exposure=.10
bpy.ops.object.light_add(type="SUN",location=(-80,-90,105))
bpy.context.object.data.energy=2.2
bpy.context.object.rotation_euler=(math.radians(24),math.radians(-17),math.radians(-29))
bpy.ops.object.light_add(type="AREA",location=(3,-34,35))
bpy.context.object.data.energy=2600
bpy.context.object.data.shape="DISK";bpy.context.object.data.size=30
bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam
def look(target):
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
def build_pos(x,y,z):
    return ca*x-sa*y,sa*x+ca*y,z
shots=[
("site_aerial",(-115,-125,92),(0,-10,1.5),45),
("forecourt",(-45,-82,7),(4,-16,3.2),40),
("entry_eye",build_pos(TX+3,F-17,1.68),build_pos(TX,F-.2,2.15),38),
("tower_identity",build_pos(TX-20,EF-23,10),build_pos(TX,EF,9.25),48),
("apron_detail",build_pos(TX-12,F-18,3.7),build_pos(TX-11,F-4,.10),43),
("roof_edge",build_pos(24,F-47,14),build_pos(0,-2,4.4),49),
("facade_oblique",build_pos(-31,F-53,10),build_pos(0,F,3),40)
]
renders=[]
for name,pos,target,lens in shots:
    cam.location=pos;look(target);cam.data.lens=lens
    dest=OUT/(ID+"_"+name+".png")
    sc.render.filepath=str(dest.resolve())
    bpy.ops.render.render(write_still=True)
    renders.append(dest)
bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for part in iter(lambda:f.read(1<<20),b""):h.update(part)
    return h.hexdigest()
site_path=OUT/"site_lock.json"
site_path.write_text(json.dumps(SITE,ensure_ascii=False,indent=2),encoding="utf-8")
manifest={
"schema_version":1,"asset_id":ID,"source_file":blend.name,
"model_file":glb.name,"source_v14_git_blob":git_blob,
"status":"V15_ART_CANDIDATE_NOT_ROUTE_OR_RUNTIME",
"blender_version":bpy.app.version_string,"origin_wgs84":SITE["origin_wgs84"],
"clips":[],"requirements":{"skins":False},"min_animation_count":0,
"font_asset_shipped":False,"browser_tested":False,"android_tested":False,
"route_accepted":False,"runtime_integrated":False,"files":{}
}
source_textures=[p for p in (OUT/"V11_procedural_asphalt.png",
                             OUT/"V11_procedural_apron_pavers.png",
                             OUT/"V14_original_roof_albedo.png",
                             OUT/"V14_original_ground_albedo.png") if p.is_file()]
for p in [blend,glb,*renders,*source_textures,*TEX_NEW,site_path]:
    manifest["files"][p.name]={"bytes":p.stat().st_size,"sha256":sha(p)}
(OUT/"asset_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
report={
 "asset_id":ID,"status":"PASS_BUILD_EXPORT_RENDER_ONLY",
 "source_v14_git_blob":git_blob,
 "source_osm_building_way":"661155704",
 "new_geometry_names":new_names,
 "views":[a[0] for a in shots],
 "new_original_textures":[p.name for p in TEX_NEW],
 "roof_asbuilt_verified":False,
 "legal_bicycle_access_verified":False,
 "ferry_to_store_route_verified":False,
 "v06_vertical_datum_available":False,
 "v06_runtime_integrated":False,
 "browser_playtest_passed":False,
 "android_playtest_passed":False,
 "limitations":["Photo-based approximation only; current store facade unverified",
 "Roof-edge visual seams and apron trims are not measured in situ",
 "OSM roads remain centerlines; do not infer bike legal access",
 "Seven Blender renders and GLB structure are not gameplay certification"]
}
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print("V15_REAL_BLENDER_EXPORT_COMPLETE",len(new_names),len(renders),glb.stat().st_size)
