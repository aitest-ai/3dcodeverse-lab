"""V31 shui: actual gravity/collision cloth rest solve + original hem repair.
Bake settled cloth to a standard skinned GLB. This is not runtime cloth physics.
All other characters and original face/hair/animation are untouched.
"""
import os,sys,json,math,struct,hashlib
from pathlib import Path
import numpy as np
import bpy,bmesh
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent
for d in (HERE,HERE.parent/'taiwan_v20',HERE.parent/'taiwan_v21',HERE.parent/'taiwan_v24'):
    sys.path.insert(0,str(d))
from source_waist import coordinates,digest_mesh
from motion_qa import arm_faces
from belt import WeightSource
INPUT=Path(os.getenv('V31_INPUT','input/v30')).resolve()
OUT=Path(os.getenv('V31_OUT','outputs/v31')).resolve()
for d in ('renders','qa','simulation'): (OUT/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=INPUT/'shui.blend'
assert sha(source)=='222140c0c1ed52f01337462837cb7c13b259f6a828e66ff87eb022fc70d7907b'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
scene.frame_set(0);bpy.context.view_layer.update()
rig=bpy.data.objects['RootRig_shui'];body=bpy.data.objects['TrueMPFBBody_shui']
shirt=bpy.data.objects['OpenSourceCloth_shui_namuhekam_male_polo_shirt']
pants=bpy.data.objects['OpenSourceCloth_shui_cortu_cargo_pants']
old=bpy.data.objects['V30_shui_DrapedShoulderTowel'];old_mat=old.data.materials[0]
original=[o for o in scene.objects if o.type=='MESH'];preserved=[o for o in original if o not in (shirt,old)]
digests={o.name:digest_mesh(o) for o in preserved}
assert len(body.data.vertices)==13380 and len(rig.data.bones)==53
assert len(body.data.shape_keys.key_blocks)==15
assert not any(m.type=='MASK' for m in body.modifiers)
action=rig.animation_data.action;assert action
image_hashes={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
height=float(coordinates(body)[:,2].max());camera=scene.camera
scene.render.engine='CYCLES';scene.cycles.samples=28;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.fps=24
images=[]

def evaluated(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:
        p=np.asarray([tuple(ev.matrix_world@v.co) for v in me.vertices])
        f=[tuple(x.vertices) for x in me.polygons]
        return p,f
    finally:ev.to_mesh_clear()

def tree(obj,exclude=None):
    p,f=evaluated(obj)
    if exclude is not None:f=[face for i,face in enumerate(f) if not exclude[i]]
    return BVHTree.FromPolygons(p.tolist(),f)

views=[('full',0,'full',0),('front',0,'chest',0),('threequarter',35,'chest',0),
 ('side',85,'chest',0),('back',180,'chest',0),('hem_front',0,'hem',0),('hem_back',180,'hem',0),
 ('raise',0,'chest',12),('bend',35,'chest',24),('step',35,'full',36),('turn',0,'chest',48)]

def render(label,angle=0,kind='chest',frame=0):
    scene.frame_set(frame);bpy.context.view_layer.update()
    if kind=='full':target=Vector((0,0,height*.53));scale=height*1.23
    elif kind=='hem':target=Vector((0,-.01,.900));scale=.49
    else:target=Vector((0,0,height-.455));scale=.72
    a=math.radians(angle);camera.location=target+Vector((3*math.sin(a),-3*math.cos(a),0))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    path=OUT/'renders'/('shui_v31_'+label+'.png');scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True);images.append(path.name)

# Fixed front projection matching separate GLB audit: not a global hole count.
def hem_scan():
    bt,st,pt=tree(body),tree(shirt),tree(pants)
    data={'rays':9801,'shirt_hits':0,'pants_in_front':0,'body_in_front':0,'either_in_front':0}
    for z in np.linspace(.82,1.03,81):
        for x in np.linspace(-.19,.19,121):
            origin=Vector((x,-1,z));direction=Vector((0,1,0))
            sh=st.ray_cast(origin,direction,2.)
            if sh[0] is None:continue
            data['shirt_hits']+=1
            bh=bt.ray_cast(origin,direction,2.);ph=pt.ray_cast(origin,direction,2.)
            b=bh[0] is not None and bh[3]<sh[3]-.001
            p=ph[0] is not None and ph[3]<sh[3]-.001
            data['body_in_front']+=int(b);data['pants_in_front']+=int(p);data['either_in_front']+=int(b or p)
    return data

before_scan={}
for f in (0,12,24,36,48,60):
    scene.frame_set(f);bpy.context.view_layer.update();before_scan[str(f)]=hem_scan()
for n,a,k,f in views:render('before_'+n,a,k,f)
scene.frame_set(0);bpy.context.view_layer.update()

# Adjust the existing untucked shirt over body and pants; maintain all original
# faces, UV, weights, and relative facial morph offsets.
start=coordinates(shirt);target=start.copy();limbs=arm_faces(body,rig)
obstacles=[tree(body,limbs),tree(pants)];center=np.array([0.,-.012])
for i,p in enumerate(start):
    if p[2]>.995 or p[2]<.80 or abs(p[0])>.26:continue
    v=p[:2]-center;r=float(np.linalg.norm(v))
    if r<.04:continue
    unit=v/r;origin=Vector((*(center+unit*.42),p[2]));direction=Vector((-unit[0],-unit[1],0.))
    candidates=[]
    for t in obstacles:
        hit,_,_,dist=t.ray_cast(origin,direction,.42)
        if hit is not None:candidates.append(np.linalg.norm(np.asarray(hit[:2])-center))
    if not candidates:continue
    fade=np.clip((.995-p[2])/.045,0,1);fade=fade*fade*(3-2*fade)
    needed=max(0.,max(candidates)+.0075-r)*fade
    if needed>.035:raise RuntimeError('Hem repair over35mm; inspect source instead '+str((i,needed)))
    target[i,:2]+=unit*needed
world_delta=target-start;local_delta=world_delta@np.asarray(shirt.matrix_world.inverted().to_3x3()).T
keys=list(shirt.data.shape_keys.key_blocks) if shirt.data.shape_keys else []
key_old=[np.asarray([tuple(v.co) for v in k.data]) for k in keys]
local=np.asarray([tuple(v.co) for v in shirt.data.vertices])
faces_before=[tuple(f.vertices) for f in shirt.data.polygons]
shirt.data.vertices.foreach_set('co',np.asarray(local+local_delta,dtype='f4').ravel())
for k,p in zip(keys,key_old):k.data.foreach_set('co',np.asarray(p+local_delta,dtype='f4').ravel())
shirt.data.update();shirt.update_tag(refresh={'DATA'});bpy.context.view_layer.update()
assert [tuple(f.vertices) for f in shirt.data.polygons]==faces_before
hem_report={'moved_original_vertices':int((np.linalg.norm(world_delta,axis=1)>1e-7).sum()),
 'maximum_shift_m':float(np.linalg.norm(world_delta,axis=1).max()),'original_faces_preserved':True,
 'all_existing_shape_keys_offset_together':len(keys),'method':'radial outer envelope of actual torso+trousers, 7.5mm clearance, lower hem only'}
assert hem_report['moved_original_vertices']>10
np.savez_compressed(OUT/'qa/hem_source_delta.npz',before=start,after=target,delta=world_delta)

# Actual cloth solver. Neutral collision proxies are not exported. Detach the
# existing action only during this solve, then restore the identical action.
rig.animation_data.action=None
for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
scene.frame_set(1);bpy.context.view_layer.update()
coll=bpy.data.collections.new('V31_SIM_ONLY_COLLIDERS');scene.collection.children.link(coll)
proxies=[]
for obj in (body,shirt):
    p,f=evaluated(obj);me=bpy.data.meshes.new('SIM_'+obj.name);me.from_pydata(p.tolist(),[],f);me.update()
    proxy=bpy.data.objects.new('SIM_'+obj.name,me);coll.objects.link(proxy);proxy.hide_render=True
    proxy.modifiers.new('ActualClothCollision','COLLISION')
    proxy.collision.thickness_outer=.002;proxy.collision.thickness_inner=.001
    proxy.collision.cloth_friction=8.;proxies.append(proxy)
obstacles=[tree(p) for p in proxies]
# Shoulder height from real vertical geometry, not a floating assumed support.
xx=-.142;yy=-.007;surfaces=[]
for t in obstacles:
    hit,_,_,_=t.ray_cast(Vector((xx,yy,height+.15)),Vector((0,0,-1)),1.)
    if hit is not None:surfaces.append(hit.z)
assert surfaces
shoulder=max(surfaces);apex=shoulder+.009
rows,cols=73,15
# Constant-width rectangular textile starts with a loose U and mild seeded fold.
# Only a tiny shoulder-contact patch is pinned to prevent numerical sliding.
front_len=.34;back_len=.275;arc_len=math.pi*.145;length=front_len+arc_len+back_len
verts=[];uv=[];pin=[]
for j,s in enumerate(np.linspace(0,length,rows)):
    if s<front_len:
        y=-.180;z=apex-.145-front_len+s;tangent=np.array([0.,0.,1.])
    elif s<=front_len+arc_len:
        ang=-math.pi/2+(s-front_len)/.145
        y=.173*math.sin(ang)-.007;z=apex-.145+.145*math.cos(ang)
        tangent=np.array([0.,.173*math.cos(ang),-.145*math.sin(ang)]);tangent/=np.linalg.norm(tangent)
    else:
        y=.166;z=apex-.145-(s-front_len-arc_len);tangent=np.array([0.,0.,-1.])
    normal=np.cross(np.array([1.,0.,0.]),tangent);normal/=np.linalg.norm(normal)
    for i,u in enumerate(np.linspace(-.5,.5,cols)):
        # Seed modest irregular folds; gravity, bending and collisions determine final shape.
        fold=.010*math.sin(2*math.pi*(u*1.3+.07*math.sin(s*9)))+.003*math.sin(u*11+s*5)
        point=np.array([xx+u*.125,y,z])+normal*fold
        verts.append(tuple(point));uv.append((i/(cols-1),j/(rows-1)))
        if abs(s-(front_len+arc_len/2))<.012 and abs(u)<.16:pin.append(j*cols+i)
if not pin:raise RuntimeError('No small shoulder pin patch')
faces=[(j*cols+i,j*cols+i+1,(j+1)*cols+i+1,(j+1)*cols+i) for j in range(rows-1) for i in range(cols-1)]
me=bpy.data.meshes.new('V31_ClothSolverSheet');me.from_pydata(verts,[],faces);me.update()
cloth=bpy.data.objects.new('V31_GravityTowel',me);scene.collection.objects.link(cloth)
layer=me.uv_layers.new(name='TerryUV')
for f in me.polygons:
    f.use_smooth=True
    for li in f.loop_indices:layer.data[li].uv=uv[me.loops[li].vertex_index]
me.materials.append(old_mat)
vg=cloth.vertex_groups.new(name='SIM_small_shoulder_contact');vg.add(pin,1.,'REPLACE')
modifier=cloth.modifiers.new('ActualGravityClothSolve','CLOTH');settings=modifier.settings
settings.quality=12;settings.mass=.15;settings.tension_stiffness=25.;settings.compression_stiffness=25.
settings.shear_stiffness=8.;settings.bending_stiffness=.08
settings.tension_damping=8.;settings.compression_damping=8.;settings.shear_damping=8.;settings.bending_damping=.5
settings.air_damping=2.;settings.vertex_group_mass=vg.name;settings.pin_stiffness=1.
collision=modifier.collision_settings;collision.use_collision=True;collision.distance_min=.003
collision.collision_quality=6;collision.use_self_collision=True;collision.self_distance_min=.003
collision.self_friction=5.;collision.collection=coll
scene.gravity=(0,0,-9.81);scene.frame_start=1;scene.frame_end=120
modifier.point_cache.frame_start=1;modifier.point_cache.frame_end=120
# This setup is editable and rerunnable; exported game mesh will be the settled state.
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'simulation/cloth_setup.blend'),compress=True)
initial_cloth=np.asarray(verts);snapshots=[];energy=[];previous=None
for f in range(1,121):
    scene.frame_set(f);bpy.context.view_layer.update();p,_=evaluated(cloth)
    if not np.isfinite(p).all() or np.max(np.abs(p))>4:raise RuntimeError('Unstable cloth simulation')
    movement=float(np.max(np.linalg.norm(p-previous,axis=1))) if previous is not None else 0.
    energy.append({'frame':f,'max_step_displacement_m':movement})
    if f in (1,12,24,48,72,96,120):snapshots.append((f,p.copy()))
    if f%12==0:print('V31_CLOTH_SOLVER_FRAME',f,movement,float(p[:,2].min()),flush=True)
    previous=p
settled=previous.copy();delta=np.linalg.norm(settled-initial_cloth,axis=1)
assert delta.max()>.005,'Cloth solver did not actually move the cloth'
np.savez_compressed(OUT/'simulation/gravity_samples.npz',initial=initial_cloth,settled=settled,pin_indices=pin,frames=np.asarray([f for f,p in snapshots]),positions=np.asarray([p for f,p in snapshots]))
solver={'engine':'Blender CLOTH modifier, actual sequential evaluation','frames':120,'fps':24,
 'gravity_m_s2':[0,0,-9.81],'pin_vertices':pin,'simulation_vertices':len(verts),'width_m':.125,
 'quality_steps':12,'mass_setting':.15,'mass_note':'Blender solver tuning parameter, not measured towel areal density',
 'tension_stiffness':25.,'shear_stiffness':8.,'bending_stiffness':.08,'self_collision':True,
 'object_distance_m':.003,'max_settle_displacement_m':float(delta.max()),
 'last12_max_step_displacement_m':max(v['max_step_displacement_m'] for v in energy[-12:]),
 'step_displacements':energy,'not_runtime_physics':True,
 'pin_note':'small fixed shoulder-contact patch prevents drift; not a validated friction-only resting solution'}
# Bake exactly evaluated geometry, then add actual thickness and smooth display.
cloth.modifiers.remove(modifier);cloth.data.vertices.foreach_set('co',settled.astype('f4').ravel())
cloth.vertex_groups.clear();cloth.data.update()
bpy.context.view_layer.objects.active=cloth
sub=cloth.modifiers.new('SettledClothSurface','SUBSURF');sub.levels=1;sub.render_levels=1
bpy.ops.object.modifier_apply(modifier=sub.name)
solid=cloth.modifiers.new('RealCottonThickness','SOLIDIFY');solid.thickness=.0016;solid.offset=0.
solid.use_even_offset=True;bpy.ops.object.modifier_apply(modifier=solid.name)
for obj in proxies:bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.collections.remove(coll)
# Return the original action, do not generate new character animation.
rig.animation_data.action=action;scene.frame_start=0;scene.frame_end=60;scene.frame_set(0);bpy.context.view_layer.update()
WeightSource(shirt,rig).bind(cloth)
cloth['accessory_group']='shoulder_towel';cloth['license']='CC0-1.0 original V31 sheet and inherited V30 material'
cloth['drape']='Actual120-frame gravity/collision solve, frozen neutral surface + source rig skinning; no realtime cloth'
bpy.data.objects.remove(old,do_unlink=True)
for n,a,k,f in views:render('after_'+n,a,k,f)
after_scan={}
for f in (0,12,24,36,48,60):
    scene.frame_set(f);bpy.context.view_layer.update();after_scan[str(f)]=hem_scan()
scene.frame_set(0);bpy.context.view_layer.update()
assert all(digest_mesh(bpy.data.objects[n])==d for n,d in digests.items())
for im in bpy.data.images:
    if im.name in image_hashes:assert im.packed_file and hashlib.sha256(im.packed_file.data).hexdigest()==image_hashes[im.name]
meshes=[o for o in scene.objects if o.type=='MESH']

def export(path,animated):
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig,*meshes]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_skins=True,
     export_animations=animated,export_morph=True,export_morph_normal=False,export_cameras=False,export_lights=False,export_extras=True)
    binary=Path(path).read_bytes();magic,version,total=struct.unpack_from('<4sII',binary);n,kind=struct.unpack_from('<I4s',binary,12)
    assert magic==b'glTF' and total==len(binary) and version==2
    doc=json.loads(binary[20:20+n]);assert len(doc['skins'][0]['joints'])==53
    assert any(len(m.get('extras',{}).get('targetNames',[]))==14 for m in doc['meshes'])
    return {'file':path.name,'bytes':len(binary),'sha256':sha(path),'animations':len(doc.get('animations',[])),
     'animation_channels':sum(len(a.get('channels',[])) for a in doc.get('animations',[])),
     'over_6mb':len(binary)>6000000}
neutral=export(OUT/'shui.glb',False);animated=export(OUT/'shui_stress.glb',True)
assert animated['animations']==1 and animated['animation_channels']==159
bpy.ops.file.pack_all();blend=OUT/'shui.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report={'version':'V31','status':'PHYSICS_REST_DRAPE_AND_HEM_CANDIDATE','source_sha256':sha(source),
 'native_body_vertices':13380,'bones':53,'body_morphs':14,'preserved_original_meshes':list(digests),
 'hem':hem_report,'hem_before_keyframes':before_scan,'hem_after_keyframes':after_scan,'cloth_solver':solver,
 'neutral_glb':neutral,'stress_glb':animated,'source_blend':{'file':blend.name,'sha256':sha(blend)},
 'renders':images,'art_approved':False,'not_runtime_cloth':True,'other_seven_characters_untouched':True}
(OUT/'qa/source_report.json').write_text(json.dumps(report,indent=2))
# Remove all character meshes, import actual delivered animation into same light scene.
for o in list(scene.objects):
    if o.type in ('MESH','ARMATURE'):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/animated['file']))
rig=next(o for o in scene.objects if o.type=='ARMATURE');assert len(rig.data.bones)==53
body=bpy.data.objects['TrueMPFBBody_shui'];shirt=bpy.data.objects['OpenSourceCloth_shui_namuhekam_male_polo_shirt']
pants=bpy.data.objects['OpenSourceCloth_shui_cortu_cargo_pants']
export_scan={}
for f in (0,12,24,36,48,60):
    scene.frame_set(f);bpy.context.view_layer.update();export_scan[str(f)]=hem_scan()
render('delivered_full',0,'full',0);render('delivered_side',85,'chest',0)
render('delivered_bend',35,'chest',24);render('delivered_hem',0,'hem',0)
bpy.ops.wm.open_mainfile(filepath=str(blend))
assert len(bpy.data.objects['TrueMPFBBody_shui'].data.vertices)==13380
assert len(bpy.data.objects['TrueMPFBBody_shui'].data.shape_keys.key_blocks)==15
for im in bpy.data.images:
    if im.source=='FILE':assert im.packed_file and len(im.pixels)>0
report.update({'renders':images,'delivered_glb_rendered':True,'hem_delivered_keyframes':export_scan,'source_reopened':True})
(OUT/'report.json').write_text(json.dumps(report,indent=2))
(OUT/'asset_manifest.json').write_text(json.dumps({'schema_version':1,'asset_id':'shui','unit':'meter','format':'glTF2.0GLB',
 'source':'V30 original shui; V31 cloth-solver neutral drape and source hem repair','model_file':'shui.glb',
 'source_file':'shui.blend','clips':[],'min_animation_count':0,'requirements':{'skins':True,'animated':False,'visual_review':True},
 'additional_animation_file':'shui_stress.glb','art_approved':False,'license_note':'Inherited MakeHuman CC0 character, original CC0 towel; all sources preserved'},indent=2))
print('V31_DONE',json.dumps({'neutral':neutral,'animated':animated,'hem_before':before_scan,'hem_after':after_scan,'solver_last_motion':solver['last12_max_step_displacement_m']}),flush=True)
