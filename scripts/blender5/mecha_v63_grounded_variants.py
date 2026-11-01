"""Generate v6.3 corrected enemy mechs from original verified v6.2 BLEND mothers.

Changes only active Run root grounding curves and tiny heavy-armor clearances,
without rebaking PBR, removing detail meshes or altering the 15-bone rig.
"""
import bpy,json,hashlib,struct,os,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SRC=Path(os.environ.get('V63_MODEL_SOURCE','.v63-source'))
OUT=Path(os.environ.get('V63_FIXED_OUTPUT','outputs/v63_fixed'))
OUT.mkdir(parents=True,exist_ok=True)
ROLES=('assault','ranger','heavy')
HEAD_SHIELD_OFFSET_M=.15

def foot_min_z(scene):
 deps=bpy.context.evaluated_depsgraph_get()
 mins=[]
 for ob in bpy.data.objects:
  if ob.type!='MESH' or not any(q in ob.name.lower() for q in ['footl','footr','toe','heel','heavywidefoot']):continue
  ev=ob.evaluated_get(deps)
  me=ev.to_mesh()
  if not me.vertices:ev.to_mesh_clear();continue
  mins.append(min((ev.matrix_world@v.co).z for v in me.vertices))
  ev.to_mesh_clear()
 if not mins:raise RuntimeError('No sole/heel geometry')
 return min(mins)

def bounds_contact(a,b):
 deps=bpy.context.evaluated_depsgraph_get()
 def sample(ob):
  ev=ob.evaluated_get(deps);me=ev.to_mesh()
  verts=[ev.matrix_world@v.co for v in me.vertices]
  faces=[tuple(p.vertices) for p in me.polygons]
  ev.to_mesh_clear()
  lo=[min(v[i] for v in verts) for i in range(3)]
  hi=[max(v[i] for v in verts) for i in range(3)]
  return verts,faces,lo,hi
 va,fa,al,ah=sample(a);vb,fb,bl,bh=sample(b)
 overlap=[min(ah[i],bh[i])-max(al[i],bl[i]) for i in range(3)]
 if min(overlap)<=0:return 0
 return len(BVHTree.FromPolygons(va,fa).overlap(BVHTree.FromPolygons(vb,fb)))

report={'schema':'taipei-v63-fixed-rigged-enemies',
  'source':'verified Blender 5.2.3 editable v6.2 mothers',
  'note':'Pose/triangle QA is evidence for review, not actual Windows WebGPU FPS or exhaustive clearance.',
  'roles':{}}
for role in ROLES:
 src=SRC/role/('enemy_'+role+'_v62.blend')
 if not src.is_file():raise FileNotFoundError(src)
 bpy.ops.wm.open_mainfile(filepath=str(src.resolve()))
 scene=bpy.context.scene
 rig=bpy.data.objects.get('MechaRig')
 assert rig and rig.type=='ARMATURE' and len(rig.data.bones)==15
 tracks=list(rig.animation_data.nla_tracks)
 assert len(tracks)>=6
 runtrack=next(t for t in tracks if t.name.lower().split('_')[-1]=='run')
 assert len(runtrack.strips)==1
 run_action=runtrack.strips[0].action
 changes=[]
 if role=='heavy':
  for ob in bpy.data.objects:
   n=ob.name
   if ob.type!='MESH':continue
   if n.startswith(('V62_HeavyBallisticShield','V62_HeavyShieldSubframe','V62_HeavyShieldRib',
      'V62_HeavyShoulderCathedralL','V62_HeavyShoulderFaceL','V62_HeavyShoulderLouverL')):
    for vertex in ob.data.vertices:vertex.co.x+=HEAD_SHIELD_OFFSET_M
    changes.append(n)
  assert len(changes)>=7, ('Missing heavy accessories',changes)
  bpy.context.view_layer.update()
 for t in tracks:t.mute=True
 rig.animation_data.action=run_action
 height_qa=[]
 for f in range(1,49):
  scene.frame_set(f)
  before=foot_min_z(scene)
  correction=0.0
  for retry in range(3):
   scene.frame_set(f)
   lower=foot_min_z(scene)
   if lower>=.005:break
   delta=max(0,min(.28,.012-lower))
   root=rig.pose.bones['root']
   root.location.y+=delta
   root.keyframe_insert(data_path='location',frame=f)
   correction+=delta
  scene.frame_set(f)
  after=foot_min_z(scene)
  height_qa.append({'frame':f,'before':round(before,5),'after':round(after,5),
    'added_root_local_y':round(correction,5)})
 rig.animation_data.action=None
 for t in tracks:t.mute=False
 if min(x['after'] for x in height_qa)<-.012:
  raise RuntimeError('Grounded Run still penetrates '+role+' '+str(min(x['after'] for x in height_qa)))
 contact_qa=[]
 role_pairs= [('HeavyBallisticShield','HeavyChestVault'),
  ('HeavyShoulderCathedralL','HeavyChestVault')] if role=='heavy' else []
 for t in tracks:t.mute=(t is not runtrack)
 for frame in (7,22,38):
  scene.frame_set(frame)
  for aa,bb in role_pairs:
   a,b=bpy.data.objects.get('V62_'+aa),bpy.data.objects.get('V62_'+bb)
   if not a or not b:raise RuntimeError('Missing contact pair')
   contact_qa.append({'frame':frame,'pair':[aa,bb],
     'triangle_intersections':bounds_contact(a,b)})
 for t in tracks:t.mute=False
 role_dir=OUT/role;role_dir.mkdir(exist_ok=True)
 scene['version']='6.3'
 scene['previous']='v6.2 editable model; animation/clipping QA repair only'
 scene['shape_review']='candidate, actual Workbench rendering; Windows WebGPU still not accepted'
 bpy.ops.file.pack_all()
 scene.frame_set(1)
 blend=role_dir/('enemy_'+role+'_v63.blend')
 bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
 bpy.ops.object.select_all(action='DESELECT')
 for ob in bpy.data.objects:
  if ob is rig or (ob.type=='MESH' and not ob.name.startswith('BAKE_ONLY_HIGH') and not ob.hide_render):ob.select_set(True)
 bpy.context.view_layer.objects.active=rig
 glb=role_dir/('enemy_'+role+'_v63.glb')
 bpy.ops.export_scene.gltf(filepath=str(glb.resolve()),export_format='GLB',use_selection=True,
  export_animations=True,export_animation_mode='ACTIONS',export_skins=True,
  export_cameras=False,export_lights=False)
 raw=glb.read_bytes();assert raw[:4]==b'glTF'
 ln,kind=struct.unpack_from('<I4s',raw,12);assert kind==b'JSON'
 doc=json.loads(raw[20:20+ln]);names=sorted(x['name'] for x in doc.get('animations',[]))
 assert names==sorted('Mecha_'+n for n in ('Idle','Run','Fire','Hit','Dodge','Punch'))
 assert len(doc.get('skins',[]))>=1 and len(doc['meshes'])>=260
 assert sum(bool(m.get('normalTexture')) for m in doc.get('materials',[]))>=8
 camera_data=bpy.data.cameras.new('V63PosePreviewCamera')
 camera=bpy.data.objects.new('V63PosePreviewCamera',camera_data)
 bpy.context.collection.objects.link(camera)
 scene.camera=camera;camera_data.type='ORTHO';camera_data.ortho_scale=4.2
 camera.location=(4,-5.6,3.8)
 camera.rotation_euler=(Vector((0,0,1.35))-camera.location).to_track_quat('-Z','Y').to_euler()
 scene.render.engine='BLENDER_WORKBENCH';scene.render.film_transparent=True
 scene.render.resolution_x=620;scene.render.resolution_y=620
 scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True
 for name in ('Run','Fire','Hit','Dodge'):
  target_track=next(t for t in tracks if t.name.lower().split('_')[-1]==name.lower())
  for t in tracks:t.mute=(t is not target_track)
  scene.frame_set(22)
  dest=role_dir/('pose_'+name.lower()+'_frame22.png')
  scene.render.filepath=str(dest.resolve())
  bpy.ops.render.render(write_still=True)
  assert dest.stat().st_size>1500
  for t in tracks:t.mute=False
 report['roles'][role]={
  'original_v62_blend_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
  'glb_sha256':hashlib.sha256(raw).hexdigest(),
  'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
  'rendered_clips':['Run','Fire','Hit','Dodge'],'animations':names,
  'meshes':len(doc['meshes']),'armature_bones':len(rig.data.bones),
  'changed_parts':changes,
  'run_before_min_z':round(min(x['before'] for x in height_qa),5),
  'run_after_min_z':round(min(x['after'] for x in height_qa),5),
  'run_correction_max':round(max(x['added_root_local_y'] for x in height_qa),5),
  'run_per_frame_qa':height_qa,'heavy_contact_qa':contact_qa,
  'human_approval':'not yet; generated actual Blender poses only'
 }
 print('V63_ACTUAL_BLENDER_MODEL_PASS',role,
  report['roles'][role]['run_after_min_z'],contact_qa,flush=True)
(OUT/'report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print('V63_THREE_NEW_EDITABLE_BLENDER_MODELS_PASS',len(report['roles']),flush=True)
