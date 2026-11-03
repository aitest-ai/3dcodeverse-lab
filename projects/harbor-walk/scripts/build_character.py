"""Build original Harbor Courier design using licensed CC0 anatomy/outfit/locomotion.
Run CC0_ROOT=/path/to/cc0 blender -b --factory-startup --python scripts/build_character.py
Keeps every upstream asset untouched. Tested on Blender 4.3.2 (not 5.2.3).
"""
import bpy,bmesh,math,json,os,hashlib,shutil
from pathlib import Path
from mathutils import Vector,Matrix,Euler
ROOT=Path(__file__).resolve().parents[1]; SRC=Path(os.environ.get('CC0_ROOT','/workspace/work/cc0'));OUT=ROOT/'assets';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
def find(name):return next(SRC.rglob(name))
def imp(path):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));return [o for o in bpy.data.objects if o not in before]
base=imp(find('Superhero_Female_FullBody.gltf'));rig=next(o for o in base if o.type=='ARMATURE');rig.name='HarborCourierRig'
body=next(o for o in base if o.name.startswith('Superhero'));body.name='Courier_Anatomy'
for o in list(base):
 if o.type=='MESH' and o not in [body] and o.name not in ['Eyes','Eyebrows']:bpy.data.objects.remove(o,do_unlink=True)
# Keep anatomically modelled face and neck, while licensed tailored clothes cover the body.
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if max(v.co.z for v in f.verts)<1.465],context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(body.data);bm.free()
# Small genuine facial blend shape, retained in GLB and exposed in the viewer.
body.shape_key_add(name='Basis');smile=body.shape_key_add(name='Smile')
changed=0
for v in smile.data:
 x,y,z=v.co
 if 1.58<z<1.66 and y<-.04 and .018<abs(x)<.07:
  v.co.z+=.007*max(0,1-abs(z-1.62)/.04);changed+=1

def rebind(o):
 o.parent=rig;o.matrix_parent_inverse=Matrix.Identity(4)
 for mod in o.modifiers:
  if mod.type=='ARMATURE':mod.object=rig

def import_meshes(path):
 new=imp(path)
 meshes=[o for o in new if o.type=='MESH']
 for o in new:
  if o.type=='MESH':rebind(o)
 for o in new:
  if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
 return meshes
clothes=import_meshes(find('Female_Peasant.gltf'))
hairpath=next(p for p in SRC.rglob('Hair_Buns.gltf') if 'Rigged to Head' in str(p));hair=import_meshes(hairpath)
for o in hair:o.name='Courier_Hair'
for o in clothes:
 if 'Body' in o.name:o.name='Courier_Shirt'
 elif 'Legs' in o.name:o.name='Courier_Trousers'
 elif 'Feet' in o.name:o.name='Courier_Shoes'
 else:o.name='Courier_SleevesHands'
# Reauthor the shirt/trouser colour palette from source shading; preserve UV and normal maps.
def recolor_material(o,color):
 for idx,old in enumerate(list(o.data.materials)):
  m=old.copy();m.name=o.name+'_Material';o.data.materials[idx]=m
  for n in m.node_tree.nodes:
   if n.type!='TEX_IMAGE' or not n.image or 'BaseColor' not in n.image.name:continue
   src=n.image;im=src.copy();im.name=o.name+'_Albedo';w,h=im.size
   pix=list(im.pixels[:])
   for i in range(0,len(pix),4):
    lum=max(.12,min(1,(pix[i]+pix[i+1]+pix[i+2])/3*1.65))
    for c in range(3):pix[i+c]=color[c]*lum
   im.pixels.foreach_set(pix);im.pack();n.image=im
  bs=m.node_tree.nodes.get('Principled BSDF')
  if bs:bs.inputs['Roughness'].default_value=.83
for o in clothes:
 if 'Shirt' in o.name:recolor_material(o,(.18,.48,.42))
 if 'Trousers' in o.name:recolor_material(o,(.58,.53,.40))
 if 'Shoes' in o.name:recolor_material(o,(.15,.21,.20))
# Remove unneeded imported T-pose actions before the shared animation library.
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
anew=imp(find('UAL1_Standard.glb'))
for o in anew:bpy.data.objects.remove(o,do_unlink=True)
KEEP={'Idle_Loop':'Idle','Walk_Loop':'Walk','Jog_Fwd_Loop':'Run','Idle_Talking_Loop':'Talk','Interact':'Interact','Dance_Loop':'Celebrate'}
for a in list(bpy.data.actions):
 k=next((old for old in KEEP if a.name==old or a.name.startswith(old+'_Armature')),None)
 if k:a.name=KEEP[k];a.use_fake_user=True
 else:bpy.data.actions.remove(a)
# Original leather mail satchel, scarf, stitched pocket and enamel badge, skinned to torso bones.
def mat(name,color,rough=.7,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
leather=mat('Satchel_ochre_leather',(.43,.23,.095));edge=mat('Canvas_binding',(.74,.58,.30));scarf=mat('Saffron_cotton',(.86,.53,.16));badge=mat('Enamel_sea',(.04,.25,.24),.3,.25)
def rigid(o,bone,material):
 o.data.materials.clear();o.data.materials.append(material);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE');m=o.modifiers.new('Skin','ARMATURE');m.object=rig;o.parent=rig
 for f in o.data.polygons:f.use_smooth=True
 return o

def box(name,loc,scale,bone,material,bevel=.02):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 m=o.modifiers.new('Rounded seams','BEVEL');m.width=bevel;m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name);return rigid(o,bone,material)
box('Original_mail_satchel',(.19,.15,1.01),(.27,.12,.25),'pelvis',leather)
box('Original_satchel_flap',(.19,.224,1.08),(.28,.022,.12),'pelvis',edge,.012)
box('Original_satchel_clasp',(.19,.242,1.06),(.035,.012,.04),'pelvis',badge,.006)
# Diagonal strap across the front torso, parented to chest; a proper skinned mesh.
a=Vector((-.15,-.13,1.44));b=Vector((.22,-.14,1.0));mid=(a+b)/2
strap=box('Original_mail_strap',mid,(.033,.018,(a-b).length),'spine_03',leather,.006)
# rotate already transformed geometry around midpoint, using local global coordinates
axis=Vector((0,0,1)).rotation_difference((a-b).normalized()).to_matrix()
for v in strap.data.vertices:v.co=axis@(v.co-mid)+mid
# Folded neckerchief with a short asymmetric tail.
box('Original_neckerchief',(.0,-.054,1.49),(.15,.15,.04),'neck_01',scarf,.02)
box('Original_scarf_tail',(.055,-.15,1.405),(.07,.028,.16),'spine_03',scarf,.012)
box('Original_pocket',(-.105,-.137,1.30),(.075,.018,.085),'spine_03',edge,.006)
# All actions are in-place, skeleton animation; root is never animated through gameplay code.
rig.animation_data_create()
turn=bpy.data.actions.new('Turn');turn.use_fake_user=True
rig.animation_data.action=turn
for pb in rig.pose.bones:pb.rotation_mode='QUATERNION';pb.rotation_quaternion=(1,0,0,0)
for frame in range(0,33,4):
 phase=frame/32*math.pi*2
 for name in ['pelvis','spine_01','spine_02']:
  pb=rig.pose.bones[name];pb.rotation_quaternion=Euler((0,math.sin(phase)*(.12 if name=='pelvis' else .06),0)).to_quaternion();pb.keyframe_insert(data_path='rotation_quaternion',frame=frame)
 for side,sign in [('l',1),('r',-1)]:
  pb=rig.pose.bones['thigh_'+side];pb.rotation_quaternion=Euler((math.sin(phase)*.12*sign,0,0)).to_quaternion();pb.keyframe_insert(data_path='rotation_quaternion',frame=frame)
for pb in rig.pose.bones:pb.rotation_quaternion=(1,0,0,0)
rig.animation_data.action=None
for action in list(bpy.data.actions):
 track=rig.animation_data.nla_tracks.new();track.name=action.name
 strip=track.strips.new(action.name,0,action);strip.action_frame_start=action.frame_range[0];strip.action_frame_end=action.frame_range[1]
sc=bpy.context.scene;sc.render.fps=24;sc.frame_set(0)
# Consolidate material references and embed all texture bytes; repair missing optional eye normal by removing that link.
for m in bpy.data.materials:
 if not m.use_nodes:continue
 for n in list(m.node_tree.nodes):
  if n.type=='TEX_IMAGE' and n.image:
   im=n.image
   if im.size[0]==0:
    m.node_tree.nodes.remove(n)
for im in bpy.data.images:
 if im.size[0]>0:
  if max(im.size)>1024:im.scale(1024,1024)
  try:im.pack()
  except Exception:pass
for o in bpy.data.objects:
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
# Keep only production objects and armature, never import preview spheres or mannequins.
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.type in ['MESH','ARMATURE']:o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'harbor-courier.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'harbor-courier.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_morph=True,export_skins=True)
shutil.copyfile(OUT/'harbor-courier.glb',ROOT/'public/models/harbor-courier.glb')
manifest={'schema_version':1,'asset_id':'harbor-courier','model_file':'harbor-courier.glb','source_file':'harbor-courier.blend','unit':'meter','coordinate_system':'Blender Z-up / glTF Y-up; visual forward checked in browser','source':'Original Harbor Courier styling/accessories; Quaternius CC0 anatomy, hair, outfit and locomotion. Pipeline informed by 3dcodeverse-lab aviator_human.py; independently implemented.','clips':['Idle','Walk','Run','Talk','Interact','Celebrate','Turn'],'min_animation_count':7,'requirements':{'skins':True,'animated':True,'visual_review':True},'license_note':'CC0 source geometry/animations plus original accessories; see THIRD_PARTY_NOTICES.md','sha256':hashlib.file_digest(open(OUT/'harbor-courier.glb','rb'),'sha256').hexdigest()}
(OUT/'asset_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(OUT/'report.json').write_text(json.dumps({'blender_version':bpy.app.version_string,'bone_count':len(rig.data.bones),'smile_vertices_changed':changed,'clips':manifest['clips'],'art_approved':False,'known_limits':['No foot IK','Satchel rigidly weighted to pelvis','CC0 outfit is adapted, not wholly original topology','Visual inspection required; structural validation alone is insufficient']},indent=2))
print('HARBOR_ASSET_COMPLETE',manifest['sha256'])
