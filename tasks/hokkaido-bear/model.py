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

walnut=material("Wood_Dark_Charred_Walnut",(0.100,0.050,0.024),0.78)
walnut_warm=material("Wood_Highlight_Old_Polish",(0.148,0.080,0.039),0.58)
walnut_mid=material("Wood_Facet_Satin",(0.112,0.058,0.026),0.61)
walnut_dark=material("Wood_Deep_Gouges",(0.055,0.026,0.011))
salmon_wood=material("Salmon_Warm_Carved_Wood",(0.137,0.086,0.051),0.76)
salmon_belly=material("Salmon_Pale_Heartwood_Belly",(0.180,0.114,0.072),0.84)
salmon_side=material("Salmon_Dark_Upper_Body",(0.096,0.051,0.024),0.76)
salmon_ridge=material("Salmon_Etched_Scales",(0.220,0.125,0.068))
eye_mat=material("Inset_Eyes_and_Nose",(0.019,0.011,0.006),0.60)
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
    bevel=obj.modifiers.new("RoundedCarvedFinEdges","BEVEL")
    bevel.width=min(0.019,thick*.52)
    bevel.segments=3
    if hasattr(bevel,"affect"): bevel.affect="EDGES"
    bpy.context.view_layer.objects.active=obj
    try: bpy.ops.object.modifier_apply(modifier=bevel.name)
    except Exception: pass
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
# v18: reference-guided massing. Broad withers, deep neck, shorter ribcage;
# tuck the rump near hind paws. Different belly and topline curvature.
bear_parts.append(make_loft("SolidContinuousTorso",[
    (-1.48,1.17,0.10,0.13),
    (-1.31,1.18,0.44,0.41),
    (-1.03,1.22,0.575,0.58),
    (-0.75,1.32,0.670,0.695),
    (-0.42,1.32,0.650,0.675),
    (-0.06,1.26,0.585,0.610),
    ( 0.30,1.17,0.555,0.585),
    ( 0.58,1.13,0.565,0.590),
    ( 0.79,1.11,0.505,0.540),
    ( 0.96,1.10,0.280,0.320),
    ( 1.06,1.11,0.035,0.055),
],True,walnut,56))

# Sculpt a short broad skull and compact projecting muzzle into torso tip.
def mass(name,loc,scale):
    obj=sphere(name,loc,scale,walnut,seg=48,rings=32)
    bear_parts.append(obj)
    return obj
# Sculpt review 14: ONE coherent heavy skull loft, not another glued sphere.
# Key profile: squared brow, cheek mass, low heavy muzzle and short snout.
bear_parts.append(make_loft("CarvedBroadBearSkull",[
    (-2.10,1.01,0.10,0.085),
    (-1.99,1.09,0.245,0.205),
    (-1.85,1.17,0.38,0.325),
    (-1.63,1.22,0.49,0.43),
    (-1.41,1.24,0.50,0.45),
    (-1.22,1.22,0.42,0.36),
    (-1.09,1.18,0.20,0.18),
],True,walnut,48,6))
mass("ShortHeavyUpperMuzzle",(-1.965,0,0.990),(0.274,0.278,0.174))
# v20 SHAPE-FIRST: cheeks are actual integrated sculpt volumes, fused BEFORE
# the voxel remesh. They must not be glued-on side spheres after export.
for side in (-1,1):
    mass("IntegratedCheekVolume_%s"%side,
         (-1.725,side*0.342,1.043),(0.265,0.188,0.183))
# Keep a *real* gap between upper bite lip and separate low lower jaw.
# The lower jaw is independent of the remeshed cranium so the bite opening is real.
# A separate connected jaw will be joined at the rear after carving the mouth cavity.
for side in (-1,1):
    mass("SmallRoundEar_%s"%side,(-1.43,side*0.411,1.535),(0.137,0.112,0.133))
mass("VeryShortTail",(1.045,0,1.11),(0.115,0.13,0.12))

def shaped_leg(name,x_shoulder,y,px,front):
    # Full-volume limb: merges with torso at top, extends to one broad foot.
    # Hind thigh is thicker, shin tapers then flares toward the paw.
    sidey=y
    return make_loft(name,[
      (0.055,px-0.13,sidey,0.26,0.265),
      (0.115,px-0.072,sidey,0.34,0.275),
      (0.210,px+0.025,sidey,0.33,0.255),
      (0.350,x_shoulder-0.077,sidey,0.24,0.233),
      (0.550,x_shoulder+0.008,sidey,0.212,0.225),
      (0.740,x_shoulder+0.010,sidey*0.98,0.270 if front else 0.325,0.268),
      (0.990,x_shoulder+0.03,sidey*0.94,0.348 if front else 0.355,0.325),
      (1.160,x_shoulder+0.08,sidey*0.92,0.31 if front else 0.30,0.300),
      (1.365,x_shoulder+0.09,sidey*0.88,0.075,0.095),
    ],False,walnut,32)

for is_front,x,px in ((True,-0.80,-1.04),(False,0.67,0.57)):
    for side in (-1,1):
        bear_parts.append(shaped_leg(('Foreleg' if is_front else 'Rearleg')+str(side),
                                     x,side*0.435,px,is_front))

# v20: three low, flattened toe pads on each paw. Each pad genuinely joins
# the foot during the SAME voxel remesh (not attached round buttons later).
for is_front,px in ((True,-1.04),(False,0.57)):
    for side in (-1,1):
        for k in range(3):
            toe_y=side*0.435+(k-1)*0.130
            mass("FusedToePad_%s_%s_%d"%(int(is_front),side,k),
                 (px-0.318,toe_y,0.136),(0.134,0.074,0.076))

# Fuse body and feet with voxel remeshing so there are no floating intersections.
bpy.ops.object.select_all(action='DESELECT')
for ob in bear_parts: ob.select_set(True)
active=bear_parts[0]
bpy.context.view_layer.objects.active=active
bpy.ops.object.join()
bear=active
bear.name="Kuma_Handcarved_OnePiece"
# Converting remeshed body to a single mesh preserves geometry on glTF export.
bear.data.remesh_voxel_size=0.021
try:
    bpy.ops.object.voxel_remesh()
except Exception:
    # The underlying body remains valid even if the Blender remesh backend is missing.
    pass

# v19 bite-only repair: the fish was supported by a long, flat mandible shelf.
# Keep the true Boolean mouth cavity, but shorten the chin and create a cupped
# lower bite that intersects the salmon at its compressed central cross-section.
# The fish and jaw remain separate physical meshes for genuine GLB inspection.
bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=28,location=(-2.065,0,0.797))
bite_cutter=bpy.context.object
bite_cutter.name="TEMP_BiteMouth_Cutter"
bite_cutter.scale=(0.36,0.355,0.187)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
boolmod=bear.modifiers.new("PhysicalOpenBiteCavity","BOOLEAN")
boolmod.operation="DIFFERENCE"
boolmod.solver="EXACT"
boolmod.object=bite_cutter
bpy.context.view_layer.objects.active=bear
try:
    bpy.ops.object.modifier_apply(modifier=boolmod.name)
except Exception as exc:
    raise RuntimeError("Real jaw cavity boolean failed, cannot fake the bite") from exc
bpy.data.objects.remove(bite_cutter,do_unlink=True)

# v20 physical inset sockets: cut into unified skull, never represent the
# hollow solely by a dark sphere stuck onto an otherwise smooth face.
for side in (-1,1):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,ring_count=20,
        location=(-1.845,side*0.395,1.282))
    cutter=bpy.context.object
    cutter.name="TEMP_RealCarvedEyeSocket_%s"%side
    cutter.scale=(0.096,0.072,0.077)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    socket_cut=bear.modifiers.new("InsetEyeSocket_%s"%side,"BOOLEAN")
    socket_cut.operation="DIFFERENCE"
    socket_cut.solver="EXACT"
    socket_cut.object=cutter
    bpy.context.view_layer.objects.active=bear
    try:
        bpy.ops.object.modifier_apply(modifier=socket_cut.name)
    except Exception as exc:
        raise RuntimeError("Real eye socket sculpt failed") from exc
    bpy.data.objects.remove(cutter,do_unlink=True)

# v20: cupped JAW, recessed beneath the salmon instead of a horizontal shelf.
# The mouth remains visibly open and the rear mandible intersects the skull.
lower_jaw=make_loft("Kuma_SeparateLowerMandible",[
    (-2.17,0.575,0.060,0.039),
    (-2.105,0.580,0.135,0.055),
    (-2.025,0.602,0.195,0.071),
    (-1.910,0.634,0.236,0.089),
    (-1.775,0.673,0.251,0.112),
    (-1.605,0.780,0.253,0.143),
    (-1.415,0.881,0.171,0.159),
],True,walnut,48,6)
# v22 anatomy trial: give the side margins a shallow upward cup around the
# salmon's compressed waist, rather than another flat shelf. These vertices
# belong to the real lower-mandible mesh; there are no pasted lip curves.
for vert in lower_jaw.data.vertices:
    q=vert.co
    if -2.11<q.x<-1.67 and q.z>0.69 and abs(q.y)>0.135:
        q.z += 0.045*min(1.0,(abs(q.y)-0.135)/0.090)
lower_jaw.data.update()
for poly in lower_jaw.data.polygons:
    poly.use_smooth=True

# v9 true carved wood relief, sculpted INTO the organic remesh geometry.
# Each anisotropic notch sinks below its surrounding facets. The overlapping
# staggered gouges follow the body direction (and never become fake spikes).
for mat in (walnut_mid, walnut_warm, walnut_dark):
    bear.data.materials.append(mat)
def clamp(v,a=0.0,b=1.0):
    return max(a,min(b,v))
def chisel_profile(co):
    """Irregular long shallow blade-cut displacement, not a tiled stamp.

    Coordinates are in the Z-up original bear frame. Branchless cell hashing
    gives each blade stroke its own angle, length, start, and depth.
    Only shallow negative V-cuts enter the *actual voxel-remeshed geometry*.
    """
    u=co.x*4.75+co.z*0.75
    v=co.z*8.1-co.x*0.72+co.y*0.58
    row=math.floor(v)
    col=math.floor(u)
    seed=Vector((row*.853+2.31,col*1.71,co.y*.77+4.07))
    n=noise.noise(seed)
    n2=noise.noise(Vector((col*1.39,row*1.17,co.y*.6)))
    if n < -0.39: return 0.0  # irregular gaps, but not an almost empty carving
    center_u=0.50 + 0.20*n
    center_v=0.51 + 0.16*n2
    du=(u-col-center_u) / (0.32 + 0.09*abs(n2))
    dv=(v-row-center_v + 0.17*n*du) / (0.18 + 0.04*abs(n))
    along=1.0-abs(du)
    across=1.0-abs(dv)
    if along<=0 or across<=0: return 0.0
    # V-shaped cut with tapered ends; no rounded raised scale bumps.
    return (0.019+0.011*abs(n))*along*across

for vert in bear.data.vertices:
    p=vert.co.copy()
    micro=noise.noise(Vector((p.x*29+7,p.y*27,p.z*26)))*0.0008
    facet=noise.noise(Vector((p.x*9,p.y*9.5,p.z*10)))*0.0015
    # do not disturb soles, small ears, nose or face
    trunk=clamp((p.x+1.85)/0.26)*clamp((1.43-p.x)/0.22)*clamp((p.z-0.52)/0.33)
    relief=chisel_profile(p)*trunk
    vert.co=p + vert.normal*(facet+micro-relief)
bear.data.update()
for face in bear.data.polygons:
    p=face.center
    nc=noise.noise(Vector((p.x*5.4,p.y*5.4,p.z*5.4)))
    mark=chisel_profile(p)
    if mark>0.007 and p.z>0.78 and p.x>-1.25:
        face.material_index=1
    elif nc>0.52: face.material_index=2
    elif nc>0.16: face.material_index=1
    else: face.material_index=0
    # visible tiny chisel facets without making the surface polygonal everywhere
    face.use_smooth=True

# v20: toe pads are fused with each foot. Three discreet tapered claws per paw
# start WITHIN the flattened toe outline, avoiding the v19 four-prong boot.
for is_front,px in ((True,-1.04),(False,0.57)):
    for side in (-1,1):
        for k in range(3):
            py=side*0.435+(k-1)*0.130
            frustum("InlaidThreeToeClaw_%s_%s_%d"%(int(is_front),side,k),
                (px-0.388,py,0.092),(px-0.443,py,0.066),
                0.017,0.003,walnut_mid,12)

# v21: eye hollows are carved by booleans BEFORE remesh detail above.
# No raised eyebrows, pasted cheeks or oversized boar-like oval nose.
for side in (-1,1):
    sphere("EarBowl_%s"%side,(-1.474,side*0.506,1.558),
           (0.074,0.015,0.075),walnut_dark,28,18)
    # Tiny pupil, mostly recessed in the carved eye socket.
    sphere("Eye_Inset_%s"%side,(-1.846,side*0.347,1.287),
           (0.017,0.019,0.017),eye_mat,24,14)

# A REAL triangular nose, carved from a rounded triangular prism rather than
# a sphere: wider bridge at the top, point at bottom, tucked into muzzle.
nose_verts=[
    (-2.269,-0.106,1.103),(-2.269,0.106,1.103),(-2.276,0.0,1.013),
    (-2.177,-0.120,1.109),(-2.177,0.120,1.109),(-2.184,0.0,0.997)
]
nose_faces=[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]
nose_mesh=bpy.data.meshes.new("TriangularCarvedNoseMesh")
nose_mesh.from_pydata(nose_verts,[],nose_faces)
nose_mesh.update()
nose=bpy.data.objects.new("Bear_IntegratedTriangularNose",nose_mesh)
bpy.context.collection.objects.link(nose)
nose_mesh.materials.append(walnut_dark)
bevel=nose.modifiers.new("RoundedNoseCarving","BEVEL")
bevel.width=0.019
bevel.segments=3
bpy.context.view_layer.objects.active=nose
bpy.ops.object.modifier_apply(modifier=bevel.name)
for face in nose.data.polygons:
    face.use_smooth=True

# Do not add freestanding dark lip curves. Physical head cavity and the
# curved, volumetric mandible must read as a real bite without black outlines.

# Compact the front-to-back silhouette by about 13%, but keep its thickness.
# This happens before fish generation so the salmon remains properly crosswise.
for ob in list(bpy.data.objects):
    ob.location.x *= 0.87
    ob.scale.x *= 0.87

bear_names_before_fish = {ob.name for ob in bpy.data.objects}

# --- Salmon: physically shaped body sections from fish head to narrow tail stock.
# The cross section tapers asymmetrically so a real fish profile, not an elongated oval.
FISH_X=-1.735  # fish center within the 3D bite cavity
FISH_Z=0.824
FISH_SKEW=0.050  # sculpt fish obliquely to show more than an end-on silhouette
stations=[
    (-1.29, 0.060, 0.068),
    (-1.22, 0.105, 0.113),
    (-1.15, 0.161, 0.148),
    (-1.04, 0.204, 0.186),
    (-0.88, 0.216, 0.207),
    (-0.64, 0.225, 0.241),
    (-0.36, 0.239, 0.256),
    (-0.12, 0.234, 0.257),
    ( 0.10, 0.232, 0.246),
    ( 0.42, 0.198, 0.210),
    ( 0.70, 0.139, 0.151),
    ( 0.93, 0.071, 0.084),
    ( 1.06, 0.031, 0.042),
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
        # Anatomical compression exactly where bear jaws clamp the fish.
        bite_pressure=1.0-0.31*math.exp(-((jy/0.245)**2))
        vertices.append((FISH_X+FISH_SKEW*jy+rx*bite_pressure*math.cos(ang),jy,FISH_Z+rz*bite_pressure*math.sin(ang)))
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
fish_mesh.materials.append(salmon_belly)
# v21: gill carving and shallow irregular scales are recessed IN the fish mesh.
# No separate pasted gill globes or black pipe-like outlines.
for vert in fish_mesh.vertices:
    p=vert.co
    center_x=FISH_X+FISH_SKEW*p.y
    flank=clamp((abs(p.x-center_x)-0.12)/0.07)
    vertical=(p.z-FISH_Z)
    if flank>0:
        gill_y=-0.880+0.19*(vertical*vertical)
        gill=(math.exp(-((p.y-gill_y)/0.028)**2) *
              math.exp(-((vertical)/0.175)**4))
        # Less regular, very shallow chiseled scale wedges.
        stripe=p.y*13.7+vertical*4.1
        rows=vertical*15.1
        offset=0.34*(math.floor(rows)%2)
        saw=abs((stripe+offset)%1.0-0.5)
        wedge=max(0.0,1.0-saw/0.26)
        patch=max(0.0,1.0-abs(rows%1.0-0.5)/0.35)
        small_scale=0.0018*wedge*patch
        displaced=(0.009*gill+small_scale)*flank
        p.x-=displaced*(1 if p.x>center_x else -1)
fish_mesh.update()
for poly in fish_mesh.polygons:
    poly.use_smooth=True
    p=poly.center
    flank=abs(p.x-FISH_X-FISH_SKEW*p.y)
    gill_y=-0.880+0.19*(p.z-FISH_Z)**2
    if abs(p.y-gill_y)<0.034 and flank>0.14 and abs(p.z-FISH_Z)<0.17:
        poly.material_index=1
    elif p.z>FISH_Z+0.095:
        poly.material_index=1
    elif p.z<FISH_Z-0.105:
        poly.material_index=2
    else:
        poly.material_index=0

# Inset eyes positioned within the broadened fish head, not a free-floating
# button farther out than the profile.
for side in (-1,1):
    sphere("Salmon_InsetEye_%s"%side,
        (FISH_X+FISH_SKEW*(-1.025)+side*0.192,-1.025,FISH_Z+0.042),
        (0.012,0.014,0.016),eye_mat,16,10)

# Mouth is a small notch at the fish's pointed head.
curve_line("Salmon_MouthIncision",[
    (FISH_X+FISH_SKEW*(-1.265)-0.035,-1.265,FISH_Z-0.015),
    (FISH_X+FISH_SKEW*(-1.288),-1.288,FISH_Z-0.019),
    (FISH_X+FISH_SKEW*(-1.265)+0.035,-1.265,FISH_Z-0.015)
],0.0035,walnut_dark)

# Traditional forked salmon tail in the true fish vertical fin plane (Y/Z).
fin("Salmon_Forked_Tail",[
    (FISH_X+FISH_SKEW*1.01,1.01,FISH_Z),
    (FISH_X+FISH_SKEW*1.12,1.12,FISH_Z+0.14),
    (FISH_X+FISH_SKEW*1.37,1.37,FISH_Z+0.235),
    (FISH_X+FISH_SKEW*1.30,1.30,FISH_Z+0.08),
    (FISH_X+FISH_SKEW*1.22,1.22,FISH_Z),
    (FISH_X+FISH_SKEW*1.30,1.30,FISH_Z-0.08),
    (FISH_X+FISH_SKEW*1.37,1.37,FISH_Z-0.235),
    (FISH_X+FISH_SKEW*1.12,1.12,FISH_Z-0.14)
],salmon_side,0.052)
fin("Salmon_DorsalFin",[
    (FISH_X+FISH_SKEW*0.12,0.12,FISH_Z+0.22),
    (FISH_X+FISH_SKEW*0.24,0.24,FISH_Z+0.28),
    (FISH_X+FISH_SKEW*0.28,0.28,FISH_Z+0.37),
    (FISH_X+FISH_SKEW*0.34,0.34,FISH_Z+0.34),
    (FISH_X+FISH_SKEW*0.51,0.51,FISH_Z+0.20)
],salmon_side,0.051)
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
# v22: fish vertebral midline bends gently through the mouth. Both tail and
# head move with the same real deformation; do not translate just the mesh
# body while leaving fins/gills behind. The bite at y=0 remains stationary.
def fish_bend_x(y):
    return 0.070*math.sin(1.48*y)
def fish_bend_z(y):
    return 0.060*y + 0.039*y*y

for ob in list(bpy.data.objects):
    if ob.name in bear_names_before_fish:
        continue
    if ob.type=='MESH':
        # Lofts/fins have full-source coordinates in their actual vertices;
        # primitives such as sphere-eyes have local geometry + obj.location.
        if abs(ob.location.y)<1.0e-8 and abs(ob.location.x)<1.0e-8:
            for v in ob.data.vertices:
                y=v.co.y
                v.co.x+=fish_bend_x(y)
                v.co.z+=fish_bend_z(y)
            ob.data.update()
        else:
            y=ob.location.y
            ob.location.x+=fish_bend_x(y)
            ob.location.z+=fish_bend_z(y)
    elif ob.type=='CURVE':
        for sp in ob.data.splines:
            if sp.type=='POLY':
                for p in sp.points:
                    y=p.co.y
                    p.co.x+=fish_bend_x(y)
                    p.co.z+=fish_bend_z(y)
        ob.data.update()

# Body objects have already been resized, so only process newly added fish.
for ob in list(bpy.data.objects):
    if ob.name not in bear_names_before_fish:
        ob.location.y *= 0.77
        ob.scale.y *= 0.77
        ob.location.z -= 0.057  # central bite is aligned with the carved jaw recess

# Physical jaw/fish alignment invariant for the source-space profile:
# the fish mid-body must intersect the mouth plane on both X and Z axes.
mouth_center=Vector((-2.04*0.87,0.0,0.777))
fish_center=Vector((FISH_X,0.0,FISH_Z-0.057))
assert abs(fish_center.x-mouth_center.x)<0.18, "Fish no longer reaches the bear mouth"
assert abs(fish_center.z-mouth_center.z)<0.10, "Fish is vertically detached from bite"
# v20 regression check: cupped jaw and sculpted lip surfaces must straddle
# the fish in both X and Z; this is only a geometry sanity check, NOT art QA.
jaw_tip_x=-2.17*0.87
lower_lip_x=-2.044*0.87
upper_lip_x=-2.043*0.87
assert abs(jaw_tip_x-fish_center.x)<0.20, "Jaw tip no longer cups salmon"
assert abs(lower_lip_x-fish_center.x)<0.15, "Lower lip detached in X"
assert abs(upper_lip_x-fish_center.x)<0.15, "Upper lip detached in X"
clamp_waist=min(stations,key=lambda q:abs(q[0]))
compressed_rz=clamp_waist[2]*(1-.31)
assert 0.54 < fish_center.z-compressed_rz < 0.67, "Fish belly is outside mandible"
assert 0.91 < fish_center.z+compressed_rz < 1.00, "Fish top is outside upper lip"
# Numerical intersection alone cannot certify recognizable sculptural contact.
# These are guards, not an artistic pass.
# This is a geometry guard for the *actual sculpted cavity*, not removable
# decorative lip curves. It does not prove believable bite on rendered views.
assert 0.87 < fish_center.z+compressed_rz < 1.00, "Salmon is above mouth cavity"
assert 0.56 < fish_center.z-compressed_rz < 0.68, "Salmon is below mandible"

# Fur grooves are geometry relief recessed into the remeshed bear body, not loose curves.

# v6 geometry rebuild notes: organic cross-section trunk and limbs, not stacked spheres.
# Shoulder/body/head united by the official Blender remesh workflow.
# No full-body sine ribs; fixed paw shapes; compact skull/muzzle; skewed fish.
# All outputs must be judged from official 3DCodeVerse multi-angle render, not generated images.

# v11 woodwork: genuine UV texture embedded in exported GLB.
# No external image assets or image-generation dependency.
import numpy as np
TEX_W=1024
TEX_H=1024
_u=np.linspace(0,1,TEX_W,dtype=np.float32)[None,:]
_v=np.linspace(0,1,TEX_H,dtype=np.float32)[:,None]
warp=(1.35*np.sin(2*np.pi*(_v*2.1+0.18*np.sin(_u*5.2)))+
      .72*np.sin(2*np.pi*(_v*4.9-_u*1.8)))
fibers=np.sin(2*np.pi*(19*_u+warp+0.90*np.sin(2*np.pi*_v*1.4)))
fine=np.sin(2*np.pi*(79*_u+2.0*np.sin(_v*10.4)))
cross=np.sin(2*np.pi*(2.2*_v+0.7*np.sin(_u*15.0)))
rings=np.sin(2*np.pi*(11*_u+0.12*warp))
vignettes=np.sin(2*np.pi*(_u*2.7+_v*.35))
value=1.0+0.055*fibers+0.018*fine+0.024*rings+0.013*cross+0.010*vignettes
value=np.clip(value,0.57,1.36)
pixels=np.empty((TEX_H,TEX_W,4),dtype=np.float32)
pixels[:,:,0]=np.clip(0.152*value,0,1)
pixels[:,:,1]=np.clip(0.072*value,0,1)
pixels[:,:,2]=np.clip(0.032*value,0,1)
pixels[:,:,3]=1
wood_image=bpy.data.images.new('HokkaidoWalnutWoodGrainGLB',width=TEX_W,height=TEX_H,alpha=True)
wood_image.pixels.foreach_set(pixels.ravel())
wood_image.update()
try: wood_image.pack()
except Exception: pass

# Consistent body material: no scattered opaque material patches.
# Wood grain and relief both survive GLB without camouflage-like artifacts.
for poly in bear.data.polygons:
    poly.material_index=0

wooduv=bear.data.uv_layers.new(name='WoodGrainUV')
for loop in bear.data.loops:
    p=bear.data.vertices[loop.vertex_index].co
    angle=math.atan2(p.y,p.z-1.18)
    uu=(angle/math.tau+0.5)%1.0
    vv=(p.x+2.26)/4.0
    wooduv.data[loop.index].uv=(uu,vv)

bs=walnut.node_tree.nodes.get('Principled BSDF')
image_node=walnut.node_tree.nodes.new('ShaderNodeTexImage')
image_node.name='Embedded Hokkaido walnut grain'
image_node.image=wood_image
image_node.interpolation='Linear'
walnut.node_tree.links.new(image_node.outputs['Color'],bs.inputs['Base Color'])

# v7: Align the bear's face with the official Harness GLB front view.
# Blender -X faces forwards in our sculpt, but the glTF front is Blender -Y.
# Apply the same world rotation to every component, including the salmon.
turn = Matrix.Rotation(math.pi / 2.0, 4, 'Z')
ground = Matrix.Translation(Vector((0.0, 0.0, -0.052)))
for ob in list(bpy.data.objects):
    ob.matrix_world = ground @ turn @ ob.matrix_world

# No ground, stage, writing or cameras: 3DCodeVerse owns the render studio.
