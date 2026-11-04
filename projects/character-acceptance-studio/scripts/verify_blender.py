"""Cold-read actual editable mother files and reimport actual delivered GLBs.
Run in a new background Blender process. Does not render or approve visual quality.
"""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];result={'blender':bpy.app.version_string,'mother_files':[],'glb_reimports':[],'art_approved':False,'offline_visual':'NOT_RENDERED_BY_THIS_CHECK'}
paths=['sources/harbor-v02/assets/harbor-courier-v02.blend','sources/oldman-v29/oldman.blend','assets/harbor-courier-review/0.1.0/harbor-courier-review.blend','assets/taiwan-oldman-review/0.1.0/oldman-retarget-baseline.blend','assets/taiwan-oldman-review/0.1.0/oldman-retarget-candidate.blend']
for rel in paths:
    path=R/rel;before=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');images=[]
    for im in bpy.data.images:
        if im.packed_file and im.size[0]:
            assert len(im.pixels)>0 and im.has_data,im.name
            pixel=float(im.pixels[0]);images.append({'name':im.name,'size':list(im.size),'packed_sha256':hashlib.sha256(im.packed_file.data).hexdigest(),'actual_pixel_read':True})
    assert images
    after=hashlib.sha256(path.read_bytes()).hexdigest();assert before==after
    result['mother_files'].append({'file':rel,'sha256':before,'bones':len(rig.data.bones),'images':images,'unchanged_after_cold_read':True,'mesh_count':sum(o.type=='MESH' for o in bpy.data.objects)})
for rel in ['assets/harbor-courier-review/0.1.0/harbor-courier-review.glb','assets/taiwan-oldman-review/0.1.0/oldman-retarget-candidate.glb']:
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30;bpy.ops.import_scene.gltf(filepath=str(R/rel));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');actions=list(bpy.data.actions);assert actions
    for o in bpy.data.objects:
        if o.animation_data:
            for track in o.animation_data.nla_tracks:track.mute=True
    walk=next(a for a in actions if 'Walk' in a.name);rig.animation_data_create();rig.animation_data.action=walk
    if walk.slots:rig.animation_data.action_slot=walk.slots[0]
    points=[]
    for f in [0,10,20]:bpy.context.scene.frame_set(f);points.append(list(rig.matrix_world@rig.pose.bones['foot_l'].matrix.translation))
    assert max(p[1] for p in points)-min(p[1] for p in points)>.2,(rel,points)
    result['glb_reimports'].append({'file':rel,'bones':len(rig.data.bones),'actions':[a.name for a in actions],'actual_walk_foot_samples':points,'scope':'Real GLB import and evaluated bone motion; not rendered image approval'})
(R/'evidence/blender-cold-read.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('BLENDER_COLD_READ_AND_REIMPORT_PASS',len(result['mother_files']),len(result['glb_reimports']))
