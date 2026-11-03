import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
bpy.ops.import_scene.fbx(filepath=str(R/'assets/harbor-courier-v02.fbx'))
rigs=[o for o in bpy.data.objects if o.type=='ARMATURE'];meshes=[o for o in bpy.data.objects if o.type=='MESH'];assert len(rigs)==1;assert len(rigs[0].data.bones)==65
clips=[a.name for a in bpy.data.actions]
for name in ['Idle','Walk','Run','Turn','Talk','Interact','Celebrate']:assert any(name in c for c in clips),name
report={'status':'PASS_FBX_REIMPORT_IN_BLENDER','bones':len(rigs[0].data.bones),'meshes':len(meshes),'clips':clips,'limit':'This is Blender FBX reimport, not Unreal Editor import validation.'}
(R/'evidence/fbx-reimport.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
