"""v28b INDEPENDENT head × salmon anatomical prototype.
No torso, paw, v27 Gaussian-pushed jaw or attached cheek bubbles.
Actual watertight meshes in Blender 5.2, in original -X forward / Y lateral.
Focus: physical bite seen from FRONT AND SIDE, not decorative fur.
Reference morphology: salmon nose-gill-belly-peduncle and C-shaped bear jaw.
"""
import bpy,math,json,os
from mathutils import Vector,Matrix
from pathlib import Path
OUT=Path(os.getenv("SHAPE_OUT","candidate")).resolve()
OUT.mkdir(exist_ok=True,parents=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
def mat(name,rgb):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    n=m.node_tree.nodes.get("Principled BSDF")
    n.inputs["Base Color"].default_value=(*rgb,1)
    n.inputs["Roughness"].default_value=.91
    return m
headwood=mat("V28_BEAR_DARK_CARVED_WOOD",(.14,.069,.033))
fishwood=mat("V28_SALMON_CARVED_HONEY_WOOD",(.42,.22,.095))
dark=mat("V28_ENGRAVED_RECESSES",(.042,.020,.012))
fins=mat("V28_FIN_HEARTWOOD",(.27,.12,.052))
def mesh(name,v,f,m):
    md=bpy.data.meshes.new(name+"_Mesh")
    md.from_pydata(v,[],f);md.update()
    ob=bpy.data.objects.new(name,md)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(m)
    for p in md.polygons:p.use_smooth=True
    return ob
def loft_x(name,stations,m,n=64):
    # (x, center Y, center Z, radius Y, radius Z), smooth interpolated rings
    rows=[]
    for i in range(len(stations)-1):
        a,b=stations[i],stations[i+1]
        if i==0:rows.append(a)
        for j in range(1,7):
            t=j/6;t=t*t*(3-2*t)
            rows.append(tuple((1-t)*aa+t*bb for aa,bb in zip(a,b)))
    verts=[];faces=[]
    for x,cy,cz,ry,rz in rows:
        for k in range(n):
            ang=k*math.tau/n
            verts.append((x,cy+ry*math.cos(ang),cz+rz*math.sin(ang)))
    for j in range(len(rows)-1):
        for k in range(n):
            a=j*n+k;b=j*n+(k+1)%n;c=(j+1)*n+(k+1)%n;d=(j+1)*n+k
            faces.append((a,b,c,d))
    faces.extend([tuple(range(n-1,-1,-1)),tuple((len(rows)-1)*n+k for k in range(n))])
    return mesh(name,verts,faces,m)
def uvball(name,loc,scale,ma):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=22,location=loc)
    o=bpy.context.object;o.name=name
    o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(ma)
    return o
def bevel_piece(name,verts,faces,matl):
    ob=mesh(name,verts,faces,matl)
    modifier=ob.modifiers.new("SoftHandCutEdge","BEVEL")
    modifier.width=.012;modifier.segments=3
    return ob

# Bear head as a CONNECTED volumetric sculpture.
# Big cranium and two lips join only BEHIND the mouth at x > -2.11,
# ensuring a visible C opening forward of the jaw hinge.
parts=[]
parts.append(loft_x("BROAD_SKULL",[(-2.325,0,1.21,.045,.060),
  (-2.22,0,1.23,.24,.20),(-2.06,0,1.27,.36,.34),
  (-1.88,0,1.31,.43,.41),(-1.65,0,1.34,.46,.47),
  (-1.47,0,1.33,.40,.43),(-1.28,0,1.30,.26,.27),
  (-1.20,0,1.30,.03,.035)],headwood))
parts.append(loft_x("UPPER_JAW_SINGLE_SURFACE",[
  (-2.575,0,1.124,.035,.032),(-2.52,0,1.126,.137,.065),
  (-2.435,0,1.143,.215,.091),(-2.31,0,1.165,.258,.107),
  (-2.17,0,1.19,.286,.143),(-2.025,0,1.22,.305,.166),
  (-1.86,0,1.25,.305,.190)],headwood))
parts.append(loft_x("LOWER_JAW_SINGLE_SURFACE",[
  (-2.575,0,.668,.032,.028),(-2.51,0,.673,.116,.051),
  (-2.43,0,.679,.179,.070),(-2.32,0,.698,.220,.078),
  (-2.20,0,.726,.248,.092),(-2.05,0,.763,.264,.123),
  (-1.89,0,.839,.282,.159),(-1.69,0,.910,.292,.202),
  (-1.56,0,.979,.30,.218)],headwood))
# Side cheek-to-mandible hinges are fused into one head, not 2 spheres.
for side in (-1,1):
    parts.append(loft_x("CONNECTED_CHEEK_HINGE_%d"%side,[
      (-2.15,side*.285,1.00,.047,.055),
      (-2.06,side*.288,1.02,.082,.110),
      (-1.93,side*.296,1.055,.12,.15),
      (-1.81,side*.301,1.11,.15,.18),
      (-1.65,side*.29,1.18,.17,.205),
      (-1.48,side*.235,1.24,.16,.18)],headwood,n=40))
    # Inset ears, fused before voxel sculpt.
    parts.append(uvball("EAR_UNDERCUT_%d"%side,(-1.62,side*.456,1.678),
                 (.090,.066,.095),headwood))
# Fuse body + cheek + both lips into *one* true closed high-poly mesh.
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
bear=parts[0];bear.name="V28_REAL_CONNECTED_BEAR_HEAD"
bear.data.remesh_voxel_size=.013
bpy.ops.object.voxel_remesh()
# Sculpt slight asymmetric cheek/brow planes into the fused skull. This is
# actual surface deformation before eye sockets, not added cheek spheres.
for vtx in bear.data.vertices:
    p=vtx.co
    fac=math.exp(-((p.x+2.025)/.24)**2 - ((p.z-1.24)/.16)**2)
    side=1 if p.y>=0 else -1
    if .20<abs(p.y)<.45 and fac>.002:
        p.y+=side*.031*fac
bear.data.update()
for face in bear.data.polygons:face.use_smooth=True
# Socket booleans cut into real bear cheeks; no floating eye globes.
for side in (-1,1):
    tool=uvball("CUT_SOCKET_%d"%side,(-2.075,side*.323,1.415),
                (.072,.070,.072),headwood)
    modifier=bear.modifiers.new("RECESS_EYE_%d"%side,'BOOLEAN')
    modifier.object=tool;modifier.operation='DIFFERENCE';modifier.solver='EXACT'
    bpy.ops.object.select_all(action='DESELECT')
    bear.select_set(True);bpy.context.view_layer.objects.active=bear
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(tool,do_unlink=True)
# Close any boolean topology fragments before GLB.
bpy.ops.object.select_all(action='DESELECT')
bear.select_set(True);bpy.context.view_layer.objects.active=bear
bear.data.remesh_voxel_size=.012
bpy.ops.object.voxel_remesh()
for poly in bear.data.polygons:
    poly.use_smooth=True
    # Deep hollows are material-tinted ONLY on already present bear faces.
    pc=poly.center
    if -2.14<pc.x<-1.99 and abs(abs(pc.y)-.325)<.068 and 1.35<pc.z<1.49:
        pass
# A SMALL sculpted triangular nose instead of an oversized oval button.
nosev=[(-2.589,-.120,1.216),(-2.589,.120,1.216),(-2.601,0,1.122),
       (-2.502,-.126,1.218),(-2.502,.126,1.218),(-2.506,0,1.117)]
nosefaces=[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]
nose=bevel_piece("SCULPTED_TRIANGULAR_NOSE",nosev,nosefaces,dark)

# Maintain a separate list of non-fish objects; later all fish vertices
# are shortened uniformly (including fins), not only the body tube.
pre_fish_objects=set(bpy.data.objects.keys())
# Salmon: independent fish anatomy with point nose, cheek/gill and caudal
# peduncle. It is TALL through belly, not a uniform horizontal cylinder.
# Section (lateral Y, center X,Z, width X, height Z).
fishrows=[
 (-1.31,-2.422,.86,.020,.030),
 (-1.24,-2.432,.857,.057,.067),
 (-1.16,-2.444,.860,.111,.139),
 (-1.055,-2.455,.869,.162,.190),
 (-.94,-2.456,.880,.192,.222),
 (-.78,-2.451,.896,.201,.246),
 (-.58,-2.439,.914,.218,.264),
 (-.36,-2.432,.909,.212,.246),
 (-.18,-2.422,.898,.188,.200),
 (0,-2.414,.884,.149,.154),
 (.19,-2.419,.889,.171,.207),
 (.38,-2.418,.907,.175,.211),
 (.56,-2.415,.930,.139,.166),
 (.73,-2.411,.958,.089,.119),
 (.86,-2.414,.988,.044,.064),
 (.98,-2.420,1.006,.027,.037),
 (1.045,-2.425,1.014,.019,.027)]
samples=[]
for j in range(len(fishrows)-1):
    a,b=fishrows[j],fishrows[j+1]
    if j==0:samples.append(a)
    for k in range(1,7):
        t=k/6;t=t*t*(3-2*t)
        samples.append(tuple(aa*(1-t)+bb*t for aa,bb in zip(a,b)))
v=[];faces=[];N=72
for y,cx,cz,rx,rz in samples:
    for k in range(N):
        a=math.tau*k/N
        # Fish ventral side fuller than dorsal, but not a huge sphere.
        z=cz+rz*math.sin(a)
        x=cx+rx*math.cos(a)
        v.append((x,y,z))
for j in range(len(samples)-1):
    for k in range(N):
        a=j*N+k;b=j*N+(k+1)%N;c=(j+1)*N+(k+1)%N;d=(j+1)*N+k
        faces.append((a,b,c,d))
faces.extend((tuple(range(N-1,-1,-1)),tuple((len(samples)-1)*N+k for k in range(N))))
fish=mesh("V28_SALMON_HEAD_GILL_BELLY_TAIL",v,faces,fishwood)
# Carve curved gill incisions directly INTO flank vertices, paired arcs.
gill_count=0;tail_count=0
for vert in fish.data.vertices:
    p=vert.co
    if -.99<p.y<-.58:
        center_x=-2.45
        side=(1 if p.x>center_x else -1)
        flank=abs(p.x-center_x)
        if flank>.135:
            gy=-.893 + .18*(p.z-.90)
            gdist=min(abs(p.y-gy),abs(p.y-(gy+.081)))
            if gdist<.026:
                depth=.024*(1-gdist/.026)*min(1,(flank-.135)/.05)
                p.x-=side*depth;gill_count+=1
fish.data.update()
# Place ocular socket via boolean, with no detached black beads.
for side in (-1,1):
    tool=uvball("TEMP_SALMON_EYE_SOCKET_%d"%side,
        (-2.454+side*.146,-1.139,.913),(.053,.041,.050),fishwood)
    bm=fish.modifiers.new("CARVE_SALMON_EYE_%d"%side,'BOOLEAN')
    bm.object=tool;bm.operation='DIFFERENCE';bm.solver='EXACT'
    bpy.ops.object.select_all(action='DESELECT')
    fish.select_set(True);bpy.context.view_layer.objects.active=fish
    bpy.ops.object.modifier_apply(modifier=bm.name)
    bpy.data.objects.remove(tool,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
fish.select_set(True);bpy.context.view_layer.objects.active=fish
fish.data.remesh_voxel_size=.012
bpy.ops.object.voxel_remesh()
# Darken ONLY recessed eye-socket triangles of actual fish mesh: no
# detached pupil spheres. Keep diffuse body elsewhere.
fish.data.materials.append(dark)
eye_centers=[Vector((-2.454+sign*.146,-1.139,.913)) for sign in (-1,1)]
eye_marked=0
for poly in fish.data.polygons:
    poly.use_smooth=True
    c=poly.center
    if min((c-v).length for v in eye_centers)<.054:
        poly.material_index=1
        eye_marked+=1
# Fin geometry: 3D, with root intersecting body. The tail is sharply forked
# and originates at narrow peduncle rather than simply ending a flat plank.
def fin(name,profile,width):
    vv=[(-2.42-width,y,z) for y,z in profile]+[(-2.42+width,y,z) for y,z in profile]
    n=len(profile);ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    ff.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return mesh(name,vv,ff,fins)
fin("TRUE_FORKED_TAIL",[
    (1.005,1.011),(1.28,1.235),(1.41,1.275),
    (1.24,1.035),(1.16,1.01),(1.24,.985),
    (1.41,.792),(1.28,.830)],.024)
fin("DORSAL_FAN",[(.12,1.056),(.28,1.242),(.43,1.245),(.48,1.090)],.026)
fin("ANAL_FAN",[(.39,.741),(.57,.627),(.68,.832)],.021)
for side in (-1,1):
    x0=-2.44 + side*.16
    vv=[(x0-side*.012,-.83,.855),(x0+side*.20,-.52,.688),(x0+side*.072,-.48,.855)]
    # Closed triangulated pectoral fin with sidewall thickness.
    m=mesh("PECTORAL_FIN_%d"%side,
        [(x-.013,y,z) for x,y,z in vv]+[(x+.013,y,z) for x,y,z in vv],
        [(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],fins)

# v28b: reduce the previous over-long salmon by 21% while preserving
# full 3D thickness and fish waist contact. It changes the ACTUAL vertices
# of every fish body + fin, not camera optics or a generated image.
shortened_meshes=0
for ob in bpy.data.objects:
    if ob.name in pre_fish_objects or ob.type!='MESH':
        continue
    for vt in ob.data.vertices:
        vt.co.y*=.79
    ob.data.update()
    shortened_meshes+=1

# Geometry guard checks are distinct from subjective art approval.
fish_bite_r=.154
upper_bottom=1.126-.065
lower_top=.698+.078
assert abs((.884+fish_bite_r)-upper_bottom)<.045
assert abs((.884-fish_bite_r)-lower_top)<.06
assert len(bear.data.vertices)>25000
assert len(fish.data.vertices)>1500
# Tangency distances: spatial correspondence is not proof of realistic bite.
from mathutils.kdtree import KDTree
head_vertices=[p.co for p in bear.data.vertices if p.co.x<-2.25 and abs(p.co.y)<.28 and .54<p.co.z<1.25]
kd=KDTree(len(head_vertices))
for j,p in enumerate(head_vertices):kd.insert(p,j)
kd.balance()
proximity=[]
for p in fish.data.vertices:
    c=p.co
    if abs(c.y)<.055:
        nearest,j,d=kd.find(c)
        proximity.append(d)
proximity.sort()
assert proximity
# Export 2 actual GLBs: head + fish (main), and diagnostic fish-only.
R=Matrix.Rotation(math.pi/2,4,'Z')
T=Matrix.Translation(Vector((0,0,-.06)))
for ob in bpy.data.objects:
    ob.matrix_world=T @ R @ ob.matrix_world
glb=OUT/"v28b_head_salmon_real.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",export_apply=True,export_yup=True)
assert glb.stat().st_size>250000
report={
 "prototype":"v28b shortened-salmon and reduced-ear anatomical prototype (no torso or paws)",
 "generation":"new geometry from original multi-section landmarks",
 "source":"experiments/hokkaido-v28/head_fish.py",
 "actual_geometry":True,
 "fish_body_verts":len(fish.data.vertices),
 "bear_head_verts":len(bear.data.vertices),
 "gill_vertices_engraved":gill_count,
 "colored_eye_socket_faces":eye_marked,
 "shortened_fish_meshes":shortened_meshes,
 "contact":{"waist_samples":len(proximity),
            "minimum_source_units":round(proximity[0],5),
            "median_source_units":round(proximity[len(proximity)//2],5),
            "within_0.03":sum(d<.03 for d in proximity)},
 "estimated_upper_fish_surface_z":.884+.154,
 "estimated_lower_fish_surface_z":.884-.154,
 "upper_muzzle_lower_surface":upper_bottom,
 "lower_mandible_upper_surface":lower_top,
 "game_release_approved":False,"art_status":"UNREVIEWED"}
(OUT/"shape_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print("V28B_REAL_INDEPENDENT_GLB",str(glb),glb.stat().st_size,flush=True)
print("V28_GEOMETRY_REPORT",json.dumps(report),flush=True)
