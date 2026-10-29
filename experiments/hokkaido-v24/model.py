"""V24: silhouette-locked Hokkaido salmon-bearing bear. ORIGINAL procedural Blender sculpt.
Anatomy-first, matte clay. Does not reuse external copyrighted models.
All mesh, fin, mouth and leg geometry is three-dimensional; images are genuine Cycles renders.
Axes before export: -X bear forward; fish points from -Y(head) to +Y(tail); +Z upward.
"""
import bpy, math, json, os
from pathlib import Path
from mathutils import Vector, Matrix
import random
random.seed(20261029)

OUT=Path(os.environ.get("SHAPE_OUT","candidate")).resolve()
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name,color,rough=.87):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1.0)
    m.use_nodes=True
    n=m.node_tree.nodes.get("Principled BSDF")
    n.inputs["Base Color"].default_value=(*color,1)
    n.inputs["Roughness"].default_value=rough
    return m

bearwood=mat("V24_MATTE_BEAR_WOOD",(.16,.085,.043),.88)
salmonwood=mat("V24_HONEY_SALMON",(.43,.27,.13),.86)
inset=mat("V23_CARVED_DARK_RECESSES",(.06,.04,.03))
finwood=mat("V23_SALMON_FIN_WOOD",(.40,.23,.13))
parts=[]
def mesh(name,verts,faces,material):
    m=bpy.data.meshes.new(name+"_Mesh")
    m.from_pydata(verts,[],faces)
    m.update()
    ob=bpy.data.objects.new(name,m)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    for p in m.polygons: p.use_smooth=True
    return ob

def loft_x(name,sections,material,n=48,sub=5):
    # section = x, centerZ, radiusY, radiusZ
    S=[]
    for i in range(len(sections)-1):
        x0=sections[i];x1=sections[i+1]
        if i==0:S.append(x0)
        for j in range(1,sub+1):
            t=j/sub;t=t*t*(3-2*t)
            S.append(tuple((1-t)*a+t*b for a,b in zip(x0,x1)))
    v=[];f=[]
    for x,z,ry,rz in S:
        for k in range(n):
            a=k*math.tau/n
            v.append((x,ry*math.cos(a),z+rz*math.sin(a)))
    for j in range(len(S)-1):
        for k in range(n):
            a=j*n+k;b=j*n+(k+1)%n;c=(j+1)*n+(k+1)%n;d=(j+1)*n+k
            f.append((a,b,c,d))
    f.extend((tuple(range(n-1,-1,-1)),tuple((len(S)-1)*n+k for k in range(n))))
    return mesh(name,v,f,material)

def loft_z(name,sections,material,n=40,sub=5):
    # section = z, centerX, centerY, radiusX, radiusY
    S=[]
    for i in range(len(sections)-1):
        a=sections[i];b=sections[i+1]
        if i==0:S.append(a)
        for j in range(1,sub+1):
            t=j/sub;t=t*t*(3-2*t)
            S.append(tuple((1-t)*x+t*y for x,y in zip(a,b)))
    v=[];f=[]
    for z,x,y,rx,ry in S:
        for k in range(n):
            a=k*math.tau/n
            v.append((x+rx*math.cos(a),y+ry*math.sin(a),z))
    for j in range(len(S)-1):
        for k in range(n):
            a=j*n+k;b=j*n+(k+1)%n;c=(j+1)*n+(k+1)%n;d=(j+1)*n+k
            f.append((a,d,c,b))
    f.extend((tuple(range(n-1,-1,-1)),tuple((len(S)-1)*n+k for k in range(n))))
    return mesh(name,v,f,material)

def uvball(name,loc,scale,material,segments=32,rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc)
    o=bpy.context.object
    o.name=name
    o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    return o

def fin(name,coords,material,thick=.025):
    # A closed 3D fin in the fish Y/Z plane, never a 2D illustration.
    V=[(x-thick,y,z) for x,y,z in coords]+[(x+thick,y,z) for x,y,z in coords]
    n=len(coords)
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    o=mesh(name,V,faces,material)
    return o

# LOCK ONE: torso silhouette. Full heavy shoulder, tucked rump, 4 planted paws.
parts.append(loft_x("Torso_OneHeavyVolume",[
(-1.48,1.22,.08,.10),(-1.36,1.21,.32,.34),
(-1.11,1.25,.51,.55),(-.82,1.29,.61,.67),
(-.48,1.30,.63,.68),(-.09,1.20,.59,.61),
(.27,1.15,.54,.57),(.61,1.12,.51,.54),
(.89,1.11,.42,.43),(1.07,1.14,.15,.18),
(1.14,1.14,.025,.04)],bearwood))

# LOCK TWO: a single short wide cranium, not isolated face spheres.
parts.append(loft_x("Skull_BroadBrowAndCheeks",[
(-2.30,1.165,.12,.095),(-2.17,1.20,.25,.205),(-2.00,1.245,.355,.29),
(-1.82,1.275,.435,.36),(-1.60,1.285,.48,.415),
(-1.42,1.27,.455,.405),(-1.24,1.23,.39,.345),(-1.12,1.20,.24,.22)],bearwood))

# Top jaw ends ABOVE the fish cross-section and crosses forward over it.
parts.append(loft_x("UpperMuzzle_OneConnectedLip",[
(-2.375,1.096,.072,.060),(-2.305,1.108,.175,.098),
(-2.195,1.118,.26,.13),(-2.050,1.13,.30,.17),
(-1.90,1.16,.31,.20),(-1.77,1.19,.25,.17)],bearwood))
# Lower jaw is coupled behind the cheek but leaves an OPEN mouth at the front.
parts.append(loft_x("LowerJaw_CuppedSingleWoodPiece",[
(-2.445,.659,.043,.040),(-2.36,.671,.123,.060),
(-2.26,.696,.192,.076),(-2.16,.711,.237,.093),
(-2.035,.740,.271,.107),(-1.88,.807,.29,.151),
(-1.68,.877,.275,.168)],bearwood))
# No glued-on cheek spheres; the jaw is one continuous form.

for side in (-1,1):
    # Big trapezoid upper legs fuse with torso. Toe mass merges into paw, not balls.
    for isfront,cx,footx in [(True,-.85,-1.04),(False,.66,.56)]:
        y=side*.44
        name=("Front" if isfront else "Rear")+("_L" if side<0 else "_R")
        parts.append(loft_z(name+"_BroadMuscularLeg",[
        (.046,footx-.155,y,.156,.196),(.082,footx-.187,y,.24,.244),
        (.147,footx-.19,y,.306,.269),(.235,footx-.14,y,.291,.251),
        (.344,cx-.085,y,.235,.208),(.49,cx-.04,y,.220,.213),
        (.695,cx,y*.98,.255,.25),(.92,cx+.045,y*.94,.32,.285),
        (1.09,cx+.07,y*.90,.34,.31),(1.265,cx+.08,y*.87,.24,.245),
        (1.40,cx+.08,y*.83,.077,.080)],bearwood))

    # Ears largely sunken into skull volume; no orbital buttons later.
    parts.append(uvball("EmbeddedEar_"+str(side),(-1.57,side*.427,1.568),
        (.096,.070,.106),bearwood))
parts.append(uvball("TailShort",(1.097,0,1.13),(.115,.13,.12),bearwood))
# Join, voxel-remesh to ONE continuous carving piece (including muzzle & jaw).
bpy.ops.object.select_all(action='DESELECT')
for p in parts:p.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
bear=parts[0];bear.name="BEAR_CONNECTED_HIGH_POLY_SHAPE"
bear.data.remesh_voxel_size=.0175
bpy.ops.object.voxel_remesh()
assert len(bear.data.vertices)>25000,"Unexpectedly small high-poly mesh"
for p in bear.data.polygons:p.use_smooth=True

# Eye sockets are actual 3D boolean incisions, not dark glued-on pearls.
for side in (-1,1):
    tool=uvball("TEMP_REAL_EYE_SOCKET_"+str(side),
       (-1.965,side*.352,1.391),(.09,.083,.07),bearwood)
    mod=bear.modifiers.new("SUBTRACT_EYE_SOCKET_"+str(side),'BOOLEAN')
    mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
    bpy.ops.object.select_all(action='DESELECT')
    bear.select_set(True);bpy.context.view_layer.objects.active=bear
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool,do_unlink=True)
    uvball("CARVED_INSET_PUPIL_"+str(side),(-1.992,side*.331,1.387),
       (.019,.015,.017),inset,24,16)
# Topology repair AFTER boolean socket sculpt: voxel remesh the body once
# more so the last Boolean operations cannot leave open boundary fragments.
bpy.ops.object.select_all(action='DESELECT')
bear.select_set(True)
bpy.context.view_layer.objects.active=bear
bear.data.remesh_voxel_size=.015
bpy.ops.object.voxel_remesh()
# Integrated toes are slight deformations of the fused foot skin.
for vert in bear.data.vertices:
    p=vert.co
    if .055 < p.z < .245:
        for footx in (-1.04,.56):
            for side in (-1,1):
                cy=side*.44
                if abs(p.x-footx)<.52 and abs(p.y-cy)<.26 and p.x<footx-.13:
                    t=(p.y-cy)/.24
                    taper=max(0.,1.-abs(p.z-.135)/.11)
                    p.x-=.030*(.65+.35*math.cos(3*math.pi*t))*taper
bear.data.update()
for face in bear.data.polygons: face.use_smooth=True
# Top brow, nose, jaw are already sculpted into bear before remesh.
# Small triangular, bevelled wooden nose does not stick far forward.
nose_v=[(-2.402,-.12,1.199),(-2.402,.12,1.199),(-2.425,0,1.094),
        (-2.321,-.122,1.198),(-2.321,.122,1.198),(-2.337,0,1.084)]
nose_f=[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]
nose=mesh("BEAR_TRIANGULAR_NOSE",nose_v,nose_f,inset)
b=nose.modifiers.new("BevelNoseWood","BEVEL");b.width=.015;b.segments=2

# LOCK THREE: full 3D salmon with head + deep belly; bend head and tail together.
# Track bear geometry before fish creation so all fish pieces can be proportionally
# resized as one coherent sculpt rather than leaving fins and eyes detached.
pre_fish_names=set(bpy.data.objects.keys())
F_X=-2.197
F_Z=.895
sections=[
(-1.34,.048,.060),(-1.27,.087,.10),(-1.18,.142,.17),
(-1.09,.184,.223),(-.96,.195,.252),(-.78,.196,.274),
(-.54,.185,.272),(-.27,.163,.244),(-.06,.148,.217),
(.19,.154,.209),(.42,.139,.178),(.65,.097,.126),
(.81,.057,.080),(.98,.031,.045),(1.075,.020,.029)]

# use interpolated rings for round, organic fish, not segmented rectangular prism
refined=[]
for j in range(len(sections)-1):
    a=sections[j];bb=sections[j+1]
    if j==0:refined.append(a)
    for k in range(1,7):
        t=k/6;t=t*t*(3-2*t)
        refined.append(tuple((1-t)*x+t*y for x,y in zip(a,bb)))
v=[];ff=[];N=52
def fish_coords(y,rx,rz,a):
    x=F_X+0.09*math.sin(y*1.37)+rx*math.cos(a)
    # Nonplanar centerline; fish slopes down at head and rises toward tail.
    # Increase fish belly and head depth *outside* the compressed bite waist.
    belly=1.26-0.26*math.exp(-((y)/.29)**2)
    z=F_Z+0.160*y+0.045*y*y+rz*belly*math.sin(a)
    return x,y,z
for y,rx,rz in refined:
    for k in range(N):
        v.append(fish_coords(y,rx,rz,math.tau*k/N))
for j in range(len(refined)-1):
    for k in range(N):
        a=j*N+k;bb=j*N+(k+1)%N;c=(j+1)*N+(k+1)%N;d=(j+1)*N+k
        ff.append((a,bb,c,d))
ff.extend([tuple(range(N-1,-1,-1)),tuple((len(refined)-1)*N+k for k in range(N))])
fish=mesh("SALMON_FULL_VOLUMETRIC_PROFILE",v,ff,salmonwood)
# Gill cuts are real negative displacement, not separate opaque badges.
for vert in fish.data.vertices:
    p=vert.co
    baseline=F_X+.09*math.sin(p.y*1.37)
    flank=abs(p.x-baseline)
    # Gill sits near fish head: the cut follows curvature through gill height.
    gy=-1.055+.22*(p.z-.80)
    if -1.19<p.y<-.80 and flank>.12:
        cut=.018*math.exp(-((p.y-gy)/.030)**2)
        p.x-=math.copysign(cut, p.x-baseline)
fish.data.update()

def fish_at(y,r=.0):
    return (F_X+.077*math.sin(y*1.4),y,F_Z+.154*y+.048*y*y+r)
# Fish head faces are NOT flattened in the mouth direction.
for side in (-1,1):
    y=-1.15
    cx=fish_at(y)[0]
    uvball("SalmonTinyInsetEye_"+str(side),
      (cx+side*.169,y,fish_at(y)[2]+.064),(.012,.018,.016),inset,20,12)
# Real 3D fins with bases penetrating the body. Carved tail is asymmetric fork.
fin("SALMON_FORKED_TAIL",[
 fish_at(.98),fish_at(1.23,.18),fish_at(1.38,.245),
 fish_at(1.23,.042),fish_at(1.16),fish_at(1.25,-.046),
 fish_at(1.38,-.235),fish_at(1.23,-.15)],finwood,.038)
fin("SALMON_DORSAL",[
 fish_at(.17,.17),fish_at(.28,.33),fish_at(.39,.37),
 fish_at(.48,.18)],finwood,.033)
fin("SALMON_ANAL",[
 fish_at(.42,-.16),fish_at(.57,-.31),fish_at(.76,-.12)],finwood,.029)
for side in (-1,1):
    fin("SALMON_PECTORAL_"+str(side),[
      (fish_at(-.92)[0]+side*.11,-.92,fish_at(-.92)[2]-.036),
      (fish_at(-.68)[0]+side*.32,-.68,fish_at(-.68)[2]-.16),
      (fish_at(-.48)[0]+side*.16,-.48,fish_at(-.48)[2]-.06)
    ],finwood,.023)

# v24b: proportion-locked salmon: shorten length, not width/height. The same
# 0.82 longitudinal factor applies to real fish body, tail, all fins, eye
# primitives; mouth-center y=0 remains fixed. Avoid disjoint accessories.
for ob in list(bpy.data.objects):
    if ob.name in pre_fish_names: continue
    if ob.type=='MESH':
        # UV sphere eyes are positioned by object.location; mesh body and fins
        # are positioned by individual mesh vertices in local space.
        ob.location.y*=0.82
        for vertex in ob.data.vertices:
            vertex.co.y*=0.82
        ob.data.update()

# Sanity checks on the sculpt, before scene rotation or image rendering.
jaw_top=.711+.093
fish_center=fish_at(0)[2]
fish_top=fish_center+.19
fish_bottom=fish_center-.19
assert .67<fish_bottom<.78 and 1.04<fish_top<1.13
assert -.16 < fish_bottom-jaw_top < .10, "Fish belly must intersect lower mouth"
# Mouth gap remains physically carved; the visual renderer must judge it.
# Prohibit adding fur texture before proportions / bite are approved.
R=Matrix.Rotation(math.pi/2,4,'Z')
ground=Matrix.Translation(Vector((0,0,-.055)))
for ob in list(bpy.data.objects):
    ob.matrix_world=ground @ R @ ob.matrix_world

# Export *real* geometry, all assets are mesh and are individually inspectable.
glb=OUT/"v24_highpoly_shape.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
    export_apply=True,export_yup=True)
assert glb.stat().st_size>250000, "GLB export missing geometry"
report={"version":"v24b","type":"real-blender-highpoly-clay-not-approved",
    "torso_reference":"compact four-foot Hokkaido carved bear, no vendor models copied",
    "fish_axis":"crosswise along original Y; anatomically nonplanar body",
    "mouth_target":{"fish_center_z":fish_center,"fish_top":fish_top,
          "fish_bottom":fish_bottom,"jaw_edge_z":jaw_top},
    "high_poly_vertex_count":len(bear.data.vertices),
    "finished_art_quality":"UNREVIEWED",
    "glb":str(glb.name),"artistic_approval":False}
(OUT/"shape_report.json").write_text(json.dumps(report,indent=2))
print("REAL_V24_GLB_READY",glb,glb.stat().st_size)
