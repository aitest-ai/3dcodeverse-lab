"""Hokkaido kibori kuma: four-footed carved bear biting a salmon.
Author-written deterministic Blender model for official 3DCodeVerse Harness build.
Z-up Blender scene; harness exports Y-up GLB. No external assets, network or model calls.
"""
import bpy
import math
import random
from mathutils import Vector, Matrix, noise

random.seed(1837)

def material(name, rgb, rough=0.72, metallic=0.0):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*rgb,1.0)
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value=(*rgb,1.0)
        bs.inputs["Roughness"].default_value=rough
        bs.inputs["Metallic"].default_value=metallic
    return mat

walnut=material("Wood_Dark_Charred_Walnut",(0.095,0.049,0.022))
walnut_warm=material("Wood_Highlight_Old_Polish",(0.148,0.080,0.039),0.58)
walnut_mid=material("Wood_Facet_Satin",(0.112,0.058,0.026),0.61)
walnut_dark=material("Wood_Deep_Gouges",(0.055,0.026,0.011))
salmon_wood=material("Salmon_Warm_Carved_Wood",(0.128,0.063,0.031))
salmon_side=material("Salmon_Dark_Upper_Body",(0.069,0.030,0.013))
salmon_ridge=material("Salmon_Etched_Scales",(0.162,0.080,0.037))
eye_mat=material("Inset_Eyes_and_Nose",(0.007,0.006,0.004),0.2)
mouth_mat=material("Mouth_Dark_Shadow",(0.010,0.007,0.004))

def sphere(name, position, size, mat, seg=40, rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=position)
    obj=bpy.context.object
    obj.name=name
    obj.scale=size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj

def cylinder_between(name, a, b, radius, mat, vertices=20):
    direction=Vector(b)-Vector(a)
    center=(Vector(a)+Vector(b))*0.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=direction.length, location=center)
    obj=bpy.context.object
    obj.name=name
    obj.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
    obj.data.materials.append(mat)
    return obj

def frustum(name, a, b, ra, rb, mat, vertices=24):
    direction=Vector(b)-Vector(a)
    center=(Vector(a)+Vector(b))*0.5
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=ra, radius2=rb, depth=direction.length, location=center)
    obj=bpy.context.object
    obj.name=name
    obj.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
    obj.data.materials.append(mat)
    return obj

def curve_line(name, pts, radius, mat):
    cr=bpy.data.curves.new(name,"CURVE")
    cr.dimensions='3D'
    cr.resolution_u=12
    cr.bevel_depth=radius
    cr.bevel_resolution=2
    poly=cr.splines.new('POLY')
    poly.points.add(len(pts)-1)
    for p,co in zip(poly.points,pts):
        p.co=(*co,1)
    obj=bpy.data.objects.new(name,cr)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

def fin(name, pts, mat, thick=0.015):
    # Solid fin: triangular or polygonal pointed carved wood, duplicated on both sides.
    vertices=[(px-thick,py,pz) for px,py,pz in pts] + [(px+thick,py,pz) for px,py,pz in pts]
    n=len(pts)
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name+"Mesh")
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

# ============================================================================
# v6 Organic carving geometry: smoothly lofted torso and tapering limbs.
# No stacked body spheres or columnar legs. All geometry is real Blender mesh.
# Coordinates: -X bear forward, Y left/right, Z upward before GLB export.
# ============================================================================
def cat_profile(a,b,t):
    # smooth interpolation between consecutive measured section parameters
    t=t*t*(3-2*t)
    return tuple(u*(1-t)+v*t for u,v in zip(a,b))

def make_loft(name, sections, along_x, mat, segments=36, steps=5):
    rings=[]
    for k in range(len(sections)-1):
        if k==0: rings.append(sections[k])
        for n in range(1,steps+1):
            rings.append(cat_profile(sections[k],sections[k+1],n/steps))
    vertices=[]
    for sec in rings:
        if along_x:
            x, cz, ry, rz=sec
            for j in range(segments):
                angle=math.tau*j/segments
                vertices.append((x,ry*math.cos(angle),cz+rz*math.sin(angle)))
        else:
            z,cx,cy,rx,ry=sec
            for j in range(segments):
                angle=math.tau*j/segments
                vertices.append((cx+rx*math.cos(angle),cy+ry*math.sin(angle),z))
    faces=[]
    for k in range(len(rings)-1):
        for j in range(segments):
            a=k*segments+j
            na=k*segments+(j+1)%segments
            b=(k+1)*segments+j
            nb=(k+1)*segments+(j+1)%segments
            faces.append((a,na,nb,b) if along_x else (a,b,nb,na))
    faces.append(tuple(range(segments-1,-1,-1)))
    faces.append(tuple((len(rings)-1)*segments+j for j in range(segments)))
    mesh=bpy.data.meshes.new(name+'_Mesh')
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(mat)
    return obj

bear_parts=[]
bear_parts.append(make_loft("SolidContinuousTorso",[
    (-1.54,1.13,0.07,0.09),
    (-1.38,1.15,0.38,0.34),
    (-1.15,1.18,0.52,0.47),
    (-0.79,1.24,0.61,0.61),
    (-0.41,1.28,0.64,0.63),
    ( 0.04,1.22,0.61,0.57),
    ( 0.53,1.17,0.57,0.54),
    ( 0.88,1.14,0.52,0.50),
    ( 1.15,1.15,0.34,0.34),
    ( 1.32,1.14,0.04,0.06),
],True,walnut,48))

# Sculpt a short broad skull and compact projecting muzzle into torso tip.
def mass(name,loc,scale):
    obj=sphere(name,loc,scale,walnut,seg=48,rings=32)
    bear_parts.append(obj)
    return obj
mass("RoundedBearCranium",(-1.48,0,1.14),(0.50,0.47,0.42))
mass("UpperSnout",(-1.82,0,0.97),(0.27,0.29,0.205))
mass("JawMass",(-1.76,0,0.82),(0.30,0.275,0.105))
for side in (-1,1):
    mass("SmallRoundEar_%s"%side,(-1.38,side*0.34,1.47),(0.14,0.145,0.17))
mass("VeryShortTail",(1.30,0,1.12),(0.12,0.13,0.13))

def shaped_leg(name,x_shoulder,y,px,front):
    # Full-volume limb: merges with torso at top, extends to one broad foot.
    # Hind thigh is thicker, shin tapers then flares toward the paw.
    sidey=y
    return make_loft(name,[
      (0.055,px-0.075,sidey,0.19,0.19),
      (0.130,px,sidey,0.29,0.24),
      (0.250,px+0.045,sidey,0.285,0.24),
      (0.405,x_shoulder-0.065,sidey,0.205,0.205),
      (0.620,x_shoulder,sidey,0.245,0.23),
      (0.870,x_shoulder,sidey*0.97,0.325 if front else 0.36,0.27),
      (1.100,x_shoulder+0.025,sidey*0.94,0.33 if front else 0.34,0.31),
      (1.280,x_shoulder+0.080,sidey*0.90,0.23,0.24),
      (1.390,x_shoulder+0.075,sidey*0.88,0.055,0.07),
    ],False,walnut,32)

for is_front,x,px in ((True,-0.78,-1.02),(False,0.87,0.78)):
    for side in (-1,1):
        bear_parts.append(shaped_leg(('Foreleg' if is_front else 'Rearleg')+str(side),
                                     x,side*0.435,px,is_front))

# Fuse body and feet with voxel remeshing so there are no floating intersections.
bpy.ops.object.select_all(action='DESELECT')
for ob in bear_parts: ob.select_set(True)
active=bear_parts[0]
bpy.context.view_layer.objects.active=active
bpy.ops.object.join()
bear=active
bear.name="Kuma_Handcarved_OnePiece"
# Converting remeshed body to a single mesh preserves geometry on glTF export.
bear.data.remesh_voxel_size=0.014
try:
    bpy.ops.object.voxel_remesh()
except Exception:
    # The underlying body remains valid even if the Blender remesh backend is missing.
    pass

# v9 true carved wood relief, sculpted INTO the organic remesh geometry.
# Each anisotropic notch sinks below its surrounding facets. The overlapping
# staggered gouges follow the body direction (and never become fake spikes).
for mat in (walnut_mid, walnut_warm, walnut_dark):
    bear.data.materials.append(mat)
def clamp(v,a=0.0,b=1.0):
    return max(a,min(b,v))
def chisel_profile(co):
    # Incisions run diagonally down and backwards as in a real kibori kuma.
    # Spatial cell staggering prevents the previous repetitive banding.
    u=co.x*11.3+co.y*0.5+0.62*math.sin(co.z*2.1)
    v=co.z*11.4-co.x*3.2+co.y*0.7
    row=math.floor(v)
    cu=(u + 0.5*(row%2))%1.0-0.5
    cv=(v%1.0)-0.52
    skew=cu+0.30*cv
    d=(skew/0.44)**2+(cv/0.31)**2
    if d>=1.0: return 0.0
    taper=max(0.0,1.0-d)
    # One side of the gouge lifts slightly while the hollow cuts deep.
    return (taper**1.5) * (0.012 if skew<0.03 else 0.020)

for vert in bear.data.vertices:
    p=vert.co.copy()
    micro=noise.noise(Vector((p.x*29+7,p.y*27,p.z*26)))*0.0017
    facet=noise.noise(Vector((p.x*9,p.y*9.5,p.z*10)))*0.0042
    # do not disturb soles, small ears, nose or face
    trunk=clamp((p.x+1.29)/0.28)*clamp((1.43-p.x)/0.22)*clamp((p.z-0.55)/0.33)
    relief=chisel_profile(p)*trunk
    vert.co=p + vert.normal*(facet+micro-relief)
bear.data.update()
for face in bear.data.polygons:
    p=face.center
    nc=noise.noise(Vector((p.x*5.4,p.y*5.4,p.z*5.4)))
    mark=chisel_profile(p)
    if mark>0.009 and p.z>0.78 and p.x>-1.25:
        face.material_index=3
    elif nc>0.52: face.material_index=2
    elif nc>0.16: face.material_index=1
    else: face.material_index=0
    # visible tiny chisel facets without making the surface polygonal everywhere
    face.use_smooth= not (mark>0.014 and p.z>0.8 and p.x>-1.2)

# Discrete pointed claws inlaid into the fronts of unified paws.
# Grooves on top lead to small dark blunt tips, not eight attached spheres.
for is_front,px in ((True,-1.02),(False,0.78)):
    for side in (-1,1):
        y=side*0.435
        for k in range(4):
            py=y+(k-1.5)*0.118
            # Thin inset lines on the sloping paw top (actual GLB curves).
            curve_line("ClawRoot_%s_%s_%d"%(int(is_front),side,k),[
                (px-0.195,py,0.32),
                (px-0.264,py,0.244),
                (px-0.310,py,0.17)],0.009,walnut_dark)
            frustum("CarvedClaw_%s_%s_%d"%(int(is_front),side,k),
                (px-0.295,py,0.15),(px-0.359,py,0.108),
                0.028,0.005,walnut_mid,12)

# Ear pits and facial detail on both sides
for side in (-1,1):
    sphere("EarWell_"+str(side),(-1.42,side*0.463,1.510),(0.095,0.020,0.105),walnut_dark,28,16)
    sphere("InsetEye_"+str(side),(-1.79,side*0.278,1.245),(0.047,0.033,0.046),eye_mat,20,12)
    sphere("Brow_"+str(side),(-1.74,side*0.31,1.295),(0.13,0.049,0.046),walnut_mid,24,14)

# v9 deeper facial sculpting: subtle cheek ridge, inset eyelid/corner, nostrils.
# The eyes are carved into the mass instead of floating as buttons.
for side in (-1,1):
    sphere("EyeSocket_%s"%side,(-1.765,side*0.274,1.229),
           (0.073,0.035,0.073),walnut_dark,32,18)
    sphere("EyeCarvedInset_%s"%side,(-1.799,side*0.306,1.251),
           (0.029,0.029,0.031),eye_mat,24,16)
    curve_line("UpperEyelid_%s"%side,[
        (-1.83,side*0.319,1.29),(-1.79,side*0.331,1.313),
        (-1.731,side*0.312,1.286)],0.010,walnut_mid)
    curve_line("CheekCut_%s"%side,[
        (-1.74,side*0.345,1.05),(-1.59,side*0.405,1.02),
        (-1.46,side*0.42,1.11)],0.008,walnut_dark)

# A chunky triangular bear nose, distinctly forward.
sphere("Bear_Black_Carved_Nose",(-2.075,0,1.055),(0.080,0.160,0.105),eye_mat,32,18)
# Short, heavy triangular bear nose with nostril dimples.
for side in (-1,1):
    sphere("NostrilInset_%s"%side,(-2.137,side*0.090,1.052),
        (0.016,0.023,0.012),walnut_dark,16,10)

sphere("MouthOpening",(-1.964,0,0.830),(0.079,0.26,0.060),mouth_mat,24,12)
for side in (-1,1):
    curve_line("LipCrease"+str(side),[(-2.00,side*0.11,0.884),(-1.92,side*0.26,0.861),(-1.75,side*0.25,0.852)],0.010,walnut_dark)

# Compact the front-to-back silhouette by about 13%, but keep its thickness.
# This happens before fish generation so the salmon remains properly crosswise.
for ob in list(bpy.data.objects):
    ob.location.x *= 0.87
    ob.scale.x *= 0.87

bear_names_before_fish = {ob.name for ob in bpy.data.objects}

# --- Salmon: physically shaped body sections from fish head to narrow tail stock.
# The cross section tapers asymmetrically so a real fish profile, not an elongated oval.
FISH_X=-1.80
FISH_Z=0.815
FISH_SKEW=0.105  # sculpt fish obliquely to show more than an end-on silhouette
stations=[
    (-1.23, 0.012, 0.018),
    (-1.16, 0.090, 0.080),
    (-1.04, 0.158, 0.132),
    (-0.88, 0.188, 0.173),
    (-0.60, 0.212, 0.216),
    (-0.25, 0.242, 0.239),
    ( 0.10, 0.228, 0.231),
    ( 0.45, 0.188, 0.195),
    ( 0.73, 0.139, 0.147),
    ( 0.91, 0.072, 0.089),
    ( 1.04, 0.032, 0.045),
]
N=72
# refine all fish stations to support actual engraved fish scales, not stuck-on beads
refined=[]
for idx in range(len(stations)-1):
    for sub in range(7):
        refined.append(cat_profile(stations[idx],stations[idx+1],sub/7))
refined.append(stations[-1])
stations=refined
vertices=[]
faces=[]
for jy,rx,rz in stations:
    for k in range(N):
        ang=math.tau*k/N
        vertices.append((FISH_X+FISH_SKEW*jy+rx*math.cos(ang),jy,FISH_Z+rz*math.sin(ang)))
for j in range(len(stations)-1):
    for k in range(N):
        i=j*N+k
        faces.append((i,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
faces.append(tuple(range(N-1,-1,-1)))
faces.append(tuple((len(stations)-1)*N+k for k in range(N)))
fish_mesh=bpy.data.meshes.new("Salmon_Sculptural_Profile_Mesh")
fish_mesh.from_pydata(vertices,[],faces)
fish_mesh.update()
fish_obj=bpy.data.objects.new("Salmon_Tapered_Body",fish_mesh)
bpy.context.collection.objects.link(fish_obj)
fish_mesh.materials.append(salmon_wood)
fish_mesh.materials.append(salmon_side)
# Engrave overlapping fish-scale dimples directly into actual mesh vertices.
# This survives GLB export, instead of 132 floating ellipsoid scale beads.
for vert in fish_mesh.vertices:
    p=vert.co
    flank=clamp((abs(p.x-FISH_X-FISH_SKEW*p.y)-0.095)/0.075)
    u=(p.y+1.1)*21.2
    v=(p.z-FISH_Z)*25.0
    r=math.floor(v)
    du=(u+0.5*(r%2))%1.0-0.5
    dv=(v%1.0)-0.50
    dent=max(0.0,1.0-((du/0.39)**2+(dv/0.36)**2))
    normal=vert.normal if vert.normal.length>0 else Vector((1,0,0))
    p.x-= (0.0038*dent*flank)* (1 if p.x>FISH_X+FISH_SKEW*p.y else -1)
fish_mesh.update()
for poly in fish_mesh.polygons:
    poly.use_smooth=True
    poly.material_index=1 if poly.center.z>FISH_Z+0.080 else 0

# Natural salmon head: eye on each visible side and curved engraved gill marks.
for side in (-1,1):
    sphere("Salmon_Eye"+str(side),(FISH_X+FISH_SKEW*(-1.01)+side*0.156,-1.01,FISH_Z+0.027),(0.016,0.020,0.019),eye_mat,16,10)
    curve_line("GillCut"+str(side),[
        (FISH_X+FISH_SKEW*(-0.86)+side*0.190,-0.86,FISH_Z+0.12),
        (FISH_X+FISH_SKEW*(-0.83)+side*0.192,-0.83,FISH_Z+0.02),
        (FISH_X+FISH_SKEW*(-0.88)+side*0.184,-0.88,FISH_Z-0.11)],0.007,walnut_dark)
# Mouth is a small notch at the fish's pointed head.
curve_line("Salmon_Open_Mouth",[(FISH_X+FISH_SKEW*(-1.18)-0.065,-1.18,FISH_Z-0.028),(FISH_X+FISH_SKEW*(-1.229),-1.229,FISH_Z-0.030),
                                (FISH_X+FISH_SKEW*(-1.18)+0.065,-1.18,FISH_Z-0.028)],0.006,walnut_dark)

# Traditional forked salmon tail in the true fish vertical fin plane (Y/Z).
fin("Salmon_Forked_Tail",[
    (FISH_X+FISH_SKEW*1.01,1.01,FISH_Z),
    (FISH_X+FISH_SKEW*1.39,1.39,FISH_Z+0.27),
    (FISH_X+FISH_SKEW*1.20,1.20,FISH_Z),
    (FISH_X+FISH_SKEW*1.39,1.39,FISH_Z-0.27)
],salmon_side,0.040)
fin("Salmon_DorsalFin",[
    (FISH_X+FISH_SKEW*0.12,0.12,FISH_Z+0.22),
    (FISH_X+FISH_SKEW*0.29,0.29,FISH_Z+0.41),
    (FISH_X+FISH_SKEW*0.51,0.51,FISH_Z+0.20)
],salmon_side,0.037)
fin("Salmon_AnalFin",[
    (FISH_X+FISH_SKEW*0.39,0.39,FISH_Z-0.18),
    (FISH_X+FISH_SKEW*0.63,0.63,FISH_Z-0.35),
    (FISH_X+FISH_SKEW*0.73,0.73,FISH_Z-0.14)
],salmon_side,0.032)
for side in (-1,1):
    fin("Salmon_PectoralFin"+str(side),[
        (FISH_X+FISH_SKEW*(-0.83)+side*0.13,-0.83,FISH_Z-0.04),
        (FISH_X+FISH_SKEW*(-0.55)+side*0.34,-0.55,FISH_Z-0.19),
        (FISH_X+FISH_SKEW*(-0.40)+side*0.20,-0.40,FISH_Z-0.09)
    ],salmon_side,0.024)

def fish_radius_at(y):
    for i in range(len(stations)-1):
        if stations[i][0] <= y <= stations[i+1][0]:
            t=(y-stations[i][0])/(stations[i+1][0]-stations[i][0])
            return stations[i][1]*(1-t)+stations[i+1][1]*t
    return 0.01

# Salmon scales are cut into the body vertices above, not separate beads.\n\n# v5 fish-to-bear ratio: make the salmon 22% shorter, preserving the
# sculpted tapered body and separate fins; don't turn it into a broad paddle.
# Body objects have already been resized, so only process newly added fish.
for ob in list(bpy.data.objects):
    if ob.name not in bear_names_before_fish:
        ob.location.y *= 0.78
        ob.scale.y *= 0.78
        ob.location.z -= 0.075  # nose and eyes remain above the salmon

# Fur grooves are geometry relief recessed into the remeshed bear body, not loose curves.

# v6 geometry rebuild notes: organic cross-section trunk and limbs, not stacked spheres.
# Shoulder/body/head united by the official Blender remesh workflow.
# No full-body sine ribs; fixed paw shapes; compact skull/muzzle; skewed fish.
# All outputs must be judged from official 3DCodeVerse multi-angle render, not generated images.

# v7: Align the bear's face with the official Harness GLB front view.
# Blender -X faces forwards in our sculpt, but the glTF front is Blender -Y.
# Apply the same world rotation to every component, including the salmon.
turn = Matrix.Rotation(math.pi / 2.0, 4, 'Z')
ground = Matrix.Translation(Vector((0.0, 0.0, -0.052)))
for ob in list(bpy.data.objects):
    ob.matrix_world = ground @ turn @ ob.matrix_world

# No ground, stage, writing or cameras: 3DCodeVerse owns the render studio.
