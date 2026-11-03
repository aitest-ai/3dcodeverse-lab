"""V27 Blender source derived from pinned GSI terrain + genuine OSM way 388716484.
Hypothetical 1.8m study strip, NOT a real road, rider animation or collision.
"""
import bpy,math,json,struct,hashlib,base64,zlib,pathlib
from mathutils import Vector
ROOT=pathlib.Path.cwd()
SRC=ROOT/"assets/setouchi/onomichi-v23-gsi-ground-sample.json"
OUT=ROOT/"outputs/onomichi-v27"
OUT.mkdir(parents=True,exist_ok=True)
d=json.loads(SRC.read_text())
assert d["osm_way_id"]=="388716484"
assert d["osm_source_sha256"]=="5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76"
raw=zlib.decompress(base64.b64decode(d["dem_ground_cm_int16_le_zlib_base64"]))
assert hashlib.sha256(raw).hexdigest()=="03726ce15167b760f6a738c1862097c258857299cae7a32353a84931c44cdbf1"
nx,ny=51,66
H=struct.unpack("<3366h",raw)
def elev(i,j):return H[j*nx+i]/100
def interp(x,y):
    f=(x+50)/2;g=(y+66)/2
    i=max(0,min(49,int(math.floor(f))));j=max(0,min(64,int(math.floor(g))))
    t=max(0,min(1,f-i));u=max(0,min(1,g-j))
    return elev(i,j)*(1-t)*(1-u)+elev(i+1,j)*t*(1-u)+elev(i,j+1)*(1-t)*u+elev(i+1,j+1)*t*u
def material(name,rgb,alpha=1):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,alpha);m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*rgb,alpha)
    bs.inputs["Roughness"].default_value=.85
    return m
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
ground_mat=material("ACTUAL_GSI_ground_not_pavement",(0.35,0.48,0.39))
study_mat=material("ASSUMED_1p8m_width_not_real_road",(0.28,0.59,0.76))
line_mat=material("OSM_centreline_not_navigation",(0.95,0.56,0.27))
marker_mat=material("QA_station_not_surveyed_roadside_feature",(0.97,0.81,0.38))
verts=[(-50+2*i,-66+2*j,elev(i,j)) for j in range(ny) for i in range(nx)]
faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
mesh=bpy.data.meshes.new("V27_GSI_DEM_3366_real_ground_values")
mesh.from_pydata(verts,[],faces);mesh.update()
ob=bpy.data.objects.new("SOURCE_GSI_GROUND_only",mesh);bpy.context.collection.objects.link(ob)
mesh.materials.append(ground_mat)
lat0,lon0=d["origin_lat_lon"]
xm=111320*math.cos(math.radians(lat0))
pts=[Vector(((lon-lon0)*xm,(lat-lat0)*111132)) for lat,lon in d["osm_way_lat_lon"]]
segments=[(pts[i+1]-pts[i]).length for i in range(3)]
dist=sum(segments)
assert 74.3<dist<74.42
def point_at(s):
    t=max(0,min(dist,s))
    for i,L in enumerate(segments):
        if t<=L or i==2:
            return pts[i]+(pts[i+1]-pts[i])*min(1,t/L)
        t-=L
def tangent(s):
    a=point_at(max(0,s-.2));b=point_at(min(dist,s+.2))
    return (b-a).normalized()
def strip_mesh(width=1.8):
    verts=[];faces=[]
    steps=150
    for k in range(steps+1):
        s=dist*k/steps;p=point_at(s);v=tangent(s)
        n=Vector((-v.y,v.x))
        for sign in (-1,1):
            pos=p+n*sign*width/2
            verts.append((pos.x,pos.y,interp(pos.x,pos.y)+.085))
    for k in range(steps):
        a=2*k;faces.append((a,a+1,a+3,a+2))
    mesh=bpy.data.meshes.new("V27_hypothetical_strip_width_1p8m_NOT_PAVEMENT")
    mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new("HYPOTHETICAL_WIDTH_1p8m_NOT_COLLIDER",mesh)
    bpy.context.collection.objects.link(o);o.data.materials.append(study_mat)
strip_mesh()
cv=bpy.data.curves.new("V27_OSM_centreline","CURVE");cv.dimensions="3D"
cv.bevel_depth=.08;cv.bevel_resolution=2
spl=cv.splines.new("POLY");spl.points.add(150)
for k,p in enumerate(spl.points):
    s=dist*k/150;pos=point_at(s)
    p.co=(pos.x,pos.y,interp(pos.x,pos.y)+.20,1)
line=bpy.data.objects.new("OSM_way388716484_source_centreline",cv)
bpy.context.collection.objects.link(line);line.data.materials.append(line_mat)
for i,s in enumerate([0,10,20,30,40,50,60,70,dist]):
    p=point_at(s);z=interp(p.x,p.y)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.35,location=(p.x,p.y,z+.55))
    obj=bpy.context.object;obj.name=f"STATION_S{i:02d}_NOT_PHYSICAL_STREET_OBJECT"
    obj.data.materials.append(marker_mat)
scene=bpy.context.scene;scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1400;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG";scene.view_settings.view_transform="AgX"
scene.world.use_nodes=True;scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.5,.6,.65,1)
scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.75
bpy.ops.object.light_add(type="SUN",location=(20,-15,80))
bpy.context.object.data.energy=3
bpy.context.object.rotation_euler=(math.radians(24),math.radians(-20),math.radians(15))
bpy.ops.object.camera_add(location=(-90,-96,100))
camera=bpy.context.object;scene.camera=camera
def render(name,loc,target,lens):
    camera.location=loc;camera.data.lens=lens
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str((OUT/name).resolve())
    bpy.ops.render.render(write_still=True)
render("V27_aerial_Blender.png",(-90,-96,100),(0,0,3),40)
render("V27_entry_Blender.png",(20,55,29),(0,0,3),43)
blend=OUT/"V27_Editable_GSI_Hypothetical_Width.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
glb=OUT/"V27_GSI_Hypothetical_Width_Only.glb"
bpy.ops.export_scene.gltf(filepath=str(glb.resolve()),export_format="GLB",
 export_apply=True,export_animations=False,export_lights=False,export_cameras=False)
report={"status":"RESEARCH_ONLY_NO_REAL_WIDTH_OR_NAVMESH",
 "source_osm_sha256":d["osm_source_sha256"],
 "source_gsi_derived_cm_sha256":hashlib.sha256(raw).hexdigest(),
 "samples":3366,"real_road_width_m":None,"hypothetical_strip_width_m":1.8,
 "source_way_m":round(dist,4),
 "no_collision_or_real_bicycle_rig_checked":True,
 "rendered_files":["V27_aerial_Blender.png","V27_entry_Blender.png"],
 "artifacts":{}}
for path in [blend,glb,*[OUT/f for f in report["rendered_files"]]]:
    report["artifacts"][path.name]={"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size}
(OUT/"V27_Blender_Report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("V27 Blender exported source-derived study terrain; NOT a road or physics test.")
