"""Blender 5.2 source-ready, NOT executed in this delivery.

Blender 5.2.x command (after extracting V008 Runtime as /project):
  NOBORIBETSU_V008_ROOT=/project blender -b -t 4 --python blender_v008_facade_master.py

Only creates independent facade master: /project/authoring/v008_facades_imported_master.blend.
Does not claim the entire V002-V008 world has been rebuilt. No old file overwritten.
"""
from __future__ import annotations
import os,hashlib,json
from pathlib import Path
import bpy

EXPECTED='ff6725b1ecb22b455203c69dd4dd194f68c2b356ce17364ad89e09941d4ca4ea'
root_string=os.environ.get('NOBORIBETSU_V008_ROOT')
if not root_string:raise RuntimeError('Set NOBORIBETSU_V008_ROOT explicitly')
root=Path(root_string).resolve();src=root/'dist/assets/v008_waraji_architecture.glb'
out=root/'authoring/v008_facades_imported_master.blend'
qa=root/'authoring/v008_facades_blender_import_qa.json'
if bpy.app.version[:2]!=(5,2):raise RuntimeError('Require Blender 5.2.x')
if not src.is_file():raise FileNotFoundError(src)
if hashlib.sha256(src.read_bytes()).hexdigest()!=EXPECTED:raise RuntimeError('Source GLB SHA mismatch')
if out.exists() or qa.exists():raise FileExistsError('Refusing to overwrite prior Blender output')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(src))
meshes=[o for o in bpy.data.objects if o.type=='MESH']
if len(meshes)<21:raise RuntimeError(f'Expected >=21 imported mesh objects; got {len(meshes)}')
collections={name:bpy.data.collections.new(name) for name in ('V007_IMMUTABLE_17_MESHES','V008_PHOTO_GUIDED_ADDITIONS')}
for c in collections.values():bpy.context.scene.collection.children.link(c)
adds=[]
for ob in meshes:
 target=collections['V008_PHOTO_GUIDED_ADDITIONS' if ob.name.startswith('v008_') else 'V007_IMMUTABLE_17_MESHES']
 for c in list(ob.users_collection):c.objects.unlink(ob)
 target.objects.link(ob)
 if ob.name.startswith('v008_'):adds.append(ob.name)
if len(adds)<4:raise RuntimeError('V008 appended geometry not found or renamed unexpectedly: '+str(adds))
bpy.context.scene['provenance']='V008 historical photo guided author estimates; official photo 2018, current post-2025 refit unverified'
bpy.context.scene['collision_preservation']='Separate visual-only facade master; frozen V007 runtime collisions untouched'
bpy.context.scene['official_photo_reference']='https://edo-trip.jp/wp/wp-content/uploads/2018/04/f0272006b776b4fd294606a2d4a80622-800x600.jpg'
bpy.ops.file.pack_all();out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=False)
if not out.is_file() or out.stat().st_size<1024:raise RuntimeError('Blender master missing')
report={'schema':'date-v008-facade-blender-import/1','status':'IMPORTED_EDITABLE_FACADE_MASTER_NOT_FULL_WORLD',
 'source_sha256':EXPECTED,'blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'all_imported_meshes':len(meshes),'new_meshes':adds,'blender_version':bpy.app.version_string,
 'not_tested':['Cycles visual review','complete world re-export','Android','WebGL2']}
qa.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))