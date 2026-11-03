extends Node3D

var player
var camera_rig: Node3D
var arm: SpringArm3D
var quest := 0
var score := 0
var collected := []
var elapsed := 0.0
var express := false
var dialog_target := ""
var nearest := ""
var started := false
var dragging := false
var ui: Control
var objective: Label
var counter: Label
var prompt: Label
var dialogue: PanelContainer
var dialogue_name: Label
var dialogue_text: Label
var options: HBoxContainer
var banner: Label
var snapshot_timer := 0.0
var ui_buttons := {}
var fps_samples := []
var physics_frames := 0
var font: Font
var face_morph_mesh: MeshInstance3D
var posture := 0
var low_quality := false

func _ready() -> void:
 player=get_node("Player")
 camera_rig=get_node("CameraRig")
 arm=camera_rig.get_node("SpringArm3D")
 arm.add_excluded_object(player.get_rid())
 for npc in get_node("NPCs").get_children():
  # NPC script expects all actors to share the scene's root for interaction state.
  npc.reparent(self)
 font=load("res://fonts/harbor.otf")
 _setup_inputs()
 _build_ui()
 camera_rig.position=player.position+Vector3(0,1.4,0)
 var shapes=player.visual.find_children("*","MeshInstance3D",true,false)
 for m in shapes:
  if m.find_blend_shape_by_name("Smile")>=0: face_morph_mesh=m

func _setup_inputs() -> void:
 for name in ["left","right","forward","back","run","interact","cancel"]:
  if not InputMap.has_action(name):InputMap.add_action(name)
 for pair in [["left",KEY_A],["right",KEY_D],["forward",KEY_W],["back",KEY_S],["run",KEY_SHIFT],["interact",KEY_E],["cancel",KEY_ESCAPE]]:
  var event=InputEventKey.new()
  event.physical_keycode=pair[1]
  InputMap.action_add_event(pair[0],event)

func panel_style() -> StyleBoxFlat:
 var s=StyleBoxFlat.new()
 s.bg_color=Color("f4efe2ef")
 s.set_corner_radius_all(5)
 s.content_margin_left=22
 s.content_margin_right=22
 s.content_margin_top=17
 s.content_margin_bottom=17
 return s

func label(text: String, size: int=17) -> Label:
 var l=Label.new()
 l.text=text
 l.add_theme_font_override("font",font)
 l.add_theme_font_size_override("font_size",size)
 l.add_theme_color_override("font_color",Color("264c43"))
 return l

func button(text: String, callback: Callable, id: String) -> Button:
 var b=Button.new()
 b.text=text
 b.add_theme_font_override("font",font)
 b.add_theme_font_size_override("font_size",16)
 b.custom_minimum_size=Vector2(180,45)
 var s=panel_style()
 s.bg_color=Color("2e6259")
 s.content_margin_top=9
 s.content_margin_bottom=9
 b.add_theme_stylebox_override("normal",s)
 b.add_theme_color_override("font_color",Color("f5edd9"))
 b.pressed.connect(callback)
 ui_buttons[id]=b
 return b

func _build_ui() -> void:
 var layer=CanvasLayer.new()
 add_child(layer)
 ui=Control.new()
 ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 ui.mouse_filter=Control.MOUSE_FILTER_IGNORE
 layer.add_child(ui)
 var brand=label("港邊散策\nHARBOR WALK · CHARACTER V02",25)
 brand.position=Vector2(28,22)
 ui.add_child(brand)
 var mission=PanelContainer.new()
 mission.position=Vector2(28,112)
 mission.custom_minimum_size=Vector2(300,145)
 mission.add_theme_stylebox_override("panel",panel_style())
 ui.add_child(mission)
 var vb=VBoxContainer.new()
 mission.add_child(vb)
 vb.add_child(label("潮汐快遞 · 一份街區手帖",19))
 objective=label("找阿澄聊聊，選擇這趟旅程的步調。",14)
 objective.custom_minimum_size.x=270
 objective.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
 vb.add_child(objective)
 counter=label("000 點  ·  00:00",16)
 vb.add_child(counter)
 banner=label("角色升級 × Godot 成熟引擎驗證",14)
 banner.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
 banner.position=Vector2(-350,30)
 ui.add_child(banner)
 var help=label("W A S D  移動    SHIFT  跑步    按住滑鼠拖曳  視角    E  對話    ESC  關閉\nQ  畫質    V  近看角色    B  表情    1/2/3  工房 Idle / Walk / Run",13)
 help.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
 help.position=Vector2(28,-63)
 ui.add_child(help)
 prompt=label("",19)
 prompt.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
 prompt.position=Vector2(-130,-130)
 ui.add_child(prompt)
 dialogue=PanelContainer.new()
 dialogue.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
 dialogue.position=Vector2(-360,-300)
 dialogue.custom_minimum_size=Vector2(720,220)
 dialogue.add_theme_stylebox_override("panel",panel_style())
 ui.add_child(dialogue)
 var dv=VBoxContainer.new()
 dv.add_theme_constant_override("separation",12)
 dialogue.add_child(dv)
 dialogue_name=label("林汐 · 海風信使",25)
 dv.add_child(dialogue_name)
 dialogue_text=label("",16)
 dialogue_text.custom_minimum_size.x=670
 dialogue_text.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
 dv.add_child(dialogue_text)
 options=HBoxContainer.new()
 options.add_theme_constant_override("separation",15)
 dv.add_child(options)
 dialogue_text.text="走進海風里，接下一份街區委託。也可以按 V，近看新版角色的服裝與動作。"
 options.add_child(button("開始散策",_start,"start"))

func _start() -> void:
 started=true
 dialogue.hide()

func _unhandled_input(event: InputEvent) -> void:
 if event is InputEventMouseButton:
  if event.button_index==MOUSE_BUTTON_LEFT: dragging=event.pressed
  if event.pressed and event.button_index==MOUSE_BUTTON_WHEEL_UP: arm.spring_length=max(1.8,arm.spring_length-0.4)
  if event.pressed and event.button_index==MOUSE_BUTTON_WHEEL_DOWN: arm.spring_length=min(7.0,arm.spring_length+0.4)
 if event is InputEventMouseMotion and dragging:
  camera_rig.rotation.y-=event.relative.x*0.005
  camera_rig.rotation.x=clamp(camera_rig.rotation.x-event.relative.y*0.003,-0.65,0.10)
 if event is InputEventKey and event.pressed and not event.echo:
  if event.physical_keycode==KEY_Q:
   low_quality=not low_quality
   get_node("Sun").shadow_enabled=not low_quality
   banner.text="畫質：省電（陰影關閉）" if low_quality else "畫質：標準（陰影開啟）"
  if event.physical_keycode==KEY_V:
   posture=(posture+1)%3
   arm.spring_length=[5.2,2.7,.85][posture]
   camera_rig.rotation.y=player.visual.rotation.y if posture>0 else 0.0
   camera_rig.rotation.x=-0.06 if posture>0 else -0.23
  if event.physical_keycode==KEY_B and face_morph_mesh:
   var i=face_morph_mesh.find_blend_shape_by_name("Smile")
   face_morph_mesh.set_blend_shape_value(i,1.0-face_morph_mesh.get_blend_shape_value(i))
  if event.physical_keycode in [KEY_1,KEY_2,KEY_3]:
   var blend=[0.0,1.45,4.2][event.physical_keycode-KEY_1]
   player.set_locomotion(blend)
   banner.text="工房預覽："+["Idle","Walk","Run"][event.physical_keycode-KEY_1]+"（按移動鍵回到操作）"
   player.set_meta("preview",blend)

func talk(id: String) -> void:
 dialog_target=id
 dialogue.show()
 for c in options.get_children():c.queue_free()
 dialogue_name.text="阿澄 · 街區嚮導" if id=="guide" else "阿青 · 潮間書店"
 if id=="guide" and quest==0:
  dialogue_text.text="替阿青收集茶香、樹影與海風三枚印記吧。你想悠閒走走，還是挑戰 60 秒港口快遞？快遞及時完成可多得 50 點。"
  options.add_child(button("慢慢走 · 街區路線",func():accept(false),"accept_slow"))
  options.add_child(button("港口快遞 · 60秒",func():accept(true),"accept_express"))
 elif id=="keeper" and quest==2:
  dialogue_text.text="三枚印記都帶來了？謝謝你，我會把這份手帖放在書店最顯眼的地方。"
  options.add_child(button("交付散策手帖",finish,"deliver"))
 else:
  dialogue_text.text="海風里有自己的步調。看看茶行門口、廣場榕樹和海堤，也許會發現小風景。" if quest<3 else "謝謝你送來的風景，下次再來坐坐。"
 options.add_child(button("繼續散步",close_dialogue,"close"))

func accept(fast: bool) -> void:
 if quest!=0:return
 quest=1
 express=fast
 elapsed=0
 close_dialogue()
 banner.text="委託已接下 · 跟著金色印記探索街區"

func close_dialogue() -> void:
 dialog_target=""
 dialogue.hide()

func finish() -> void:
 if quest!=2:return
 quest=3
 score+=75
 if express and elapsed<=60:score+=50
 dialogue_name.text="手帖送到了，海風也記住了你。"
 dialogue_text.text="完成委託 · %d 點\n%s"%[score,"快遞及時送達，額外 +50 點。" if express and elapsed<=60 else "謝謝你慢慢看見這座街區。"]
 for c in options.get_children():c.queue_free()
 options.add_child(button("繼續散策",close_dialogue,"continue"))
 banner.text="委託完成 · 新版角色與成熟引擎實際運行"

func _physics_process(delta: float) -> void:
 if not player:return
 physics_frames+=1
 var input_vector=Input.get_vector("left","right","forward","back")
 var blocked=not started or dialogue.visible
 if not player.has_meta("preview") or input_vector.length()>0:
  if player.has_meta("preview"):player.remove_meta("preview")
  player.drive(input_vector,Input.is_action_pressed("run"),camera_rig.rotation.y,delta,blocked)
 else:player.move_character(Vector3.ZERO,0,delta);player.set_locomotion(player.get_meta("preview"))
 var height=1.66 if posture==2 else (1.02 if posture==1 else 1.4)
 camera_rig.position=camera_rig.position.lerp(player.position+Vector3(0,height,0),1-exp(-12*delta))
 if quest in [1,2] and not dialogue.visible: elapsed+=delta
 nearest=""
 var best=2.65
 for n in [get_node_or_null("Guide"),get_node_or_null("Keeper")]:
  if n:
   var distance=player.position.distance_to(n.position)
   if distance<best:best=distance;nearest=n.npc_id
 if Input.is_action_just_pressed("interact") and nearest!="" and not blocked:talk(nearest)
 if Input.is_action_just_pressed("cancel") and started:close_dialogue()
 prompt.text="E  與"+("阿澄" if nearest=="guide" else "阿青")+"聊聊" if nearest!="" and not blocked else ""
 var pickups=get_node("Pickups")
 for node in pickups.get_children():
  node.visible=quest==1 and not collected.has(node.name)
  node.rotation.y+=delta*0.8
  if node.visible and not blocked and player.position.distance_to(Vector3(node.position.x,0,node.position.z))<0.95:
   collected.append(node.name)
   score+=25
   banner.text="印記已收集 · +25 點"
   if collected.size()==3:quest=2
 var instructions=["找阿澄聊聊，選擇這趟旅程的步調。","收集茶香、樹影、海風三枚印記。","將手帖送到潮間書店，找阿青交付。","委託完成，繼續享受海風。"]
 objective.text=instructions[quest]+("\n快遞剩餘 %d 秒"%max(0,60-int(elapsed)) if express and quest in [1,2] else "")
 counter.text="%03d 點  ·  印記 %d / 3  ·  %02d:%02d"%[score,collected.size(),int(elapsed)/60,int(elapsed)%60]
 snapshot_timer+=delta
 if snapshot_timer>.15:
  snapshot_timer=0
  if OS.has_feature("web"):
   var data=snapshot()
   JavaScriptBridge.eval("window.__harborGodot = "+JSON.stringify(data),true)

func snapshot() -> Dictionary:
 var npc_states=[]
 for n in [get_node_or_null("Guide"),get_node_or_null("Keeper")]:
  if n:npc_states.append({"id":n.npc_id,"position":[n.position.x,n.position.y,n.position.z],"motion":n.motion_state,"attention":n.attention})
 var collisions=[]
 for i in range(player.get_slide_collision_count()):
  var hit=player.get_slide_collision(i)
  var n=hit.get_normal()
  collisions.append({"path":str(hit.get_collider().get_path()),"normal":[n.x,n.y,n.z]})
 var controls={}
 for id in ui_buttons:
  var b=ui_buttons[id]
  if is_instance_valid(b) and b.is_visible_in_tree():
   var r=b.get_global_rect()
   controls[id]=[r.position.x+r.size.x/2,r.position.y+r.size.y/2]
 return {"collisions":collisions,"process_frames":Engine.get_process_frames(),"input":[Input.get_action_strength("left"),Input.get_action_strength("right"),Input.get_action_strength("forward"),Input.get_action_strength("back"),Input.is_action_pressed("run")],"velocity":[player.velocity.x,player.velocity.y,player.velocity.z],"npcs":npc_states,"engine":"Godot "+Engine.get_version_info().string,"ready":true,"started":started,"position":[player.position.x,player.position.y,player.position.z],"smile":face_morph_mesh.get_blend_shape_value(face_morph_mesh.find_blend_shape_by_name("Smile")) if face_morph_mesh else -1,"motion":player.motion_state,"bones":player.skeleton_sample(),"quest":quest,"score":score,"collected":collected,"express":express,"elapsed":elapsed,"dialog":dialogue.visible,"nearest":nearest,"camera_yaw":camera_rig.rotation.y,"arm_length":arm.get_hit_length(),"desired_arm":arm.spring_length,"buttons":controls,"viewport":[get_viewport().get_visible_rect().size.x,get_viewport().get_visible_rect().size.y],"physics_frames":physics_frames,"low_quality":low_quality,"fps":Engine.get_frames_per_second()}
