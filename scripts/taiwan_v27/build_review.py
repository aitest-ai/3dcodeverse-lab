"""V27 missing-role production pilot. New original MPFB humans, not GLB copies.
Exports native source, neutral/stress GLBs, actual portraits and expressions.
Existing V20/V24/V25/V26 four-character assets are never read or overwritten.
"""
import os,sys,json,hashlib,math,struct
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from profiles import PROFILES,REQUIRED_KEYS
from native import create,coordinates
from accessories import build as add_accessories
CID=os.environ['V27_ID'];assert CID in PROFILES
OUT=Path(os.getenv('V27_OUT','outputs/v27/'+CID)).resolve()
OUT.mkdir(parents=True,exist_ok=True);(OUT/'renders').mkdir(exist_ok=True);(OUT/'qa').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
body,rig,attached,garments,hair,report=create(CID,OUT)
basecoords=coordinates(body).copy()
added,accessory=add_accessories(CID,body,rig,*garments,attached)
assert np.array_equal(coordinates(body),basecoords),'Accessories changed native body'
meshes=[body,*attached,*added]
report.update(accessory)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=28;scene.cycles.use_denoising=True
scene.cycles.device='CPU';scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.fps=24;scene.frame_start=0;scene.frame_end=60
if not scene.world:scene.world=bpy.data.worlds.new('V27_Studio')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.17,.19,.21,1.)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
camera_data=bpy.data.cameras.new('V27_Camera');camera=bpy.data.objects.new('V27_Camera',camera_data)
scene.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO'
for name,position,energy in [('Key',(3,-4,4),480),('Fill',(-3,-3,3),310),('Rim',(-2,3,4),310)]:
    light=bpy.data.lights.new(name,'AREA');ob=bpy.data.objects.new(name,light);scene.collection.objects.link(ob)
    ob.location=position;ob.rotation_euler=(Vector((0,0,1.1))-ob.location).to_track_quat('-Z','Y').to_euler()
    light.energy=energy;light.size=3.3
h=float(coordinates(body)[:,2].max());images=[]
def render(name,angle=0,portrait=False):
    if portrait:target=Vector((0,0,h-.13));scale=.50
    else:target=Vector((0,0,h*.54));scale=h*1.25
    a=math.radians(angle);camera.location=target+Vector((math.sin(a)*3,-math.cos(a)*3,0))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    path=OUT/'renders'/(CID+'_'+name+'.png');scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True);images.append(path.name)
    return path.name

def parse(path):
    b=Path(path).read_bytes();magic,version,total=struct.unpack_from('<4sII',b,0)
    n,kind=struct.unpack_from('<I4s',b,12)
    assert magic==b'glTF' and version==2 and total==len(b) and kind==b'JSON'
    return json.loads(b[20:20+n])

def export(path,animated=False):
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig,*meshes]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_skins=True,
        export_morph=True,export_animations=animated,export_morph_normal=False,export_cameras=False,export_lights=False,export_extras=True)
    doc=parse(path)
    assert len(doc.get('skins',[]))==1 and len(doc['skins'][0]['joints'])==53
    assert any(REQUIRED_KEYS<=set(m.get('extras',{}).get('targetNames',[])) for m in doc['meshes'])
    if path.stat().st_size>6000000:raise RuntimeError('New GLB exceeds 6MB '+str(path.stat().st_size))
    for node in doc['nodes']:
        if node.get('name','').startswith('V27_'+CID+'_') and 'mesh' in node:assert 'skin' in node
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'animations':len(doc.get('animations',[])),
            'animation_channels':sum(len(a.get('channels',[])) for a in doc.get('animations',[])),'mesh_count':len(doc['meshes'])}

neutral=export(OUT/(CID+'.glb'))
for name,angle in [('front',0),('threequarter',35),('side',90),('back',180)]:render(name,angle)
render('face',0,True);render('face_threequarter',35,True)
# A second portrait without removable head accessories makes the new face inspectable.
head_groups={'baseball_cap','peaked_cap','straw_hat','white_headband','glasses'}
headwear=[ob for ob in added if ob.get('accessory_group') in head_groups]
for ob in headwear:ob.hide_render=True
render('face_without_headwear',0,True)
for ob in headwear:ob.hide_render=False
keys_objects=[ob for ob in meshes if ob.data.shape_keys]
expression_metrics={}
for name,values in [('smile',{'mouthSmile':.70}),('mouth_open',{'mouthOpen':.65}),('blink',{'eyeBlinkLeft':.92,'eyeBlinkRight':.92}),('frown',{'mouthFrown':.55,'browDownLeft':.45,'browDownRight':.45})]:
    for ob in keys_objects:
        for key in ob.data.shape_keys.key_blocks[1:]:key.value=values.get(key.name,0.)
    bpy.context.view_layer.update();render('expression_'+name,0,True);expression_metrics[name]=values
for ob in keys_objects:
    for key in ob.data.shape_keys.key_blocks[1:]:key.value=0.
bpy.context.view_layer.update()

# Calibrate real hand lift on this newly fitted skeleton instead of assuming axes.
def reset():
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4);bone.rotation_mode='XYZ'
    bpy.context.view_layer.update()

def best_raise(side):
    reset();wrist=rig.pose.bones['hand_'+side]
    start=rig.matrix_world@wrist.head;choices=[]
    for axis in range(3):
        for a in (-.90,.90):
            reset();rot=[0.,0.,0.];rot[axis]=a
            rig.pose.bones['upperarm_'+side].rotation_euler=rot;bpy.context.view_layer.update()
            end=rig.matrix_world@wrist.head;choices.append((end.z-start.z,rot,tuple(end-start)))
    chosen=max(choices,key=lambda x:x[0]);reset()
    if chosen[0]<.15:raise RuntimeError('Unable to verify true upward wrist motion '+side)
    return chosen
raise_l=best_raise('l');raise_r=best_raise('r')
poses={'neutral':(0,{}),'arms_raise':(12,{'upperarm_l':raise_l[1],'upperarm_r':raise_r[1]}),
       'bend':(24,{'spine_02':(.22,0,0)}),'step':(36,{'thigh_l':(.32,0,0),'thigh_r':(-.22,0,0)}),
       'look':(48,{'head':(0,.27,0)}),'reset':(60,{})}
for name,(frame,values) in poses.items():
    scene.frame_set(frame);reset()
    for b,v in values.items():rig.pose.bones[b].rotation_euler=v
    bpy.context.view_layer.update()
    for bone in rig.pose.bones:bone.keyframe_insert(data_path='rotation_euler',frame=frame,group=bone.name)
if rig.animation_data and rig.animation_data.action:rig.animation_data.action.name='V27_'+CID+'_Stress_NotWalk'

def evaluated_points(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:return np.asarray([tuple(ev.matrix_world@v.co) for v in me.vertices])
    finally:ev.to_mesh_clear()
scene.frame_set(0);bpy.context.view_layer.update()
representatives={group:next(ob for ob in added if ob.name==names[0]) for group,names in accessory['accessory_groups'].items()}
rest={group:evaluated_points(ob) for group,ob in representatives.items()};motions={group:0. for group in rest}
for frame in range(0,61,3):
    scene.frame_set(frame);bpy.context.view_layer.update()
    for group,ob in representatives.items():motions[group]=max(motions[group],float(np.linalg.norm(evaluated_points(ob)-rest[group],axis=1).max()))
    if frame==12:render('pose_arms_raise',0)
    if frame==24:render('pose_bend',35)
    if frame==48:render('pose_look',0,True)
assert all(d>.001 for d in motions.values()),motions
scene.frame_set(0);bpy.context.view_layer.update()
animated=export(OUT/(CID+'_stress.glb'),True);assert animated['animations']==1
# Store real source with embedded images; no headgear visibility flags remain set.
bpy.ops.file.pack_all();blend=OUT/(CID+'.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report.update({'character':CID,'status':'MISSING_ROLE_FIRST_SOURCE_PILOT','build_commit':os.getenv('GITHUB_SHA'),
    'blender':bpy.app.version_string,'neutral_glb':neutral,'stress_glb':animated,
    'editable_blend':{'file':blend.name,'bytes':blend.stat().st_size,'sha256':sha(blend)},
    'source_accessory_motion_max_m':motions,'source_motion_sample_frames':list(range(0,61,3)),
    'wrist_raise':{'left_m':raise_l[0],'right_m':raise_r[0]},'expression_presets':expression_metrics,
    'motion_scope':'Own new 0-2.5 second FK stress clip, not a walk/run/squat cycle or cloth simulation',
    'renders':images,'original_four_untouched':True,'art_approved':False})
(OUT/'qa/source_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))

# Remove model objects but retain exact source lights for actual exported-model render.
for ob in list(scene.objects):
    if ob.type in ('MESH','ARMATURE'):bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/animated['file']))
rig=next(o for o in scene.objects if o.type=='ARMATURE');assert len(rig.data.bones)==53
reimport_meshes=[o for o in scene.objects if o.type=='MESH']
assert len([o for o in reimport_meshes if o.name.startswith('V27_'+CID+'_')])==len(added)
scene.frame_set(0);bpy.context.view_layer.update();render('delivered_front',0);render('delivered_face',0,True)
reps={group:bpy.data.objects[names[0]] for group,names in accessory['accessory_groups'].items()}
rest={g:evaluated_points(o) for g,o in reps.items()};moved={g:0. for g in reps}
for frame in range(0,61,6):
    scene.frame_set(frame);bpy.context.view_layer.update()
    for g,o in reps.items():moved[g]=max(moved[g],float(np.linalg.norm(evaluated_points(o)-rest[g],axis=1).max()))
    if frame==12:render('delivered_arms_raise',0)
assert all(v>.001 for v in moved.values()),moved
bpy.ops.wm.open_mainfile(filepath=str(blend))
assert len(bpy.data.objects['TrueMPFBBody_'+CID].data.vertices)==13380
assert len(bpy.data.objects['RootRig_'+CID].data.bones)==53
source_images=[]
for image in bpy.data.images:
    if image.source=='FILE':
        assert image.packed_file and len(image.pixels)>0 and max(image.size)<=512
        source_images.append({'name':image.name,'size':list(image.size)})
report['delivered_reimport']={'accessory_motion_max_m':moved,'sample_frames':list(range(0,61,6)),
 'actual_model_rendered':True,'source_blend_reopened':True,'decoded_source_images':source_images,
 'scope':'Actual exported skin follows test clip; movement checks are not collision approval'}
report['renders']=images
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
manifest={'schema_version':1,'asset_id':CID,'format':'glTF 2.0 GLB','unit':'meter',
 'source':'New original MPFB phenotype and face targets; licensed MakeHuman MHCLO plus original occupational accessories',
 'model_file':CID+'.glb','source_file':CID+'.blend','clips':[],'min_animation_count':0,
 'requirements':{'skins':True,'animated':False,'visual_review':True},'additional_animation_file':CID+'_stress.glb',
 'license_note':'MakeHuman core/system/Faceunits/shirts01/pants01 CC0; used source headers and hashes in report; original accessory geometry CC0',
 'character_label':PROFILES[CID]['label'],'source_body_vertices':13380,'body_morph_count':14,'art_approved':False}
(OUT/'asset_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('V27_ACTUAL_NEW_ROLE_DONE',CID,json.dumps({'neutral':neutral,'animated':animated,'source_vertices':13380,'renders':len(images),'accessory_motion':moved}),flush=True)
