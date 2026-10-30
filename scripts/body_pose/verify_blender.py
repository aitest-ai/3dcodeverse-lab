"""Fresh Blender process: reimport GLB and compare evaluated joint positions."""
import json,sys
from pathlib import Path
import bpy
from mathutils import Vector
report_path=Path(sys.argv[sys.argv.index('--')+1]);report=json.loads(report_path.read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.fps=round(report['fps']);scene.render.fps_base=round(report['fps'])/report['fps']
bpy.ops.import_scene.gltf(filepath=str(report_path.parent/report['glb']))
rigs=[o for o in scene.objects if o.type=='ARMATURE'];assert len(rigs)==1
rig=rigs[0];assert len(rig.data.bones)==report['source_bones']
if len(bpy.data.actions)!=1:raise RuntimeError('Round-trip verifier requires explicit clip activation for multi-action files')
max_error=0.;count=0
for sample in report['pose_samples']:
    scene.frame_set(sample['frame']);bpy.context.view_layer.update()
    for name,expected in sample['joints'].items():
        actual=rig.matrix_world@rig.pose.bones[name].head;error=(actual-Vector(expected)).length;max_error=max(max_error,error);count+=1
if max_error>.002:raise RuntimeError(f'GLB round-trip joint error {max_error:.6f} m exceeds 2 mm')
result={'status':'PASS','samples':count,'max_joint_position_error_m':max_error,'blender_version':bpy.app.version_string,'engine_tested':'Blender glTF importer; NOT Three.js/Unity runtime'}
(report_path.parent/'roundtrip.json').write_text(json.dumps(result,indent=2));print('ROUNDTRIP_PASS',json.dumps(result))
