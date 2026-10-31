"""V25 returns to character identity: bento-shop boss apron and headscarf.
Starts from native V20 boss source, retains all existing mesh data/materials.
Creates a NEW documented pose test (source has no animation), not a walk.
Only the boss is edited; the approved uncle belt is kept on its prior branch.
"""
import os,sys,json,hashlib,math
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent
for folder in (HERE,HERE.parent/'taiwan_v24',HERE.parent/'taiwan_v21',HERE.parent/'taiwan_v20'):sys.path.insert(0,str(folder))
from source_waist import coordinates,digest_mesh
from motion_qa import GLB,evaluated_bvh
from apron import build
INPUT=Path(os.getenv('V25_INPUT','input/v20')).resolve()
OUT=Path(os.getenv('V25_OUT','outputs/v25')).resolve()
for d in ('renders','qa'): (OUT/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=INPUT/'blend/boss_v20_source.blend'
assert sha(source)=='0d30371698623cbe7f6112beac5b187cd9f9a9e94becb257271c301c915f920b'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;rig=bpy.data.objects['RootRig_boss']
body=bpy.data.objects['TrueMPFBBody_boss']
shirt=bpy.data.objects['OpenSourceCloth_boss_toigo_fisherman_sweater']
pants=bpy.data.objects['OpenSourceCloth_boss_toigo_wool_pants']
hair=bpy.data.objects['HairFitted_boss']
original=[o for o in scene.objects if o.type=='MESH']
assert len(body.data.vertices)==13380 and len(rig.data.bones)==53
assert len(body.data.shape_keys.key_blocks)==11
assert not any(m.type=='MASK' for m in body.modifiers)
assert not rig.animation_data or not rig.animation_data.action,'Unexpected existing animation; do not overwrite'
scene.render.fps=24;scene.frame_start=0;scene.frame_end=60;scene.frame_set(0)
for obj in original:
    if obj.data.shape_keys:
        for key in obj.data.shape_keys.key_blocks[1:]:key.value=0.
bpy.context.view_layer.update()
initial={o.name:digest_mesh(o) for o in original}
textures={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.source=='FILE' and im.packed_file}
for im in bpy.data.images:
    if im.source=='FILE':assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
height=float(coordinates(body)[:,2].max())
added,design=build(body,shirt,pants,hair,rig)
assert all(digest_mesh(o)==initial[o.name] for o in original)
for ob in added:
    for v in ob.data.vertices:
        assert 1<=len(v.groups)<=4
        assert abs(sum(g.weight for g in v.groups)-1)<2e-6

# Calibrate stress poses from measured bone endpoints rather than assumed axes.
def reset_pose():
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4);b.rotation_mode='XYZ'
    bpy.context.view_layer.update()
def endpoint(name):return rig.matrix_world@rig.pose.bones[name].head

def choose(bone_name,end_name,axis_goal,sign,angles,min_distance):
    reset_pose();base=endpoint(end_name).copy();options=[]
    for axis in range(3):
        for angle in angles:
            reset_pose();r=[0.,0.,0.];r[axis]=angle
            rig.pose.bones[bone_name].rotation_euler=r;bpy.context.view_layer.update()
            delta=endpoint(end_name)-base
            score=sign*delta[axis_goal]-(abs(delta.x)*.5 if axis_goal!=2 else 0.)
            options.append((score,tuple(r),tuple(delta)))
    score,r,d=max(options,key=lambda p:p[0]);reset_pose()
    assert sign*d[axis_goal]>min_distance,(bone_name,d)
    return r,{'bone':bone_name,'endpoint':end_name,'rotation_xyz':r,'world_delta_m':d}
calibration={};raised={}
for side in ('l','r'):
    r,p=choose('upperarm_'+side,'hand_'+side,2,1,(-.75,.75,-.95,.95),.18)
    raised['upperarm_'+side]=r;calibration['raise_'+side]=p
r,calibration['bend']=choose('spine_02','head',1,-1,(-.25,.25),.025)
bend={'spine_02':r};step={}
for side,sign in (('l',-1),('r',1)):
    r,p=choose('thigh_'+side,'foot_'+side,1,sign,(-.30,.30),.04)
    step['thigh_'+side]=r;calibration['step_'+side]=p
poses={'neutral':(0,{}),'arms_raise':(12,raised),'torso_bend':(24,bend),
       'step':(36,step),'head_turn':(48,{'head':(0.,.30,0.)}),'reset':(60,{})}
for name,(frame,angles) in poses.items():
    scene.frame_set(frame);reset_pose()
    for name,r in angles.items():rig.pose.bones[name].rotation_euler=r
    bpy.context.view_layer.update()
    for b in rig.pose.bones:b.keyframe_insert(data_path='rotation_euler',frame=frame,group=b.name)
scene.frame_set(0);bpy.context.view_layer.update()

camera=scene.camera;scene.render.engine='CYCLES';scene.cycles.samples=28;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=720;scene.render.resolution_y=840;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
views=[('full_front',0,0,'full'),('full_threequarter',0,35,'full'),('full_back',0,180,'full'),
       ('portrait',0,0,'portrait'),('portrait_threequarter',0,35,'portrait'),
       ('apron_detail',0,0,'apron'),('raise_full',12,0,'full'),('bend_full',24,35,'full'),
       ('bend_back',24,150,'full'),('step_full',36,35,'full'),('head_turn',48,0,'portrait')]
images=[]
def render(label,frame,angle,kind):
    scene.frame_set(frame);bpy.context.view_layer.update()
    if kind=='full':target=Vector((0,0,height*.51));scale=height*1.20
    elif kind=='portrait':target=Vector((0,-.015,height-.13));scale=.47
    else:target=Vector((0,-.06,.94));scale=.80
    a=math.radians(angle);camera.location=target+Vector((math.sin(a)*3,-math.cos(a)*3,0))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    path=OUT/'renders'/('boss_v25_'+label+'.png');scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True);images.append(path.name)
for state in ('before','after'):
    for ob in added:ob.hide_render=(state=='before')
    for name,frame,angle,kind in views:render(state+'_'+name,frame,angle,kind)
for ob in added:ob.hide_render=False
scene.frame_set(0);bpy.context.view_layer.update()

# Inspect evaluated source front cloth points in the existing stress poses.
# This is a bounded front-view diagnostic, NOT cloth simulation or art approval.
def evaluated(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
    try:return np.asarray([tuple(ev.matrix_world@v.co) for v in m.vertices])
    finally:ev.to_mesh_clear()
panel=bpy.data.objects['V25_Apron_Main'];scarf=bpy.data.objects['V25_Headscarf_Crown']
rest_panel=evaluated(panel);rest_scarf=evaluated(scarf)
max_panel_motion=max_scarf_motion=0.;frame_checks={}
for frame in range(61):
    scene.frame_set(frame);bpy.context.view_layer.update()
    p=evaluated(panel);h=evaluated(scarf)
    max_panel_motion=max(max_panel_motion,float(np.linalg.norm(p-rest_panel,axis=1).max()))
    max_scarf_motion=max(max_scarf_motion,float(np.linalg.norm(h-rest_scarf,axis=1).max()))
    trees=[evaluated_bvh(o) for o in (body,shirt,pants)]
    checked=visible=0;examples=[]
    for j in range(2,32,3):
        for i in range(3,26,3):
            q=p[j*29+i];origin=Vector((q[0],-1.,q[2]));checked+=1
            hits=[]
            for t in trees:
                hit,_,_,_=t.ray_cast(origin,Vector((0,1,0)),2.)
                if hit is not None:hits.append(hit.y)
            if hits and min(hits)<q[1]-.0015:
                visible+=1
                if len(examples)<5:examples.append({'row':j,'column':i,'depth_m':float(q[1]-min(hits))})
    frame_checks[str(frame)]={'samples':checked,'underlying_surface_in_front':visible,'first_positions':examples}
assert max_panel_motion>.01 and max_scarf_motion>.005
scene.frame_set(0);bpy.context.view_layer.update()
assert all(digest_mesh(o)==initial[o.name] for o in original)
for im in bpy.data.images:
    if im.name in textures:assert hashlib.sha256(im.packed_file.data).hexdigest()==textures[im.name]

def export(path,animated):
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig,*original,*added]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_skins=True,export_morph=True,
        export_animations=animated,export_morph_normal=False,export_cameras=False,export_lights=False)
    d=GLB(path).doc
    assert len(d['skins'])==1 and len(d['skins'][0]['joints'])==53
    assert any(len(m.get('extras',{}).get('targetNames',[]))==10 for m in d['meshes'])
    assert path.stat().st_size<6000000
    for n in d['nodes']:
        if n.get('name','').startswith('V25_') and 'mesh' in n:assert 'skin' in n
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'animations':len(d.get('animations',[])),
      'mesh_count':len(d['meshes']),'animation_channels':sum(len(a.get('channels',[])) for a in d.get('animations',[]))}
neutral=export(OUT/'boss_v25_apron.glb',False)
stress=export(OUT/'boss_v25_apron_stress.glb',True);assert stress['animations']==1
scene.frame_set(0);bpy.context.view_layer.update()
target=Vector((0,0,height*.51));camera.location=(1.5,-3,height*.51)
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=height*1.20
bpy.ops.file.pack_all();blend=OUT/'boss_v25_apron.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report={'status':'OCCUPATION_WARDROBE_PILOT_REQUIRES_VISUAL_REVIEW','source_blend_sha256':sha(source),
 'role':'bento-shop boss, orange-yellow apron and headscarf','source_run':41149410362,
 'native_body_vertices':13380,'bones':53,'body_morphs':10,'new_accessories_only':True,
 'unchanged_original_meshes':list(initial),'existing_texture_bytes_unchanged':list(textures),
 'design':design,'neutral_glb':neutral,'stress_glb':stress,'source_blend':{'file':blend.name,'sha256':sha(blend)},
 'new_pose_calibration':calibration,'new_pose_angles':poses,'source_61_frame_front_panel_checks':frame_checks,
 'source_max_panel_motion_m':max_panel_motion,'source_max_headscarf_motion_m':max_scarf_motion,
 'motion_scope':'New 0-2.5s pose stress clip, source had no animation. Not walk/run or simulated cloth.',
 'original_hair_brief_pending':True,'original_short_curly_hair_not_completed':True,
 'renders':images,'art_approved':False,'other_characters_changed':False}
(OUT/'qa/source_report.json').write_text(json.dumps(report,indent=2))

# Reimport final bytes in a fresh scene; source vertex indices need not survive.
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=24
bpy.ops.import_scene.gltf(filepath=str(OUT/stress['file']))
rig=next(o for o in scene.objects if o.type=='ARMATURE');assert len(rig.data.bones)==53
new=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('V25_')];assert len(new)==len(added)
for o in new:
    assert any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)
panel=bpy.data.objects['V25_Apron_Main'];scarf=bpy.data.objects['V25_Headscarf_Crown']
scene.frame_set(0);bpy.context.view_layer.update();p0=evaluated(panel);h0=evaluated(scarf);pm=hm=0.
for frame in range(0,61,6):
    scene.frame_set(frame);bpy.context.view_layer.update()
    pm=max(pm,float(np.linalg.norm(evaluated(panel)-p0,axis=1).max()))
    hm=max(hm,float(np.linalg.norm(evaluated(scarf)-h0,axis=1).max()))
assert pm>.01 and hm>.005
roundtrip={'new_skinned_meshes':[o.name for o in new],'frames_checked':list(range(0,61,6)),
 'max_apron_motion_m':pm,'max_headscarf_motion_m':hm,'final_glb_sha256':stress['sha256'],
 'scope':'11 reimported pose times, not all61 source times; shape and art still require view inspection'}
# Photograph delivered GLB in exactly the source light rig, not generated imagery.
bpy.ops.wm.open_mainfile(filepath=str(blend));scene=bpy.context.scene;camera=scene.camera
for o in list(scene.objects):
    if o.type in ('MESH','ARMATURE'):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/stress['file']))
for name,frame,angle,kind in [('full_front',0,0,'full'),('portrait',0,0,'portrait'),('bend_full',24,35,'full')]:render('delivered_'+name,frame,angle,kind)
bpy.ops.wm.open_mainfile(filepath=str(blend))
assert len(bpy.data.objects['TrueMPFBBody_boss'].data.vertices)==13380
assert len(bpy.data.objects['RootRig_boss'].data.bones)==53
for im in bpy.data.images:
    if im.source=='FILE':assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
(OUT/'qa/roundtrip.json').write_text(json.dumps(roundtrip,indent=2))
report['renders']=images;report['delivered_reimport']=roundtrip
(OUT/'report.json').write_text(json.dumps(report,indent=2))
manifest={'schema_version':1,'asset_id':'boss_v25_apron','format':'glTF 2.0 GLB','unit':'meter',
 'source':'Verified V20 native MPFB boss + original CC0 apron and headscarf geometry',
 'model_file':neutral['file'],'source_file':blend.name,'clips':[],'min_animation_count':0,
 'requirements':{'skins':True,'animated':False,'visual_review':True},
 'additional_animation_file':stress['file'],'license_note':'Original accessory geometry CC0-1.0; inherited MakeHuman assets retain existing provenance; software licenses unchanged'}
(OUT/'asset_manifest.json').write_text(json.dumps(manifest,indent=2))
print('V25_DONE',json.dumps({'neutral':neutral,'stress':stress,'added':len(added),'renders':len(images),'source_geometry_unchanged':True}),flush=True)
