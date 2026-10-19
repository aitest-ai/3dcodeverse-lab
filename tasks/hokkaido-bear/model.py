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

walnut=material("Wood_Dark_Charred_Walnut",(0.115,0.057,0.029))
walnut_warm=material("Wood_Highlight_Old_Polish",(0.205,0.112,0.052))
walnut_mid=material("Wood_Facet_Satin",(0.153,0.073,0.033))
walnut_dark=material("Wood_Deep_Gouges",(0.063,0.033,0.018))
salmon_wood=material("Salmon_Warm_Carved_Wood",(0.31,0.168,0.079))
salmon_side=material("Salmon_Dark_Upper_Body",(0.175,0.092,0.044))
salmon_ridge=material("Salmon_Etched_Scales",(0.39,0.224,0.109))
eye_mat=material("Inset_Eyes_and_Nose",(0.032,0.026,0.020),0.2)
mouth_mat=material("Mouth_Dark_Shadow",(0.038,0.025,0.014))

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

# A substantial low-bodied bear, familiar Hokkaido tourist carving silhouette:
# head to left (-X), prominent shoulders, squat trunk, thick separate feet.
bear_parts=[]
bear_parts.append(sphere("TorsoCarved", (0.16,0.0,1.06),(1.21,0.58,0.62),walnut))
bear_parts.append(sphere("ShoulderHump",(-0.55,0,1.25),(0.65,0.60,0.67),walnut))
bear_parts.append(sphere("Haunch",(0.90,0,1.10),(0.57,0.53,0.54),walnut))
bear_parts.append(sphere("Neck",(-0.94,0,1.10),(0.56,0.50,0.49),walnut))
bear_parts.append(sphere("CheekHead",(-1.32,0,1.12),(0.50,0.45,0.42),walnut))
bear_parts.append(sphere("Muzzle",(-1.71,0,0.99),(0.31,0.32,0.22),walnut))
bear_parts.append(sphere("LowerJaw",(-1.64,0,0.80),(0.27,0.28,0.11),walnut))
# sculpt ears into the main silhouette, smaller and far apart
for side in (-1,1):
    bear_parts.append(sphere("Ear"+str(side),(-1.28,side*0.335,1.52),(0.16,0.14,0.19),walnut))
# limb cylinders merge into paws, no stick legs
for fore,x in ((True,-0.76),(False,0.93)):
    for side in (-1,1):
        y=side*0.43
        bear_parts.append(sphere(("Fore" if fore else "Hind")+"Thigh"+str(side),(x,y,0.78),(0.31,0.25,0.50),walnut))
        bear_parts.append(sphere(("Fore" if fore else "Hind")+"Shin"+str(side),(x-0.08,y,0.46),(0.22,0.22,0.37),walnut))
        bear_parts.append(sphere(("Fore" if fore else "Hind")+"Paw"+str(side),(x-0.20,y,0.19),(0.33,0.24,0.20),walnut))
bear_parts.append(sphere("StubTail",(1.47,0.0,1.06),(0.16,0.17,0.16),walnut))

# Fuse body and feet with voxel remeshing so there are no floating intersections.
bpy.ops.object.select_all(action='DESELECT')
for ob in bear_parts: ob.select_set(True)
active=bear_parts[0]
bpy.context.view_layer.objects.active=active
bpy.ops.object.join()
bear=active
bear.name="Kuma_Handcarved_OnePiece"
# Converting remeshed body to a single mesh preserves geometry on glTF export.
bear.data.remesh_voxel_size=0.030
try:
    bpy.ops.object.voxel_remesh()
except Exception:
    # The underlying body remains valid even if the Blender remesh backend is missing.
    pass

# Apply low amplitude chisel-like surface displacement and dark/light wood facets.
for mat in (walnut_mid,walnut_warm,walnut_dark):
    bear.data.materials.append(mat)
for v in bear.data.vertices:
    co=v.co
    nx=noise.noise(Vector((co.x*13,co.y*13,co.z*13)))
    fur=math.sin(co.x*31 + co.z*19 + co.y*9) * 0.0055
    v.co=co + v.normal * (0.0062*nx+fur)
bear.data.update()
for face in bear.data.polygons:
    cx=face.center.x; cy=face.center.y; cz=face.center.z
    n=noise.noise(Vector((cx*18,cy*18,cz*18)))
    if n>0.39: face.material_index=2
    elif n < -0.40: face.material_index=3
    elif n>0.16: face.material_index=1
    else: face.material_index=0
    face.use_smooth=True

# Four sets of deeply sculpted, discernible toes and carved claws.
for fore,x in ((True,-0.76),(False,0.93)):
    for side in (-1,1):
        y=side*0.43
        for k in range(4):
            py=y+(k-1.5)*0.105
            tipx=x-0.43
            sphere("WoodenToe_%s_%s_%d"%(int(fore),int(side),k),(tipx,py,0.125),(0.13,0.052,0.075),walnut_mid,20,12)
            frustum("DarkClaw_%s_%s_%d"%(int(fore),int(side),k),(tipx-0.09,py,0.12),(tipx-0.18,py,0.10),0.040,0.005,walnut_dark,12)

# Ear pits and facial detail on both sides
for side in (-1,1):
    sphere("EarWell_"+str(side),(-1.34,side*0.444,1.545),(0.087,0.015,0.10),walnut_dark,20,12)
    sphere("InsetEye_"+str(side),(-1.64,side*0.315,1.190),(0.047,0.033,0.046),eye_mat,20,12)
    sphere("Brow_"+str(side),(-1.55,side*0.327,1.25),(0.13,0.049,0.046),walnut_mid,24,14)

# A chunky triangular bear nose, distinctly forward.
sphere("Bear_Black_Carved_Nose",(-1.975,0,1.035),(0.080,0.160,0.105),eye_mat,32,18)
sphere("MouthOpening",(-1.864,0,0.856),(0.079,0.26,0.060),mouth_mat,24,12)
for side in (-1,1):
    curve_line("LipCrease"+str(side),[(-1.95,side*0.11,0.881),(-1.83,side*0.26,0.860),(-1.65,side*0.25,0.850)],0.010,walnut_dark)

# --- Salmon: lengthwise across the bear's jaws along Y ---
# Entire fish is wood, carved with dark back and warm sides.
fish_center=(-1.82,0.0,0.865)
fish=sphere("Salmon_Whole_Tapered_Body",fish_center,(0.145,1.005,0.159),salmon_wood,64,32)
# Upper dark stripe through back; unlike photo texture this remains in GLB.
sphere("Salmon_Dark_Dorsal",(-1.82,0,0.946),(0.092,0.90,0.097),salmon_side,48,22)
# Carved salmon head at negative Y; blunt jaws, eye and gill.
sphere("Salmon_Head",(-1.82,-0.882,0.867),(0.147,0.195,0.145),salmon_side,32,20)
sphere("Salmon_Jaw",(-1.83,-1.059,0.811),(0.105,0.09,0.039),salmon_wood,20,12)
for sx in (-1,1):
    sphere("Salmon_Eye"+str(sx),(-1.82+sx*0.145,-0.936,0.908),(0.018,0.018,0.020),eye_mat,16,10)
    curve_line("GillSlit"+str(sx),[(-1.82+sx*0.147,-0.78,0.975),(-1.82+sx*0.152,-0.75,0.895),(-1.82+sx*0.139,-0.80,0.81)],0.009,walnut_dark)
# A separate forked tail, beyond positive Y end.
fin("Salmon_Tail_Fork",[(-1.82,0.90,0.87),(-1.82,1.25,1.10),(-1.82,1.15,0.86),(-1.82,1.25,0.65)],salmon_side,0.035)
fin("Salmon_Dorsal_Fin",[(-1.82,0.16,1.009),(-1.82,0.38,1.20),(-1.82,0.53,1.013)],salmon_side,0.032)
fin("Salmon_Belly_Fin",[(-1.82,-0.1,0.737),(-1.82,0.10,0.600),(-1.82,0.20,0.747)],salmon_side,0.027)
for side in (-1,1):
    fin("Salmon_Pectoral_Fin"+str(side),[(-1.82+side*0.11,-0.64,0.82),(-1.82+side*0.33,-0.38,0.73),(-1.82+side*0.13,-0.25,0.82)],salmon_wood,0.022)

# Engrave interleaved scales on fish's visible flanks as raised almond-like cuts.
for side in (-1,1):
    for row in range(3):
        for i in range(23):
            sy=-0.71+i*0.067+(row%2)*0.032
            circ=max(0.10, 1-(sy/1.02)**2)
            xcoord=-1.82+side*(0.143*math.sqrt(circ)+0.004)
            zcoord=0.819+row*0.046
            # hundreds of small, physically present scales on the GLB
            ob=sphere("SalmonScale_%d_%d_%d"%(side,row,i),(xcoord,sy,zcoord),(0.006,0.037,0.018),salmon_ridge,10,8)
            ob.rotation_euler[0]=(-0.16 if side==1 else 0.16)

# Chisel slash traces across upper back and shoulders: visible carved ridges.
# Every groove is a small stained cut on the visible upper silhouette.
for idx in range(170):
    x=-0.84+idx/169.0*1.88
    for side in (-1,1):
        y=side*(0.12+0.26*(0.5+0.5*math.sin(idx*2.4)))
        # upper ellipsoid estimate, with hump shaping at shoulders
        rad=max(0.12, 1-((x-0.14)/1.24)**2-(y/0.60)**2)
        z=1.06+0.62*math.sqrt(rad)
        if x<0.1: z=max(z,1.25+0.67*math.sqrt(max(.03,1-((x+0.55)/.65)**2-(y/.62)**2)))
        # groove should touch surface; slender almond strokes.
        if z < 1.47: continue
        curve_line("CarvedFurSlash_%03d_%+d"%(idx,side),[(x-0.031,y, z+0.009),(x,y+side*0.015,z+0.012),(x+0.034,y+side*0.035,z+0.008)],0.005,walnut_dark)

# No ground, stage, writing or cameras: 3DCodeVerse owns the render studio.
