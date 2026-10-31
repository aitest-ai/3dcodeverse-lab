"""V21 uncle: edit genuine V20 .blend, preserve all non-pants mesh data.
Four FK-calibrated stress poses, source/export scans, actual before/after Cycles.
Not a new from-scratch MPFB build; not a walk cycle or final art approval.
"""
import os,sys,json,hashlib,math
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent/'taiwan_v20'))
from waist_fit import candidate,opening,periodic
from source_waist import coordinates,digest_mesh
from motion_qa import GLB,arm_faces,evaluated_bvh
INPUT=Path(os.getenv('V21_INPUT','input/v20')).resolve()
OUT=Path(os.getenv('V21_OUT','outputs/v21')).resolve()
for name in ('models','blend','motion','renders','qa'): (OUT/name).mkdir(parents=True,exist_ok=True)
source=INPUT/'blend/uncle_v20_source.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)=='5d3167a5668cdca90f10bc3dc273d656e00e51610f134cc569985984ee147960'
bpy.ops.wm.open_mainfile(filepath=str(source))
body=bpy.data.objects['TrueMPFBBody_uncle'];rig=bpy.data.objects['RootRig_uncle']
shirt=bpy.data.objects['OpenSourceCloth_uncle_toigo_basic_tucked_t-shirt']
pants=bpy.data.objects['OpenSourceCloth_uncle_toigo_wool_pants']
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(body.data.vertices)==13380 and len(rig.data.bones)==53
assert len(body.data.shape_keys.key_blocks)==11
assert not any(m.type=='MASK' for m in body.modifiers)
textures=[]
for im in bpy.data.images:
    if im.source!='FILE':continue
    assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
    textures.append({'name':im.name,'size':list(im.size),'sha256':hashlib.sha256(im.packed_file.data).hexdigest()})
initial={o.name:digest_mesh(o) for o in meshes}
scene=bpy.context.scene;camera=scene.camera
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.fps=24
scene.frame_start=0;scene.frame_end=48
for o in meshes:
    if o.data.shape_keys:
        for k in o.data.shape_keys.key_blocks[1:]:k.value=0.

def reset():
    rig.animation_data_clear();scene.frame_set(0)
    for b in rig.pose.bones:
        b.matrix_basis=Matrix.Identity(4);b.rotation_mode='XYZ'
    bpy.context.view_layer.update()
reset()
original=coordinates(pants)
delta,center,fade,fitmeta=candidate(original,[list(p.vertices) for p in pants.data.polygons],
    coordinates(shirt),[list(p.vertices) for p in shirt.data.polygons])
roi=fitmeta['roi_z'];limbs=arm_faces(body,rig)

# Calibrate FK using actual world endpoints, never infer Euler-axis labels.
def endpoint(name):return rig.matrix_world@rig.pose.bones[name].head

def choose(bone_name,end_name,axis_goal,sign,angles,min_distance):
    reset();baseline=endpoint(end_name).copy();options=[]
    for axis in range(3):
        for angle in angles:
            reset();rot=[0.,0.,0.];rot[axis]=angle
            rig.pose.bones[bone_name].rotation_euler=rot;bpy.context.view_layer.update()
            difference=endpoint(end_name)-baseline
            score=sign*difference[axis_goal]-abs(difference.x)*(.0 if axis_goal==2 else .6)
            options.append((score,tuple(rot),tuple(difference)))
    score,rot,diff=max(options,key=lambda x:x[0]);reset()
    if sign*diff[axis_goal]<min_distance:raise RuntimeError('FK calibration failed '+bone_name)
    return rot,{'bone':bone_name,'endpoint':end_name,'rotation_xyz':rot,'world_displacement':diff}

calibration={};raised={}
for side in ('l','r'):
    rot,proof=choose('upperarm_'+side,'hand_'+side,2,1,(-1.,-.8,.8,1.),.20)
    raised['upperarm_'+side]=rot;calibration['raise_'+side]=proof
head=next(n for n in ('head','neck_01','neck') if n in rig.pose.bones)
rot,calibration['bend']=choose('spine_02',head,1,-1,(-.32,.32),.025)
bend={'spine_02':rot}
step={}
for side,sign in (('l',-1),('r',1)):
    foot=next(n for n in ('foot_'+side,'calf_'+side) if n in rig.pose.bones)
    rot,proof=choose('thigh_'+side,foot,1,sign,(-.38,.38),.05)
    step['thigh_'+side]=rot;calibration['step_'+side]=proof
poses={'neutral':(0,{}),'arms_raise':(12,raised),'torso_bend':(24,bend),'step':(36,step),'reset':(48,{})}

def pose(angles):
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4);b.rotation_mode='XYZ'
    for name,rotation in angles.items():rig.pose.bones[name].rotation_euler=rotation
    bpy.context.view_layer.update()

def render(label,angle=0,full=False):
    middle=(roi[0]+roi[1])/2;target=Vector((center[0],center[1],middle))
    if full:
        h=max(coordinates(body)[:,2]);target=Vector((0,0,h*.52));scale=h*1.25
    else:scale=.53
    a=math.radians(angle);camera.location=target+Vector((math.sin(a)*3,-math.cos(a)*3,0))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=scale
    path=OUT/'renders'/('uncle_v21_'+label+'.png');scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    return path.name

def evaluated_points(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    try:return np.array([tuple(ev.matrix_world@v.co) for v in mesh.vertices])
    finally:ev.to_mesh_clear()

# Waist-only rays. Pants must cover a tucked shirt BELOW their real upper edge.
# Shirt-over-pants above that edge is normal and explicitly not a defect.
def scan(body,shirt,pants,limbs):
    trees=[evaluated_bvh(o) for o in (body,shirt,pants)]
    p,indices,_=opening(evaluated_points(pants),[list(f.vertices) for f in pants.data.polygons],True)
    theta=np.arctan2(p[indices,1]-center[1],p[indices,0]-center[0]);heights=p[indices,2]
    counts={'rays':8200,'waist_body_hits':0,'natural_limb_hits':0,'visible_skin':0,'shirt_outside_below_band':0}
    views=[]
    for view in range(8):
        a=view*math.pi/4;r=Vector((math.sin(a),-math.cos(a),0));t=Vector((math.cos(a),math.sin(a),0))
        row={'degrees':view*45,'skin':0,'shirt_below_band':0}
        for iz in range(25):
            z=roi[0]+(roi[1]-roi[0])*iz/24
            for ix in range(41):
                origin=Vector((center[0],center[1],z))+r+t*(-.22+.44*ix/40)
                hits=[tree.ray_cast(origin,-r,2.) for tree in trees]
                point,_,face,bd=hits[0]
                if point is None:continue
                if limbs[face]:counts['natural_limb_hits']+=1;continue
                counts['waist_body_hits']+=1
                sd=hits[1][3] if hits[1][0] is not None else float('inf')
                pd=hits[2][3] if hits[2][0] is not None else float('inf')
                if bd<min(sd,pd)-.0015:counts['visible_skin']+=1;row['skin']+=1
                if math.isfinite(sd) and math.isfinite(pd) and sd<pd-.0015:
                    q=hits[2][0];ang=math.atan2(q.y-center[1],q.x-center[0])
                    rim=float(periodic(theta,heights,np.array([ang]))[0])
                    if z<rim-.008:
                        counts['shirt_outside_below_band']+=1;row['shirt_below_band']+=1
        views.append(row)
    return {**counts,'views':views}

before={};images=[]
for name,(frame,angles) in poses.items():
    if name=='reset':continue
    pose(angles);before[name]=scan(body,shirt,pants,limbs)
    for view,angle in (('front',0),('back45',135)):
        images.append(render('before_'+name+'_'+view,angle))
pose({});images.append(render('before_full',full=True))

# Refine radial fit against actual body+shirt at the proposed height.
# This is real source vertex displacement, not a mesh cover or painted patch.
body_tree=evaluated_bvh(body);shirt_tree=evaluated_bvh(shirt)
candidates=original+delta
for i,point in enumerate(candidates):
    if fade[i]<.05:continue
    radial=point[:2]-center;radius=np.linalg.norm(radial)
    if radius<.01:continue
    direction=radial/radius;origin=Vector((*(center+direction),point[2]));ray=Vector((-direction[0],-direction[1],0))
    for tree in (body_tree,shirt_tree):
        hit,_,_,_=tree.ray_cast(origin,ray,1.)
        if hit is None:continue
        needed=np.linalg.norm(np.array(hit[:2])-center)+.007
        if needed>radius:
            point[:2]+=direction*(needed-radius)*fade[i];radius=np.linalg.norm(point[:2]-center)
delta=candidates-original
if np.linalg.norm(delta,axis=1).max()>.055:raise RuntimeError('Source correction exceeds 55mm')
keys=list(pants.data.shape_keys.key_blocks) if pants.data.shape_keys else []
snapshots=[np.array([tuple(v.co) for v in k.data]) for k in keys]
local=np.array([tuple(v.co) for v in pants.data.vertices]);local_delta=delta@np.array(pants.matrix_world.inverted().to_3x3()).T
pants.data.vertices.foreach_set('co',np.asarray(local+local_delta,dtype='f4').ravel())
for k,old in zip(keys,snapshots):k.data.foreach_set('co',np.asarray(old+local_delta,dtype='f4').ravel())
pants.data.update();pants.update_tag(refresh={'DATA'});bpy.context.view_layer.update()
assert np.allclose(coordinates(pants),candidates,atol=2e-6)
changed=[o.name for o in meshes if digest_mesh(o)!=initial[o.name]]
assert changed==[pants.name],changed
basis=np.array([tuple(v.co) for v in keys[0].data])
error=max(float(np.max(np.abs((np.array([tuple(v.co) for v in k.data])-basis)-(old-snapshots[0])))) for k,old in zip(keys[1:],snapshots[1:]))
assert error<2e-6
fitmeta.update({'moved_vertices':int((np.linalg.norm(delta,axis=1)>1e-7).sum()),'maximum_shift_m':float(np.linalg.norm(delta,axis=1).max()),'relative_morph_error':error})

def export(path,animated):
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig,*meshes]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_skins=True,export_morph=True,export_animations=animated,export_morph_normal=False,export_cameras=False,export_lights=False)
    d=GLB(path).doc
    assert len(d['skins'])==1 and len(d['skins'][0]['joints'])==53
    assert any(len(m.get('extras',{}).get('targetNames',[]))==10 for m in d['meshes'])
    assert path.stat().st_size<6000000
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'animations':len(d.get('animations',[]))}

neutral=export(OUT/'models/uncle_v21_source.glb',False)
bpy.ops.file.pack_all();blend=OUT/'blend/uncle_v21_source.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
images.append(render('after_full',full=True))
for name,(frame,angles) in poses.items():
    scene.frame_set(frame);pose(angles)
    for b in rig.pose.bones:b.keyframe_insert(data_path='rotation_euler',frame=frame,group=b.name)
after={}
for frame in range(49):
    scene.frame_set(frame);bpy.context.view_layer.update();after[str(frame)]=scan(body,shirt,pants,limbs)
    print('V21_SOURCE_FRAME',frame,after[str(frame)]['visible_skin'],after[str(frame)]['shirt_outside_below_band'],flush=True)
    for name,(keyframe,_) in poses.items():
        if keyframe==frame and name!='reset':
            for view,angle in (('front',0),('back45',135)):images.append(render('after_'+name+'_'+view,angle))
scene.frame_set(0);bpy.context.view_layer.update()
animation=export(OUT/'motion/uncle_v21_stress.glb',True)
assert animation['animations']==1
report={'status':'SOURCE_CANDIDATE_NOT_ART_APPROVED','input_blend_sha256':sha(source),'native_body_vertices':13380,'bones':53,'body_morphs':10,'changed_meshes':changed,'non_target_meshes_unchanged':True,'fit':fitmeta,'calibration':calibration,'before_key_poses':before,'after_49_frames':after,'roi_z':roi,'center_xy':center.tolist(),'grid':[8,41,25],'tolerance_m':.0015,'neutral_glb':neutral,'stress_glb':animation,'source_blend':{'file':blend.name,'sha256':sha(blend)},'decoded_textures':textures,'renders':images,'art_approved':False,'motion_scope':'Own native FK-calibrated uncle stress poses, not a walk or cloth simulation'}
(OUT/'qa/uncle_v21_source_qa.json').write_text(json.dumps(report,indent=2))

# Independent scene reload of the actual delivered animation, not authored pose data.
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=24
bpy.ops.import_scene.gltf(filepath=str(OUT/'motion'/animation['file']))
rig=next(o for o in scene.objects if o.type=='ARMATURE')
body=bpy.data.objects['TrueMPFBBody_uncle'];shirt=bpy.data.objects['OpenSourceCloth_uncle_toigo_basic_tucked_t-shirt'];pants=bpy.data.objects['OpenSourceCloth_uncle_toigo_wool_pants']
limbs=arm_faces(body,rig);roundtrip={}
for frame in range(49):
    scene.frame_set(frame);bpy.context.view_layer.update();roundtrip[str(frame)]=scan(body,shirt,pants,limbs)
    print('V21_DELIVERED_FRAME',frame,roundtrip[str(frame)]['visible_skin'],flush=True)
bpy.ops.wm.open_mainfile(filepath=str(blend))
assert len(bpy.data.objects['TrueMPFBBody_uncle'].data.vertices)==13380
assert len(bpy.data.objects['RootRig_uncle'].data.bones)==53
source_reopened=[]
for im in bpy.data.images:
    if im.source=='FILE':
        assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
        source_reopened.append(im.name)
validation={'animation_sha256':animation['sha256'],'source_blend_sha256':sha(blend),'source_reopened_body_vertices':13380,'packed_images_decoded':source_reopened,'export_frames':roundtrip,'source_skin_hits':sum(v['visible_skin'] for v in after.values()),'export_skin_hits':sum(v['visible_skin'] for v in roundtrip.values()),'source_shirt_below_band_hits':sum(v['shirt_outside_below_band'] for v in after.values()),'export_shirt_below_band_hits':sum(v['shirt_outside_below_band'] for v in roundtrip.values()),'art_approved':False,'scope':'Two checks of the same 49-frame stress clip, 401800 rays each; no claim about other actions'}
(OUT/'qa/uncle_v21_roundtrip.json').write_text(json.dumps(validation,indent=2))
print('V21_DONE',json.dumps({k:v for k,v in validation.items() if k!='export_frames'}),flush=True)
