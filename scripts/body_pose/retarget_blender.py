"""Nova77 position-based, reference-calibrated FK retarget pilot.
Blender background only. No mesh, rest-rig or facial-key edits.
Not a twist, IK/contact, finger solver or proof of NVIDIA inference.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Quaternion,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pose_io import SEGMENTS,REQUIRED_JOINTS,load_nova,sha256,verify_glb

def signature(rig,meshes):
    h=hashlib.sha256()
    for b in rig.data.bones:h.update(repr((b.name,b.parent.name if b.parent else None,tuple(tuple(r) for r in b.matrix_local),b.length)).encode())
    rig_hash=h.hexdigest();h=hashlib.sha256()
    for m in sorted(meshes,key=lambda x:x.name):
        h.update(m.name.encode())
        for v in m.data.vertices:h.update(repr((tuple(v.co),tuple((g.group,g.weight) for g in v.groups))).encode())
        if m.data.shape_keys:
            for k in m.data.shape_keys.key_blocks:
                h.update(k.name.encode())
                for v in k.data:h.update(repr(tuple(v.co)).encode())
    return {'rest_rig_sha256':rig_hash,'geometry_weights_morphs_sha256':h.hexdigest()}

def source_basis(points,name):
    a,b=SEGMENTS[name];direction=points[b]-points[a]
    if direction.length<1e-5:raise ValueError('Degenerate source segment '+name)
    y=direction.normalized();across=points[67]-points[72];up=points[3]-points[0]
    if across.length<1e-5 or up.length<1e-5:raise ValueError('Degenerate torso frame')
    front=up.cross(across).normalized();guide=across.normalized() if name.startswith(('foot_','ball_')) else front
    z=guide-y*guide.dot(y)
    if z.length<1e-4:raise ValueError('Unobservable roll plane '+name)
    z.normalize();x=y.cross(z).normalized();z=x.cross(y).normalized()
    return Matrix((x,y,z)).transposed().to_quaternion()

def make_fixture(path):
    """Original synthetic TEST data. Never calls or impersonates NVIDIA."""
    points=[Vector((0,0,1)) for _ in range(77)]
    torso=[(0,0,1),(0,0,1.12),(0,0,1.28),(0,0,1.42),(0,0,1.50),(0,0,1.58),(0,0,1.64),(0,0,1.82)]
    for i,p in enumerate(torso):points[i]=Vector(p)
    for i,p in {8:(.07,0,1.70),9:(-.07,0,1.70),10:(0,-.07,1.72)}.items():points[i]=Vector(p)
    for side,start,hip in [(1,11,67),(-1,39,72)]:
        for j,x in enumerate((.07,.20,.48,.72)):points[start+j]=Vector((side*x,0,1.44))
        for j,p in enumerate(((.1,0,1),(.1,0,.55),(.1,0,.1),(.1,-.12,.08),(.1,-.23,.08))):points[hip+j]=Vector((side*p[0],p[1],p[2]))
        wrist=start+3
        for j in range(wrist+1,start+28):points[j]=points[wrist]+Vector((side*.012*(j-wrist),-.02,.01))
    rows=[]
    for f in range(61):
        p=[v.copy() for v in points];phase=math.sin(math.pi*f/60);rot=Quaternion((0,-1,0),.95*phase);shoulder=p[12].copy()
        for i in range(13,39):p[i]=shoulder+rot@(p[i]-shoulder)
        shift=Vector((.20*phase,0,0));p=[v+shift for v in p]
        camera=[[v.x,-v.z,v.y+3] for v in p]
        body={'tracking_id':1,'keypoints_3d':camera,'keypoints_confidence':[1.0]*77,'joint_rotations':[[0,0,0,1] for _ in range(77)]}
        rows.append({'frame_id':f,'detections':[body]})
    path.write_text('\n'.join(json.dumps(r) for r in rows),encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--asset',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--pose',type=Path);p.add_argument('--fixture',action='store_true');p.add_argument('--fps',type=float,default=30);p.add_argument('--track-id',type=int,default=1)
    p.add_argument('--calibration-frame',type=int,default=0);p.add_argument('--root-motion',choices=['in-place','keep'],default='in-place');p.add_argument('--confidence',type=float,default=.35);p.add_argument('--max-hold',type=int,default=5);p.add_argument('--smoothing',type=float,default=1.0);p.add_argument('--render',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not 0<args.smoothing<=1 or args.max_hold<0 or args.confidence<0:raise ValueError('Invalid filter settings')
    if args.fixture==bool(args.pose):raise ValueError('Choose exactly one of --fixture or --pose')
    args.output.mkdir(parents=True,exist_ok=True);asset=args.asset.resolve();before_sha=sha256(asset)
    if args.fixture:raw=args.output/'SYNTHETIC_NOT_NVIDIA.json';make_fixture(raw)
    else:raw=args.pose
    motion=load_nova(raw,args.fps,args.track_id,'opencv','synthetic' if args.fixture else 'unverified-input')
    if args.calibration_frame not in [f['frame'] for f in motion['frames']]:raise ValueError('Calibration frame missing')
    reference=next(f for f in motion['frames'] if f['frame']==args.calibration_frame)
    if min(reference['confidence'][i] for i in REQUIRED_JOINTS)<args.confidence:raise ValueError('Low-confidence calibration frame')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if asset.suffix.lower()=='.blend':bpy.ops.wm.open_mainfile(filepath=str(asset),load_ui=False,use_scripts=False)
    elif asset.suffix.lower()=='.glb':bpy.ops.import_scene.gltf(filepath=str(asset))
    else:raise ValueError('Only .blend or .glb input is supported')
    rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    if len(rigs)!=1:raise ValueError('Expected exactly one armature; choose one explicitly')
    rig=rigs[0];meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    missing=sorted((set(SEGMENTS)|{'Root','hand_l','hand_r'})-set(rig.pose.bones.keys()))
    if missing:raise ValueError('Not the MPFB game53 profile; missing '+str(missing))
    if len(rig.data.bones)!=53:raise ValueError('Explicit game53 profile requires exactly 53 bones')
    if rig.pose.bones['Root'].parent:raise ValueError('Root must be a top-level bone')
    if any(c for b in rig.pose.bones for c in b.constraints if not c.mute):raise ValueError('Bake control-rig constraints first; will not delete them')
    world_scale=rig.matrix_world.to_scale()
    if min(world_scale)<=0 or max(world_scale)-min(world_scale)>1e-5:raise ValueError('Positive uniform armature scale required')
    original_signature=signature(rig,meshes);original_actions=[a.name for a in bpy.data.actions]
    for a in bpy.data.actions:a.use_fake_user=True
    rig.animation_data_create()
    for t in rig.animation_data.nla_tracks:t.mute=True
    rig.animation_data.action=None
    for b in rig.pose.bones:b.rotation_mode='QUATERNION';b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
    bpy.context.view_layer.update();scene=bpy.context.scene;scene.render.fps=round(args.fps);scene.render.fps_base=round(args.fps)/args.fps;scene.frame_start=1;scene.frame_end=len(motion['frames'])
    clip='PoseBridge_SYNTHETIC' if args.fixture else 'PoseBridge_CAPTURE_UNVERIFIED'
    if clip in bpy.data.actions:raise ValueError('Clip name already exists; use a clean source')
    action=bpy.data.actions.new(clip);action.use_fake_user=True;rig.animation_data.action=action
    refp=[Vector(x) for x in reference['points']];refbasis={n:source_basis(refp,n) for n in SEGMENTS}
    rest_world={n:(rig.matrix_world@rig.data.bones[n].matrix_local).to_quaternion() for n in SEGMENTS};rig_rot_inv=rig.matrix_world.to_quaternion().inverted();ordered=sorted(SEGMENTS,key=lambda n:len(rig.pose.bones[n].parent_recursive))
    target_leg=sum((rig.matrix_world.to_3x3()@(rig.data.bones[a].head_local-rig.data.bones[b].head_local)).length for a,b in [('thigh_l','calf_l'),('calf_l','foot_l')]);source_leg=(refp[67]-refp[68]).length+(refp[68]-refp[69]).length;scale=target_leg/source_leg
    if not .1<scale<10:raise ValueError('Unreasonable body scale; check units/calibration')
    previous={};holds={n:0 for n in SEGMENTS};held_frames=0;max_jump=0.;samples=[];root=rig.pose.bones['Root']
    for i,frame in enumerate(motion['frames'],1):
        scene.frame_set(i);points=[Vector(x) for x in frame['points']]
        if min(frame['confidence'][j] for j in (0,3,67,72))<args.confidence:raise ValueError(f'Frame {frame["frame"]}: torso/root tracking unreliable; split the clip')
        delta=(points[0]-refp[0])*scale if args.root_motion=='keep' else Vector((0,0,0))
        root.location=root.bone.matrix_local.to_3x3().inverted()@rig.matrix_world.inverted().to_3x3()@delta;root.keyframe_insert(data_path='location',frame=i);bpy.context.view_layer.update()
        for name in ordered:
            a,b=SEGMENTS[name]
            try:
                if min(frame['confidence'][a],frame['confidence'][b])<args.confidence:raise ValueError('confidence')
                current=source_basis(points,name);world_q=current@refbasis[name].inverted()@rest_world[name];desired_q=rig_rot_inv@world_q;holds[name]=0
            except ValueError:
                holds[name]+=1;held_frames+=1
                if name not in previous or holds[name]>args.max_hold:raise ValueError(f'Unreliable {name} at frame {frame["frame"]}; hold limit exceeded')
                desired_q=previous[name].copy()
            if name in previous:
                if previous[name].dot(desired_q)<0:desired_q.negate()
                jump=previous[name].rotation_difference(desired_q).angle;max_jump=max(max_jump,jump);desired_q=previous[name].slerp(desired_q,args.smoothing)
            previous[name]=desired_q.copy();bone=rig.pose.bones[name];data=bone.bone;parent_matrix=bone.parent.matrix.copy() if bone.parent else Matrix.Identity(4);parent_rest=bone.parent.bone.matrix_local if bone.parent else Matrix.Identity(4);base=parent_matrix@parent_rest.inverted()@data.matrix_local
            desired=desired_q.to_matrix().to_4x4();desired.translation=base.translation
            basis=data.convert_local_to_pose(desired,data.matrix_local,parent_matrix=parent_matrix,parent_matrix_local=parent_rest,invert=True)
            bone.rotation_quaternion=basis.to_quaternion().normalized();bone.keyframe_insert(data_path='rotation_quaternion',frame=i,group=name);bpy.context.view_layer.update()
        samples.append({'frame':i,'joints':{n:list(rig.matrix_world@rig.pose.bones[n].head) for n in ['Root','hand_l','hand_r','foot_l','foot_r']}})
    if hasattr(action,'fcurves'):curves=list(action.fcurves)
    else:curves=[f for layer in action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]
    for curve in curves:
        for key in curve.keyframe_points:key.interpolation='LINEAR'
    if signature(rig,meshes)!=original_signature:raise RuntimeError('Rest rig, geometry, weights or facial shape keys were changed')
    def relative_pos(s,n):return Vector(s['joints'][n])-Vector(s['joints']['Root'])
    left=max((relative_pos(s,'hand_l')-relative_pos(samples[0],'hand_l')).length for s in samples);right=max((relative_pos(s,'hand_r')-relative_pos(samples[0],'hand_r')).length for s in samples);root_motion=max((Vector(s['joints']['Root'])-Vector(samples[0]['joints']['Root'])).length for s in samples)
    if args.fixture:
        if left<.10 or right>.005:raise RuntimeError(f'Synthetic left/right regression failed: {left=}, {right=}')
        if args.root_motion=='in-place' and root_motion>1e-5:raise RuntimeError('In-place root moved')
        if args.root_motion=='keep' and root_motion<.05:raise RuntimeError('Root motion disappeared')
    scene.frame_set(1);bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT')
    for o in [rig]+meshes:o.select_set(True)
    bpy.context.view_layer.objects.active=rig;stem=asset.stem+'_'+args.root_motion.replace('-','_');glb=args.output/(stem+'.glb');blend=args.output/(stem+'.blend')
    opts=dict(filepath=str(glb),export_format='GLB',use_selection=True,export_skins=True,export_animations=True,export_morph=True,export_morph_normal=False,export_cameras=False,export_lights=False,export_force_sampling=True)
    properties=bpy.ops.export_scene.gltf.get_rna_type().properties
    if 'export_animation_mode' in properties:opts['export_animation_mode']='ACTIONS'
    if 'export_anim_single_armature' in properties:opts['export_anim_single_armature']=True
    bpy.ops.export_scene.gltf(**opts);validation=verify_glb(glb,clip)
    if set(validation['skins'][0])!=set(rig.data.bones.keys()):raise RuntimeError('Bone loss on GLB export')
    source_validation=verify_glb(asset) if asset.suffix=='.glb' else None
    if source_validation:
        if source_validation['morph_target_sets']!=validation['morph_target_sets']:raise RuntimeError('Morph target loss on GLB export')
        old_names={a['name'] for a in source_validation['clips']};new_names={a['name'] for a in validation['clips']}
        if not old_names.issubset(new_names):raise RuntimeError('Existing GLB animation clip lost')
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    report={'schema':1,'status':'SYNTHETIC_PIPELINE_PASS' if args.fixture else 'CAPTURE_RETARGET_REQUIRES_REVIEW','source_asset':asset.name,'source_sha256':before_sha,'blender_version':bpy.app.version_string,'source_motion':{k:v for k,v in motion.items() if k!='frames'},'live_nvidia_inference':False,'art_approved':False,'foot_contact_approved':False,'clip':clip,'fps':args.fps,'frames':len(samples),'source_bones':len(rig.data.bones),'rotation_mapped_bones':SEGMENTS,'preserved_unmapped_bones':sorted(set(rig.data.bones.keys())-set(SEGMENTS)-{'Root'}),'root_motion_mode':args.root_motion,'root_translation_scale':scale,'left_hand_relative_displacement_m':left,'right_hand_relative_displacement_m':right,'root_displacement_m':root_motion,'held_joint_frames':held_frames,'max_source_step_rad':max_jump,'source_actions_preserved_in_blend':original_actions,'invariant_hashes':original_signature,'glb':glb.name,'blend':blend.name,'glb_validation':validation,'pose_samples':samples,'limitations':['Calibration pose must correspond to intended target rest pose','Position-derived roll is approximation, not axial twist capture','Fingers and face are not retargeted','No foot locking/IK/contact or clothing collision correction','Camera movement is not world-space actor movement']}
    (args.output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(args.output/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2))
    manifest={'schema_version':1,'asset_id':stem,'model_file':glb.name,'source_file':blend.name,'unit':'meter','format':'glTF 2.0 GLB','coordinate_system':'Blender Z-up; glTF Y-up','clips':[clip],'min_animation_count':1,'source':'Existing V17 character + original synthetic fixture' if args.fixture else 'Existing character + supplied pose JSONL','requirements':{'skins':True,'animated':True,'visual_review':True},'license_note':'Original source character licensing remains applicable. Synthetic motion is not NVIDIA output.'}
    (args.output/'asset_manifest.json').write_text(json.dumps(manifest,indent=2))
    if args.render:
        scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.resolution_x=480;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
        if scene.world is None:scene.world=bpy.data.worlds.new('QA World')
        scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
        coords=[m.matrix_world@Vector(v) for m in meshes for v in m.bound_box];zmin=min(v.z for v in coords);zmax=max(v.z for v in coords);height=zmax-zmin;center=Vector((0,0,(zmin+zmax)/2))
        cam_data=bpy.data.cameras.new('Pose QA');cam=bpy.data.objects.new('Pose QA',cam_data);scene.collection.objects.link(cam);cam_data.type='ORTHO';cam_data.ortho_scale=height*1.65;scene.camera=cam
        for name,loc,energy in [('Key',(3,-4,4),450),('Fill',(-3,-2,3),250)]:
            d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;d.energy=energy;d.size=3;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
        for frame,view in [(1,'front'),(31,'front'),(31,'side')]:
            scene.frame_set(min(frame,scene.frame_end));bpy.context.view_layer.update();cam.location=center+Vector((0,-4,0) if view=='front' else (4,0,0));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(args.output/f'preview_{view}_{frame:03d}.png');bpy.ops.render.render(write_still=True)
    if sha256(asset)!=before_sha:raise RuntimeError('Original source asset changed')
    print('POSE_BRIDGE_PASS',json.dumps({k:report[k] for k in ['status','source_bones','frames','left_hand_relative_displacement_m','right_hand_relative_displacement_m','root_displacement_m']}))
if __name__=='__main__':main()
