"""Halows V14: source-locked V11 real Blender geometry refinement.

Standalone art candidate. No simulated road access, no V06 runtime changes.
Camera renders and GLB are produced by actual Blender 5.2.3.
"""
import bpy, math, hashlib, json, random, glob
from pathlib import Path
from mathutils import Vector

PARENT=Path(__file__).parent/"halows_mukaishima_v11_facade.py"
raw=PARENT.read_bytes()
git_blob=hashlib.sha1(("blob %d\0"%len(raw)).encode()+raw).hexdigest()
EXPECTED_BLOB="12480d7767a179b4453331617ad6d856ac418685"
if git_blob!=EXPECTED_BLOB:
    raise RuntimeError("V11 source-lock mismatch: "+git_blob)
source=raw.decode("utf-8")
marker='\nblend=OUT/(ID+".blend"); glb=OUT/(ID+".glb")'
if source.count(marker)!=1:
    raise RuntimeError("Cannot find V11 geometry / export boundary")
prefix=source.split(marker)[0]
prefix=prefix.replace('ID="halows-mukaishima-v11-facade"',
                      'ID="halows-mukaishima-v14-forecourt"')
prefix=prefix.replace('if ID!="halows-mukaishima-v11-facade"',
                      'if ID!="halows-mukaishima-v14-forecourt"')
exec(compile(prefix,str(PARENT),"exec"),globals())
if ID!="halows-mukaishima-v14-forecourt":
    raise RuntimeError("Did not inherit V11 geometry correctly")
before=set(o.name for o in bpy.context.scene.objects)

# Inherit all original model dimensions, orientation and V09 site lock.
# The original V11 storefront tower sign, two baked asphalt/paver texture
# images and all roads are preserved byte-for-byte in input source.
# All new near-field components are modeling estimates, not a 2026 survey.
WALL_CAP=mat("V14_warm_wall_caps",(.75,.68,.61,1),.84)
PINK_JOINT=mat("V14_pale_grout",(.59,.458,.43,1),.94)
EDGE_METAL=mat("V14_satin_brushed_metal",(.43,.49,.48,1),.37,.48)
FOOT=mat("V14_slate_base",(.24,.28,.28,1),.84)
GREEN_TRIM=mat("V14_canopy_dark_trim",(.038,.175,.158,1),.65,.11)
PAVEDGE=mat("V14_apron_edge_stone",(.49,.46,.43,1),.87)

# Adjust material warmth instead of inventing a different architecture.
# Exterior source photo was supplied by Halows as historic reference.
for matobj,rgb in ((W,(.68,.595,.55,1)),(SH,(.60,.47,.44,1)),
                   (C,(.68,.66,.60,1)),(TERR,(.33,.385,.29,1))):
    matobj.diffuse_color=rgb
    principled=matobj.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value=rgb

# Very small facade panel controls: low-contrast, no distressed cracks.
# Work in building-local coordinates, then place using V10's ENU helper.
for side in (-1,1):
    for k in (1,2,3):
        local_x=side*(L/2-.10)
        local_y=-D/2+3+k*6.4
        building_aligned_box("V14_side_pier_{}_{}".format(side,k),
                             (local_x,local_y,2.78),
                             (.036,.022,5.18),PINK_JOINT)
# The roof is not plain plastic; a restrained cap and roof drainage/edge
# indicators help visual scale, without changing original building footprint.
for y,label in [(-D/2+.28,"front"),(D/2-.28,"rear")]:
    building_aligned_box("V14_roof_cap_"+label,(0,y,H+.40),
                         (L-.58,.19,.07),WALL_CAP)
for x,label in [(-L/2+.25,"west"),(L/2-.25,"east")]:
    building_aligned_box("V14_roof_cap_"+label,(x,0,H+.40),
                         (.19,D-.60,.07),WALL_CAP)
for i,x in enumerate((-L/2+7,-L/2+14,L/2-12)):
    building_aligned_box("V14_roof_service_strip_%d"%i,
                         (x,D/2-4.4,H+.15),(.10,5.2,.045),EDGE_METAL)
# Subtle shadow line directly under green canopy and an improved thin lip.
building_aligned_box("V14_canopy_shadowline",(0,F-4.35,2.93),
                     (L-2.2,.075,.045),GREEN_TRIM)
building_aligned_box("V14_canopy_edge_cap",(0,F-4.32,3.525),
                     (L-1.05,.065,.064),EDGE_METAL)
# Entrance reveals and lower seals, with an actual inset gap retained.
for sign in (-1,1):
    building_aligned_box("V14_entry_jamb_shadow_%s"%sign,
                        (TX+sign*2.46,EF-.39,1.45),
                        (.055,.073,2.60),FOOT)
building_aligned_box("V14_entry_weep_sill",(TX,EF-.53,.092),
                     (4.68,.30,.045),EDGE_METAL)
# Bollard socket feet and dark-capped top match usual real-scale fixtures.
for i,x in enumerate([TX-3.5+j*(7/6) for j in range(7)]):
    # metal foot with no new invisible access opening
    ob=cyl("V14_bollard_foot_%02d"%i,(x,F-5,.08),.148,.085,FOOT)
    ob.location=(ca*ob.location.x-sa*ob.location.y,sa*ob.location.x+ca*ob.location.y,ob.location.z)
    cap=cyl("V14_bollard_cap_%02d"%i,(x,F-5,.835),.073,.045,EDGE_METAL)
    cap.location=(ca*cap.location.x-sa*cap.location.y,sa*cap.location.x+ca*cap.location.y,cap.location.z)

# Parking and apron have a visibly abrupt edge in V11. Add low-profile
# trim along *only* source-estimated lot bounds. Do NOT invent pedestrian
# crossing, curb cut, ramp, sidewalk access or bicycle blue line.
parking_y=F-20.5
lot_width=L+22
lot_depth=28
for side,label in ((-1,"west"),(1,"east")):
    building_aligned_box("V14_lot_skirting_"+label,
        (side*(lot_width/2-.09),parking_y,-.092),
        (.18,lot_depth-.2,.085),FOOT)
for y,label in ((parking_y-lot_depth/2,"south"),
                (parking_y+lot_depth/2,"north")):
    building_aligned_box("V14_lot_edge_"+label,
        (0,y,-.09),(lot_width-.36,.15,.07),PAVEDGE)
# Appear as contact trim, not a route boundary.
for side,label in ((-1,"left"),(1,"right")):
    building_aligned_box("V14_apron_side_"+label,
        (side*(L+1.2)/2,F-3.25,.087),
        (.085,5.8,.10),PAVEDGE)

# A deterministic low-contrast original albedo texture for the roof.
# Baked PNG is embedded in the final GLB, not procedural Blender-only nodes.
ROOF_TEXTURES=[]
def original_albedo(name,base,seed,dim=256):
    rng=random.Random(seed)
    image=bpy.data.images.new(name,width=dim,height=dim,alpha=True)
    vals=[]
    for y in range(dim):
        for x in range(dim):
            grain=(rng.random()-.5)*.027
            wave=math.sin(x*.085+y*.041)*.005
            rgb=[min(.96,max(.04,c+grain+wave)) for c in base]
            vals.extend((*rgb,1.0))
    image.pixels.foreach_set(vals)
    p=OUT/(name+".png")
    image.filepath_raw=str(p.resolve())
    image.file_format="PNG"
    image.save()
    image.pack()
    ROOF_TEXTURES.append(p)
    return image
roofimg=original_albedo("V14_original_roof_albedo",(.54,.56,.555),2041)
roofobj=bpy.data.objects.get("roof")
if roofobj and roofobj.type=="MESH":
    # Dedicated material means original W/M materials remain intact.
    roofmat=mat("V14_roof_microcolor",(.54,.56,.555,1),.88)
    tex=roofmat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image=roofimg
    roofmat.node_tree.links.new(tex.outputs["Color"],
       roofmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    roofobj.data.materials.clear()
    roofobj.data.materials.append(roofmat)
    planar_uv(roofobj,4.0)

# Terrain gets original fine ground colour from packed tile image.
ground=original_albedo("V14_original_ground_albedo",(.33,.39,.30),889,dim=256)
groundmat=mat("V14_grass_subtle_color",(.33,.39,.30,1),.98)
tex=groundmat.node_tree.nodes.new("ShaderNodeTexImage")
tex.image=ground
groundmat.node_tree.links.new(tex.outputs["Color"],
    groundmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
terr=bpy.data.objects.get("Terrain_GSI_DEM5A")
if terr and terr.type=="MESH":
    terr.data.materials.clear()
    terr.data.materials.append(groundmat)
    planar_uv(terr,11.0)

# Set explicit evidence flags: a green Blender CI cannot certify rideability.
bpy.context.scene["asset_id"]=ID
bpy.context.scene["source_v11_git_blob"]=EXPECTED_BLOB
bpy.context.scene["route_accepted"]=False
bpy.context.scene["store_access_verified"]=False
bpy.context.scene["v06_runtime_integrated"]=False
bpy.context.scene["surveyed_curb_cuts"]=False
new_names=sorted({o.name for o in bpy.context.scene.objects}-before)
blend=OUT/(ID+".blend"); glb=OUT/(ID+".glb")
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
bpy.ops.export_scene.gltf(filepath=str(glb.resolve()),export_format="GLB",
                           export_apply=True,export_animations=False)
# Real Blender render; preserve 4 same-camera V11 views, plus focused QA views.
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=1400
sc.render.resolution_y=900
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.54,.67,.79,1)
bg.inputs["Strength"].default_value=.72
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=.10
bpy.ops.object.light_add(type="SUN",location=(-80,-90,105))
bpy.context.object.data.energy=2.2
bpy.context.object.rotation_euler=(math.radians(24),math.radians(-17),math.radians(-29))
bpy.ops.object.light_add(type="AREA",location=(3,-34,35))
bpy.context.object.data.energy=2600
bpy.context.object.data.shape="DISK"
bpy.context.object.data.size=30
bpy.ops.object.camera_add()
cam=bpy.context.object; sc.camera=cam
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
    cam.location=pos
    look(target)
    cam.data.lens=lens
    dest=OUT/(ID+"_"+name+".png")
    sc.render.filepath=str(dest.resolve())
    bpy.ops.render.render(write_still=True)
    renders.append(dest)
bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
(OUT/"site_lock.json").write_text(json.dumps(SITE,ensure_ascii=False,indent=2))
manifest={
 "schema_version":1,"asset_id":ID,"source_file":blend.name,
 "model_file":glb.name,"status":"V14_VISUAL_FORECOURT_CANDIDATE_NOT_RIDEABLE",
 "source_v11_git_blob":git_blob,
 "origin_wgs84":SITE["origin_wgs84"],
 "blender_version":bpy.app.version_string,
 "font_asset_shipped":False,"clips":[],"requirements":{"skins":False},
 "min_animation_count":0,"files":{},
 "route_accepted":False,"browser_tested":False,"android_tested":False,
 "v06_runtime_integrated":False,"estimated":["facade joints","roof caps",
 "parking and apron edge finish","roof and terrain albedo",
 "bollard mounts","unverified slab junctions"]
}
for p in [blend,glb,*renders,*ROOF_TEXTURES,*TEXTURES,OUT/"site_lock.json"]:
    manifest["files"][p.name]={"bytes":p.stat().st_size,"sha256":sha(p)}
(OUT/"asset_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
report={
 "status":"PASS_BUILD_EXPORT_RENDER_ONLY",
 "asset_id":ID,"source_parent_git_blob":git_blob,
 "original_source_osm_footprint":"661155704",
 "new_geometry_names":new_names,
 "view_names":[s[0] for s in shots],
 "images":[p.name for p in ROOF_TEXTURES],
 "source_historic_store_photo":"https://www.halows.com/stores/detail/77",
 "source_terrain":"GSI DEM5A 20m display subsample from original V09",
 "store_pad_m_estimate":PAD,"grading_feather_m_estimate":18,
 "surveyed":False,"bike_route_approved":False,"access_certified":False,
 "browser_3d_tested":False,"android_tested":False,"runtime_integrated":False,
 "limitations":["No 2026 survey or site plan","No actual bicycle blue-line mapping",
 "No certified legal access or crossing","No V06 world elevation datum",
 "Blender render and GLB structure do not prove visual acceptance or gameplay"]}
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print("V14_REAL_BLENDER_BUILD_COMPLETE",glb.stat().st_size,
      len(new_names),len(renders))
