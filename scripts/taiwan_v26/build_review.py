"""V26: actual native Blender wardrobe for hero and courier, no image proxies.
Both start from hash-pinned V20 sources. New pose clip is explicitly separate
from any source Action. Original body/face/clothing and textures are preserved.
"""
import os,sys,json,hashlib,math
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent
for folder in (HERE,HERE.parent/'taiwan_v25',HERE.parent/'taiwan_v24',HERE.parent/'taiwan_v21',HERE.parent/'taiwan_v20'):sys.path.insert(0,str(folder))
from source_waist import coordinates,digest_mesh
from motion_qa import GLB,evaluated_bvh
from wardrobe import build
ROLE=os.environ.get('V26_ROLE','jie');assert ROLE in ('you','jie')
INPUT=Path(os.getenv('V26_INPUT','input/v20')).resolve()
OUT=Path(os.getenv('V26_OUT','outputs/v26')).resolve()/ROLE
for d in ('renders','qa'): (OUT/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=INPUT/'blend'/(ROLE+'_v20_source.blend')
expected={'you':'16187a515aa6102eed599408927de16bc7d571e99f580440fc926e930a1752ab','jie':'f48a6e2ef3cbfa384327ab881ffc062bad63cd74ffb77566505d21438d3f6f6c'}
assert sha(source)==expected[ROLE]
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;rig=bpy.data.objects['RootRig_'+ROLE];body=bpy.data.objects['TrueMPFBBody_'+ROLE]
shirt=next(o for o in scene.objects if o.type=='MESH' and o.name.startswith('OpenSourceCloth_'+ROLE) and 'pants' not in o.name)
pants=next(o for o in scene.objects if o.type=='MESH' and o.name.startswith('OpenSourceCloth_'+ROLE) and 'pants' in o.name)
hair=bpy.data.objects['HairFitted_'+ROLE];original=[o for o in scene.objects if o.type=='MESH']
assert len(original)==10 and len(body.data.vertices)==13380 and len(rig.data.bones)==53
assert len(body.data.shape_keys.key_blocks)==11 and not any(m.type=='MASK' for m in body.modifiers)
source_action=rig.animation_data.action if rig.animation_data else None
source_action_name=source_action.name if source_action else None
if source_action:source_action.use_fake_user=True
rig.animation_data_clear()
scene.render.fps=24;scene.frame_start=0;scene.frame_end=60;scene.frame_set(0)
for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4);bone.rotation_mode='XYZ'
for ob in original:
    if ob.data.shape_keys:
        for k in ob.data.shape_keys.key_blocks[1:]:k.value=0.
bpy.context.view_layer.update()
initial={o.name:digest_mesh(o) for o in original}
textures={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.source=='FILE' and im.packed_file}
for im in bpy.data.images:
    if im.source=='FILE':assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
height=float(coordinates(body)[:,2].max())
added,design=build(ROLE,body,shirt,pants,hair,rig)
assert all(digest_mesh(o)==initial[o.name] for o in original),'Original source mesh was modified'
for ob in added:
    for vertex in ob.data.vertices:
        assert len(vertex.groups)>0,(ob.name,vertex.index)
        assert abs(sum(g.weight for g in vertex.groups)-1.)<1e-4,(ob.name,vertex.index)

# New stress Action; the old source Action (if any) is retained, not overwritten.
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
            d=endpoint(end_name)-base
            score=sign*d[axis_goal]-(abs(d.x)*.5 if axis_goal!=2 else 0.)
            options.append((score,tuple(r),tuple(d)))
    score,r,d=max(options,key=lambda p:p[0]);reset_pose()
    assert sign*d[axis_goal]>min_distance,(bone_name,d)
    return r,{'bone':bone_name,'endpoint':end_name,'rotation_xyz':r,'world_delta_m':d}
cal={};raised={}
for side in ('l','r'):
    r,p=choose('upperarm_'+side,'hand_'+side,2,1,(-.70,.70,-.90,.90),.18)
    raised['upperarm_'+side]=r;cal['raise_'+side]=p
r,cal['bend']=choose('spine_02','head',1,-1,(-.25,.25),.025);bend={'spine_02':r};step={}
for side,sign in (('l',-1),('r',1)):
    r,p=choose('thigh_'+side,'foot_'+side,1,sign,(-.30,.30),.04)
    step['thigh_'+side]=r;cal['step_'+side]=p
poses={'neutral':(0,{}),'arms_raise':(12,raised),'torso_bend':(24,bend),'step':(36,step),
       'head_turn':(48,{'head':(0.,.30,0.)}),'reset':(60,{})}
for name,(frame,angles) in poses.items():
    scene.frame_set(frame);reset_pose()
    for name,r in angles.items():rig.pose.bones[name].rotation_euler=r
    bpy.context.view_layer.update()
    for b in rig.pose.bones:b.keyframe_insert(data_path='rotation_euler',frame=frame,group=b.name)
rig.animation_data.action.name='V26_'+ROLE+'_IdentityStress'
scene.frame_set(0);bpy.context.view_layer.update()
camera=scene.camera
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
views=[('full_front',0,0,'full'),('full_threequarter',0,35,'full'),('full_back',0,180,'full'),
       ('portrait',0,0,'portrait'),('portrait_threequarter',0,35,'portrait'),
       ('raise_full',12,0,'full'),('bend_full',24,90,'full'),('head_turn',48,0,'portrait')]
images=[]
def render(label,frame,angle,kind):
    scene.frame_set(frame);bpy.context.view_layer.update()
    if kind=='full':target=Vector((0,.035,height*.52));scale=height*1.23
    else:target=Vector((0,-.020,height-.15));scale=.55
    a=math.radians(angle);camera.location=target+Vector((math.sin(a)*3,-math.cos(a)*3,0))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    path=OUT/'renders'/(ROLE+'_v26_'+label+'.png');scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True);images.append(path.name)
for stage in ('before','after'):
    for ob in added:ob.hide_render=(stage=='before')
    for name,frame,angle,kind in views:render(stage+'_'+name,frame,angle,kind)
for ob in added:ob.hide_render=False
render('after_full_side',0,90,'full')
scene.frame_set(0);bpy.context.view_layer.update()

# Track actual deformation across each whole accessory group (not image motion).
def evaluated(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:return np.asarray([tuple(ev.matrix_world@v.co) for v in me.vertices])
    finally:ev.to_mesh_clear()
representatives={group:names[0] for group,names in design['groups'].items()}
rest={group:evaluated(bpy.data.objects[name]) for group,name in representatives.items()}
maximum={group:0. for group in representatives};per_frame={}
for frame in range(61):
    scene.frame_set(frame);bpy.context.view_layer.update();values={}
    for group,name in representatives.items():
        p=evaluated(bpy.data.objects[name]);distance=float(np.linalg.norm(p-rest[group],axis=1).max())
        maximum[group]=max(maximum[group],distance);values[group]=distance
    per_frame[str(frame)]=values
assert all(v>.001 for v in maximum.values()),maximum
scene.frame_set(0);bpy.context.view_layer.update()
assert all(digest_mesh(o)==initial[o.name] for o in original)
for im in bpy.data.images:
    if im.name in textures:assert hashlib.sha256(im.packed_file.data).hexdigest()==textures[im.name]

def export(path,animated):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in [rig,*original,*added]:ob.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_skins=True,export_morph=True,
        export_animations=animated,export_morph_normal=False,export_cameras=False,export_lights=False,export_extras=True)
    doc=GLB(path).doc
    assert len(doc['skins'])==1 and len(doc['skins'][0]['joints'])==53
    assert any(len(m.get('extras',{}).get('targetNames',[]))==10 for m in doc['meshes'])
    assert path.stat().st_size<6000000,('6MB limit',path.stat().st_size)
    for node in doc['nodes']:
        if node.get('name','').startswith('V26_') and 'mesh' in node:assert 'skin' in node,node
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'animations':len(doc.get('animations',[])),
      'mesh_count':len(doc['meshes']),'animation_channels':sum(len(a.get('channels',[])) for a in doc.get('animations',[]))}
neutral=export(OUT/(ROLE+'_v26_identity.glb'),False)
stress=export(OUT/(ROLE+'_v26_identity_stress.glb'),True);assert stress['animations']>=1
scene.frame_set(0);bpy.context.view_layer.update()
# Leave the editable scene in a useful full-body view.
target=Vector((0,.035,height*.52));camera.location=(1.5,-3,height*.52)
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=height*1.23
bpy.ops.file.pack_all();blend=OUT/(ROLE+'_v26_identity.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report={'status':'ROLE_IDENTITY_CANDIDATE_REQUIRES_VISUAL_REVIEW','role':ROLE,'source_run':41149410362,'source_blend_sha256':sha(source),
 'native_body_vertices':13380,'bones':53,'body_morphs':10,'unchanged_original_meshes':list(initial),
 'existing_texture_bytes_unchanged':list(textures),'source_original_action':source_action_name,
 'source_action_retained_if_present':True,'new_stress_action':'V26_'+ROLE+'_IdentityStress',
 'design':design,'neutral_glb':neutral,'stress_glb':stress,'source_blend':{'file':blend.name,'sha256':sha(blend)},
 'source_61_times':per_frame,'source_max_group_motion_m':maximum,'pose_calibration':cal,'pose_angles':poses,
 'renders':images,'art_approved':False,'scope':'Hero and courier identity wardrobe only; no new face/hair or other two character rebuild',
 'motion_scope':'New 0-2.5s stress clip, not walk/run/squat or cloth simulation','collision_approved':False}
(OUT/'qa/source_report.json').write_text(json.dumps(report,indent=2))

# Check the actual delivered bytes in a fresh Blender scene.
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=24
bpy.ops.import_scene.gltf(filepath=str(OUT/stress['file']))
rig=next(ob for ob in scene.objects if ob.type=='ARMATURE');assert len(rig.data.bones)==53
new=[ob for ob in scene.objects if ob.type=='MESH' and ob.name.startswith('V26_')]
assert len(new)==len(added),(len(new),len(added))
for ob in new:assert any(m.type=='ARMATURE' and m.object==rig for m in ob.modifiers),ob.name
scene.frame_set(0);bpy.context.view_layer.update()
rest={g:evaluated(bpy.data.objects[n]) for g,n in representatives.items()}
movement={g:0. for g in rest}
for frame in range(0,61,6):
    scene.frame_set(frame);bpy.context.view_layer.update()
    for g,name in representatives.items():movement[g]=max(movement[g],float(np.linalg.norm(evaluated(bpy.data.objects[name])-rest[g],axis=1).max()))
assert all(v>.001 for v in movement.values()),movement
roundtrip={'final_glb_sha256':stress['sha256'],'added_skin_objects':[o.name for o in new],
 'frames_checked':list(range(0,61,6)),'max_group_motion_m':movement,'source61_reload11_not_same_count':True}
# Same source lights with final GLB replacing model, to expose export differences.
bpy.ops.wm.open_mainfile(filepath=str(blend));scene=bpy.context.scene;camera=scene.camera
for ob in list(scene.objects):
    if ob.type in ('MESH','ARMATURE'):bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/stress['file']))
for label,frame,angle,kind in [('full_front',0,0,'full'),('portrait',0,35,'portrait'),('bend_side',24,90,'full')]:
    render('delivered_'+label,frame,angle,kind)
bpy.ops.wm.open_mainfile(filepath=str(blend))
assert len(bpy.data.objects['TrueMPFBBody_'+ROLE].data.vertices)==13380
assert len(bpy.data.objects['RootRig_'+ROLE].data.bones)==53
for im in bpy.data.images:
    if im.source=='FILE':assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
(OUT/'qa/roundtrip.json').write_text(json.dumps(roundtrip,indent=2))
report['renders']=images;report['delivered_reimport']=roundtrip
(OUT/'report.json').write_text(json.dumps(report,indent=2))
manifest={'schema_version':1,'asset_id':ROLE+'_v26_identity','format':'glTF 2.0 GLB','unit':'meter',
 'source':'Verified native V20 character with original occupational accessories and independently copied CC0 garment derivative',
 'model_file':neutral['file'],'source_file':blend.name,'clips':[],'min_animation_count':0,
 'requirements':{'skins':True,'animated':False,'visual_review':True},'additional_animation_file':stress['file'],
 'license_note':'New original accessory geometry CC0-1.0; garment derivatives retain MakeHuman CC0 provenance; software licenses unchanged'}
(OUT/'asset_manifest.json').write_text(json.dumps(manifest,indent=2))
print('V26_COMPLETE',json.dumps({'role':ROLE,'neutral':neutral,'stress':stress,'new_meshes':len(added),'renders':len(images),'source_unchanged':True}),flush=True)
