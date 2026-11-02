"""V23: 377/317 original GSI terrain grid + true OSM way centreline.
Technical Blender preview ONLY, not a navigable road.
"""
import bpy, json, math, hashlib, base64, zlib, struct, pathlib, random
from mathutils import Vector
ROOT=pathlib.Path.cwd()
OUT=ROOT/"outputs/onomichi-v23";OUT.mkdir(parents=True,exist_ok=True)
P=ROOT/"assets/setouchi/onomichi-v23-gsi-ground-sample.json"
d=json.loads(P.read_text(encoding="utf-8"))
assert d["gsi_tile_sha256"]=="79dc9e009a448aec5726ee1c13906270fef196e92c36286075e5474310318e9c"
assert d["osm_source_sha256"]=="5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76"
assert d["osm_way_id"]=="388716484" and len(d["osm_way_lat_lon"])==4
x0,x1,step_x=d["x_m"];n0,n1,step_n=d["north_m"]
nx=round((x1-x0)/step_x)+1;ny=round((n1-n0)/step_n)+1
raw=zlib.decompress(base64.b64decode(d["dem_ground_cm_int16_le_zlib_base64"]))
assert len(raw)==nx*ny*2
heights=struct.unpack("<%dh"%(nx*ny),raw)
assert hashlib.sha256(raw).hexdigest()=="03726ce15167b760f6a738c1862097c258857299cae7a32353a84931c44cdbf1"
assert nx==51 and ny==66 and min(heights)==148 and max(heights)==1161
H=lambda i,j:heights[j*nx+i]*.01
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
def mat(name,rgb,roughness=.86,metallic=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*rgb,1)
    bs.inputs["Roughness"].default_value=roughness
    bs.inputs["Metallic"].default_value=metallic
    return m
GROUND=mat("V23__GSI_ground_not_road",(0.32,0.43,0.34),.93)
ROUTE=mat("V23__OSM_line_marker_not_road",(0.92,0.42,0.16),.48)
PIN=mat("V23__GSI_sample_location",(0.14,0.61,0.66),.47,.15)
HAZ=mat("V23__road_access_unverified",(0.78,.23,.20),.53)
CAP=mat("V23__readability_text",(0.95,0.95,0.87),.67)
SIDE=mat("V23__soil_vertical_cut",(0.18,0.24,0.22),.98)
# Preserve x East, y North, z Up in editable .blend. glTF export uses Y Up.
verts=[(x0+i*step_x,n0+j*step_n,H(i,j))
       for j in range(ny) for i in range(nx)]
faces=[]
for j in range(ny-1):
    for i in range(nx-1):
        a=j*nx+i;b=a+1;c=a+nx+1;d0=a+nx
        faces.append((a,b,c,d0))
mesh=bpy.data.meshes.new("V23_true_sampled_GSI_DEM_mesh")
mesh.from_pydata(verts,[],faces);mesh.update()
obj=bpy.data.objects.new("GSI_100x130m_DEM_ground_no_navigable_surface",mesh)
bpy.context.collection.objects.link(obj);obj.data.materials.append(GROUND)
for p in mesh.polygons:p.use_smooth=False
# A side-skirt makes a 3D study surface easier to judge, not a real cliff.
bottom=-1.8
v2=list(verts);f2=list(faces)
boundary=[]
for i in range(nx):boundary.append(i)
for j in range(1,ny):boundary.append(j*nx+nx-1)
for i in range(nx-2,-1,-1):boundary.append((ny-1)*nx+i)
for j in range(ny-2,0,-1):boundary.append(j*nx)
first=len(v2)
for i in boundary:v2.append((v2[i][0],v2[i][1],bottom))
for k,a in enumerate(boundary):
    b=boundary[(k+1)%len(boundary)]
    f2.append((a,b,first+(k+1)%len(boundary),first+k))
bpy.data.objects.remove(obj,do_unlink=True)
mesh=bpy.data.meshes.new("V23_ground_and_diagnostic_skirt");mesh.from_pydata(v2,[],f2);mesh.update()
obj=bpy.data.objects.new("GSI_DEM_original_height_samples",mesh)
bpy.context.collection.objects.link(obj)
obj.data.materials.append(GROUND)
obj.data.materials.append(SIDE)
for i,poly in enumerate(mesh.polygons):
    if i>=len(faces):poly.material_index=1
def height(x,y):
    fx=(x-x0)/step_x;fy=(y-n0)/step_n
    ix=max(0,min(nx-2,int(math.floor(fx))))
    iy=max(0,min(ny-2,int(math.floor(fy))))
    tx=max(0,min(1,fx-ix));ty=max(0,min(1,fy-iy))
    return (H(ix,iy)*(1-tx)*(1-ty)+H(ix+1,iy)*tx*(1-ty)
            +H(ix,iy+1)*(1-tx)*ty+H(ix+1,iy+1)*tx*ty)
lat0,lon0=d["origin_lat_lon"];yl=111132.;xl=111320*math.cos(math.radians(lat0))
points=[((lon-lon0)*xl,(lat-lat0)*yl) for lat,lon in d["osm_way_lat_lon"]]
line=[]
for a,b in zip(points,points[1:]):
    count=max(2,math.ceil(math.dist(a,b)))
    for k in range(count):
        t=k/count
        x=a[0]*(1-t)+b[0]*t;y=a[1]*(1-t)+b[1]*t
        line.append((x,y,height(x,y)+.24))
line.append((*points[-1],height(*points[-1])+.24))
cv=bpy.data.curves.new("V23_OSM_centreline_visual_indicator_not_road","CURVE")
cv.dimensions="3D";cv.bevel_depth=.09;cv.bevel_resolution=3
sp=cv.splines.new("POLY");sp.points.add(len(line)-1)
for p,pt in zip(sp.points,line):p.co=(*pt,1)
r=bpy.data.objects.new("OSM_way_388716484__90mm_visual_only",cv)
bpy.context.collection.objects.link(r);cv.materials.append(ROUTE)
# four diagnostic markers. No road width or curb inferred.
for i,(x,y) in enumerate(points):
    z=height(x,y)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.50,location=(x,y,z+.62))
    o=bpy.context.object;o.name=f"OSM_node_{i+1}_{d['osm_nodes'][i]}"
    o.data.materials.append(PIN if i in (1,2) else HAZ)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.075,depth=1.12,location=(x,y,z+.55))
    o=bpy.context.object;o.name=f"SurveyMarker_Pole_{i+1}"
    o.data.materials.append(PIN)
# backdrop, lights, cameras
sc=bpy.context.scene;sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=1400;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.world.use_nodes=True
sc.world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.38,.56,.64,1)
sc.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.75
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=.10
bpy.ops.object.light_add(type="SUN",location=(-20,30,65))
bpy.context.object.name="V23_sun";bpy.context.object.data.energy=2.5
bpy.context.object.rotation_euler=(math.radians(30),math.radians(-20),math.radians(18))
bpy.ops.object.light_add(type="AREA",location=(10,-12,40))
bpy.context.object.data.energy=1700;bpy.context.object.data.shape="DISK";bpy.context.object.data.size=35
bpy.ops.object.camera_add(location=(-96,-123,112))
cam=bpy.context.object;sc.camera=cam
def look(tar):
    cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat("-Z","Y").to_euler()
sc.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=str((OUT/"onomichi-v23-gsi-entry-ground.blend").resolve()))
bpy.ops.export_scene.gltf(filepath=str((OUT/"onomichi-v23-gsi-entry-ground.glb").resolve()),
    export_format="GLB",export_apply=True,export_animations=False,
    export_lights=False,export_cameras=False)
views=[
 ("aerial",(-95,-110,115),(0,0,2.1),40),
 ("route_end",(-33,57,25),(0,0,2.5),38),
 ("junction_end",(52,-58,25),(2,-15,2.3),45),
 ("terrain_oblique",(35,84,67),(0,0,4),42)]
imgs=[]
for name,cpos,target,lens in views:
    cam.location=cpos;cam.data.lens=lens;look(target)
    p=OUT/(f"V23_{name}_Blender.png")
    sc.render.filepath=str(p.resolve())
    bpy.ops.render.render(write_still=True);imgs.append(p)
bpy.ops.wm.save_as_mainfile(filepath=str((OUT/"onomichi-v23-gsi-entry-ground.blend").resolve()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={"status":"BLENDER_MODEL_AND_RENDER_ONLY__NOT_RIDEABLE","source_osm_sha256":d["osm_source_sha256"],
"gsi_tile_sha256":d["gsi_tile_sha256"],"sampled_heights_sha256":hashlib.sha256(raw).hexdigest(),
"source_dem_height_min_m":min(heights)*.01,"source_dem_height_max_m":max(heights)*.01,
"grid_vertices":nx*ny,"grid_resolution_m":2,"no_photographic_reconstruction":True,
"original_osm_way":d["osm_way_id"],"original_osm_nodes":d["osm_nodes"],
"actual_road_width_m":None,"actual_pavement_height_m":None,"field_traffic_signs_verified":False,
"legality_verified":False,"road_collision_verified":False,"browser_webgl2_tested":False,
"android_tested":False,"v06_runtime_merged":False,
"rendered_views":[p.name for p in imgs],"files":{}}
for p in [OUT/"onomichi-v23-gsi-entry-ground.blend",OUT/"onomichi-v23-gsi-entry-ground.glb",*imgs]:
    report["files"][p.name]={"bytes":p.stat().st_size,"sha256":sha(p)}
(OUT/"V23_Build_Report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print("V23_SOURCE_LOCKED_BLENDER_EXPORT_PASS",len(verts),len(faces),len(imgs))
