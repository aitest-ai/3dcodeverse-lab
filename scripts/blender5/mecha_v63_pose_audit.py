"""Blender 5.2.3 genuine animated v6.2 enemy audit for v6.3.

Twelve poses for each of three original editable rigs. Reports candidate mesh
interference using world-space AABB broadphase + triangle BVH narrowphase.
These are *engineering signals*, not proof of visible clearance or gameplay FPS.
"""
import bpy, os, json, hashlib, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

src=Path(os.environ.get('V63_MODEL_SOURCE','.v63-source'))
out=Path(os.environ.get('V63_AUDIT_OUTPUT','outputs/v63_pose_audit'))
out.mkdir(parents=True,exist_ok=True)
roles=('assault','ranger','heavy')
clips=('Run','Fire','Hit','Dodge')
frames=(7,22,38)
pairs={
 'assault':[('AssaultElbowBladeL','AssaultNarrowBreastplate'),
           ('AssaultElbowBladeR','AssaultNarrowBreastplate'),
           ('AssaultElbowBladeL','AssaultShinSplitterL'),
           ('AssaultElbowBladeR','AssaultShinSplitterR')],
 'ranger':[('RangerRailgunChassis','RangerBackFin'),
           ('RangerRailgunChassis','RangerCalfSensorR'),
           ('RangerRailgunChassis','RangerChestReadout0')],
 'heavy':[('HeavyBallisticShield','HeavyChestVault'),
          ('HeavyBallisticShield','HeavyShinIronL'),
          ('HeavyBallisticShield','HeavyWideFootL'),
          ('HeavyShoulderCathedralL','HeavyChestVault')]
}

def sampled(ob,depsgraph):
 ev=ob.evaluated_get(depsgraph)
 me=ev.to_mesh()
 try:
  verts=[ev.matrix_world @ v.co for v in me.vertices]
  faces=[tuple(p.vertices) for p in me.polygons]
  if not verts or not faces:return None
  lo=[min(v[i] for v in verts) for i in range(3)]
  hi=[max(v[i] for v in verts) for i in range(3)]
  return verts,faces,lo,hi
 finally:
  ev.to_mesh_clear()

def contact(a,b):
 if not a or not b:return None
 va,fa,alo,ahi=a;vb,fb,blo,bhi=b
 overlap=[min(ahi[i],bhi[i])-max(alo[i],blo[i]) for i in range(3)]
 if min(overlap)<=0:return {'aabb_overlap_m3':0,'triangle_intersections':0}
 tree_a=BVHTree.FromPolygons(va,fa,all_triangles=False,epsilon=.00002)
 tree_b=BVHTree.FromPolygons(vb,fb,all_triangles=False,epsilon=.00002)
 return {'aabb_overlap_m3':round(math.prod(overlap),7),
         'triangle_intersections':len(tree_a.overlap(tree_b))}

report={'schema':'mech-v63-motion-contact-audit',
        'basis':'actual Blender 5.2.3 evaluated, skinned scene geometry',
        'notes':['BVH triangle intersections only; intersecting AABBs are NOT confirmed penetration.',
                 'Nested/fully-contained meshes and physical collision resolution not proven.',
                 'Workbench images are genuine Blender renders, NOT Taipei Windows WebGPU gameplay.'],
        'roles':{}}
for role in roles:
 path=src/role/('enemy_'+role+'_v62.blend')
 if not path.is_file():raise FileNotFoundError(str(path))
 bpy.ops.wm.open_mainfile(filepath=str(path.resolve()))
 scene=bpy.context.scene
 rig=bpy.data.objects.get('MechaRig')
 assert rig and len(rig.data.bones)==15 and rig.animation_data
 tracklist=list(rig.animation_data.nla_tracks)
 names=[t.name for t in tracklist]
 assert len(tracklist)>=6,(role,names)
 cam_data=bpy.data.cameras.new('V63PoseAuditCamera')
 cam=bpy.data.objects.new('V63PoseAuditCamera',cam_data)
 bpy.context.collection.objects.link(cam)
 scene.camera=cam;cam_data.type='ORTHO';cam_data.ortho_scale=4.2
 cam.location=(4.0,-5.6,3.8)
 cam.rotation_euler=(Vector((0,0,1.35))-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.engine='BLENDER_WORKBENCH'
 scene.render.film_transparent=True
 scene.render.resolution_x=540;scene.render.resolution_y=540
 scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG'
 scene.display.shading.color_type='MATERIAL'
 scene.display.shading.light='STUDIO'
 scene.display.shading.show_cavity=True
 folder=out/role;folder.mkdir(exist_ok=True)
 entry={'clips':names,'samples':[],'model_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 for clip in clips:
  matching=[t for t in tracklist if t.name.lower().split('_')[-1]==clip.lower()]
  if len(matching)!=1:raise RuntimeError((role,clip,names))
  for tr in tracklist:tr.mute=(tr is not matching[0])
  for frame in frames:
   scene.frame_set(frame)
   bpy.context.view_layer.update()
   depsgraph=bpy.context.evaluated_depsgraph_get()
   names_needed={'V62_'+n for pair in pairs[role] for n in pair}
   names_needed.update(o.name for o in bpy.data.objects if o.type=='MESH' and
      any(s in o.name.lower() for s in ['footl','footr','toe','heel','heavywidefoot']))
   geometry={}
   for name in names_needed:
    ob=bpy.data.objects.get(name)
    if ob and ob.type=='MESH':geometry[name]=sampled(ob,depsgraph)
   footprints=[]
   for name,value in geometry.items():
    if value and any(s in name.lower() for s in ['footl','footr','toe','heel','heavywidefoot']):
     footprints.append(value[2][2])
   contacts=[]
   for aa,bb in pairs[role]:
    a,b='V62_'+aa,'V62_'+bb
    if not geometry.get(a) or not geometry.get(b):raise RuntimeError('Missing source parts '+a+' / '+b)
    c=contact(geometry[a],geometry[b])
    contacts.append({'pair':[aa,bb],**c})
   frameinfo={'clip':clip,'frame':frame,
       'lowest_sole_z_m':round(min(footprints),4) if footprints else None,
       'contacts':contacts}
   target=folder/('pose_'+clip.lower()+'_frame_'+str(frame).zfill(2)+'.png')
   scene.render.filepath=str(target.resolve())
   bpy.ops.render.render(write_still=True)
   assert target.stat().st_size>1500
   frameinfo['preview_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
   entry['samples'].append(frameinfo)
  for tr in tracklist:tr.mute=False
 report['roles'][role]=entry
 print('V63_POSE_AUDIT_ROLE_PASS',role,
       {'samples':len(entry['samples']),
        'mesh_contact_samples':sum(sum(c['triangle_intersections']>0 for c in s['contacts']) for s in entry['samples'])},flush=True)
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('V63_POSE_AUDIT_REAL_BLENDER_COMPLETE',sum(len(x['samples']) for x in report['roles'].values()),flush=True)
