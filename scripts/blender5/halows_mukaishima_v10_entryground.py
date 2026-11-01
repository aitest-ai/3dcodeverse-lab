import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
OUT=Path("outputs"); OUT.mkdir(exist_ok=True)
sys.path.append(str(Path(__file__).parent))
from halows_site_v09_data import load_site_data
SITE=load_site_data()
ID="halows-mukaishima-v10-entryground"; L=46.798; D=33.309; H=5.55; F=-D/2
TX=8.6; TW=10.4; TD=4.8; TB=7.45; TT=12.4; BZ=F+0.85; EF=F-1.57
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
def mat(n,c,r=.75,m=0):
 x=bpy.data.materials.new(n); x.diffuse_color=c; x.use_nodes=True; b=x.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value=c; b.inputs["Roughness"].default_value=r; b.inputs["Metallic"].default_value=m
 if c[3]<.999: b.inputs["Alpha"].default_value=c[3]; x.surface_render_method="DITHERED"
 return x
W=mat("warm pink",(.76,.54,.48,1)); W2=mat("tower pink",(.69,.43,.39,1)); C=mat("cream",(.93,.87,.74,1)); G=mat("green",(.035,.24,.17,1),.45,.05); GD=mat("dark green",(.018,.15,.105,1),.4,.08); SG=mat("sign green",(.015,.28,.18,1),.38,.05); R=mat("red",(.46,.04,.03,1)); GL=mat("glass",(.09,.20,.23,.44),.15); M=mat("metal",(.55,.58,.56,1),.35,.35); WH=mat("white",(.88,.88,.82,1)); A=mat("asphalt",(.125,.135,.14,1),.95); P=mat("paving",(.54,.30,.20,1),.9); LN=mat("line",(.88,.88,.82,1)); RF=mat("roof",(.27,.29,.29,1),.85); SH=mat("joint",(.38,.24,.21,1))
def cube(n,loc,size,ma,bev=0):
 bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=n; o.scale=(size[0]/2,size[1]/2,size[2]/2); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(ma)
 if bev: q=o.modifiers.new("bevel","BEVEL"); q.width=bev; q.segments=2
 return o
def cyl(n,loc,r,d,ma,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d,location=loc,rotation=rot); o=bpy.context.object; o.name=n; o.data.materials.append(ma); return o
def bar(n,a,b,w,d,ma):
 a,b=Vector(a),Vector(b); v=b-a; o=cube(n,(a+b)/2,(v.length,d,w),ma); o.rotation_euler[1]=-math.atan2(v.z,v.x); return o
def textmesh(n,body,loc,size,ma):
 bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=n; o.data.body=body; o.data.align_x="CENTER"; o.data.align_y="CENTER"; o.data.size=size; o.data.extrude=.025; o.data.bevel_depth=.006; o.data.materials.append(ma); bpy.ops.object.convert(target="MESH"); return o
# V10 hollow building shell: the V09 glass was in front of an opaque main cube.
# Do not reconstruct unknown shelves or indoor merchandise.
cube("A_floor_slab",(0,0,.115),(L,D,.23),W,.035)
cube("A_roof_band",(0,0,H-.50),(L,D,1.0),W,.06)
cube("A_rear_wall",(0,D/2-.16,(H+.23)/2),(L,.32,H-.23),W,.02)
for side in (-1,1):
 cube(f"A_side_wall_{side}",(side*(L/2-.17),0,(H+.23)/2),(.34,D-.48,H-.23),W,.025)
cube("A_front_sill",(0,F+.16,.22),(L,.32,.44),W,.02)
cube("A_front_header",(0,F+.16,(H+2.90)/2),(L,.32,H-2.90),W,.02)
BACK=mat("unknown_interior_occlusion_only",(.055,.077,.079,1),.94)
cube("A_interior_shadow_screen",(0,F+3.35,1.53),(L-.75,.04,2.70),BACK)
cube("roof",(0,0,H+.04),(L-.45,D-.45,.2),RF)
for y in (-D/2+.16,D/2-.16): cube("parapet",(0,y,H+.18),(L,.3,.5),C)
for x in (-L/2+.16,L/2-.16): cube("parapet_side",(x,0,H+.18),(.3,D-.6,.5),C)
for i,x in enumerate([(-L/2+1.7)+j*((TX-TW/2-1.3)-(-L/2+1.7))/7 for j in range(8)]):
 cube(f"glassW{i}",(x,F-.045,1.52),(2.7,.08,2.55),GL); cube(f"mullion{i}",(x-1.38,F-.09,1.52),(.075,.12,2.75),M)
for i,x in enumerate([TX+TW/2+1.8+j*((L/2-1.8)-(TX+TW/2+1.8))/2 for j in range(3)]): cube(f"glassE{i}",(x,F-.045,1.52),(2.7,.08,2.55),GL)
# Replace opaque vestibule cube with piers and upper header for true door depth.
OPEN_W=5.15
for side in (-1,1):
 pier_w=(TW-OPEN_W)/2
 pier_x=TX+side*(OPEN_W/2+pier_w/2)
 cube(f"tower_pier_{side}",(pier_x,BZ,TB/2),(pier_w,TD,TB),W2,.04)
cube("tower_over_entry",(TX,BZ,(3.10+TB)/2),(OPEN_W,TD,TB-3.10),W2,.04)
cube("tower_sign",(TX,BZ,(TT+TB)/2),(TW,TD,TT-TB),C,.04)
cube("tower_trim",(TX,BZ,TB+.08),(TW+.36,TD+.22,.42),M)
for i,x in enumerate([TX-TW/2+.45+j*.55 for j in range(19)]): cube(f"rib{i}",(x,EF-.055,(TT+TB)/2),(.035,.06,TT-TB-.28),SH)
for i,z in enumerate([.45+j*.48 for j in range(15)]): cube(f"joint{i}",(TX,EF-.055,z),(TW-.18,.04,.025),SH)
cube("entrance_recess",(TX,EF-.10,1.50),(4.75,.10,3),GD)
for i,dx in enumerate((-1.08,1.08)): cube(f"door{i}",(TX+dx,EF-.17,1.48),(2.05,.08,2.75),GL)
for i,dx in enumerate((-2.16,0,2.16)): cube(f"doorframe{i}",(TX+dx,EF-.22,1.48),(.08,.10,2.9),M)
ARCH=mat("arch_cream",(.98,.94,.82,1),.98,0)
curve=bpy.data.curves.new("arch","CURVE"); curve.dimensions="3D"; curve.bevel_depth=.18; curve.bevel_resolution=3; sp=curve.splines.new("POLY"); pts=[(TX+3.35*math.cos(a),EF-.25,4.85+1.65*math.sin(a)) for a in [math.pi-i*math.pi/30 for i in range(31)]]; sp.points.add(len(pts)-1)
for p,co in zip(sp.points,pts): p.co=(*co,1)
o=bpy.data.objects.new("arch",curve); bpy.context.collection.objects.link(o); curve.materials.append(ARCH)
cy=F-4.25/2+.12; cube("canopy",(0,cy,3.04),(L-1.5,4.25,.15),M); cube("green_fascia",(0,F-4.19,3.28),(L-1.2,.30,.45),GD)
for i,x in enumerate([(-L/2+2.2)+j*((L-4.4)/9) for j in range(10)]): cube(f"col{i}",(x,F-4.03,1.52),(.18,.18,3.04),WH)
cube("customer_apron",(0,F-3.25,.06),(L+1.2,6.5,.12),P); cube("parking",(0,F-20.5,-.045),(L+22,28,.08),A)
for i,x in enumerate([(-L/2-6)+j*((L+12)/14) for j in range(15)]): cube(f"parkline{i}",(x,F-9,.008),(.07,5.5,.018),LN)
for i,x in enumerate([TX-3.5+j*(7/6) for j in range(7)]): cyl(f"bollard{i}",(x,F-5,.41),.075,.82,M)
for i,x in enumerate([(-L/2+3)+j*(15/7) for j in range(8)]):
 cube(f"rackL{i}",(x-.42,F-4.7,.47),(.07,.07,.88),M); cube(f"rackR{i}",(x+.42,F-4.7,.47),(.07,.07,.88),M); cube(f"rackT{i}",(x,F-4.7,.91),(.84,.07,.07),M)
gy=EF-.28
for i,dx in enumerate((-2.7,0,2.7)): cube(f"red{i}",(TX+dx,gy,10.75),(1.25,.11,2.05),R); cyl(f"disc{i}",(TX+dx+.48,gy-.07,10.70),.42,.13,G,rot=(math.pi/2,0,0))
textmesh("HALOWS_word","HALOWS",(TX,gy-.13,8.62),.72,SG)
textmesh("HALOWS_24H","24H OPEN",(TX,gy-.13,7.75),.34,SG)
# V08 near-field refinements: facade joints, entrance depth, column bases/caps, cycle shelter, cart corral, lighting and restrained rear loading context.
# These remain photo/plan-informed estimates rather than surveyed dimensions.
cube("wall_base_front",(0,F-.16,.23),(L-.8,.16,.46),SH,.02)
for i,z in enumerate([.70,1.45,2.20,2.95,3.70,4.45,5.18]):
    cube(f"front_joint_{i}",(TX,EF-.19,z),(TW-.30,.035,.025),SH)
for i,x in enumerate([TX-TW/2+.65+j*(TW-1.3)/10 for j in range(11)]):
    cube(f"tower_rib_v08_{i}",(x,EF-.195,(TT+TB)/2),(.025,.045,TT-TB-.42),SH)
# Entrance vestibule depth and header.
cube("entry_inner_header",(TX,EF+.34,2.95),(5.1,.75,.24),M,.025)
cube("entry_inner_left",(TX-2.46,EF+.34,1.44),(.16,.75,2.72),M,.015)
cube("entry_inner_right",(TX+2.46,EF+.34,1.44),(.16,.75,2.72),M,.015)
cube("entry_inner_glass",(TX,EF+.64,1.48),(4.65,.06,2.72),GL)
# Column feet and caps under the canopy.
for i,x in enumerate([(-L/2+2.2)+j*((L-4.4)/9) for j in range(10)]):
    cyl(f"colfoot_{i}",(x,F-4.03,.09),.18,.18,M)
    cube(f"colcap_{i}",(x,F-4.03,2.98),(.34,.34,.12),M,.015)
# Small cycle shelter with representative racks only; not a 117-position reconstruction.
cube("cycle_shelter_roof",(-12.5,F-7.45,2.35),(10.8,2.7,.16),GD,.04)
for i,x in enumerate([-17,-12.5,-8]):
    cube(f"cycle_shelter_post_{i}",(x,F-7.45,1.18),(.16,.16,2.36),M)
# Shopping-cart corral near the customer apron.
cube("cart_roof",(17.2,F-7.2,2.15),(5.0,2.6,.13),M,.03)
for x in [15.0,19.4]:
    cube("cart_post",(x,F-7.2,1.07),(.12,.12,2.14),M)
# Accessible parking indication near entrance; placement is representative.
for x in [TX-5.2,TX-1.8]:
    cube("accessible_bay_line",(x,F-10.2,.012),(3.0,.055,.024),LN)
AB=mat("accessible_blue",(.06,.24,.55,1),.82)
cyl("accessible_sign_post",(TX-3.5,F-9.25,.72),.045,1.44,M)
cube("accessible_sign",(TX-3.5,F-9.25,1.48),(.62,.08,.62),AB,.03)
# Parking light poles seen in the official photo context.
for i,(x,y) in enumerate([(-20,F-18),(20,F-18)]):
    cyl(f"lightpole_{i}",(x,y,4.6),.08,9.2,M)
    bar(f"lightarm_{i}",(x,y,8.95),(x+1.2,y,8.95),.10,.10,M)
    cube(f"lighthead_{i}",(x+1.28,y,8.88),(1.0,.36,.18),WH,.03)
# Restrained rear/NE loading context from the 2017 plan direction only.
cube("rear_loading_pad",(L/2-6,D/2+2.2,.035),(11.5,4.0,.07),A)
cube("rear_loading_canopy",(L/2-6,D/2+.9,2.7),(8.5,2.2,.18),M,.03)
for x in [L/2-9.4,L/2-2.6]:
    cube("rear_loading_post",(x,D/2+.9,1.35),(.16,.16,2.7),M)

# V10 slender glazing frames. Actual partition locations remain estimated.
for key,lo,hi in [("west",-L/2+1.3,TX-TW/2-1.0),("east",TX+TW/2+1.0,L/2-1.2)]:
 if hi>lo:
  mid=(lo+hi)/2
  cube(f"storefront_{key}_head",(mid,F-.14,2.82),(hi-lo,.12,.09),M,.01)
  cube(f"storefront_{key}_sill",(mid,F-.14,.36),(hi-lo,.12,.09),M,.01)
  cube(f"storefront_{key}_transom",(mid,F-.145,1.90),(hi-lo,.07,.055),M)
cube("entry_threshold",(TX,EF-.36,.065),(4.75,.34,.13),M,.012)
# --- V10 georeferenced site on unchanged V09 OSM/GSI source lock ---
HEAD=math.radians(SITE["building"]["long_axis_heading_deg_from_east_ccw"])
PAD=SITE["building"]["store_pad_elevation_m"]
ca,sa=math.cos(HEAD),math.sin(HEAD)

# Rotate the complete V08 building/forecourt candidate from local-building axes into ENU.
asset_objects=list(bpy.context.scene.objects)
for o in asset_objects:
    x,y,z=o.location
    o.location=(ca*x-sa*y,sa*x+ca*y,z)
    o.rotation_euler.z += HEAD

TERR=mat("terrain",(.31,.385,.265,1),.96)
SITEPAD=mat("graded_pad",(.38,.32,.25,1),.92)
ROAD=mat("road_asphalt",(.13,.14,.15,1),.96)
SERVICE=mat("service_asphalt",(.15,.16,.165,1),.94)
CURB=mat("curb",(.48,.49,.47,1),.82)

def to_building_local(x,y):
    return ca*x+sa*y,-sa*x+ca*y
def grading_weight(x,y):
    lx,ly=to_building_local(x,y)
    # Flat graded core preserves the V08 parking/forecourt; 18m feather to DEM.
    dx=max(abs(lx)-38.0,0.0)
    dy=max(ly-27.0,-53.0-ly,0.0)
    d=math.hypot(dx,dy)
    if d<=0: return 1.0
    if d>=18.0: return 0.0
    t=d/18.0
    return 1.0-(t*t*(3.0-2.0*t))
def graded_rel_z(x,y,elev_abs):
    w=grading_weight(x,y)
    target=PAD-0.08
    return ((elev_abs*(1-w)+target*w)-PAD)

# 5m GSI DEM5A terrain lock.
grid=SITE["terrain"]["grid"]; step=grid["step_m"]; xmin=grid["x_min"]; ymin=grid["y_min"]
rows=grid["rows"]; ny=len(rows); nx=len(rows[0])
verts=[]; faces=[]
for iy,row in enumerate(rows):
    y=ymin+iy*step
    for ix,elev in enumerate(row):
        x=xmin+ix*step
        if elev is None: elev=PAD
        verts.append((x,y,graded_rel_z(x,y,elev)))
for iy in range(ny-1):
    for ix in range(nx-1):
        a=iy*nx+ix; b=a+1; c0=a+nx+1; d=a+nx
        faces.append((a,b,c0,d))
mesh=bpy.data.meshes.new("terrain_mesh"); mesh.from_pydata(verts,[],faces); mesh.update()
terrain=bpy.data.objects.new("Terrain_GSI_DEM5A",mesh); bpy.context.collection.objects.link(terrain); mesh.materials.append(TERR)

def road_z(x,y,elev,follow_site_grade=False):
    if follow_site_grade:
        return graded_rel_z(x,y,elev)+.035
    return elev-PAD+.035
def make_road(name,points,width,material,follow_site_grade=False):
    # Visual site clip only. Full OSM point sequences remain unchanged in site_lock.json.
    xmax=xmin+(nx-1)*step; ymax=ymin+(ny-1)*step
    pts=[p for p in points if p.get("elev_m") is not None and xmin<=p["x"]<=xmax and ymin<=p["y"]<=ymax]
    if len(pts)<2: return None
    left=[]; right=[]
    for i,p in enumerate(pts):
        if i==0:
            dx=pts[1]["x"]-p["x"]; dy=pts[1]["y"]-p["y"]
        elif i==len(pts)-1:
            dx=p["x"]-pts[i-1]["x"]; dy=p["y"]-pts[i-1]["y"]
        else:
            dx=pts[i+1]["x"]-pts[i-1]["x"]; dy=pts[i+1]["y"]-pts[i-1]["y"]
        ln=max(math.hypot(dx,dy),1e-6); nxv=-dy/ln; nyv=dx/ln
        z=road_z(p["x"],p["y"],p["elev_m"],follow_site_grade)
        left.append((p["x"]+nxv*width/2,p["y"]+nyv*width/2,z))
        right.append((p["x"]-nxv*width/2,p["y"]-nyv*width/2,z))
    rv=[]; rf=[]
    for l,r in zip(left,right): rv.extend([l,r])
    for i in range(len(pts)-1): rf.append((2*i,2*i+1,2*i+3,2*i+2))
    me=bpy.data.meshes.new(name+"_mesh"); me.from_pydata(rv,[],rf); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob); me.materials.append(material); return ob

for r in SITE["roads"]:
    ref=r["tags"].get("ref")
    hw=r["tags"].get("highway")
    width=7.4 if ref=="317" else (6.3 if hw=="tertiary" else 4.8)
    make_road("OSM_road_"+r["osm_way_id"],r["points"],width,ROAD if ref=="317" or hw=="tertiary" else SERVICE,follow_site_grade=(hw=="service"))

# Low curb strip on the building-side Route 317 approach, kept deliberately simple.
# The low apron-edge visual is an estimate, NOT an authenticated cycle curb-cut.
def building_aligned_box(name,coord,size,material):
 x,y,z=coord
 obj=cube(name,(ca*x-sa*y,sa*x+ca*y,z),size,material,.015)
 obj.rotation_euler.z=HEAD
 return obj
CURB_COLOR=mat("forecourt_curb_soft",(.52,.51,.48,1),.91)
edge_y=F-6.48
for name,start,end in [("west",-L/2-.55,TX-4.1),("east",TX+4.1,L/2+.55)]:
 building_aligned_box(f"forecourt_edge_{name}",((start+end)/2,edge_y,.045),(end-start,.12,.09),CURB_COLOR)
# OSM road nodes remain location markers, not routed access gates.
for key in ("south_service_access","east_service_access"):
    ap=SITE["access_points"][key]
    cyl("AccessMarker_"+key,(ap["x"],ap["y"],ap["elev_m"]-PAD+.25),.18,.50,CURB)

bpy.context.scene["asset_id"]=ID
bpy.context.scene["osm_way_id"]="661155704"
bpy.context.scene["origin_wgs84"]=json.dumps(SITE["origin_wgs84"])
bpy.context.scene["building_heading_deg"]=SITE["building"]["long_axis_heading_deg_from_east_ccw"]
bpy.context.scene["store_pad_elevation_m"]=PAD
bpy.context.scene["source_note"]="V08 Blender asset placed on OSM footprint; GSI DEM5A terrain; grading plane estimated; route geometry OSM snapshot"

blend=OUT/f"{ID}.blend"; glb=OUT/f"{ID}.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
bpy.ops.export_scene.gltf(filepath=str(glb.resolve()),export_format="GLB",export_apply=True,export_animations=False)

sc=bpy.context.scene; sc.render.engine="BLENDER_EEVEE"; sc.render.resolution_x=1400; sc.render.resolution_y=900
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.42,.55,.69,1)
bg.inputs["Strength"].default_value=.55
sc.view_settings.view_transform="AgX"; sc.view_settings.exposure=0.0
bpy.ops.object.light_add(type="SUN",location=(-80,-100,120)); bpy.context.object.data.energy=2.0
# Render-only area fill. Three.js/Unity runtime must supply its own scene lighting.
bpy.ops.object.light_add(type="AREA",location=(12,-40,50))
bpy.context.object.data.energy=4800
bpy.context.object.data.shape="DISK"; bpy.context.object.data.size=44
bpy.ops.object.light_add(type="AREA",location=(-30,20,44))
bpy.context.object.data.energy=2100
bpy.context.object.data.shape="DISK"; bpy.context.object.data.size=35
bpy.ops.object.camera_add(); cam=bpy.context.object; sc.camera=cam
def look(pt): cam.rotation_euler=(Vector(pt)-cam.location).to_track_quat("-Z","Y").to_euler()
imgs=[]
shots=[
 ("site_aerial",(-115,-125,92),(0,-10,1.5),45),
 ("route317_arrival",(92,-92,8),(5,-18,3.0),42),
 ("forecourt",(-45,-82,7),(4,-16,3.2),40),
 ("north_overview",(-90,105,62),(0,-5,2.0),48),
 ("entry_eye",(ca*(TX+3)-sa*(F-17),sa*(TX+3)+ca*(F-17),1.68),
              (ca*TX-sa*(F-.2),sa*TX+ca*(F-.2),2.15),38)
]
for nm,pos,tgt,lens in shots:
 cam.location=pos; look(tgt); cam.data.lens=lens
 p=OUT/f"{ID}_{nm}.png"; sc.render.filepath=str(p.resolve()); bpy.ops.render.render(write_still=True); imgs.append(p)

# Preserve the exact lighting and final camera in the editable Blender mother file.
# The earlier pre-render save protects geometry during the build; this final save
# ensures the delivered .blend is inspectable with its real render setup intact.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()

(OUT/"site_lock.json").write_text(json.dumps(SITE,ensure_ascii=False,indent=2))
man={"schema_version":1,"asset_id":ID,"model_file":glb.name,"source_file":blend.name,"clips":[],"requirements":{"skins":False},"min_animation_count":0,
"status":"V10_ENTRY_DEPTH_GROUNDING_CANDIDATE_NOT_RUNTIME_INTEGRATED","blender_version":bpy.app.version_string,"files":{},"browser_tested":False,"android_tested":False,
"georeferenced":True,"origin_wgs84":SITE["origin_wgs84"],"heading_deg":SITE["building"]["long_axis_heading_deg_from_east_ccw"],
"estimated":["finished floor / grading plane","parking circulation","entry threshold","visual forecourt edge segments","facade subdivisions","dark non-reconstructed interior screen","curb cuts and current door coordinates; NOT a certified cycle approach"]}
for p in [blend,glb,*imgs,OUT/"site_lock.json"]: man["files"][p.name]={"bytes":p.stat().st_size,"sha256":sha(p)}
(OUT/"asset_manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2))
(OUT/"report.json").write_text(json.dumps({"status":"PASS_BUILD_EXPORT_RENDER_ENTRYGROUND_ONLY","origin_wgs84":SITE["origin_wgs84"],
"building_heading_deg":SITE["building"]["long_axis_heading_deg_from_east_ccw"],"store_pad_elevation_m":PAD,"grading_feather_m":18.0,"road_render_clip":"terrain grid bounds; source roads remain full in site_lock",
"road_way_ids":[r["osm_way_id"] for r in SITE["roads"]],"v10_changes":["hollow storefront and tower doorway","glazing frame/threshold depth","daylight area fill, neutral asphalt/terrain","visual apron edge with central break; NOT a certified access","correct grading feather report from 10m to actual 18m"],"source_site_asset_id":SITE["asset_id"],"real_route_verified":False,
"limitations":SITE["integration_limits"]+["No browser/Android playtest","No actor/bicycle runtime integration in this workflow","Route 317 and tertiary roads preserve locked DEM elevations; only service roads may follow estimated site grading"]},ensure_ascii=False,indent=2))
