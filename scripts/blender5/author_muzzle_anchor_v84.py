"""Blender 5-only, non-destructive candidate muzzle marker. Actual source .blend required.
Run blender -b mecha_v50.blend --python author_muzzle_anchor_v84.py -- --output-dir NEW_FOLDER
No Blender runtime available in the ChatGPT environment; not yet full-model verified.
"""
import argparse, hashlib, json, sys, struct, math
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from muzzle_geometry_v84 import infer_muzzle_v84
from verify_glb_v84 import verify_document

NAME='MuzzleTip_R'
EXPECTED_SKIN_JOINTS=15
BASE_GLTF_NODE='weapon_socket.R'

def fail(message):
    raise RuntimeError('V84 safe authoring refused: '+message)

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as fp:
        for chunk in iter(lambda: fp.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

def mesh_snapshot():
    h=hashlib.sha256()
    for obj in sorted((o for o in bpy.data.objects if o.type=='MESH'),key=lambda o:o.name):
        h.update(obj.name.encode());h.update(str(len(obj.data.vertices)).encode())
        for v in obj.data.vertices:h.update(struct.pack('<3d',*v.co))
    return h.hexdigest()

def mesh_world_points(obj):
    return [tuple(obj.matrix_world @ v.co) for v in obj.data.vertices]

def glb_document(path):
    with path.open('rb') as f:
        header=f.read(12)
        if len(header)!=12:fail('Incomplete GLB header')
        magic,version,length=struct.unpack('<4sII',header)
        if magic!=b'glTF' or version!=2 or length!=path.stat().st_size:fail('Invalid GLB v2 header')
        sz,kind=struct.unpack('<I4s',f.read(8))
        if kind!=b'JSON':fail('GLB first chunk is not JSON')
        return json.loads(f.read(sz).decode('utf-8'))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    source=Path(bpy.data.filepath).resolve()
    if not source.is_file() or source.suffix.lower()!='.blend':fail('Load actual original .blend input first')
    output=Path(args.output_dir).resolve();output.mkdir(parents=True,exist_ok=True)
    blend_path=output/'mecha_v84_muzzle_anchor.blend';glb_path=output/'mecha_v84_muzzle_anchor.glb'
    if source==blend_path or blend_path.exists() or glb_path.exists():
        fail('Output already exists or overlaps source; select an empty new folder')
    source_digest=sha256(source)
    rig=bpy.data.objects.get('MechaRig')
    if not rig or rig.type!='ARMATURE':fail('Original MechaRig armature missing')
    names=list(rig.data.bones.keys())
    if len(names)!=EXPECTED_SKIN_JOINTS or BASE_GLTF_NODE not in names:
        fail('Original 15-bone rig and weapon_socket.R required')
    if bpy.data.objects.get(NAME):fail('MuzzleTip_R already exists')
    bore=bpy.data.objects.get('PrimaryCannon_energy_bore')
    outer=bpy.data.objects.get('PrimaryCannon_outer_barrel')
    if not bore or not outer or bore.type!='MESH' or outer.type!='MESH':
        fail('Original cannon energy bore and outer barrel geometry required')
    for obj in (bore,outer):
        if rig not in [m.object for m in obj.modifiers if m.type=='ARMATURE']:
            fail(obj.name+' not driven by original rig')
    old_pose=rig.data.pose_position
    try:
        rig.data.pose_position='REST'
        bpy.context.scene.frame_set(bpy.context.scene.frame_start)
        bpy.context.view_layer.update()
        before=mesh_snapshot()
        measure=infer_muzzle_v84(mesh_world_points(bore),mesh_world_points(outer))
        position=Vector(measure['muzzle']);direction=Vector(measure['forward'])
        empty=bpy.data.objects.new(NAME,None)
        bpy.context.scene.collection.objects.link(empty)
        empty.empty_display_type='ARROWS';empty.empty_display_size=.10
        empty['asset_role']='visual_muzzle_anchor_only'
        empty['source_geometry']=measure['geometry_basis']
        empty['validated_geometry']='two_actual_endrings'
        empty['visual_only']=True
        empty.parent=rig;empty.parent_type='BONE';empty.parent_bone=BASE_GLTF_NODE
        orientation=Vector((0,-1,0)).rotation_difference(direction)
        empty.matrix_world=Matrix.Translation(position)@orientation.to_matrix().to_4x4()
        bpy.context.view_layer.update()
        err=(empty.matrix_world.translation-position).length
        if not math.isfinite(err) or err>.005:
            fail(f'Bone parent muzzle marker drifted {err:.4f}m')
        if mesh_snapshot()!=before:fail('Mesh vertices unexpectedly changed')
        if len(rig.data.bones)!=EXPECTED_SKIN_JOINTS:fail('Rig joint count changed')
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
        bpy.ops.export_scene.gltf(filepath=str(glb_path),export_format='GLB',
            export_animations=True,export_animation_mode='ACTIONS',export_skins=True,
            export_extras=True)
        info=glb_document(glb_path)
        if len(info.get('animations',[]))<6:fail('Original six animations not preserved')
        verify_document(info)
        report={'schema':'taipei-mecha-v84-blender-anchor','version':'8.4',
            'status':'passed_real_blender_source_export','source_blend_sha256':source_digest,
            'output_blend_sha256':sha256(blend_path),'output_glb_sha256':sha256(glb_path),
            'original_mesh_snapshot_sha256':before,
            'glb_animation_count':len(info.get('animations',[])),
            'original_skin_joint_count':EXPECTED_SKIN_JOINTS,
            'socket_world_position_rest_blender_m':list(position),
            'muzzle_forward_rest_blender':list(direction),
            'muzzle_geometry':measure,
            'authority':'visual-only candidate; combat.fire unchanged',
            'limitations':['Windows WebGPU visual calibration and gameplay acceptance required',
                'Blender Z-up coordinates must not be reused as Three.js world coordinates']}
        (output/'QA_V84_MODEL_EXPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print('V84 MODEL GENERATED AND VERIFIED',json.dumps({'glb_sha256':report['output_glb_sha256'],
            'animations':report['glb_animation_count']}))
    finally:
        rig.data.pose_position=old_pose
    if sha256(source)!=source_digest:fail('Source blend changed unexpectedly')

if __name__=='__main__':main()
