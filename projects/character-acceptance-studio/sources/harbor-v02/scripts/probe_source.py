import bpy,json
from pathlib import Path
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
f=next(Path('/workspace/work/cc0').rglob('Superhero_Female_FullBody.gltf'));bpy.ops.import_scene.gltf(filepath=str(f))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
print('BONE_LOCATIONS',[(b.name,tuple(round(x,4) for x in b.head_local)) for b in rig.data.bones if b.name in ['pelvis','Head','neck_01','thigh_l','calf_l','foot_l','ball_l','upperarm_l','lowerarm_l','hand_l','spine_03']])
for o in bpy.data.objects:
 if o.type=='MESH':
  print('MESH',o.name,tuple(round(x,4) for x in o.dimensions),[(round(min(v.co[i] for v in o.data.vertices),4),round(max(v.co[i] for v in o.data.vertices),4)) for i in range(3)])
