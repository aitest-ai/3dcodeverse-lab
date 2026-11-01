"""Optional Blender 5.2.x source-ready replay for the V004 merchant-street extension only.

Run with a new, independent output folder:
  NOBORIBETSU_V004_WORKDIR=/path/to/extracted_v004 \
  blender -b -t 4 --python build_v004_blender_source.py

Does not overwrite V002 or V003 editable masters. This writes a V004 extension-only
.blend sourced from three verified exported GLBs; geometry remains editable in Blender.
Integration with the full V003 master requires the latter to be actually produced.
"""
import hashlib,json,os
from pathlib import Path
import bpy
root=Path(os.environ['NOBORIBETSU_V004_WORKDIR']).resolve()
assets=root/'runtime/dist/assets';meta=json.loads((root/'runtime/dist/extension_manifest.json').read_text())
if bpy.app.version[:2]!=(5,2):raise RuntimeError('Blender 5.2.x required')
out=root/'authoring/date_v004_merchant_extension.blend'
if out.exists():raise FileExistsError('Refusing to overwrite existing V004 Blender master')
for name,item in meta['models'].items():
 file=assets/name
 actual=hashlib.sha256(file.read_bytes()).hexdigest()
 if actual!=item['sha256']:raise ValueError('Model integrity mismatch: '+name)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['v004_status']='exterior-only author-estimated candidate; NOT surveyed or photogrammetry'
scene['source_origin']='V002 ENU origin; GLB importer converts EUS to Blender axes'
scene['route_length_m']=meta['route_new_length_m']
scene['route_add_m']=meta['added_length_m']
for tag,name in [('ROAD','v004_merchant_road.glb'),('FACADES','v004_merchant_facades.glb'),('SIGNS','v004_merchant_signs.glb')]:
 before=set(bpy.data.objects)
 bpy.ops.import_scene.gltf(filepath=str(assets/name))
 imported=set(bpy.data.objects)-before
 collection=bpy.data.collections.new('V004_'+tag)
 scene.collection.children.link(collection)
 for obj in imported:
  for c in list(obj.users_collection):c.objects.unlink(obj)
  collection.objects.link(obj)
  obj['v004_source_glb_sha256']=meta['models'][name]['sha256']
  obj['v004_estimated']=True
scene['unavailable_baseline']='Full V003 native Blender master not included; do not imply whole-scene authoring acceptance.'
scene['interiors_open']=False;scene['third_person']=False
out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=False)
print('V004_EXTENSION_BLENDER_MASTER_WRITTEN',out)