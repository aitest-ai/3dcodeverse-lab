extends SceneTree
var world: Node3D
var batches={}
var mats={}
func add(node: Node, parent: Node) -> Node:
 parent.add_child(node)
 node.owner=world
 return node
func material(hex: String) -> StandardMaterial3D:
 if not mats.has(hex):
  var m=StandardMaterial3D.new()
  m.albedo_color=Color(hex)
  m.roughness=0.84
  mats[hex]=m
 return mats[hex]
func cube(p: Vector3, size: Vector3, color: String, solid: bool=false) -> void:
 var key="box:"+color
 if not batches.has(key):batches[key]=[]
 batches[key].append(Transform3D(Basis.IDENTITY.scaled(size),p))
 if solid:
  var body=StaticBody3D.new()
  add(body,world)
  body.position=p
  var shape=CollisionShape3D.new()
  var box=BoxShape3D.new()
  box.size=size
  shape.shape=box
  add(shape,body)
func ball(p: Vector3, size: Vector3, color: String) -> void:
 var key="sphere:"+color
 if not batches.has(key):batches[key]=[]
 batches[key].append(Transform3D(Basis.IDENTITY.scaled(size),p))
func cylinder(p: Vector3, radius: float, height: float, color: String) -> void:
 var key="cylinder:"+color
 if not batches.has(key):batches[key]=[]
 batches[key].append(Transform3D(Basis.IDENTITY.scaled(Vector3(radius,height,radius)),p))
func sign_text(text: String, p: Vector3, size: int=34, color: String="f4e7c8") -> void:
 var l=Label3D.new()
 l.text=text
 l.position=p
 l.font=load("res://fonts/harbor.otf")
 l.font_size=size
 l.pixel_size=0.012
 l.modulate=Color(color)
 l.outline_size=0
 add(l,world)
func shop(x: float,z: float,color: String,title: String) -> void:
 cube(Vector3(x,2.8,z),Vector3(6.6,5.6,4.3),color,true)
 cube(Vector3(x,0.18,z+2.23),Vector3(6.7,0.36,0.18),"a69d86")
 for dx in [-2.95,2.95]:cube(Vector3(x+dx,2.8,z+2.23),Vector3(.24,5.6,.18),"ece1c3")
 cube(Vector3(x,2.8,z+2.27),Vector3(6.1,.6,.14),"326c62")
 sign_text(title,Vector3(x,2.8,z+2.36),36)
 for dx in [-1.9,0.0,1.9]:
  cube(Vector3(x+dx,1.25,z+2.22),Vector3(1.65,2.2,.18),"355f57")
  cube(Vector3(x+dx,1.27,z+2.33),Vector3(1.45,1.95,.03),"87a9a2")
  cube(Vector3(x+dx,1.25,z+2.36),Vector3(.065,2,.04),"e7dcc1")
  cube(Vector3(x+dx,1.20,z+2.36),Vector3(1.5,.06,.04),"e7dcc1")
  cube(Vector3(x+dx,4.3,z+2.24),Vector3(1.55,1.45,.14),"355f57")
  cube(Vector3(x+dx,4.3,z+2.33),Vector3(1.32,1.26,.03),"8caaa1")
  cube(Vector3(x+dx,4.3,z+2.37),Vector3(.065,1.3,.03),"e7dcc1")
 cube(Vector3(x,3.55,z+2.4),Vector3(6.1,.12,.72),"456c59")
 for dx in range(-14,15):cube(Vector3(x+dx*.2,3.9,z+2.73),Vector3(.035,.63,.035),"456c59")
 cube(Vector3(x,4.22,z+2.73),Vector3(6,.055,.07),"456c59")
 for i in range(12):
  cube(Vector3(x-3.05+i*.55,2.35,z+2.9),Vector3(.55,.08,1.25),"ead9b3" if i%2==0 else "658e72")
  cube(Vector3(x-3.05+i*.55,2.24,z+3.48),Vector3(.55,.21,.06),"ead9b3" if i%2==0 else "658e72")
 for i in range(15):cube(Vector3(x,5.7+sin(i/14.0*PI)*.38,z-2.1+i*.3),Vector3(7,.12,.34),"4e7465")
 cube(Vector3(x,6.15,z),Vector3(7.1,.12,.18),"b4b29a")
func actor(name: String,p: Vector3,is_player: bool,id: String,points: PackedVector3Array,parent: Node) -> void:
 var a=CharacterBody3D.new()
 a.name=name
 a.set_script(load("res://scripts/actor.gd"))
 a.set("is_player",is_player)
 a.set("npc_id",id)
 a.set("patrol_points",points)
 a.collision_layer=2
 a.collision_mask=3
 a.floor_snap_length=.25
 add(a,parent)
 a.position=p+Vector3(0,.04,0)
 var c=CollisionShape3D.new()
 var cap=CapsuleShape3D.new()
 cap.radius=.28
 cap.height=1.78
 c.shape=cap
 c.position.y=.89
 add(c,a)
 var v=(load("res://assets/harbor-courier-v02.glb") as PackedScene).instantiate()
 v.name="Visual"
 add(v,a)
 v.position.y=0.0
func _initialize() -> void:
 world=Node3D.new()
 world.name="HarborQualityPilot"
 world.set_script(load("res://scripts/game.gd"))
 var env=WorldEnvironment.new()
 var e=Environment.new()
 e.background_mode=Environment.BG_SKY
 var sky=Sky.new()
 var skymat=ProceduralSkyMaterial.new()
 skymat.sky_top_color=Color("78a9bc")
 skymat.sky_horizon_color=Color("e0e4ca")
 skymat.ground_horizon_color=Color("d6dcc5")
 skymat.ground_bottom_color=Color("5c7970")
 sky.sky_material=skymat
 e.sky=sky
 e.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
 e.ambient_light_color=Color("dce6d0")
 e.ambient_light_energy=.28
 e.tonemap_mode=Environment.TONE_MAPPER_LINEAR
 env.environment=e
 add(env,world)
 var sun=DirectionalLight3D.new()
 sun.name="Sun"
 sun.rotation_degrees=Vector3(-48,-35,0)
 sun.light_color=Color("ffe1ac")
 sun.light_energy=.55
 sun.shadow_enabled=true
 sun.directional_shadow_mode=DirectionalLight3D.SHADOW_ORTHOGONAL
 sun.shadow_bias=.22
 sun.shadow_normal_bias=2.0
 sun.directional_shadow_max_distance=35
 add(sun,world)
 cube(Vector3(0,-.2,0),Vector3(32,.4,27),"b3b09b")
 cube(Vector3(0,-.15,0),Vector3(32,.4,27),"00000000",true)
 for z in range(-10,11):
  for x in range(-13,14):
   cube(Vector3(x*1.1+(0.55 if z%2==0 else 0),.035,z*1.1),Vector3(1.075,.03,1.075),"d2cebb" if (x+z)%3 else "c9c4af")
 for i in range(-15,16):cube(Vector3(i,.07,11.75),Vector3(.96,.14,.62),"e2d6b9")
 shop(-8,-9,"d7c4a3","春日茶行")
 shop(0,-9.5,"c29273","海風旅舍")
 shop(8,-9,"dce0c4","潮間書店")
 for pair in [Vector2(-8,3.5),Vector2(9,4.5)]:
  var x=pair.x
  var z=pair.y
  cube(Vector3(x,.22,z),Vector3(3,.44,2),"b5aa8d",true)
  cube(Vector3(x,.46,z),Vector3(2.8,.04,1.8),"7c8359")
  cylinder(Vector3(x,1.8,z),.13,3.0,"83704e")
  for k in range(9):ball(Vector3(x+sin(k*2.4)*.7,3.3+sin(k*3.0)*.4,z+cos(k*2.4)*.7),Vector3(1.05,.8,1.02),"7e9567" if k%2 else "97a56e")
  for k in range(8):ball(Vector3(x+sin(k*6.0)*1.1,.65,z+cos(k*6.0)*.7),Vector3(.22,.32,.20),"8c9a68")
 for x in [-5.0,6.0]:
  for n in range(5):cube(Vector3(x,.47,6+(n-2)*.11),Vector3(2,.075,.09),"957851")
  for y in [.75,.91,1.06]:cube(Vector3(x,y,6.3),Vector3(2,.10,.065),"957851")
  for dx in [-.75,.75]:cube(Vector3(x+dx,.25,6),Vector3(.055,.5,.65),"466257")
  cube(Vector3(x,.45,6),Vector3(2,.9,.7),"95785100",true)
 for x in range(-14,15,4):
  cylinder(Vector3(x,.45,11),.11,.9,"576c60")
  cylinder(Vector3(x,.92,11),.15,.075,"c4ba94")
 for i in range(13):
  var x=-12+i*2.0
  var y=4.5-sin(i/12.0*PI)*.65
  ball(Vector3(x,y,-2),Vector3(.2,.25,.2),"e6b976")
  cylinder(Vector3(x,y+.27,-2),.015,.16,"677760")
 var sea=MeshInstance3D.new()
 var plane=PlaneMesh.new()
 plane.size=Vector2(180,90)
 sea.mesh=plane
 sea.position=Vector3(0,-.12,57)
 var water=StandardMaterial3D.new()
 water.albedo_color=Color("528a92")
 water.roughness=.25
 water.metallic=.22
 sea.material_override=water
 add(sea,world)
 for k in range(20):cube(Vector3(sin(k*19)*40,-.105,15+k*1.5),Vector3(2.4,.01,.035),"b8cebb")
 cube(Vector3(0,1,12.2),Vector3(34,2,.4),"00000000",true)
 cube(Vector3(-16,1,0),Vector3(.3,2,28),"00000000",true)
 cube(Vector3(16,1,0),Vector3(.3,2,28),"00000000",true)
 cube(Vector3(0,1,-13.5),Vector3(34,2,.4),"00000000",true)
 # Store static repeated geometry as actual MultiMesh editor resources.
 for key in batches:
  var spec=key.split(":")
  if spec[1].ends_with("00"):continue
  var node=MultiMeshInstance3D.new()
  var multi=MultiMesh.new()
  multi.transform_format=MultiMesh.TRANSFORM_3D
  var mesh: PrimitiveMesh
  if spec[0]=="box":mesh=BoxMesh.new();mesh.size=Vector3.ONE
  elif spec[0]=="sphere":mesh=SphereMesh.new();mesh.radius=1;mesh.height=2;mesh.radial_segments=14;mesh.rings=7
  else:mesh=CylinderMesh.new();mesh.top_radius=1;mesh.bottom_radius=1;mesh.height=1;mesh.radial_segments=12
  mesh.material=material(spec[1])
  multi.mesh=mesh
  multi.instance_count=batches[key].size()
  for i in range(multi.instance_count):multi.set_instance_transform(i,batches[key][i])
  node.multimesh=multi
  node.set_script(load("res://scripts/static_batch.gd"))
  var authored: Array[Transform3D]=[]
  for transform in batches[key]:authored.append(transform)
  node.set("authored_transforms",authored)
  node.name=spec[0]+"_"+spec[1]
  add(node,world)
 actor("Player",Vector3(0,.04,4),true,"",PackedVector3Array(),world)
 var npcs=Node3D.new()
 npcs.name="NPCs"
 add(npcs,world)
 actor("Guide",Vector3(-2,.04,0),false,"guide",PackedVector3Array([Vector3(-2,0,0),Vector3(-3,0,-2),Vector3(-1,0,-2)]),npcs)
 actor("Keeper",Vector3(8,.04,-5),false,"keeper",PackedVector3Array([Vector3(8,0,-5),Vector3(6.5,0,-5)]),npcs)
 var pickups=Node3D.new()
 pickups.name="Pickups"
 add(pickups,world)
 for item in [["tea",Vector3(-5,.85,-4)],["tree",Vector3(-5,.85,2.5)],["sea",Vector3(6,.85,9)]]:
  var m=MeshInstance3D.new()
  var sphere=SphereMesh.new()
  sphere.radius=.19
  sphere.height=.38
  sphere.radial_segments=8
  sphere.rings=4
  m.mesh=sphere
  m.material_override=material("d7ad61")
  m.name=item[0]
  m.position=item[1]
  add(m,pickups)
 var pivot=Node3D.new()
 pivot.name="CameraRig"
 pivot.rotation.x=-.23
 add(pivot,world)
 var spring=SpringArm3D.new()
 spring.name="SpringArm3D"
 spring.spring_length=5.2
 spring.collision_mask=1
 spring.margin=.18
 var shape=SphereShape3D.new()
 shape.radius=.15
 spring.shape=shape
 add(spring,pivot)
 var cam=Camera3D.new()
 cam.current=true
 cam.fov=49
 cam.near=.08
 cam.far=150
 add(cam,spring)
 var packed=PackedScene.new()
 var err=packed.pack(world)
 assert(err==OK)
 assert(ResourceSaver.save(packed,"res://main.tscn")==OK)
 print("SCENE_SAVED ",batches.size()," static batches; native CharacterBody3D + SpringArm3D + AnimationTree")
 world.free()
 quit()
