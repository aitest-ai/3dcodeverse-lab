extends CharacterBody3D

@export var is_player := false
@export var npc_id := ""
@export var display_name := ""
@export var patrol_points := PackedVector3Array()
var animation_player: AnimationPlayer
var animation_tree: AnimationTree
var visual: Node3D
var horizontal := Vector3.ZERO
var patrol_index := 0
var wait_time := 1.5
var motion_state := "Idle"
var moved_distance := 0.0
var previous_position := Vector3.ZERO
var attention := false

func _ready() -> void:
 visual = get_node("Visual")
 animation_player = visual.find_children("*", "AnimationPlayer", true, false)[0]
 for name in animation_player.get_animation_list():
  animation_player.get_animation(name).loop_mode = Animation.LOOP_LINEAR
 if is_player:
  animation_tree = AnimationTree.new()
  visual.add_child(animation_tree)
  animation_tree.anim_player = animation_tree.get_path_to(animation_player)
  var blend = AnimationNodeBlendSpace1D.new()
  blend.min_space = 0
  blend.max_space = 4.2
  for spec in [["Idle",0.0],["Walk",1.45],["Run",4.2]]:
   var node = AnimationNodeAnimation.new()
   node.animation = spec[0]
   blend.add_blend_point(node,spec[1])
  var tree=AnimationNodeBlendTree.new()
  tree.add_node("Locomotion",blend)
  tree.add_node("StrideScale",AnimationNodeTimeScale.new())
  tree.connect_node("StrideScale",0,"Locomotion")
  tree.connect_node("output",0,"StrideScale")
  animation_tree.tree_root = tree
  animation_tree.active = true
 else:
  animation_player.play("Idle")
 previous_position = global_position

func move_character(direction: Vector3, speed: float, delta: float) -> void:
 horizontal = horizontal.lerp(direction * speed, 1.0-exp(-10.0*delta))
 velocity.x = horizontal.x
 velocity.z = horizontal.z
 if not is_on_floor(): velocity.y -= 9.81*delta
 else: velocity.y = -0.2
 move_and_slide()
 moved_distance += global_position.distance_to(previous_position)
 previous_position = global_position
 if horizontal.length() > 0.1:
  var desired = atan2(horizontal.x,horizontal.z)
  visual.rotation.y = lerp_angle(visual.rotation.y,desired,1.0-exp(-12.0*delta))
 motion_state = "Run" if horizontal.length()>2.4 else ("Walk" if horizontal.length()>0.12 else "Idle")
 if is_player:
  set_locomotion(horizontal.length())
 elif not attention:
  if animation_player.current_animation != motion_state: animation_player.play(motion_state,0.18)

func set_locomotion(speed: float) -> void:
 animation_tree.set("parameters/Locomotion/blend_position",speed)
 var t=clamp((speed-1.45)/(4.2-1.45),0.0,1.0)
 var source_speed=lerp(0.9858,5.8817,t)
 animation_tree.set("parameters/StrideScale/scale",clamp(speed/source_speed,0.4,1.8) if speed>0.12 else 1.0)

func drive(input_vector: Vector2, running: bool, yaw: float, delta: float, blocked: bool) -> void:
 var direction = Vector3(input_vector.x,0,input_vector.y).rotated(Vector3.UP,yaw)
 if blocked: direction = Vector3.ZERO
 move_character(direction,4.2 if running else 1.45,delta)

func _physics_process(delta: float) -> void:
 if is_player: return
 var player = get_parent().get_node("Player")
 attention = global_position.distance_to(player.global_position)<2.6
 if attention:
  move_character(Vector3.ZERO,0,delta)
  var d = player.global_position-global_position
  visual.rotation.y = lerp_angle(visual.rotation.y,atan2(d.x,d.z),1.0-exp(-5*delta))
  var talking = get_parent().get("dialog_target") == npc_id
  var clip = "Celebrate" if talking and npc_id=="keeper" and get_parent().get("quest")==3 else ("Talk" if talking else "Idle")
  if animation_player.current_animation != clip: animation_player.play(clip,0.2)
 elif wait_time>0:
  wait_time-=delta
  move_character(Vector3.ZERO,0,delta)
 elif not patrol_points.is_empty():
  var d = patrol_points[patrol_index]-global_position
  d.y=0
  if d.length()<0.25:
   patrol_index=(patrol_index+1)%patrol_points.size()
   wait_time=1.7
  move_character(d.normalized(),0.85,delta)

func skeleton_sample() -> Array:
 var s = visual.find_children("*","Skeleton3D",true,false)[0]
 var output=[]
 for name in ["upperarm_l","thigh_l","calf_l"]:
  var q = s.get_bone_pose_rotation(s.find_bone(name))
  output.append([q.x,q.y,q.z,q.w])
 return output
