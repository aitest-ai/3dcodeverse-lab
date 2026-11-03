"""New original Harbor Courier v02 styling. CC0 anatomy/hair/locomotion; original fitted outfit.
CC0_ROOT=/path/to/packs blender -b --factory-startup --python scripts/build_courier_v02.py
"""
import bpy,bmesh,math,json,os,hashlib,shutil
from pathlib import Path
from mathutils import Vector,Matrix,Euler
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets';OUT.mkdir(exist_ok=True);(ROOT/'textures').mkdir(exist_ok=True);SRC=Path(os.environ.get('CC0_ROOT','/workspace/work/cc0'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
def find(name):return next(SRC.rglob(name))
def load(path):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));return [o for o in bpy.data.objects if o not in before]
objects=load(find('Superhero_Female_FullBody.gltf'));rig=next(o for o in objects if o.type=='ARMATURE');rig.name='LinXiRig'
body=next(o for o in objects if o.name.startswith('Superhero'));body.name='LinXi_Anatomy';eyes=next(o for o in objects if o.name=='Eyes');brows=next(o for o in objects if o.name=='Eyebrows')
for o in objects:
 if o.type=='MESH' and o not in [body,eyes,brows]:bpy.data.objects.remove(o,do_unlink=True)
# Keep real 3D facial topology. Small proportional edits soften the licensed base's angular superhero face.
def head_shape(v,face=False):
 z=v.z
 if z>1.55:
  t=min(1,(z-1.55)/.07);v.x*=1+.035*t
  if face:
   nose=math.exp(-((v.x/.023)**2+((z-1.615)/.035)**2))
   if v.y<-.075:v.y+=.009*nose
   if z<1.60:v.x*=.96;v.z+=.004*(1-(z-1.55)/.05)
for o in [body,eyes,brows]:
 for v in o.data.vertices:head_shape(v.co,o==body)
# Original PBR cloth textures, with packed sRGB albedo and Non-Color roughness.
def material(name,c,rough=.7,metal=0,weave=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1);bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 if weave:
  size=256;im=bpy.data.images.new(name+'_Albedo',width=size,height=size);pix=[];rp=[]
  for y in range(size):
   for x in range(size):
    f=1+.025*math.sin(x*math.pi/2)*math.cos(y*math.pi/2)+.012*math.sin((x+y)*.67)
    pix.extend([min(1,k*f) for k in c]+[1]);v=rough+.025*math.sin((x-y)*math.pi/2);rp.extend([v,v,v,1])
  im.pixels.foreach_set(pix);im.filepath_raw=str(ROOT/'textures'/(name+'_Albedo.png'));im.file_format='PNG';im.save();im.source='FILE';im.reload();im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
  rm=bpy.data.images.new(name+'_Roughness',width=size,height=size);rm.colorspace_settings.name='Non-Color';rm.pixels.foreach_set(rp);rm.filepath_raw=str(ROOT/'textures'/(name+'_Roughness.png'));rm.file_format='PNG';rm.save();rm.source='FILE';rm.reload();rm.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=rm;m.node_tree.links.new(n.outputs['Color'],bs.inputs['Roughness'])
 return m
skin=material('Skin_soft_warm',(.64,.37,.235),.63);skin.node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value=.04
teal=material('Jacket_sea_green',(.035,.205,.19),.83,weave=True);cream=material('Shirt_oat_canvas',(.75,.69,.54),.89,weave=True);navy=material('Trousers_ink',(.035,.055,.078),.86,weave=True)
shoe=material('Sneakers_ivory',(.80,.76,.65),.7);sole=material('Sneaker_rubber',(.38,.43,.4),.92);hairmat=material('Hair_chestnut',(.085,.033,.019),.48);hairlight=material('Hair_soft_copper',(.16,.069,.036),.48);leather=material('Satchel_cognac',(.32,.135,.057),.69);trim=material('Leather_edge',(.48,.26,.095),.74);brass=material('Brushed_brass',(.46,.29,.10),.38,.75);ribbon=material('Ribbon_coral',(.56,.17,.08),.84)
brows.data.materials.clear();brows.data.materials.append(hairmat)
# Snapshot anatomy for continuous garment construction and fitted accessory placement.
source=body.data.copy();groups={g.index:g.name for g in body.vertex_groups};dominant={}
for v in source.vertices:
 dominant[v.index]=groups[max(v.groups,key=lambda x:x.weight).group] if v.groups else 'root'
body_bvh=BVHTree.FromPolygons([v.co for v in source.vertices],[list(p.vertices) for p in source.polygons])
def front_y(x,z,back=False):
 hit=body_bvh.ray_cast(Vector((x,1 if back else -1,z)),Vector((0,-1 if back else 1,0)))
 return (hit[0].y if hit[0] else (.13 if back else -.12))+(.035 if back else -.035)
def category(p):
 ids=list(p.vertices);z=sum(source.vertices[i].co.z for i in ids)/len(ids);x=sum(abs(source.vertices[i].co.x) for i in ids)/len(ids);names=[dominant[i] for i in ids]
 if any(n.startswith(('Head','neck')) for n in names):return 'skin'
 if all(n.startswith(('hand','index','middle','ring','pinky','thumb')) for n in names):return 'skin'
 if z<.105:return 'shoes'
 if z<.98:return 'pants'
 if x>.59:return 'skin'
 if any(n.startswith(('spine','pelvis','clavicle','upperarm','lowerarm')) for n in names):return 'jacket'
 return 'skin'
facecat={p.index:category(p) for p in source.polygons}

def garment(name,cat,mat,offset,thickness=0):
 # Duplicate the weighted source mesh, preserve UVs/weights and retain only intended faces.
 o=body.copy();o.data=source.copy();bpy.context.collection.objects.link(o);o.name=name;o.data.materials.clear();o.data.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table()
 def keep(f):
  if cat=='socks':return max(v.co.z for v in f.verts)>.065 and min(v.co.z for v in f.verts)<.205 and max(abs(v.co.x) for v in f.verts)<.23
  if cat=='jacket':return facecat[f.index]=='jacket' or (max(v.co.z for v in f.verts)>1.0 and min(v.co.z for v in f.verts)<1.06 and max(abs(v.co.x) for v in f.verts)<.31)
  if cat=='pants':return (facecat[f.index]=='pants' or (min(v.co.z for v in f.verts)<1.06 and max(abs(v.co.x) for v in f.verts)<.31))
  return facecat[f.index]==cat
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if not keep(f)],context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
 def cut(z,inner):
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,z),plane_no=(0,0,1),clear_inner=inner,clear_outer=not inner,dist=.00001)
 if cat=='jacket':cut(1.018,True)
 if cat=='pants':cut(1.045,False);cut(.145,True)
 if cat=='socks':cut(.075,True);cut(.205,False)
 if cat=='jacket':
  for x in [-.052,.052]:bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(x,0,0),plane_no=(1,0,0),clear_inner=False,clear_outer=False,dist=.00001)
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,1.125),plane_no=(0,0,1),clear_inner=False,clear_outer=False,dist=.00001)
 bm.normal_update()
 if cat=='jacket':
  for f in bm.faces:
   c=f.calc_center_median();f.material_index=1 if c.y<-.04 and abs(c.x)<.052001 and c.z>1.12499 else 0
 for v in bm.verts:
  v.co+=v.normal*offset
  if cat=='pants' and v.co.z<.46:
   center=.1114 if v.co.x>0 else -.1114
   v.co.x=center+(v.co.x-center)*1.12
 if cat=='shoes':
  for v in bm.verts:v.co.z=max(.012,v.co.z+.016);v.co.y-=.012
 if cat=='jacket':cut(1.025,True)
 if cat=='pants':cut(.15,True);cut(1.05,False)
 if cat=='socks':cut(.08,True);cut(.20,False)
 bm.to_mesh(o.data);bm.free()
 for p in o.data.polygons:
  if cat!='jacket':p.material_index=0
  p.use_smooth=True
 for mod in o.modifiers:
  if mod.type=='ARMATURE':mod.object=rig
 if thickness:
  m=o.modifiers.new('Real_fabric_thickness','SOLIDIFY');m.thickness=thickness;m.offset=-1
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_move_up(modifier=m.name)
 if o.data.uv_layers:
  for uv in o.data.uv_layers.active.data:uv.uv*=24 if cat in ['jacket','pants'] else 1
 return o
jacket=garment('Original_Tailored_Jacket','jacket',teal,.012,.003);pants=garment('Original_Tapered_Trousers','pants',navy,.012,.003);sneakers=garment('Original_Anatomical_Sneakers','shoes',shoe,.008)
socks=garment('Original_Fitted_Ankle_Socks','socks',cream,.003,.002)
# A restrained inset shirt panel uses material faces, avoiding a thick floating block.
jacket.data.materials.append(cream)
# Keep only exposed skin; remove covered geometry rather than hide intersections.
bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[f for f in bm.faces if facecat[f.index]!='skin'],context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(body.data);bm.free();body.data.materials.clear();body.data.materials.append(skin)
# Genuine facial morph targets on the modeled face.
body.shape_key_add(name='Basis');smile=body.shape_key_add(name='Smile');blink=body.shape_key_add(name='Blink')
smile_count=blink_count=0
for v in smile.data:
 if 1.56<v.co.z<1.62 and v.co.y<-.07 and .012<abs(v.co.x)<.055:v.co.z+=.006*math.exp(-((v.co.z-1.59)/.022)**2);smile_count+=1
for v in blink.data:
 if 1.645<v.co.z<1.686 and v.co.y<-.04 and .012<abs(v.co.x)<.065:v.co.z-=.008*math.exp(-((v.co.z-1.665)/.017)**2);blink_count+=1
# Licensed short hair silhouette plus original swept framing locks and ponytail.
hpath=next(p for p in SRC.rglob('Hair_SimpleParted.gltf') if 'Rigged to Head' in str(p));new=load(hpath)
for o in new:
 if o.type=='MESH' and o.data.materials:
  o.name='Hair_Sculpted_Base';o.parent=rig;o.matrix_parent_inverse=Matrix.Identity(4);o.data.materials.clear();o.data.materials.append(hairmat)
  for v in o.data.vertices:head_shape(v.co)
  for m in o.modifiers:
   if m.type=='ARMATURE':m.object=rig
 else:bpy.data.objects.remove(o,do_unlink=True)

def weight(o,bone='spine_03',by_height=False):
 o.parent=rig;o.matrix_parent_inverse=Matrix.Identity(4)
 if by_height:
  vgs={g.name:o.vertex_groups.new(name=g.name) for g in body.vertex_groups}
  for v in o.data.vertices:
   pos,normal,idx,dist=body_bvh.find_nearest(v.co);indices=source.polygons[idx].vertices;weights={};norm=0
   for i in indices:
    d=1/max(.00001,(source.vertices[i].co-pos).length);norm+=d
    for g in source.vertices[i].groups:weights[groups[g.group]]=weights.get(groups[g.group],0)+g.weight*d
   total=sum(weights.values())
   for name,w in weights.items():vgs[name].add([v.index],w/total,'REPLACE')
 else:
  g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE')
 m=o.modifiers.new('Skin','ARMATURE');m.object=rig
 for p in o.data.polygons:p.use_smooth=True
 return o

def curve(name,points,radius,mat,bone='Head',radii=None,by_height=False):
 bpy.ops.object.select_all(action='DESELECT');c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=radius;c.bevel_resolution=3;s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for i,(p,co) in enumerate(zip(s.bezier_points,points)):
  p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO';p.radius=radii[i] if radii else 1
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(mat);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return weight(o,bone,by_height)
for side in [-1,1]:
 curve('Original_face_framing_lock',[(side*.048,-.005,1.79),(side*.104,-.065,1.72),(side*.104,-.058,1.61)],.013,hairmat,radii=[1.2,1,.10])
 for k in range(3):curve('Original_hair_highlight',[(side*(.025+k*.022),.006,1.792),(side*(.065+k*.012),-.065,1.75),(side*(.075+k*.010),-.077,1.67)],.0018,hairlight,radii=[.3,1,.1])
curve('Original_short_ponytail',[(0,.10,1.71),(.025,.17,1.64),(.025,.185,1.52),(.01,.15,1.46)],.033,hairmat,radii=[.7,1,.6,.03])
# Garment collars are thin swept surfaces with skin weights.
def patch(name,verts,faces,mat,bone='spine_03',by_height=False,thickness=.002):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 if thickness:m=o.modifiers.new('Cloth_thickness','SOLIDIFY');m.thickness=thickness
 return weight(o,bone,by_height)
for side in [-1,1]:
 patch('Original_folded_collar',[(side*.015,-.043,1.477),(side*.071,-.016,1.474),(side*.105,-.087,1.405),(side*.047,-.125,1.417)],[(0,1,2,3)],cream,bone='neck_01')
 # Narrow cuffs follow forearm anatomy; smooth multi-section rings avoid block geometry.
 verts=[];faces=[]
 for x in [side*.568,side*.607]:
  for k in range(16):
   a=k/16*math.tau;verts.append((x,.052+math.cos(a)*.037,1.418+math.sin(a)*.039))
 for k in range(16):faces.append((k,(k+1)%16,(k+1)%16+16,k+16))
 patch('Original_sleeve_cuff',verts,faces,cream,bone='lowerarm_'+('l' if side>0 else 'r'),thickness=.004)
# Continuous thin collar band conceals the neckline seam and maintains fabric thickness.
verts=[];faces=[]
for z in [1.44,1.478]:
 for k in range(32):
  a=k/32*math.tau;verts.append((.073*math.cos(a),.024+.067*math.sin(a),z))
for k in range(32):faces.append((k,(k+1)%32,(k+1)%32+32,k+32))
patch('Original_continuous_collar_band',verts,faces,teal,bone='neck_01',thickness=.003)
# Fitted flexible shoulder strap, sampled against real torso front/back surface.
for back in [False,True]:
 verts=[];faces=[]
 for i in range(21):
  t=i/20;x=-.145+t*.37;z=1.46-t*.43
  for d in [-.012,.012]:verts.append((x+d,front_y(x+d,z,back),z))
 for i in range(20):faces.append((i*2,i*2+1,i*2+3,i*2+2))
 patch('Original_flexible_mail_strap',verts,faces,leather,by_height=True,thickness=.003)
# Rounded sewn mail pouch; rounded mesh corners, thin flap and small hardware.
def rounded(name,loc,scale,mat,bone='pelvis',bevel=.012):
 bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 m=o.modifiers.new('Sewn_round_corners','BEVEL');m.width=bevel;m.segments=5;bpy.ops.object.modifier_apply(modifier=m.name);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.materials.append(mat);return weight(o,bone)
rounded('Original_soft_mail_pouch',(.225,.035,1.0),(.215,.10,.205),leather)
rounded('Original_thin_envelope_flap',(.225,-.021,1.047),(.216,.008,.116),trim,bevel=.009)
rounded('Original_magnetic_clasp',(.225,-.029,1.015),(.023,.006,.027),brass,bevel=.004)
# Fine seams on pocket and pouch, never fake 2D silhouette replacements.
curve('Original_pouch_stitch',[(.133,-.029,1.08),(.133,-.029,.925),(.31,-.029,.925),(.31,-.029,1.08)],.0009,cream,bone='pelvis')
rounded('Original_jacket_patch_pocket',(-.09,front_y(-.09,1.30)-.004,1.30),(.073,.004,.076),teal,bone='spine_03',bevel=.007)
curve('Original_pocket_topstitch',[(-.125,front_y(-.125,1.33)-.007,1.33),(-.125,front_y(-.125,1.27)-.007,1.27),(-.055,front_y(-.055,1.27)-.007,1.27),(-.055,front_y(-.055,1.33)-.007,1.33)],.0007,cream,bone='spine_03')
# Original coral neck scarf, a thin folded triangular fabric rather than a thick cube.
patch('Original_coral_neckerchief',[(-.051,-.044,1.476),(.052,-.044,1.476),(.039,-.132,1.422),(.01,-.145,1.357),(-.035,-.12,1.416)],[(0,1,2,4),(4,2,3)],ribbon,bone='neck_01',thickness=.0015)
for side in [-1,1]:
 for y in [-.025,-.052,-.079]:
  curve('Original_sneaker_lace',[(side*.111-.026,y,.061),(side*.111,y-.005,.068),(side*.111+.026,y,.061)],.0018,cream,bone='foot_'+('l' if side>0 else 'r'))
# Closed anatomical sneaker outsoles with smooth elliptical perimeter and real thickness.
for side in [-1,1]:
 verts=[];faces=[]
 for z,scale in [(.004,.96),(.021,1),(.035,.985)]:
  for k in range(32):
   a=k/32*math.tau;verts.append((side*.1114+math.sin(a)*.060*scale,-.015+math.cos(a)*.151*scale,z))
 for r in range(2):
  for k in range(32):faces.append((r*32+k,r*32+(k+1)%32,(r+1)*32+(k+1)%32,(r+1)*32+k))
 faces.append(tuple(reversed(range(32))));faces.append(tuple(range(64,96)))
 patch('Original_closed_sneaker_outsole',verts,faces,sole,bone='foot_'+('l' if side>0 else 'r'),thickness=0)
# Clear any imported actions and copy only the licensed motion library's needed clips.
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
new=load(find('UAL1_Standard.glb'))
for o in new:bpy.data.objects.remove(o,do_unlink=True)
KEEP={'Idle_Loop':'Idle','Walk_Loop':'Walk','Jog_Fwd_Loop':'Run','Idle_Talking_Loop':'Talk','Interact':'Interact','Dance_Loop':'Celebrate'}
for a in list(bpy.data.actions):
 k=next((s for s in KEEP if a.name==s or a.name.startswith(s+'_Armature')),None)
 if k:a.name=KEEP[k];a.use_fake_user=True
 else:bpy.data.actions.remove(a)
# New Turn uses the complete Idle pose, with a restrained authored torso weight shift.
# This replaces v01's incomplete action; arms and non-keyed joints cannot fall back to T-pose.
turn=bpy.data.actions['Idle'].copy();turn.name='Turn';turn.use_fake_user=True
rig.animation_data_create()
for frame in range(0,61,3):
 rig.animation_data.action=bpy.data.actions['Idle'];bpy.context.scene.frame_set(frame)
 poses={n:rig.pose.bones[n].rotation_quaternion.copy() for n in ['spine_01','spine_03','neck_01']}
 rig.animation_data.action=turn
 for n,factor in [('spine_01',.055),('spine_03',.075),('neck_01',-.025)]:
  pb=rig.pose.bones[n];pb.rotation_quaternion=poses[n]@Euler((0,math.sin(frame/60*math.tau)*factor,0)).to_quaternion();pb.keyframe_insert(data_path='rotation_quaternion',frame=frame)
# Measure real evaluated outsole geometry for every integer frame before creating NLA.
sole_meshes=[o for o in bpy.data.objects if o.type=='MESH' and any(m and m.name=='Sneaker_rubber' for m in o.data.materials)]
corrections={}
for action in list(bpy.data.actions):
 rig.animation_data.action=action;rig.location.z=0
 for pb in rig.pose.bones:pb.rotation_mode='QUATERNION'
 a0,a1=map(int,action.frame_range);low=math.inf
 for frame in range(a0,a1+1):
  bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get()
  for ob in sole_meshes:
   ev=ob.evaluated_get(deps);me=ev.to_mesh();low=min(low,min((ev.matrix_world@v.co).z for v in me.vertices));ev.to_mesh_clear()
 delta=max(0,.005-low);corrections[action.name]={'sampled_min_before_m':low,'static_vertical_correction_m':delta,'method':'evaluated outsole sampling; no Foot IK claim'}
 rig.location.z=delta
 for frame in [a0,a1]:rig.keyframe_insert(data_path='location',index=2,frame=frame)
rig.location.z=0
(OUT/'ground-corrections.json').write_text(json.dumps(corrections,indent=2))
rig.animation_data_create()
for pb in rig.pose.bones:pb.rotation_mode='QUATERNION';pb.rotation_quaternion=(1,0,0,0)
rig.animation_data.action=None
for a in list(bpy.data.actions):
 track=rig.animation_data.nla_tracks.new();track.name=a.name;st=track.strips.new(a.name,0,a);st.action_frame_start=a.frame_range[0];st.action_frame_end=a.frame_range[1]
for o in bpy.data.objects:
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
for mat in bpy.data.materials:
 if mat.use_nodes:
  for n in list(mat.node_tree.nodes):
   if n.type=='TEX_IMAGE' and n.image and n.image.size[0]==0:mat.node_tree.nodes.remove(n)
# Merge compatible skinned accessories by material; preserve facial morph mesh separately.
batches={}
for o in list(bpy.data.objects):
 if o.type=='MESH' and o!=body and not o.data.shape_keys and len(o.data.materials)==1:
  batches.setdefault(o.data.materials[0].name,[]).append(o)
for name,objects in batches.items():
 if len(objects)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name='Merged_'+name
for im in bpy.data.images:
 if im.size[0]>0:
  if max(im.size)>1024:im.scale(1024,1024)
  try:im.pack()
  except RuntimeError:pass
sc=bpy.context.scene;sc.render.fps=24;sc.frame_set(0)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.type in ['MESH','ARMATURE']:o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'harbor-courier-v02.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'harbor-courier-v02.glb'),export_format='GLB',use_selection=True,export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_morph=True,export_skins=True,export_animations=True)
bpy.ops.export_scene.fbx(filepath=str(OUT/'harbor-courier-v02.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_anim=True,bake_anim_use_nla_strips=True,bake_anim_use_all_actions=False,path_mode='COPY',embed_textures=True,axis_forward='-Z',axis_up='Y')
manifest={'schema_version':1,'asset_id':'harbor-courier-v02','model_file':'harbor-courier-v02.glb','source_file':'harbor-courier-v02.blend','unit':'meter','clips':['Idle','Walk','Run','Turn','Talk','Interact','Celebrate'],'min_animation_count':7,'requirements':{'skins':True,'animated':True,'visual_review':True},'source':'Quaternius CC0 anatomy, short base hair and locomotion; original anatomically fitted jacket/trousers/shoes, collars, cuffs, pouch, flexible straps, framing hair locks and scarf; proportional facial edits.','license_note':'CC0 base inputs; original styling and newly authored geometry; no KochiGame assets','sha256':hashlib.file_digest(open(OUT/'harbor-courier-v02.glb','rb'),'sha256').hexdigest()}
(OUT/'asset_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(OUT/'report.json').write_text(json.dumps({'asset_id':manifest['asset_id'],'blender':bpy.app.version_string,'bone_count':len(rig.data.bones),'smile_vertices':smile_count,'blink_vertices':blink_count,'art_approved':False,'changes':['Fitted continuous weighted garments replace fantasy outfit','New thin collars/cuffs/seams and anatomically shaped shoes','Flexible weighted straps sampled from anatomy','Warm skin and chestnut layered hair with original framing strands','Original thin folded scarf and rounded mail pouch'],'pending':['Visual approval','All-frame deformation and sole-motion measurement','Unreal Editor import not run']},ensure_ascii=False,indent=2))
print('V02_COMPLETE',manifest['sha256'])
