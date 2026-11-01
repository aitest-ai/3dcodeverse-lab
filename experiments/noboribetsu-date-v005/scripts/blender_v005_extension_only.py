"""Blender 5.2 LTS SOURCE-READY tool. Run through Blender Python; not executed in this chat host.

Usage:
  DATE_V005_ROOT=/path/to/extracted/V005/runtime blender -b -t 4 \
    --python blender_v005_extension_only.py

Creates independent, editable extension-only scene. Does not alter V004, V003 or V002.
It never claims a complete V005 main/master .blend. Preserve original GLB in runtime.
"""
from pathlib import Path
import os, json, hashlib
import bpy

root=Path(os.environ['DATE_V005_ROOT']).resolve()
dist=root/'dist';models=dist/'assets';meta=json.loads((dist/'v005_manifest.json').read_text())
assert bpy.app.version[:2]==(5,2),f'Blender 5.2 required: {bpy.app.version_string}'
assert meta['schema']=='noboribetsu-date-v005-east/1'
output=root/'authoring'/'v005_east_extension_only.blend'
if output.exists():raise FileExistsError('Never overwrite existing V005 source')
output.parent.mkdir(parents=True,exist_ok=True)
for name,m in meta['models'].items():
 p=models/name
 assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'],name
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.name='V005 east merchant-street source-ready extension'
scene['provenance']='OSM locations + original authored exterior; roof dimensions artist-estimated'
scene['does_not_contain']='V002/V003/V004 full master, interiors, survey-grade facade'
scene['version']='V005-east-candidate-r1'
for filename,label in [('v005_east_road.glb','ROAD_BOTH'),('v005_east_facades.glb','FACADES_B_ONLY'),('v005_east_signs.glb','SIGNS_B_ONLY')]:
 before=set(bpy.data.objects)
 bpy.ops.import_scene.gltf(filepath=str(models/filename))
 objects=[o for o in bpy.data.objects if o not in before]
 col=bpy.data.collections.new(label)
 scene.collection.children.link(col)
 for obj in objects:
  for prev in list(obj.users_collection):prev.objects.unlink(obj)
  col.objects.link(obj)
  obj['imported_from']=filename
  obj['editable_source_kind']='GLB imported to Blender; mesh geometry can be refined'
assert bpy.data.objects
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=False)
print('V005_SOURCE_READY_EXTENSION_ONLY',output)