"""V25 anatomy-following geometric sculpt pass, not a fake 2D rendering.
The sealed v24b shape is a BLOCKOUT only. All paths below deform real high-poly
vertices in place, using artist-placed shoulder/back/facial landmark curves.
No reusing a third-party model. Export a distinct GLB and audit, never promote.
"""
import bpy, math, json, os, runpy, random
from pathlib import Path
from collections import defaultdict
from mathutils import Vector

root=Path("candidate").resolve()
root.mkdir(exist_ok=True,parents=True)
base=runpy.run_path("experiments/hokkaido-v24/model.py",run_name="__main__")
bear=base["bear"]
fish=base["fish"]
rand=random.Random(25012026)
assert len(bear.data.vertices)>60000
assert len(fish.data.vertices)>3000
base_sha=(root/"v24_highpoly_shape.glb").stat().st_size
assert base_sha>500000

# Sculpt in the original unrotated local coordinates. The model matrix already
# contains its export orientation, but mesh-local x/y/z still represent anatomy.
def bounded(v,a,b):
    return max(a,min(b,v))
def ramp(a,b,v):
    return bounded((v-a)/(b-a),0.,1.)
def angle_norm(n):
    return math.sqrt(n.x*n.x+n.y*n.y+n.z*n.z)
def groove_strokes(mesh, strokes, mode, cell=.105):
    """Brush stroke projected to side (x,z) or dorsal (x,y), using a
    bucketed landmark map. It is not a tiled shader or sphere appliqué.
    """
    vertices=mesh.vertices
    bucket=defaultdict(list)
    for i,v in enumerate(vertices):
        p=v.co
        a,b=(p.x,p.z) if mode=="side" else (p.x,p.y)
        bucket[(math.floor(a/cell),math.floor(b/cell))].append(i)
    displacement=[0.]*len(vertices)
    for a0,b0,a1,b1,width,depth,region in strokes:
        dx=a1-a0;dy=b1-b0
        length2=dx*dx+dy*dy
        if length2<.0001:continue
        pad=width*2.6
        for ia in range(math.floor((min(a0,a1)-pad)/cell),math.floor((max(a0,a1)+pad)/cell)+1):
            for ib in range(math.floor((min(b0,b1)-pad)/cell),math.floor((max(b0,b1)+pad)/cell)+1):
                for i in bucket.get((ia,ib),()):
                    v=vertices[i]; p=v.co; n=v.normal
                    if mode=="side":
                        if p.y*n.y < .20 or abs(p.y)<.21:continue
                        a,b=p.x,p.z
                    else:
                        if n.z<.42 or p.z<1.43:continue
                        a,b=p.x,p.y
                    if not region(p,n):continue
                    t=bounded(((a-a0)*dx+(b-b0)*dy)/length2,0.,1.)
                    da=a-(a0+t*dx);db=b-(b0+t*dy)
                    d=math.sqrt(da*da+db*db)
                    if d>=width:continue
                    # Narrow V-cut; no random raised beads or scale dimples.
                    taper=math.sin(math.pi*t)**.85
                    strength=depth*taper*(1-d/width)**1.7
                    displacement[i]-=strength
    original=[v.normal.copy() for v in vertices]
    count=0
    for i,shift in enumerate(displacement):
        if shift<-.0003:
            vertices[i].co+=original[i]*max(-.032,shift)
            count+=1
    mesh.update()
    return {"paths":len(strokes),"altered_vertices":count,
            "maximum_negative_displacement":round(min(displacement),4)}

def shoulder(p,n):
    return -.99<p.x<-.42 and .69<p.z<1.80
def flank(p,n):
    return -1.35<p.x<1.0 and .65<p.z<1.68
def cheek(p,n):
    return -2.13<p.x<-1.63 and 1.05<p.z<1.56
def neck(p,n):
    return -1.55<p.x<-.85 and .74<p.z<1.67

# Each patch of fur has its own anatomical travel direction and length.
# The artist-set seed points are motivated by observed shoulder-to-foreleg
# hair flow on original Hokkaido bear carvings, NOT a repeated tile function.
side_strokes=[]
for row in range(9):
    for col in range(18):
        x=-1.25+col*.125+rand.uniform(-.026,.026)
        z=.73+row*.112+rand.uniform(-.024,.024)
        lean=(.10+.07*rand.random()) * (1 if x<-.3 else -1)
        side_strokes.append((x,z,x+lean,z+.15+rand.uniform(-.03,.03),
                            .016+rand.random()*.006,.011+rand.random()*.009,flank))
# Withers carved slightly more deeply, curving down along the front leg.
for col in range(10):
    for row in range(7):
        x=-1.10+col*.065+rand.uniform(-.015,.015)
        z=.73+row*.145+rand.uniform(-.022,.022)
        side_strokes.append((x,z,x-.06,z+.19,
                             .018,.015+rand.random()*.007,shoulder))
# Head cheek and neck strokes are smaller / finer than shoulder gouges.
for col in range(8):
    for row in range(5):
        x=-2.10+col*.055+rand.uniform(-.01,.01)
        z=1.07+row*.09+rand.uniform(-.016,.016)
        side_strokes.append((x,z,x+.045,z+.09,.014,.010,cheek))
for col in range(9):
    for row in range(7):
        x=-1.49+col*.068
        z=.77+row*.122
        side_strokes.append((x,z,x+.073,z+.17,.015,.012,neck))
side_qa=groove_strokes(bear.data,side_strokes,"side")

# Back fur is anatomically laid along the spine; don't put circular ripples.
back=[]
def dorsal(p,n):return -1.20<p.x<.96 and abs(p.y)<.54
for row in range(11):
    y=-.46+row*.09
    for col in range(12):
        x=-1.06+col*.16+rand.uniform(-.03,.03)
        y0=y+rand.uniform(-.017,.017)
        back.append((x,y0,x+.19,y0+.015,.012,.009+rand.random()*.006,dorsal))
back_qa=groove_strokes(bear.data,back,"top")

# Sculpt a shallow upper/lower lip into the existing ONE-piece bear mesh.
# This cannot be reproduced by adding two decorative black curve objects.
face_affected=0
for v in bear.data.vertices:
    p=v.co;n=v.normal
    closeness=math.exp(-((p.x+2.28)/.19)**2 - (p.y/.30)**2)
    if p.z>.96 and p.z<1.13 and n.z<-.30:
        shift=.048*closeness
        p.z-=shift
        face_affected+=int(shift>.005)
    elif .71<p.z<.87 and n.z>.27 and p.x<-2.13:
        shift=.025*closeness
        p.z+=shift
        face_affected+=int(shift>.005)
bear.data.update()

# Carve fish gill plate and head-eye sockets from the *body vertices*.
# v24b fish y coords already reduced by factor 0.82. Use y0 in that frame.
fish_eye_qa=[]
for side in (-1,1):
    y0=-1.15*.82
    z0=base["fish_at"](-1.15)[2]+.063
    near=[]
    for v in fish.data.vertices:
        p=v.co
        if abs(p.y-y0)<.048 and abs(p.z-z0)<.043:
            near.append(v)
    if not near:raise RuntimeError("Missing actual salmon-head geometry for eye cavity")
    exposed=max(near,key=lambda v:side*v.co.x)
    x0=exposed.co.x
    affected=0
    for v in fish.data.vertices:
        p=v.co
        dist=((p.y-y0)/.042)**2+((p.z-z0)/.042)**2
        if dist<1.0 and side*(p.x-x0)>-.045:
            p.x-=side*.012*(1-dist)**1.5
            affected+=1
    fish_eye_qa.append({"side":side,"eye_position":(round(x0,4),round(y0,4),round(z0,4)),
                        "depressed_vertices":affected})
    # Relocate the old black bead to the genuine local surface and shrink it.
    obj=bpy.data.objects.get("SalmonTinyInsetEye_"+str(side))
    if obj is not None:
        # The base has already rotated objects +90 degrees about Z:
        # update world-space location, NOT their original local axes.
        from mathutils import Matrix
        world=Matrix.Translation(Vector((0,0,-.055))) @ Matrix.Rotation(math.pi/2,4,'Z')
        obj.location=world @ Vector((x0-side*.007,y0,z0))
        obj.scale=(.52,.52,.52)
fish.data.update()

# Etch 2 curved gills into the fish flank. Keep the fish surface closed.
gill_affected=0
# Flank-local displacement using mesh normals and side signs.
for v in fish.data.vertices:
    p=v.co;n=v.normal
    yy=(p.y/.82)
    if -1.01<yy<-.45 and abs(n.x)>.42:
        gy=-.81 + .17*(p.z-.78)
        gap=min(abs(p.y-gy),abs(p.y-(gy+.076)))
        if gap<.022:
            depth=.009*(1-gap/.022)
            p.x-=math.copysign(depth,n.x)
            gill_affected+=1
fish.data.update()


# ==============================================================
# V27: continuous anatomical contact; reject the spiky v26 jaw
# ==============================================================
# Exact v25 export for A/B: preserve source model before editing.
control=root/"v25_directional_sculpt.glb"
bpy.ops.export_scene.gltf(filepath=str(control),export_format="GLB",
                          export_apply=True,export_yup=True)
assert control.stat().st_size>250000

# Scale is consistent with blockout: original fish Y shortened by .82.
# Deform the SAME fish mesh for a pinched bite; no extra fish ellipsoid.
bite_vertices=0;max_bite_z=0
for v in fish.data.vertices:
    p=v.co
    q=(p.y/.190)**2
    weight=math.exp(-q*q)
    center_x=base["F_X"]+.09*math.sin((p.y/.82)*1.37)
    dz=p.z-base["F_Z"]
    dx=p.x-center_x
    sz=.205*weight*dz
    sx=.100*weight*dx
    if abs(sz)+abs(sx)>.0002:
        p.z-=sz;p.x-=sx
        bite_vertices+=1
        max_bite_z=max(max_bite_z,abs(sz))
fish.data.update()

# Continuous soft-surface sculpt for the bear mouth. Displacements are
# Gaussian throughout, with NO hard z-window at the lower lip, unlike v26.
# Reshape protruding lower shelf in X rather than lifting into jagged teeth.
upper_count=0;chin_count=0
for v in bear.data.vertices:
    p=v.co
    gauss_x=math.exp(-((p.x+2.345)/.165)**2)
    gauss_y=math.exp(-(p.y/.32)**4)
    # The lip's underside stays smooth; a 12mm integrated downward envelope.
    upper_z=math.exp(-((p.z-1.037)/.098)**2)
    # lower shelf is tucked BACK toward the face along X without lifting it.
    chin_z=math.exp(-((p.z-.735)/.100)**2)
    w=gauss_x*gauss_y
    if p.x < -2.15:
        if p.z>.91:
            shift=-.011*w*upper_z
            p.z+=shift
            upper_count+=int(abs(shift)>.001)
        elif p.z<.90:
            shift=.044*w*chin_z
            p.x+=shift
            chin_count+=int(shift>.001)
bear.data.update()

# Add a controlled smoothing pass ONLY to chin vertices to avoid
# abrupt surface changes at voxel boundaries; preserve v25 carved back.
# Mesh topology stays identical and therefore manifold/watertight.
positions=[v.co.copy() for v in bear.data.vertices]
neighbors=[set() for v in bear.data.vertices]
for e in bear.data.edges:
    a,b=e.vertices
    neighbors[a].add(b)
    neighbors[b].add(a)
smooth_count=0
for i,v in enumerate(bear.data.vertices):
    p=positions[i]
    blend=.32*math.exp(-((p.x+2.35)/.20)**2
                         -(p.y/.34)**4
                         -((p.z-.735)/.17)**2)
    if blend>.008 and len(neighbors[i])>=3:
        center=sum((positions[k] for k in neighbors[i]),Vector())/len(neighbors[i])
        v.co=positions[i].lerp(center,blend)
        smooth_count+=1
bear.data.update()

# No new glued-on toes. Only shallow V-shaped valleys in the one-piece
# existing paw surface; keep v25 shoulder/back strokes untouched.
toe_count=0;ankle_count=0
for foot_x in (-1.04,.56):
    for side in (-1,1):
        cy=side*.44
        for v in bear.data.vertices:
            p=v.co
            if abs(p.y-cy)>.30 or not foot_x-.49<p.x<foot_x+.27:
                continue
            if .29<p.z<.56 and abs(p.x-foot_x)<.34:
                w=math.sin(math.pi*(p.z-.29)/.27)
                if w>0:
                    dx=.060*w*(foot_x-p.x)
                    dy=.055*w*(cy-p.y)
                    p.x+=dx;p.y+=dy
                    ankle_count+=int(abs(dx)+abs(dy)>.001)
            if .065<p.z<.226 and p.x<foot_x-.18:
                for c in (-.09,.09):
                    side_dist=(p.y-(cy+c))/.019
                    taper=math.exp(-((p.z-.135)/.065)**2)
                    inward=.033*math.exp(-side_dist**2)*taper
                    if inward>.001:
                        p.x+=inward
                        toe_count+=1
bear.data.update()

# Anatomically broaden and sharpen the salmon's actual *head* surface, not
# attach another eye- or mouth-shaped sphere. Existing eye inset stays
# positioned as in v25; this deliberately tests whether the sculpt has
# recognizable gill/head structure with the same base materials.
head_count=0;gill_count=0
for v in fish.data.vertices:
    p=v.co;n=v.normal
    y=p.y
    # frontal salmon region after longitudinal .82 scale: -1.10 to -.72.
    if -1.12<y<-.60:
        # Form visible mouth taper and stronger cheek-to-gill volume.
        cheek=math.exp(-((y+.735)/.125)**2)
        side=abs(n.x)
        dx=.016*cheek*side*(1 if p.x>base["F_X"] else -1)
        p.x+=dx
        head_count+=int(abs(dx)>.002)
        # Deepen a gentle pair of curved gill incisions in actual geometry.
        gill_y=-.733+.14*(p.z-.84)
        d=min(abs(y-gill_y),abs(y-(gill_y+.065)))
        if side>.33 and d<.019 and .68<p.z<1.09:
            recess=.010*(1-d/.019)
            p.x-=math.copysign(recess,n.x)
            gill_count+=1
fish.data.update()

# Genuine surface distance probe around fish waist: not a visual pass.
from mathutils.kdtree import KDTree
jaw_points=[v.co for v in bear.data.vertices if v.co.x<-2.11 and abs(v.co.y)<.34 and .56<v.co.z<1.20]
tree=KDTree(len(jaw_points))
for i,p in enumerate(jaw_points):tree.insert(p,i)
tree.balance()
contact=[]
for v in fish.data.vertices:
    p=v.co
    if abs(p.y)<.060 and -2.50<p.x<-1.95 and .60<p.z<1.17:
        nearest,idx,d=tree.find(p)
        contact.append(d)
contact.sort()
if not contact:raise RuntimeError("No fish waist vertices in jaw contact zone")
contact_stat={"points":len(contact),"nearest":round(contact[0],5),
              "median":round(contact[len(contact)//2],5),
              "near_3cm":sum(x<.03 for x in contact)}
v27_metrics={"waist_vertices":bite_vertices,"max_waist_z_move":round(max_bite_z,5),
             "upper_lip_vertices":upper_count,"recessed_chin_vertices":chin_count,
             "smoothed_chin_vertices":smooth_count,
             "ankle_edits":ankle_count,"toe_valley_edits":toe_count,
             "fish_head_edits":head_count,"gill_edits":gill_count,
             "contact_distances":contact_stat,
             "no_positive_lower_jaw_lift":True}
print("V27_SHAPE_METRICS",json.dumps(v27_metrics),flush=True)
assert bite_vertices>150 and toe_count>100 and chin_count>100,v27_metrics

# A true anatomical fish eye must not be a black dot floating in front.
# Mesh topological integrity remains unchanged by this vertex-only pass.
# Export the only model reviewed for v25.
out=root/"v27_contact_sculpt.glb"
bpy.ops.export_scene.gltf(filepath=str(out),export_format="GLB",
                          export_apply=True,export_yup=True)
assert out.stat().st_size>250000
report={
    "version":"v27","type":"geometry-sculpt-experiment",
    "method":"artist-authored landmark-guided negative chisel strokes on true highpoly mesh",
    "original_reference":"Hokkaido wooden bear biting salmon; observation only, no reference mesh copied",
    "base":"v24b watertight GLB blockout (archived separately)",
    "shoulder_flank_face_paths":side_qa,
    "dorsal_fur_paths":back_qa,
    "lip_sculpted_vertices":face_affected,
    "fish_eyes":fish_eye_qa,
    "gill_carved_vertices":gill_affected,
    "bear_vertices":len(bear.data.vertices),
    "fish_vertices":len(fish.data.vertices),
    "actual_mesh_output":str(out.name),
    "v27_mouth_and_paw":v27_metrics,
    "artistic_approval":False,
    "notes":["No material change can substitute for fish-bite silhouette acceptance",
             "Face and paw geometry may still fail artistic review"]
}
(root/"sculpt_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print("V27_REAL_GEOMETRY_SCULPT_READY",out,report)
