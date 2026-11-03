"""Blender 5 candidate audit: 6 original NLA tracks x all 48 frames.
Run on REAL v8.4 .blend, using the unchanged original cannon mesh; this does not
create a GLB, edit its bones, or update Windows game/official raycast.
Full Windows launcher and offline HTML are separately provided in the ZIP.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Vector
from trajectory_math_v85 import CLIPS,FRAMES,ring_indices,measure_frame,summarize_samples

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def evaluated_vertices(obj):
    dg=bpy.context.evaluated_depsgraph_get()
    eval_obj=obj.evaluated_get(dg)
    mesh=eval_obj.to_mesh(preserve_all_data_layers=False,depsgraph=dg)
    try:return [tuple(eval_obj.matrix_world @ v.co) for v in mesh.vertices]
    finally:eval_obj.to_mesh_clear()

def run():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',required=True)
    args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    source=Path(bpy.data.filepath).resolve()
    if source.name!='mecha_v84_muzzle_anchor.blend' or not source.is_file():
        raise RuntimeError('Must load original v8.4 candidate .blend')
    source_sha=sha(source)
    output=Path(args.output).resolve()
    if output==source.parent:raise RuntimeError('Output must be separate from mother file')
    output.mkdir(parents=True,exist_ok=True)
    result_file=output/'QA_V85_FULLFRAME_ANIMATION.json'
    if result_file.exists():raise RuntimeError('Refusing to overwrite existing QA')
    rig=bpy.data.objects.get('MechaRig')
    marker=bpy.data.objects.get('MuzzleTip_R')
    bore=bpy.data.objects.get('PrimaryCannon_energy_bore')
    if not rig or rig.type!='ARMATURE' or len(rig.data.bones)!=15:
        raise RuntimeError('Original 15-bone armature missing')
    if not marker or marker.parent!=rig or marker.parent_type!='BONE' or marker.parent_bone!='weapon_socket.R':
        raise RuntimeError('Real v8.4 socket-child Empty required')
    if not bore or bore.type!='MESH' or not any(m.type=='ARMATURE' and m.object==rig for m in bore.modifiers):
        raise RuntimeError('True original skinned cannon bore required')
    anim=rig.animation_data
    if not anim or len(anim.nla_tracks)<6:raise RuntimeError('Six source NLA tracks required')
    tracks={}
    for tr in anim.nla_tracks:
        if tr.name in CLIPS:
            if tr.name in tracks or len(tr.strips)!=1 or not tr.strips[0].action or tr.strips[0].action.name!='Mecha_'+tr.name:
                raise RuntimeError('Ambiguous or incorrect NLA track')
            tracks[tr.name]=tr
    if set(tracks)!=set(CLIPS):raise RuntimeError('Missing six original NLA actions')
    frame_was=bpy.context.scene.frame_current
    pose_was=rig.data.pose_position
    action_was=anim.action
    mute_was=[(tr,tr.mute) for tr in anim.nla_tracks]
    samples=[]
    try:
        anim.action=None
        for t in anim.nla_tracks:t.mute=True
        rig.data.pose_position='REST'
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        indices=ring_indices(evaluated_vertices(bore))
        rig.data.pose_position='POSE'
        for clip in CLIPS:
            for t in anim.nla_tracks:t.mute=(t is not tracks[clip])
            for frame in FRAMES:
                bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
                tip=tuple(marker.matrix_world.translation)
                forward=tuple(marker.matrix_world.to_quaternion() @ Vector((0,-1,0)))
                samples.append({'clip':clip,'frame':frame,
                    **measure_frame(tip,forward,evaluated_vertices(bore),indices)})
    finally:
        for t,mute in mute_was:t.mute=mute
        rig.data.pose_position=pose_was
        anim.action=action_was
        bpy.context.scene.frame_set(frame_was);bpy.context.view_layer.update()
    report=summarize_samples(samples)
    glb=source.with_suffix('.glb')
    if not glb.is_file():raise RuntimeError('Original candidate GLB missing')
    if sha(source)!=source_sha:raise RuntimeError('Original .blend changed')
    data={'schema':'taipei-mecha-v85-fullframe-muzzle-qa','version':'8.5',
          'source_blend_sha256':source_sha,'candidate_glb_sha256':sha(glb),
          'method':'original Blender evaluated armature after one NLA clip per full frame',
          'blender_version':bpy.app.version_string,**report,'samples':samples,
          'limitations':['Not a real Windows WebGPU gameplay test','combat.fire ray and damage are unchanged']}
    pending=result_file.with_suffix('.json.pending')
    pending.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    pending.replace(result_file)
    print('V85 FULLFRAME QA',report['passed'],report['total_samples'])
    if not report['passed']:raise SystemExit('FAIL: muzzle marker drift; inspect independent QA report')

if __name__=='__main__':run()
