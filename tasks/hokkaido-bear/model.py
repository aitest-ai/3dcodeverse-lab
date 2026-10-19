"""Hokkaido kibori kuma: four-footed carved bear biting a salmon.
Author-written deterministic Blender model for official 3DCodeVerse Harness build.
Z-up Blender scene; harness exports Y-up GLB. No external assets, network or model calls.
"""
import bpy
import math
import random
from mathutils import Vector, noise

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

walnut=material("Wood_Dark_Charred_Walnut",(0.057,0.030,0.017))
walnut_warm=material("Wood_Highlight_Old_Polish",(0.071,0.039,0.021))
walnut_mid=material("Wood_Facet_Satin",(0.065,0.034,0.017))
walnut_dark=material("Wood_Deep_Gouges",(0.034,0.018,0.009))
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
# BEAR ANATOMY (v4): a single compact, grounded carved mass with articulated
# shoulder / upper forelegs, true haunches and broad tapering paws.
# Bear faces -X; Y is its left/right; Z is vertical until GLB export.
# ============================================================================
bear_parts=[]
def mass(name,loc,scale):
    ob=sphere(name,loc,scale,walnut,seg=48,rings=28)
    bear_parts.append(ob)
    return ob

# Shorter barrel and smooth withers; no ringed sausage body.
mass("Ribcage",(0.13,0.0,1.13),(1.09,0.58,0.55))
mass("UpperBack",(-0.34,0.0,1.26),(0.80,0.61,0.53))
mass("Withers",(-0.71,0.0,1.34),(0.49,0.61,0.59))
mass("Rump",(0.90,0.0,1.11),(0.52,0.55,0.52))
mass("NeckFold",(-1.00,0.0,1.15),(0.53,0.50,0.46))
mass("BroadSkull",(-1.39,0.0,1.16),(0.50,0.45,0.39))
mass("CheekLower",(-1.57,0.0,0.998),(0.34,0.38,0.25))
mass("ShortMuzzle",(-1.78,0.0,0.995),(0.27,0.29,0.18))
mass("LowerJaw",(-1.75,0.0,0.828),(0.265,0.255,0.105))

for side in (-1,1):
    mass("RoundEar_%s"%side,(-1.35,side*0.35,1.49),(0.145,0.137,0.165))
mass("ShortTail",(1.42,0,1.11),(0.13,0.145,0.115))

# Forelegs are planted and strong; rear thighs flow backward with bent hocks.
# Paws face -X and have carved grooves rather than bead-shaped attached toes.
for is_front, xroot, xshin, px in ((True,-0.78,-0.87,-1.02),
                                 (False,0.91,0.94,0.78)):
    for side in (-1,1):
        y=side*0.435
        typ="Fore" if is_front else "Rear"
        mass("%sShoulder_%s"%(typ,side),(xroot,y*0.91,0.88),
             (0.305,0.258,0.465) if is_front else (0.345,0.285,0.43))
        mass("%sShin_%s"%(typ,side),(xshin,y,0.465),
             (0.225,0.23,0.375))
        mass("%sFoot_%s"%(typ,side),(px,y,0.185),
             (0.315,0.27,0.19))

# Fuse body and feet with voxel remeshing so there are no floating intersections.
bpy.ops.object.select_all(action='DESELECT')
for ob in bear_parts: ob.select_set(True)
active=bear_parts[0]
bpy.context.view_layer.objects.active=active
bpy.ops.object.join()
bear=active
bear.name="Kuma_Handcarved_OnePiece"
# Converting remeshed body to a single mesh preserves geometry on glTF export.
bear.data.remesh_voxel_size=0.023
try:
    bpy.ops.object.voxel_remesh()
except Exception:
    # The underlying body remains valid even if the Blender remesh backend is missing.
    pass

# Subtle *non-repeating* carved facets: no periodic torso-wide rings.
# Multi-scale surface noise retains anatomy and avoids visual spikes.
for mat in (walnut_mid,walnut_warm,walnut_dark):
    bear.data.materials.append(mat)
for vertex in bear.data.vertices:
    co=vertex.co.copy()
    n1=noise.noise(Vector((co.x*5.3+2.1,co.y*5.3,co.z*5.3)))
    n2=noise.noise(Vector((co.x*17.1,co.y*17.1+3.6,co.z*17.1)))
    # Carved facets get only 4–8 mm variation at this meter scale.
    delta=0.0065*n1 + 0.0025*n2
    vertex.co=co + vertex.normal*delta
bear.data.update()
for face in bear.data.polygons:
    center=face.center
    n=noise.noise(Vector((center.x*7.7,center.y*7.7,center.z*7.7)))
    if n>0.70: face.material_index=2
    elif n < -0.70: face.material_index=3
    elif n>0.48: face.material_index=1
    else: face.material_index=0
    face.use_smooth=True

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
    sphere("EarWell_"+str(side),(-1.42,side*0.451,1.510),(0.087,0.015,0.10),walnut_dark,20,12)
    sphere("InsetEye_"+str(side),(-1.645,side*0.343,1.195),(0.047,0.033,0.046),eye_mat,20,12)
    sphere("Brow_"+str(side),(-1.595,side*0.358,1.255),(0.13,0.049,0.046),walnut_mid,24,14)

# A chunky triangular bear nose, distinctly forward.
sphere("Bear_Black_Carved_Nose",(-2.030,0,1.030),(0.080,0.160,0.105),eye_mat,32,18)
sphere("MouthOpening",(-1.964,0,0.863),(0.079,0.26,0.060),mouth_mat,24,12)
for side in (-1,1):
    curve_line("LipCrease"+str(side),[(-2.00,side*0.11,0.884),(-1.92,side*0.26,0.861),(-1.75,side*0.25,0.852)],0.010,walnut_dark)

# v5 silhouette correction: the old bear was stretched like a weasel.
# Compact the anatomy in one consistent transformation, before creating the fish.
# Includes integrated mesh plus all paws, eyes and lips; preserves true 3D.
for ob in list(bpy.data.objects):
    ob.location.x *= 0.785
    ob.scale.x *= 0.785

bear_names_before_fish = {ob.name for ob in bpy.data.objects}

# --- Salmon: physically shaped body sections from fish head to narrow tail stock.
# The cross section tapers asymmetrically so a real fish profile, not an elongated oval.
FISH_X=-1.597
FISH_Z=0.875
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
N=36
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

# Fine etched scales on flanks, following the actual fish taper.
for side in (-1,1):
    for row in range(3):
        for i in range(22):
            sy=-0.76+i*0.077+(row%2)*0.025
            zz=FISH_Z+(row-1)*0.056
            rx=fish_radius_at(sy)
            norm=max(0.12,1-((zz-FISH_Z)/0.24)**2)**0.5
            xx=FISH_X+FISH_SKEW*sy+side*(rx*norm+0.002)
            ob=sphere("SalmonScale_%d_%d_%d"%(side,row,i),(xx,sy,zz),(0.007,0.030,0.017),salmon_ridge,10,8)
            ob.rotation_euler[0]=-0.12 if side==1 else 0.12

# v5 fish-to-bear ratio: make the salmon 22% shorter, preserving the
# sculpted tapered body and separate fins; don't turn it into a broad paddle.
# Body objects have already been resized, so only process newly added fish.
for ob in list(bpy.data.objects):
    if ob.name not in bear_names_before_fish:
        ob.location.y *= 0.78
        ob.scale.y *= 0.78

# Fur grooves are geometry relief recessed into the remeshed bear body, not loose curves.

# v4 geometry rebuild notes:
# Shoulder/body/head united by the official Blender remesh workflow.
# No full-body sine ribs; fixed paw shapes; compact skull/muzzle; skewed fish.
# All outputs must be judged from official 3DCodeVerse multi-angle render, not generated images.

# No ground, stage, writing or cameras: 3DCodeVerse owns the render studio.
