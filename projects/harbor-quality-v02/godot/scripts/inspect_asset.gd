extends SceneTree
func _initialize() -> void:
 var packed = load("res://assets/harbor-courier-v02.glb") as PackedScene
 assert(packed != null, "GLB import failed")
 var instance = packed.instantiate()
 root.add_child(instance)
 var skeletons = instance.find_children("*", "Skeleton3D", true, false)
 var players = instance.find_children("*", "AnimationPlayer", true, false)
 var meshes = instance.find_children("*", "MeshInstance3D", true, false)
 assert(skeletons.size() == 1)
 assert(skeletons[0].get_bone_count() == 65)
 assert(players.size() > 0)
 var clips = Array(players[0].get_animation_list())
 for clip in ["Idle", "Walk", "Run", "Turn", "Talk", "Interact", "Celebrate"]:
  assert(clips.has(clip), "Missing clip: " + clip)
 var report = {"status":"PASS","engine":Engine.get_version_info(),"bones":65,"animations":clips,"mesh_count":meshes.size(),"animation_player_name":str(players[0].name),"limitation":"Headless import and scene structure verification; rendering is verified separately in Web export."}
 var f = FileAccess.open("res://../evidence/godot-import.json",FileAccess.WRITE)
 f.store_string(JSON.stringify(report,"  "))
 print(JSON.stringify(report))
 instance.free()
 quit()
