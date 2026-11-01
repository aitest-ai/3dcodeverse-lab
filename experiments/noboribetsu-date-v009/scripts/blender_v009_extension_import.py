#!/usr/bin/env python3
"""Run with Blender 5.2.x only, for editable V009 FACADES source.

Example:
 blender -b --python blender_v009_extension_import.py -- \
   /path/to/v009_utsuroi_facade.glb /new/output/V009_Utsuroi_Architecture.blend

This does NOT merge into the private V002 complete scene/master. No claim of
Cycles visual acceptance. The original V008 GLB remains separately archived.
"""
from pathlib import Path
import sys,json
import bpy

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if len(args)!=2:raise SystemExit('Expected: input_v009_glb output_new_blend')
src,dst=map(lambda p:Path(p).resolve(),args)
if not src.is_file() or src.suffix.lower()!='.glb':raise FileNotFoundError(src)
if dst.exists():raise FileExistsError('Refusing to overwrite existing .blend: '+str(dst))
if bpy.app.version[:2]!=(5,2):raise RuntimeError('Expected Blender 5.2.x; got '+bpy.app.version_string)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(src))
meshes=[x for x in bpy.data.objects if x.type=='MESH']
if len(meshes)!=25:raise RuntimeError(f'Expected 25 source meshes, imported {len(meshes)}')
if sum(len(x.data.polygons) for x in meshes)!=17104:
 raise RuntimeError('Native mesh triangle count unexpectedly changed')

coll_old=bpy.data.collections.new('V009_ARCHIVED_V008_AND_PRESERVED_ASSETS')
coll_edit=bpy.data.collections.new('V009_UTSUROI_AUTHOR_ESTIMATED_REPAIR')
bpy.context.scene.collection.children.link(coll_old)
bpy.context.scene.collection.children.link(coll_edit)
for ob in meshes:
 target=coll_edit if ob.name.startswith('v009_') else coll_old
 for coll in list(ob.users_collection):coll.objects.unlink(ob)
 target.objects.link(ob)
 ob['noboribetsu_v009_provenance']='new V009 geometry; author-estimated' if target==coll_edit else 'source V008 frozen'

scene=bpy.context.scene
scene['project']='Noboribetsu Date Jidaimura V009 Utsuroi facade candidate'
scene['source_glb']=src.name
scene['known_location']='OSM way/283905580'
scene['source_use_reference']='https://edo-trip.jp/facility/utsuroi-kan/'
scene['exterior_evidence']='insufficient to claim 2026 exact appearance'
scene['route_collision']='separate runtime, not modified by this import'
scene['visual_qa']='not yet run Cycles; do not claim full park Blender-native'
scene['v009_expected_triangles']=17104
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=False)
if not dst.is_file() or dst.stat().st_size<1000:raise RuntimeError('No Blender source file generated')
print('V009_EXTENSION_BLEND_SAVED',json.dumps({'path':str(dst),'mesh_count':len(meshes),'triangles':17104}))