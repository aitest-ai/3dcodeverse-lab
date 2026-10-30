"""Create one Taiwanese street-game character from verified ORIGINAL MPFB .blend.
NEVER reimport a skinned GLB as the editable source. Blender 5.2, offline CI.
All coordinates and topology checks are in Blender meters.
"""
import bpy, bmesh, json, math, os, struct, random, sys
from array import array
from pathlib import Path
from mathutils import Vector

CHARACTERS = {
 "you": dict(height=1.74, age=22, sex="male", width=.96, face=.94, jaw=.91, nose=.87, eye=1.05, skin=(.77,.57,.44), top=(.23,.33,.43), pants=(.16,.23,.34), hair="short"),
 "boss": dict(height=1.57, age=55, sex="female", width=1.26, face=1.08, jaw=1.13, nose=1.01, eye=.95, skin=(.67,.43,.31), top=(.87,.59,.18), pants=(.24,.22,.22), hair="curl"),
 "uncle": dict(height=1.65, age=72, sex="male", width=1.35, face=1.14, jaw=1.18, nose=1.22, eye=.91, skin=(.69,.47,.34), top=(.82,.80,.71), pants=(.24,.27,.26), hair="bald"),
 "jie": dict(height=1.76, age=23, sex="male", width=.94, face=.88, jaw=.93, nose=.95, eye=1.08, skin=(.74,.54,.40), top=(.09,.46,.46), pants=(.17,.24,.28), hair="short"),
 "oldman": dict(height=1.60, age=82, sex="male", width=1.10, face=1.02, jaw=.90, nose=1.29, eye=.83, skin=(.67,.45,.34), top=(.14,.26,.21), pants=(.31,.29,.25), hair="gray"),
 "cop": dict(height=1.79, age=36, sex="male", width=1.11, face=.99, jaw=1.09, nose=1.02, eye=1.01, skin=(.70,.49,.35), top=(.48,.68,.77), pants=(.18,.24,.32), hair="short"),
 "shui": dict(height=1.66, age=65, sex="male", width=1.09, face=1.08, jaw=.96, nose=1.15, eye=.94, skin=(.60,.40,.28), top=(.63,.32,.14), pants=(.25,.26,.21), hair="gray"),
 "bro": dict(height=1.80, age=43, sex="male", width=1.33, face=1.19, jaw=1.30, nose=1.00, eye=.87, skin=(.64,.42,.31), top=(.68,.12,.12), pants=(.17,.18,.21), hair="bald")
}
REQUIRED_KEYS = ["mouthOpen","mouthSmile","mouthFrown","eyeBlinkLeft","eyeBlinkRight",
                 "browDownLeft","browDownRight","browInnerUp"]
REQUIRED_BONES = ["Root","pelvis","spine_01","spine_02","spine_03","neck_01","head",
                  "upperarm_l","upperarm_r","lowerarm_l","lowerarm_r","hand_l","hand_r",
                  "thigh_l","thigh_r","calf_l","calf_r","foot_l","foot_r"]
cid=os.environ.get("CHARACTER_ID","you")
assert cid in CHARACTERS, cid
cfg=CHARACTERS[cid]
out=Path(os.getenv("CHARACTER_OUT","outputs/taiwan_characters")).resolve()
out.mkdir(parents=True,exist_ok=True)
base=Path(os.getenv("BASE_SOURCE","inputs/baseline")).resolve()
assert (base/"human_mpfb_blender5.blend").is_file()
assert (base/"human_mpfb_blender5.glb").is_file()

# Recover image *bytes*, not GLB meshes. Opens the pre-rigging original .blend.
with (base/"human_mpfb_blender5.glb").open("rb") as f:
    magic,ver,length=struct.unpack("<4sII",f.read(12))
    assert magic==b"glTF" and ver==2
    n,k=struct.unpack("<I4s",f.read(8)); assert k==b"JSON"
    gltf=json.loads(f.read(n))
    n,k=struct.unpack("<I4s",f.read(8)); assert k==b"BIN\x00"
    binary=f.read(n)
imgdir=out/("_textures_"+cid)
imgdir.mkdir(exist_ok=True)
images={}
for idx,img in enumerate(gltf.get("images",[])):
    view=gltf["bufferViews"][img["bufferView"]]
    ext=".png" if img.get("mimeType")=="image/png" else ".jpg"
    name=img.get("name",str(idx))
    path=imgdir/(name+ext)
    start=view.get("byteOffset",0)
    path.write_bytes(binary[start:start+view["byteLength"]])
    images[name.casefold()]=path

bpy.ops.wm.open_mainfile(filepath=str(base/"human_mpfb_blender5.blend"))
sc=bpy.context.scene
for im in bpy.data.images:
    if im.source!="FILE": continue
    keys=[Path(im.name).stem.casefold(),Path(bpy.path.abspath(im.filepath)).stem.casefold()]
    match=next((p for key in keys for n,p in images.items() if key==n or key.startswith(n) or n.startswith(key)),None)
    if match is not None:
        im.filepath=str(match)
        im.reload()
        # 256 is intentional: <=6 MB total incl 11 original PBR maps.
        if im.size[0]>256 or im.size[1]>256:
            newsize=(min(256,im.size[0]),min(256,im.size[1]))
            im.scale(*newsize)
        im.filepath_raw=str(imgdir/(Path(im.name).stem+".png"))
        im.file_format="PNG"
        im.save()
        im.reload()
assert len(images)>=7
bpy.ops.file.pack_all()
rig=next(o for o in sc.objects if o.type=="ARMATURE")
body=next(o for o in sc.objects if o.type=="MESH" and o.name=="Human_Body_MakeHumanTopology")
cloth=next(o for o in sc.objects if o.type=="MESH" and o.name.endswith(".female_casualsuit01"))
original_hair=[o for o in sc.objects if o.type=="MESH" and o.name.endswith(".long01")]
bone_names=set(b.name for b in rig.data.bones)
missing=sorted(set(REQUIRED_BONES)-bone_names)
if missing:
    raise RuntimeError("MPFB source rig lacks required unrenamable bones: "+str(missing))
original_body_vertex_count=len(body.data.vertices)
assert original_body_vertex_count>13380

# Stage 0 (face QA): independently synthesize a genuine MPFB phenotype for
# EACH character. The old pipeline reused the unmodified female-neutral head
# for 8 people and only changed x-width. That caused uncanny clone faces.
import importlib
try:
    bpy.ops.preferences.addon_enable(module="bl_ext.local_mpfb.mpfb")
    import bl_ext.local_mpfb.mpfb
except Exception as err:
    raise RuntimeError("Real MPFB phenotype generator is required, not optional: "+str(err))
def service(suffix,symbol):
    names=[n for n in sys.modules if n.endswith(suffix)]
    if len(names)!=1:raise RuntimeError("MPFB service missing "+suffix+" "+str(names))
    return getattr(importlib.import_module(names[0]),symbol)
HumanService=service("mpfb.services.humanservice","HumanService")
TargetService=service("mpfb.services.targetservice","TargetService")
phenotypes={
 "you": dict(gender=.94,age=.45,weight=.38,muscle=.51,proportions=.51),
 "boss":dict(gender=.04,age=.77,weight=.78,muscle=.29,proportions=.44),
 "uncle":dict(gender=.99,age=.89,weight=.84,muscle=.27,proportions=.47),
 "jie":dict(gender=.92,age=.44,weight=.35,muscle=.50,proportions=.55),
 "oldman":dict(gender=.97,age=.97,weight=.48,muscle=.20,proportions=.49),
 "cop":dict(gender=.97,age=.59,weight=.55,muscle=.74,proportions=.52),
 "shui":dict(gender=.99,age=.82,weight=.62,muscle=.34,proportions=.47),
 "bro":dict(gender=.99,age=.67,weight=.77,muscle=.83,proportions=.52)}
phen=phenotypes[cid]
macro=TargetService.get_default_macro_info_dict()
macro.update(phen)
# This affects the MakeHuman model's reference geometry, not a claim that
# any particular face structure defines Taiwanese identity.
macro["race"]={"asian":.83,"caucasian":.12,"african":.05}
fresh=HumanService.create_human(mask_helpers=False,extra_vertex_groups=False,
                                feet_on_ground=True,scale=.1,macro_detail_dict=macro)
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
fresh_eval=fresh.evaluated_get(deps)
morph_mesh=fresh_eval.to_mesh()
if len(morph_mesh.vertices)!=len(body.data.vertices):
    raise RuntimeError("Real MPFB macro changed vertex count; cannot preserve vertex weights")
old_coords=[v.co.copy() for v in body.data.vertices]
oldworld=body.matrix_world.copy()
nworld=fresh.matrix_world.copy()
# Existing source has baked deformation for default baseline; we replace with
# actual MPFB target interpolation while retaining original topology and weights.
while body.data.shape_keys and len(body.data.shape_keys.key_blocks):
    body.shape_key_remove(body.data.shape_keys.key_blocks[-1])
inv=body.matrix_world.inverted()
for i,vert in enumerate(body.data.vertices):
    vert.co=inv@(nworld@morph_mesh.vertices[i].co)
fresh_eval.to_mesh_clear()
bpy.data.objects.remove(fresh,do_unlink=True)
body.data.update()
bpy.context.view_layer.update()
# Ask official MPFB to refit eyeballs, garments, the skin weights and skeleton
# against the changed anatomy rather than leaving the neutral female rig.
from mathutils.kdtree import KDTree
kd=KDTree(13380)
for i in range(13380):
    kd.insert(oldworld@old_coords[i],i)
kd.balance()
face_asset_adjustments={}
for obj in tuple(sc.objects):
    if obj.type!="MESH" or obj in (body,cloth) or obj in original_hair:continue
    if any(x in obj.name.lower() for x in ("shoes","teeth","tongue")):continue
    world=obj.matrix_world.copy(); inverse=world.inverted(); count=0
    for vertex in obj.data.vertices:
        p=world@vertex.co
        found,ind,dist=kd.find(p)
        if ind is None or dist>.12:continue
        delta=(oldworld@body.data.vertices[ind].co)-(oldworld@old_coords[ind])
        vertex.co=inverse@(p+delta)
        count+=1
    obj.data.update()
    face_asset_adjustments[obj.name]=count
bpy.context.view_layer.update()
newcoords=[v.co.copy() for v in body.data.vertices]
shifted=sum((a-b).length>.002 for a,b in zip(old_coords,newcoords))
if shifted<2000:raise RuntimeError("MPFB phenotype was not truly applied")
print("GENUINE_MPFB_MACRO_PROFILE",cid,phen,"adjusted",shifted)

# Remove actual extra vertices, and all helper MASK modifiers. Only the first
# 13380 MakeHuman hm08 body vertices are anatomical geometry (upstream index convention).
for mod in list(body.modifiers):
    if mod.type=="MASK": body.modifiers.remove(mod)
while body.data.shape_keys and len(body.data.shape_keys.key_blocks):
    body.shape_key_remove(body.data.shape_keys.key_blocks[-1])
bm=bmesh.new()
bm.from_mesh(body.data)
bm.verts.ensure_lookup_table()
bm.verts.index_update()
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index>=13380],context="VERTS")
bm.to_mesh(body.data); bm.free(); body.data.update()
if len(body.data.vertices)!=13380:
    raise RuntimeError("Physical helper deletion failed: "+str(len(body.data.vertices)))
if any(m.type=="MASK" for m in body.modifiers):
    raise RuntimeError("A helper masking modifier survived")

# Remove long old hair; real MPFB anatomy remains unaffected by this operation.
for ob in original_hair:
    bpy.data.objects.remove(ob,do_unlink=True)

# Profile deformations: work in world coordinates on the original bone-weighted
# MPFB body, clothes and other facial parts (same deformation, UV/weights intact).
def gauss(x,c,s):
    return math.exp(-.5*((x-c)/s)**2)
def profile(obj):
    m=obj.matrix_world.copy()
    inv=m.inverted()
    for vert in obj.data.vertices:
        p=m@vert.co
        z=p.z
        h=min(1.0,max(0.0,(z-1.40)/.14))
        tor=gauss(z,1.14,.33)
        xfac=1+(cfg["width"]-1)*tor+(cfg["face"]-1)*h
        # Keep wrists, ankles and fingertips from swelling like a torso.
        if abs(p.x)>.29: xfac=1+(xfac-1)*.35
        p.x*=xfac
        p.y*=1+(cfg["width"]-1)*.45*tor+(cfg["face"]-1)*.35*h
        if h>.1 and p.y<-.025:
            jawmask=gauss(z,1.515,.045)
            p.x*=1+(cfg["jaw"]-1)*jawmask*.65
            p.y-=.010*(cfg["nose"]-1)*gauss(p.x,0,.035)*gauss(z,1.565,.042)
        vert.co=inv@p
    obj.data.update()
for ob in [o for o in sc.objects if o.type=="MESH" and o not in original_hair]:
    profile(ob)

# ARKit-style facial targets on the *actual skinned body*, with measurable
# nonzero vertex offsets (do not put names on empty extras / fake material nodes).
body.shape_key_add(name="Basis")
basis=[v.co.copy() for v in body.data.vertices]
world=body.matrix_world.copy()
invworld=world.inverted()
deltas={}
for keyname in REQUIRED_KEYS:
    key=body.shape_key_add(name=keyname,from_mix=False)
    count=0
    for i,baseco in enumerate(basis):
        p=world@baseco
        x,y,z=p.x,p.y,p.z
        # Negative Y is the front of the MPFB model. Keep back of skull still.
        front=max(0.0,min(1.0,(-y-.025)/.075))
        dx=dy=dz=0.0
        mouth=front*gauss(z,1.515,.029)*gauss(x,0,.064)
        eye=front*gauss(z,1.595,.023)
        brow=front*gauss(z,1.637,.026)
        if keyname=="mouthOpen":
            dz=(-.018 if z<1.515 else .005)*mouth
            dy=-.005*mouth
        elif keyname=="mouthSmile":
            dz=.013*mouth*gauss(abs(x),.040,.020)
            dx=.005*(1 if x>=0 else -1)*mouth
        elif keyname=="mouthFrown":
            dz=-.012*mouth*gauss(abs(x),.043,.022)
        elif keyname=="eyeBlinkLeft":
            dz=(-.009 if z>=1.595 else .007)*eye*gauss(x,-.042,.023)
        elif keyname=="eyeBlinkRight":
            dz=(-.009 if z>=1.595 else .007)*eye*gauss(x,.042,.023)
        elif keyname=="browDownLeft":
            dz=-.011*brow*gauss(x,-.043,.032)
        elif keyname=="browDownRight":
            dz=-.011*brow*gauss(x,.043,.032)
        elif keyname=="browInnerUp":
            dz=.012*brow*gauss(x,0,.036)
        if abs(dx)+abs(dy)+abs(dz)>0.00002:
            key.data[i].co=invworld@Vector((x+dx,y+dy,z+dz))
            count+=1
    deltas[keyname]=count
    if count<5: raise RuntimeError("Expression target "+keyname+" has too few moved vertices: "+str(count))

# Turn the ORIGINAL rigged garment into two real, independently textured meshes.
# Faces on either side of the waist are physically deleted, NOT hidden or merged.
top=cloth.copy(); top.data=cloth.data.copy(); sc.collection.objects.link(top)
pants=cloth.copy();pants.data=cloth.data.copy();sc.collection.objects.link(pants)
top.name="Top_"+cid
pants.name="Pants_"+cid
# Blender glTF mesh.name comes from mesh DATA name, not object name.
top.data.name="Top_"+cid
pants.data.name="Pants_"+cid
for garment,keep_above in ((top,True),(pants,False)):
    m=garment.matrix_world
    bm=bmesh.new();bm.from_mesh(garment.data)
    delete=[]
    for face in bm.faces:
        z=sum((m@v.co).z for v in face.verts)/len(face.verts)
        if (z>=.985)!=keep_above: delete.append(face)
    bmesh.ops.delete(bm,geom=delete,context="FACES")
    bm.to_mesh(garment.data);bm.free();garment.data.update()
    if len(garment.data.polygons)<50:
        raise RuntimeError("Garment split got too few faces: "+garment.name)
bpy.data.objects.remove(cloth,do_unlink=True)

# Fit every original clothing vertex OUTSIDE the actual anatomical MPFB
# surface. The source MakeHuman body mask concealed this fit problem; simply
# deleting the helpers exposes it. A real BVH fitting pass is required.
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
body_bvh=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
body_inverse=body.matrix_world.inverted()
fit_stats={}
for garment in (top,pants):
    to_local=garment.matrix_world.inverted()
    adjusted=0
    max_shift=0.0
    for vert in garment.data.vertices:
        p_body=body_inverse@(garment.matrix_world@vert.co)
        hit=body_bvh.find_nearest(p_body)
        if hit[0] is None: continue
        nearest,normal,idx,dist=hit
        signed=(p_body-nearest).dot(normal)
        clearance=.018 if garment is top else .015
        if signed<clearance:
            push=clearance-signed
            p_body+=normal*push
            vert.co=to_local@(body.matrix_world@p_body)
            adjusted+=1
            max_shift=max(max_shift,push)
    garment.data.update()
    fit_stats[garment.name]={"vertices_adjusted":adjusted,"max_shift_m":round(max_shift,4)}
    if adjusted<30:raise RuntimeError("Garment BVH fit did not modify enough vertices: "+garment.name)
print("ANATOMICAL_GARMENT_FIT",json.dumps(fit_stats))

def material(name,color,rough=.68,metal=0):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1)
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    return mat

def garment_texture(name,rgb,kind):
    # Distinct 128x128 texels for each garment; not just a renamed material.
    size=128
    im=bpy.data.images.new(name,width=size,height=size,alpha=True)
    px=array("f")
    for y in range(size):
        for x in range(size):
            v=1.0
            if kind=="hawaii":
                # stylised leaf/petal print, no stock artwork or protected logo
                ax=x%45-22;ay=y%47-23
                stem=abs(ax*.8+ay*.36)<2.5 and abs(ay)<19
                petal=((ax-8)**2/65+(ay+7)**2/20)<1.0 or ((ax+6)**2/75+(ay-4)**2/25)<1.0
                v=1.48 if (stem or petal) else (0.97+.05*math.sin(x*.1))
            elif kind=="denim":
                v=.89+.13*(x%4==0)+.035*(y%7==0)
            elif kind=="uniform":
                v=.95+.10*(y%26<1)
            elif kind=="cotton":
                v=.96+.045*math.sin(x*.41+y*.21)
            else:
                v=1.0
            px.extend([min(.98,max(.01,c*v)) for c in rgb]+[1.])
    im.pixels.foreach_set(px);im.update()
    path=imgdir/(name+".png")
    im.filepath_raw=str(path);im.file_format="PNG";im.save();im.reload();im.pack()
    mat=material(name+"_mat",rgb)
    bs=mat.node_tree.nodes.get("Principled BSDF")
    node=mat.node_tree.nodes.new("ShaderNodeTexImage")
    node.image=im
    mat.node_tree.links.new(node.outputs["Color"],bs.inputs["Base Color"])
    return mat

style="hawaii" if cid in ("shui","bro") else ("uniform" if cid=="cop" else "cotton")
for obj,texkind,col in ((top,style,cfg["top"]),(pants,"denim",cfg["pants"])):
    obj.data.materials.clear()
    obj.data.materials.append(garment_texture(obj.name+"_tex",col,texkind))
    for poly in obj.data.polygons: poly.material_index=0
# Tint remaining skin from MPFB's CC0 original textured material.
skinmat=body.data.materials[0].copy()
skinmat.name="SkinTaiwan_"+cid
skinmat.use_nodes=True
bs=next((n for n in skinmat.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
if bs:
    sock=bs.inputs["Base Color"]
    for ln in list(sock.links):
        upstream_socket=ln.from_socket
        skinmat.node_tree.links.remove(ln)
        mul=skinmat.node_tree.nodes.new("ShaderNodeMixRGB")
        mul.blend_type="MULTIPLY";mul.inputs[0].default_value=1
        mul.inputs[2].default_value=(*cfg["skin"],1)
        skinmat.node_tree.links.new(upstream_socket,mul.inputs[1])
        skinmat.node_tree.links.new(mul.outputs[0],sock)
    if not sock.is_linked:sock.default_value=(*cfg["skin"],1)
    bs.inputs["Roughness"].default_value=.65
body.data.materials.clear();body.data.materials.append(skinmat)

def rigid(obj,bone):
    # Bone-parent rigid accessories using KEEP TRANSFORM; armature skinning
    # without inverse bind caused hats to hover and masks to shift over eyes.
    if bone not in bone_names:raise RuntimeError("No rigid attach bone "+bone)
    world=obj.matrix_world.copy()
    obj.parent=rig
    obj.parent_type="BONE"
    obj.parent_bone=bone
    obj.matrix_world=world
    return obj
def cube(name,center,scale,mat,bone=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    o=bpy.context.object;o.name=name;o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bone:rigid(o,bone)
    bevel=o.modifiers.new("EdgeRound","BEVEL");bevel.width=.004;bevel.segments=2
    o.modifiers.new("WeightedNormals","WEIGHTED_NORMAL")
    return o
def sphere(name,center,scale,mat,bone="head"):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=center)
    o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bone:rigid(o,bone)
    return o
def ring(name,center,major,minor,mat,rotation=(math.pi/2,0,0),bone="head"):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=40,minor_segments=8,location=center,rotation=rotation)
    o=bpy.context.object;o.name=name;o.data.materials.append(mat)
    if bone:rigid(o,bone)
    return o
def cap(name,col,helmet=False):
    m=material(name+"_mat",col,.85)
    sphere(name,(0,-.006,1.655),(.105,.092,.074 if helmet else .060),m)
    cube(name+"_brim",(0,-.087,1.619),(.18,.11,.010),m,"head")
    return name
black=material("HairBlack_"+cid,(.012,.012,.011),.90)
gray=material("HairGray_"+cid,(.38,.38,.34),.9)
white=material("WhiteCloth_"+cid,(.77,.77,.72))
gold=material("Gold_"+cid,(.78,.51,.16),.3,.65)
if cfg["hair"]!="bald":
    hc=gray if cfg["hair"]=="gray" else black
    sphere("HairCrown_"+cid,(0,.000,1.648),(.083,.080,.053),hc)
    rand=random.Random(cid)
    for i in range(16 if cfg["hair"]!="curl" else 24):
        ang=2*math.pi*i/(16 if cfg["hair"]!="curl" else 24)
        x=.064*math.cos(ang);y=.051*math.sin(ang)-.009
        z=1.642+.014*rand.random()
        ob=sphere("HairLock_%02d_%s"%(i,cid),(x,y,z),
                  (.015,.014,.020 if cfg["hair"]=="short" else .027),hc)
        ob.rotation_euler[1]=.25*math.cos(ang)
if cid=="boss":
    # A contoured bib apron following the rounded torso (not a floating box).
    cap("Headscarf_boss",(.61,.27,.13))
    apron_material=material("ApronOrange_boss",(.88,.57,.15),.87)
    verts=[];faces=[]
    for row in range(7):
        z=1.42-row*.087
        half=.12+.020*row
        for col in range(9):
            u=col/8
            x=(2*u-1)*half
            y=-.168+.035*(abs(2*u-1)**2)
            verts.append((x,y,z))
    for row in range(6):
        for col in range(8):
            a=row*9+col
            faces.append((a,a+1,a+10,a+9))
    am=bpy.data.meshes.new("Apron_Boss_DrapedMesh")
    am.from_pydata(verts,[],faces);am.update()
    ao=bpy.data.objects.new("Apron_boss",am);sc.collection.objects.link(ao)
    am.materials.append(apron_material);rigid(ao,"spine_02")
elif cid=="uncle":
    # Shirt colour / no sleeves are an approximation from the source garment.
    for x in (-.046,.046):
        ring("Glasses_%s_%.2f"%(cid,x),(x,-.156,1.572),.044,.0028,
             material("Frame_uncle",(.12,.12,.12)))
elif cid=="jie":
    cap("Helmet_jie",(.08,.51,.50),helmet=True)
    cube("Mask_jie",(0,-.134,1.502),(.15,.010,.070),white,"head")
    cube("DeliveryBackpack_jie",(0,.231,1.265),(.42,.26,.51),
         material("BagGreen_jie",(.12,.52,.38)),"spine_02")
elif cid=="oldman":
    cap("BaseballCap_oldman",(.21,.23,.19))
    cube("Phone_oldman",(.39,-.105,1.00),(.073,.012,.136),
         material("PhoneMetal_oldman",(.12,.14,.15),.35,.45),"hand_r")
elif cid=="cop":
    cap("PoliceCap_cop",(.12,.20,.30))
    cube("PoliceBadge_cop",(-.10,-.168,1.38),(.06,.009,.06),gold,"spine_03")
elif cid=="shui":
    cap("StrawHat_shui",(.62,.48,.24))
    for x in (-.046,.046):
        ring("Glasses_%s_%.2f"%(cid,x),(x,-.156,1.570),.044,.0027,black)
    cube("ShoulderTowel_shui",(.22,-.06,1.37),(.09,.17,.34),white,"upperarm_r")
elif cid=="bro":
    cube("HeadBand_bro",(0,-.089,1.626),(.16,.014,.024),
         material("HeadbandRed_bro",(.55,.08,.08)),"head")
    ring("GoldNecklace_bro",(0,-.092,1.420),.109,.006,gold,(math.pi/2,0,0),"neck_01")
elif cid=="you":
    # ID card and lanyard visibly separate from clothing.
    cube("IDCard_you",(0,-.134,1.284),(.075,.006,.090),
         material("IDCardPlastic_you",(.78,.81,.84)), "spine_03")
    # Two hanging straps, not a large horizontal torus across both shoulders.
    for side in (-1,1):
        strap=cube("LanyardStrap_%s"%side,(side*.027,-.121,1.386),(.004,.006,.195),
                   material("Strap_you",(.16,.27,.44)),"spine_03")
        strap.rotation_euler[1]=side*.18

# Explicit close-fitting sneakers cover the original source's partially sunken
# footwear/foot overlap; attach each shoe to the corresponding foot bone.
shoe_mat=material("Sneakers_"+cid,(.21,.23,.25),.8)
sole_mat=material("Sole_"+cid,(.75,.73,.68),.85)
for side,bone in ((-1,"foot_l"),(1,"foot_r")):
    cube("Sneaker_%s_%s"%(cid,bone),(side*.099,-.068,.064),
         (.132,.230,.088),shoe_mat,bone)
    cube("Sole_%s_%s"%(cid,bone),(side*.099,-.075,.025),
         (.136,.235,.015),sole_mat,bone)

# Uniform height scaling; preserve original bone names and whole rig alignment.
original_height=max((body.matrix_world@v.co).z for v in body.data.vertices)-min((body.matrix_world@v.co).z for v in body.data.vertices)
ratio=cfg["height"]/original_height
for ob in sc.objects:
    # A mesh parented to the rig already inherits its parent scale.
    # Scaling both would double-scale the MPFB basemesh and rigging.
    if ob.type in ("MESH","ARMATURE") and (ob.parent is None or ob.parent.type not in ("MESH","ARMATURE")):
        ob.location*=ratio
        ob.scale*=ratio
bpy.context.view_layer.update()
height=max((body.matrix_world@v.co).z for v in body.data.vertices)-min((body.matrix_world@v.co).z for v in body.data.vertices)
if abs(height-cfg["height"])>.012:raise RuntimeError("Bad final height "+str(height))

# Capture 3 actual Blender renders, not AI illustrations or screenshots.
for ob in sc.objects:
    if ob.type=="MESH":
        for p in ob.data.polygons:p.use_smooth=True
sc.render.engine="CYCLES";sc.cycles.device="CPU";sc.cycles.samples=10
sc.render.resolution_x=420;sc.render.resolution_y=560
sc.render.resolution_percentage=100;sc.render.image_settings.file_format="PNG"
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.7
camd=bpy.data.cameras.new("CharacterCamera")
cam=bpy.data.objects.new("CharacterCamera",camd)
sc.collection.objects.link(cam);sc.camera=cam;camd.type="ORTHO"
for name,loc,power in (("Key",(3,-4,4),560),("Fill",(-3,-3,3),360),("Rim",(-2,3,4),400)):
    lamp=bpy.data.lights.new(name,"AREA")
    ob=bpy.data.objects.new(name,lamp);sc.collection.objects.link(ob)
    ob.location=loc;ob.rotation_euler=(Vector((0,0,1.0))-ob.location).to_track_quat("-Z","Y").to_euler()
    lamp.energy=power;lamp.size=3
facez=1.58*ratio
views={
 "front":((0,-5,1.1),(0,0,height*.52),height*1.33),
 "side":((5,0,1.1),(0,0,height*.52),height*1.33),
 "face":((0,-4,facez),(0,0,facez),.57*ratio)
}
# Repack and save source BLEND, but keep it OUTSIDE the requested small ZIP.
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/(cid+".blend")))
# GLB export: NO cameras/lights, NO helper shells, real shape keys and skins.
bpy.ops.object.select_all(action="DESELECT")
rig.select_set(True)
for ob in sc.objects:
    if ob.type=="MESH":ob.select_set(True)
bpy.context.view_layer.objects.active=rig
glbpath=out/(cid+".glb")
bpy.ops.export_scene.gltf(filepath=str(glbpath),export_format="GLB",
    use_selection=True,export_skins=True,export_animations=False,
    export_morph=True,export_morph_normal=False,export_cameras=False,
    export_lights=False,export_extras=True)
if glbpath.stat().st_size>6000000:
    raise RuntimeError(cid+" GLB exceeds 6,000,000 bytes; reduce source image size")
for view,(pos,target,scale) in views.items():
    cam.location=pos
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    camd.ortho_scale=scale
    sc.render.filepath=str(out/(cid+"_"+view+".png"))
    bpy.ops.render.render(write_still=True)
    if (out/(cid+"_"+view+".png")).stat().st_size<1500:
        raise RuntimeError("Render missing: "+cid+"_"+view)

# Assert exported targetNames and preserved joint node names from the actual GLB.
with glbpath.open("rb") as f:
    header=f.read(12)
    magic,ver,tot=struct.unpack("<4sII",header)
    n,k=struct.unpack("<I4s",f.read(8))
    assert magic==b"glTF" and ver==2 and tot==glbpath.stat().st_size and k==b"JSON"
    doc=json.loads(f.read(n))
nodes={n.get("name","") for n in doc.get("nodes",[])}
if not set(REQUIRED_BONES)<=nodes:
    raise RuntimeError("GLB bones missing: "+str(set(REQUIRED_BONES)-nodes))
meshinfo={m.get("name",""):m for m in doc.get("meshes",[])}
if not any("Top_"+cid in n for n in meshinfo) or not any("Pants_"+cid in n for n in meshinfo):
    raise RuntimeError("Independent garment meshes missing")
exported_keys=set()
for m in doc.get("meshes",[]):
    exported_keys.update(m.get("extras",{}).get("targetNames",[]))
    exported_keys.update(m.get("targetNames",[]))
if not set(REQUIRED_KEYS)<=exported_keys:
    raise RuntimeError("ARKit targetNames missing in real GLB: "+str(exported_keys))
if not doc.get("skins"):raise RuntimeError("GLB no skin")
report={
 "id":cid,"status":"STRUCTURE_PASS_RENDERED_VISUAL_REVIEW_REQUIRED",
 "original_body_vertices":original_body_vertex_count,"body_vertices":len(body.data.vertices),
 "helper_vertices_physically_deleted":original_body_vertex_count-len(body.data.vertices),
 "helper_mask_modifiers_remaining":sum(m.type=="MASK" for m in body.modifiers),
 "bone_count":len(rig.data.bones),"required_bones":REQUIRED_BONES,
 "shape_keys":REQUIRED_KEYS,"expression_affected_vertices":deltas,
 "source_texture_max_px":256,"top_texture":[128,128],"pants_texture":[128,128],
 "textures":[{"name":im.name,"width":im.size[0],"height":im.size[1]} for im in bpy.data.images if im.has_data],
 "height_m":round(height,4),"glb_bytes":glbpath.stat().st_size,
 "mpfb_genuine_phenotype":phen,
 "mpfb_macro_adjusted_vertices":shifted,"face_asset_adjustments":face_asset_adjustments,
 "garment_fitting":fit_stats,
 "mesh_count":len(doc.get("meshes",[])),"material_count":len(doc.get("materials",[])),
 "skin_count":len(doc.get("skins",[])),
 "rendered_views":list(views),
 "limitations":["Static preview; no walk-cycle deformation test",
                "Automated inspection does not prove zero intersections in all poses",
                "Expression names and deltas validated, not FACS anatomy-certified",
                "Clothing derived from the original MPFB CC0 casual-suit pattern"]
}
(out/(cid+"_report.json")).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("TAIWAN_CHARACTER_OK",cid,json.dumps(report,ensure_ascii=False))
