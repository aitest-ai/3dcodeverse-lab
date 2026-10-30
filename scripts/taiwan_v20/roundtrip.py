"""Reopen delivered files: verify source topology, then audit the exported GLB
in a new Blender scene. This catches differences between authored and exported data.
"""
import os,sys,json,hashlib
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from motion_qa import GLB,arm_faces,scan8
OUT=Path(os.getenv('V20_OUT','outputs/v20')).resolve()
source_checks={}
for role in ('you','boss','uncle','jie'):
    path=OUT/'blend'/(role+'_v20_source.blend')
    bpy.ops.wm.open_mainfile(filepath=str(path))
    body=bpy.data.objects['TrueMPFBBody_'+role]
    rig=bpy.data.objects['RootRig_'+role]
    assert len(body.data.vertices)==13380
    assert len(rig.data.bones)==53
    assert len(body.data.shape_keys.key_blocks)==11
    assert not any(m.type=='MASK' for m in body.modifiers)
    images=[im for im in bpy.data.images if im.source=='FILE' and im.has_data]
    assert images and all(im.packed_file is not None for im in images)
    source_checks[role]={'native_body_vertices':len(body.data.vertices),'bones':len(rig.data.bones),
                        'body_morphs':len(body.data.shape_keys.key_blocks)-1,
                        'packed_image_count':len(images),'bytes':path.stat().st_size,
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

path=OUT/'motion'/'jie_v20_source_stress.glb'
g=GLB(path)
assert len(g.doc['skins'][0]['joints'])==53
assert len(g.doc['animations'])==1
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.fps=24
bpy.ops.import_scene.gltf(filepath=str(path))
rig=next(o for o in scene.objects if o.type=='ARMATURE')
body=bpy.data.objects['TrueMPFBBody_jie']
shirt=next(o for o in scene.objects if 'OpenSourceCloth_jie_toigo_basic_tucked_t-shirt' in o.name)
pants=next(o for o in scene.objects if 'OpenSourceCloth_jie_cortu_cargo_pants' in o.name)
limbs=arm_faces(body,rig)
results={}
for frame in range(49):
    scene.frame_set(frame);bpy.context.view_layer.update()
    row=scan8(body,shirt,pants,limbs)
    results[str(frame)]={'seconds':frame/24,**row}
    print('V20_EXPORTED_WAIST_FRAME',frame,row['visible_waist_skin'],flush=True)
report={'source_blends_reopened':source_checks,
        'exported_animation_file':path.name,
        'exported_animation_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'exported_animation_channels':sum(len(a['channels']) for a in g.doc['animations']),
        'frames':results,'frame_count':49,'rays':49*8200,
        'visible_waist_skin':sum(r['visible_waist_skin'] for r in results.values()),
        'scope':'Waist region only, same sampled reference stress clip; not arbitrary animation proof',
        'art_approved':False}
(OUT/'qa'/'v20_reopened_deliverables.json').write_text(json.dumps(report,indent=2))
assert report['visible_waist_skin']==0,'Exported animation regressed; see report'
print('V20_DELIVERABLES_REOPENED',json.dumps(report),flush=True)
