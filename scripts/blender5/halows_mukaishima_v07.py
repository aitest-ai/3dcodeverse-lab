import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path("outputs"); OUT.mkdir(exist_ok=True)
ID="halows-mukaishima-v07"; L=46.798; D=33.309; H=5.55; F=-D/2
TX=8.6; TW=10.4; TD=4.8; TB=7.45; TT=12.4; BZ=F+0.85; EF=F-1.57
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
def mat(n,c,r=.75,m=0):
 x=bpy.data.materials.new(n); x.diffuse_color=c; x.use_nodes=True; b=x.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value=c; b.inputs["Roughness"].default_value=r; b.inputs["Metallic"].default_value=m
 if c[3]<.999: b.inputs["Alpha"].default_value=c[3]; x.surface_render_method="DITHERED"
 return x
W=mat("warm pink",(0.68,.48,.40,1)); W2=mat("tower pink",(.61,.39,.34,1)); C=mat("cream",(.84,.79,.65,1)); G=mat("green",(.035,.19,.15,1),.45,.05); GD=mat("dark green",(.02,.11,.09,1),.4,.08); R=mat("red",(.46,.04,.03,1)); GL=mat("glass",(.05,.16,.17,.48),.22); M=mat("metal",(.55,.58,.56,1),.35,.35); WH=mat("white",(.88,.88,.82,1)); A=mat("asphalt",(.055,.06,.065,1),.95); P=mat("paving",(.54,.30,.20,1),.9); LN=mat("line",(.88,.88,.82,1)); RF=mat("roof",(.27,.29,.29,1),.85); SH=mat("joint",(.38,.24,.21,1))
def cube(n,loc,size,ma,bev=0):
 bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=n; o.scale=(size[0]/2,size[1]/2,size[2]/2); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(ma)
 if bev: q=o.modifiers.new("bevel","BEVEL"); q.width=bev; q.segments=2
 return o
def cyl(n,loc,r,d,ma,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d,location=loc,rotation=rot); o=bpy.context.object; o.name=n; o.data.materials.append(ma); return o
def bar(n,a,b,w,d,ma):
 a,b=Vector(a),Vector(b); v=b-a; o=cube(n,(a+b)/2,(v.length,d,w),ma); o.rotation_euler[1]=-math.atan2(v.z,v.x); return o
cube("A_main",(0,0,H/2),(L,D,H),W,.07); cube("roof",(0,0,H+.04),(L-.45,D-.45,.2),RF)
for y in (-D/2+.16,D/2-.16): cube("parapet",(0,y,H+.18),(L,.3,.5),C)
for x in (-L/2+.16,L/2-.16): cube("parapet_side",(x,0,H+.18),(.3,D-.6,.5),C)
for i,x in enumerate([(-L/2+1.7)+j*((TX-TW/2-1.3)-(-L/2+1.7))/7 for j in range(8)]):
 cube(f"glassW{i}",(x,F-.045,1.52),(2.7,.08,2.55),GL); cube(f"mullion{i}",(x-1.38,F-.09,1.52),(.075,.12,2.75),M)
for i,x in enumerate([TX+TW/2+1.8+j*((L/2-1.8)-(TX+TW/2+1.8))/2 for j in range(3)]): cube(f"glassE{i}",(x,F-.045,1.52),(2.7,.08,2.55),GL)
cube("tower_base",(TX,BZ,TB/2),(TW,TD,TB),W2,.05); cube("tower_sign",(TX,BZ,(TT+TB)/2),(TW,TD,TT-TB),C,.04); cube("tower_trim",(TX,BZ,TB+.08),(TW+.36,TD+.22,.42),M)
for i,x in enumerate([TX-TW/2+.45+j*.55 for j in range(19)]): cube(f"rib{i}",(x,EF-.055,(TT+TB)/2),(.035,.06,TT-TB-.28),SH)
for i,z in enumerate([.45+j*.48 for j in range(15)]): cube(f"joint{i}",(TX,EF-.055,z),(TW-.18,.04,.025),SH)
cube("entrance_recess",(TX,EF-.10,1.50),(4.75,.10,3),GD)
for i,dx in enumerate((-1.08,1.08)): cube(f"door{i}",(TX+dx,EF-.17,1.48),(2.05,.08,2.75),GL)
for i,dx in enumerate((-2.16,0,2.16)): cube(f"doorframe{i}",(TX+dx,EF-.22,1.48),(.08,.10,2.9),M)
curve=bpy.data.curves.new("arch","CURVE"); curve.dimensions="3D"; curve.bevel_depth=.13; curve.bevel_resolution=2; sp=curve.splines.new("POLY"); pts=[(TX+3.35*math.cos(a),EF-.25,4.85+1.65*math.sin(a)) for a in [math.pi-i*math.pi/30 for i in range(31)]]; sp.points.add(len(pts)-1)
for p,co in zip(sp.points,pts): p.co=(*co,1)
o=bpy.data.objects.new("arch",curve); bpy.context.collection.objects.link(o); curve.materials.append(WH)
cy=F-4.25/2+.12; cube("canopy",(0,cy,3.04),(L-1.5,4.25,.15),M); cube("green_fascia",(0,F-4.19,3.28),(L-1.2,.30,.45),GD)
for i,x in enumerate([(-L/2+2.2)+j*((L-4.4)/9) for j in range(10)]): cube(f"col{i}",(x,F-4.03,1.52),(.18,.18,3.04),WH)
cube("customer_apron",(0,F-3.25,.06),(L+1.2,6.5,.12),P); cube("parking",(0,F-20.5,-.045),(L+22,28,.08),A)
for i,x in enumerate([(-L/2-6)+j*((L+12)/14) for j in range(15)]): cube(f"parkline{i}",(x,F-9,.008),(.07,5.5,.018),LN)
for i,x in enumerate([TX-3.5+j*(7/6) for j in range(7)]): cyl(f"bollard{i}",(x,F-5,.41),.075,.82,M)
for i,x in enumerate([(-L/2+3)+j*(15/7) for j in range(8)]):
 cube(f"rackL{i}",(x-.42,F-4.7,.47),(.07,.07,.88),M); cube(f"rackR{i}",(x+.42,F-4.7,.47),(.07,.07,.88),M); cube(f"rackT{i}",(x,F-4.7,.91),(.84,.07,.07),M)
gy=EF-.28
for i,dx in enumerate((-2.7,0,2.7)): cube(f"red{i}",(TX+dx,gy,10.75),(1.25,.11,2.05),R); cyl(f"disc{i}",(TX+dx+.48,gy-.07,10.70),.42,.13,G,rot=(math.pi/2,0,0))
bpy.context.scene["asset_id"]=ID; bpy.context.scene["osm_way_id"]="661155704"; bpy.context.scene["source_note"]="OSM footprint; official Halows photo + Onomichi 2017 plan; heights and facade subdivisions partly estimated"
blend=OUT/f"{ID}.blend"; glb=OUT/f"{ID}.glb"; bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve())); bpy.ops.export_scene.gltf(filepath=str(glb.resolve()),export_format="GLB",export_apply=True,export_animations=False)
sc=bpy.context.scene; sc.render.engine="BLENDER_EEVEE_NEXT"; sc.render.resolution_x=1200; sc.render.resolution_y=800; sc.world.color=(.62,.72,.75)
bpy.ops.object.light_add(type="SUN",location=(-30,-40,60)); bpy.context.object.data.energy=2.2
bpy.ops.object.camera_add(); cam=bpy.context.object; sc.camera=cam
def look(pt): cam.rotation_euler=(Vector(pt)-cam.location).to_track_quat("-Z","Y").to_euler()
imgs=[]
for nm,pos,tgt in [("front_sw",(-48,-58,18),(5,-12,4)),("front",(0,-72,14),(3,-10,4)),("aerial",(-44,-62,55),(0,0,0))]:
 cam.location=pos; look(tgt); cam.data.lens=38; p=OUT/f"{ID}_{nm}.png"; sc.render.filepath=str(p.resolve()); bpy.ops.render.render(write_still=True); imgs.append(p)
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
man={"asset_id":ID,"status":"BLENDER_GENERATED_CANDIDATE_NOT_RUNTIME_INTEGRATED","blender_version":bpy.app.version_string,"files":{},"browser_tested":False,"android_tested":False,"estimated":["heights","canopy projection","door/glazing subdivisions","parking preview"]}
for p in [blend,glb,*imgs]: man["files"][p.name]={"bytes":p.stat().st_size,"sha256":sha(p)}
(OUT/"asset_manifest.json").write_text(json.dumps(man,indent=2)); (OUT/"report.json").write_text(json.dumps({"status":"PASS_BUILD_EXPORT_RENDER_ONLY","limitations":["no full route integration","no surveyed store elevation","no browser or Android test"]},indent=2))
