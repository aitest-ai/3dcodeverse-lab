"""Run in Blender background, one asset per process. Keep all upstream masters immutable."""
import bpy,json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];aid=sys.argv[sys.argv.index('--')+1];entry=next(x for x in json.loads((R/'library-v04/intake.json').read_text())['entries'] if x['id']==aid);dst=R/'library-v04'/aid/entry['version'];master=R/entry['editable']['path']
if entry['editable']['kind']=='derived-blender-working-copy':
 if master.exists():bpy.ops.wm.open_mainfile(filepath=str(master))
 else:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(dst/'model.glb'));bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True)
else:bpy.ops.wm.open_mainfile(filepath=str(master))
rigs=[]
for o in bpy.data.objects:
 if o.type!='ARMATURE':continue
 rigs.append({'object':o.name,'matrix_world':list(sum((list(row) for row in o.matrix_world),[])),'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'head_local':list(b.head_local),'tail_local':list(b.tail_local),'length':b.length,'rest_matrix_row_major':list(sum((list(row) for row in b.matrix_local),[]))} for b in o.data.bones]})
imgs=[]
for im in bpy.data.images:
 if im.type not in ['IMAGE','UV_TEST']:continue
 try:im.pixels[0];ok=im.has_data
 except Exception:ok=False
 imgs.append({'name':im.name,'dimensions':list(im.size),'pixel_readable':ok,'packed':bool(im.packed_file),'users':im.users,'used_by_materials':[m.name for m in bpy.data.materials if m.use_nodes and any(getattr(n,'image',None)==im for n in m.node_tree.nodes)]})
report={'id':aid,'blender_version':bpy.app.version_string,'master_path':entry['editable']['path'],'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'kind':entry['editable']['kind'],'original_master':entry['editable']['original_blend_available'],'rigs':rigs,'actions':[{'name':a.name,'range':list(a.frame_range)} for a in bpy.data.actions],'mesh_count':sum(o.type=='MESH' for o in bpy.data.objects),'shape_key_count':sum(len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0 for o in bpy.data.objects if o.type=='MESH'),'images':imgs,'status':'BLENDER_OPEN_AND_DATA_READ_PASS','visual_render':'not-tested','vrm_round_trip':'not-supported; original VRM retained for MToon/expressions/spring bones','art_approved':False}
report['missing_images']=[x for x in imgs if not x['pixel_readable']]
report['status']='BLENDER_OPEN_WITH_UNUSED_IMAGE_WARNING' if report['missing_images'] else 'BLENDER_OPEN_AND_DATA_READ_PASS'
assert rigs and report['mesh_count']>0 and all(x['pixel_readable'] or not x['used_by_materials'] for x in imgs)
(R/'evidence-v04'/f'{aid}-editor.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('EDITOR_PASS',aid,len(rigs),report['mesh_count'],len(imgs))
