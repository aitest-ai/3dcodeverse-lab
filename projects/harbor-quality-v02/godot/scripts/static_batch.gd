@tool
extends MultiMeshInstance3D
# Authored transforms stay in the editable scene even when generated using a headless
# editor's dummy RenderingServer. Upload them to the real renderer when instantiated.
@export var authored_transforms: Array[Transform3D] = []
func _ready() -> void:
 if multimesh == null:return
 multimesh.instance_count=authored_transforms.size()
 for i in range(authored_transforms.size()):multimesh.set_instance_transform(i,authored_transforms[i])
