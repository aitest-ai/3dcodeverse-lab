"""Background Blender exporter. Original sources stay immutable; all new motion is a review candidate.
blender -b --python-exit-code 1 --python scripts/build_harbor.py
No external service, trained model, realtime cloth or runtime IK is used.
"""
import bpy, math, json, hashlib, statistics,sys,os
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
R=Path(__file__).resolve().parents[1];BUILD_ROOT=Path(os.environ.get('STUDIO_BUILD_ROOT',str(R/'work/rebuilt-assets'))).resolve();OUT=BUILD_ROOT/'harbor-courier-review/0.1.0';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'sources/harbor-v02/assets/harbor-courier-v02.blend'))
sc=bpy.context.scene;rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');original_fps=sc.render.fps
for tr in rig.animation_data.nla_tracks:tr.mute=True
sys.path.insert(0,str(R/'scripts'))
from repair_harbor_clothes import repair
cloth_changes=repair(rig)
bones=list(rig.data.bones);names=[b.name for b in bones]
soles=next(o for o in bpy.data.objects if o.type=='MESH' and o.name=='Merged_Sneaker_rubber')
sole_groups={s:[v.index for v in soles.data.vertices if (soles.matrix_world@v.co).x*(1 if s=='l' else -1)>0] for s in ['l','r']}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evaluated_soles():
    deps=bpy.context.evaluated_depsgraph_get();ob=soles.evaluated_get(deps);me=ob.to_mesh()
    result={s:min((ob.matrix_world@me.vertices[i].co).z for i in ids) for s,ids in sole_groups.items()};ob.to_mesh_clear();return result
def capture(action,seconds):
    rig.animation_data.action=action
    if action.slots:rig.animation_data.action_slot=action.slots[0]
    sc.frame_set(int(seconds*original_fps),subframe=(seconds*original_fps)%1)
    return {'q':{n:list(rig.pose.bones[n].matrix.to_quaternion()) for n in names},'p':{n:list(rig.pose.bones[n].matrix.translation) for n in names},'loc':list(rig.location),'sole':evaluated_soles()}
FPS=30;source={};raw={}
for name in ['Idle','Walk','Run']:
    a=bpy.data.actions[name];d=float(a.frame_range[1])/original_fps;count=round(d*FPS)
    samples=[capture(a,i/count*d) for i in range(count+1)]
    raw[name]={'duration':d,'samples':samples}
    speeds=[]
    for s in ['l','r']:
        floor=min(f['sole'][s] for f in samples)
        for a,b in zip(samples,samples[1:]):
            v=(b['p']['foot_'+s][1]-a['p']['foot_'+s][1])/(d/count)
            if max(a['sole'][s],b['sole'][s])<floor+.025 and v>.15:speeds.append(v)
    source[name]={'speed_mps':statistics.median(speeds) if speeds and name!='Idle' else 0,'duration':d,'sole_min_m':min(min(f['sole'].values()) for f in samples),'sole_max_lowest_m':max(min(f['sole'].values()) for f in samples)}
assert max(f['p']['foot_l'][1] for f in raw['Walk']['samples'])-min(f['p']['foot_l'][1] for f in raw['Walk']['samples'])>.2, 'Source Walk did not evaluate; check action slot'
write(OUT/'source-motion.json',{'fps':FPS,'rig':'Quaternius65','bone_rest':{b.name:[list(row) for row in b.matrix_local] for b in bones},'motions':raw,'metrics':source})
rig.animation_data.action=None
for tr in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(tr)
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
sc.render.fps=FPS
def apply_pose(frame):
    rig.location=frame['loc']
    for b in bones:
        pb=rig.pose.bones[b.name];pb.rotation_mode='QUATERNION';pb.matrix=Matrix.LocRotScale(Vector(frame['p'][b.name]),Quaternion(frame['q'][b.name]),Vector((1,1,1)))
        # pb.matrix's setter depends on its evaluated parent matrix. Update each
        # parent before calculating the next child's basis; otherwise frame zero
        # retains the prior clip's hierarchy and the loop seam can jump ~1 metre.
        bpy.context.view_layer.update()
    bpy.context.view_layer.update()
def record(frame):
    rig.keyframe_insert(data_path='location',frame=frame)
    for pb in rig.pose.bones:
        for prop in ['location','rotation_quaternion','scale']:pb.keyframe_insert(data_path=prop,frame=frame,group=pb.name)
def pose_points(s):return {n:Vector(v) for n,v in s['p'].items()}
def ik(side,target):
    # Analytic two-bone solve; keep the source knee bend plane and foot world orientation.
    thigh,calf,foot=[rig.pose.bones[n+'_'+side] for n in ['thigh','calf','foot']]
    H=thigh.matrix.translation.copy();K=calf.matrix.translation.copy();A=foot.matrix.translation.copy();qr=[p.matrix.to_quaternion().copy() for p in [thigh,calf,foot]]
    l1=(K-H).length;l2=(A-K).length;vec=target-H;d=min(max(vec.length,.001),l1+l2-.00001);u=vec.normalized();a=(l1*l1-l2*l2+d*d)/(2*d);height=math.sqrt(max(0,l1*l1-a*a))
    bend=K-H-u*(K-H).dot(u)
    if bend.length<.0001:bend=Vector((0,-1,0))-u*u.dot(Vector((0,-1,0)))
    newK=H+u*a+bend.normalized()*height;newA=H+u*d
    for pb,oldvec,newvec,pos,q in [(thigh,K-H,newK-H,H,qr[0]),(calf,A-K,newA-newK,newK,qr[1])]:
        rot=oldvec.rotation_difference(newvec)@q;pb.matrix=Matrix.LocRotScale(pos,rot,Vector((1,1,1)));bpy.context.view_layer.update()
    foot.matrix=Matrix.LocRotScale(newA,qr[2],Vector((1,1,1)));bpy.context.view_layer.update()
    return (target-newA).length
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def blend(a,b,w):
    return {'q':{n:list(Quaternion(a['q'][n]).slerp(Quaternion(b['q'][n]),w)) for n in names},'p':{n:list(Vector(a['p'][n]).lerp(Vector(b['p'][n]),w)) for n in names},'loc':list(Vector(a['loc']).lerp(Vector(b['loc']),w))}
def at(name,phase):
    arr=raw[name]['samples'];f=(phase%1)*(len(arr)-1);i=int(f);return blend(arr[i],arr[min(i+1,len(arr)-1)],f-i)
actions=[];reports={}
for name in ['Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight']:
    base=name if name in raw else 'Walk';d=raw[base]['duration'] if name in raw else .8 if name in ['Start','Stop'] else 1.6;count=round(d*FPS)
    action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action;samples=[];anchors={};clamped=0
    for i in range(count+1):
        sec=i/FPS;phase=i/count
        if name in raw:f=raw[name]['samples'][min(i,len(raw[name]['samples'])-1)]
        elif name=='Start':f=blend(at('Idle',0),at('Walk',sec/raw['Walk']['duration']),smooth(phase))
        elif name=='Stop':f=blend(at('Walk',sec/raw['Walk']['duration']),at('Idle',0),smooth(phase))
        else:f=at('Walk',phase)
        sc.frame_set(i);apply_pose(f)
        # Per-frame ground alignment for walking/idle. Running retains airborne intervals.
        low=min(evaluated_soles().values());delta=.004-low if name!='Run' else .004-source['Run']['sole_min_m']
        rig.location.z+=delta;bpy.context.view_layer.update()
        if name in ['Walk','Run']:
            src=raw[name]['samples'];speed=source[name]['speed_mps']
            for side in ['l','r']:
                idx=min(i,len(src)-1);floor=min(x['sole'][side] for x in src);contact=src[idx]['sole'][side]<floor+.023
                if i<len(src)-1:vel=(src[i+1]['p']['foot_'+side][1]-src[i]['p']['foot_'+side][1])*FPS
                else:vel=speed
                contact=contact and vel>.1
                foot=rig.pose.bones['foot_'+side];p=foot.matrix.translation.copy()
                if contact:
                    # Find the contact's start on a circular clip, including across its seam.
                    period=len(src)-1;j=i%period
                    for _ in range(period-1):
                        prev=(j-1)%period
                        pv=(src[(prev+1)%period]['p']['foot_'+side][1]-src[prev]['p']['foot_'+side][1])*FPS
                        if src[prev]['sole'][side]>=floor+.023 or pv<=.1:break
                        j=prev
                    anchor=Vector(src[j]['p']['foot_'+side]);elapsed=((i%period-j)%period)/FPS
                    desired=p.copy();desired.y=anchor.y+speed*elapsed;desired.x=anchor.x
                    # Contact blend only at the threshold edge to avoid a sudden knee snap.
                    w=min(1,max(0,(.023-(src[idx]['sole'][side]-floor))/.009));target=p.lerp(desired,w)
                    clamped+=ik(side,target)>.001
                else:anchors.pop(side,None)
        if name in ['Walk','Idle']:
            rig.location.z+=.004-min(evaluated_soles().values());bpy.context.view_layer.update()
        if name in ['TurnLeft','TurnRight']:
            angle=(1 if name=='TurnLeft' else -1)*math.pi/2*smooth(phase);root=rig.pose.bones['root'];root.matrix=Matrix.Rotation(angle,4,'Z')@root.matrix;bpy.context.view_layer.update()
        record(i);sole=evaluated_soles();P={n:list(rig.matrix_world@rig.pose.bones[n].matrix.translation) for n in ['pelvis','spine_03','Head','foot_l','foot_r','ball_l','ball_r','upperarm_l','lowerarm_l','hand_l','upperarm_r','lowerarm_r','hand_r']}
        torso=Vector(P['spine_03'])-Vector(P['pelvis']);lean=math.degrees(math.atan2(-torso.y,torso.z))
        samples.append({'frame':i,'time_s':sec,'soles':sole,'points':P,'torso_forward_lean_deg':lean})
    rig.animation_data.action=None;actions.append(action)
    reports[name]={'duration_s':count/FPS,'fps':FPS,'frames':len(samples),'minimum_sole_z_m':min(min(s['soles'].values()) for s in samples),'max_lowest_sole_z_m':max(min(s['soles'].values()) for s in samples),'ik_target_clamps':clamped,'torso_forward_lean_range_deg':[min(s['torso_forward_lean_deg'] for s in samples),max(s['torso_forward_lean_deg'] for s in samples)],'speed_mps':source.get(name,{}).get('speed_mps',0),'status':'candidate_not_art_approved','samples':samples}
for action in actions:
    tr=rig.animation_data.nla_tracks.new();tr.name=action.name;st=tr.strips.new(action.name,0,action)
    if action.slots:st.action_slot=action.slots[0]
rig.location=(0,0,0);sc.frame_set(0)
for pb in rig.pose.bones:pb.rotation_quaternion=(1,0,0,0);pb.location=(0,0,0);pb.scale=(1,1,1)
for tr in rig.animation_data.nla_tracks:tr.mute=False
textures=OUT/'textures';textures.mkdir(exist_ok=True);images=[]
for im in bpy.data.images:
    if im.packed_file and im.size[0]:
        p=textures/(im.name+'.png');p.write_bytes(im.packed_file.data);images.append({'name':im.name,'dimensions':list(im.size),'sha256':digest(p),'file':'textures/'+p.name})
semantic={'root':'root','hips':'pelvis','spineLower':'spine_01','spineUpper':'spine_03','neck':'neck_01','head':'Head'}
for s,k in [('l','left'),('r','right')]:
    for a,b in [('Shoulder','clavicle'),('UpperArm','upperarm'),('Forearm','lowerarm'),('Hand','hand'),('UpperLeg','thigh'),('LowerLeg','calf'),('Foot','foot'),('Toe','ball')]:semantic[k+a]=b+'_'+s
profile={'schema_version':1,'id':'quaternius65-harbor-v02','unit':'meter','authoring_up':'+Z','authoring_forward':'-Y','runtime_up':'+Y','runtime_forward':'+Z','reference_pose':'source T-pose (arms horizontal)','root_motion':'in-place; root yaw for experimental 90 degree turn; vertical rig correction baked per clip','semantic':semantic,'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'length_m':b.length,'rest_matrix':[list(r) for r in b.matrix_local]} for b in bones],'ratios':{'leg_length_m':sum(rig.data.bones[n].length for n in ['thigh_l','calf_l']),'upper_arm_to_forearm':rig.data.bones['upperarm_l'].length/rig.data.bones['lowerarm_l'].length},'compatibility':'Only this exact source bind. MPFB53 requires independent rest/axis retarget; do not copy animation accessor arrays.'}
write(OUT/'skeleton-profile.json',profile)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type in ['MESH','ARMATURE']:o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'harbor-courier-review.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'harbor-courier-review.glb'),export_format='GLB',use_selection=True,export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_animations=True,export_skins=True,export_morph=True)
write(OUT/'motion-audit.json',{'method':'Actual evaluated skinned outsole vertices at 30 fps; analytic two-bone contact adjustment for Walk/Run; not continuous collision proof','clips':reports,'art_approved':False,'known_limitations':['No full garment collision correction','Start/Stop are smooth pose blends, stance lock not implemented','90 degree turns follow a walk cycle with baked root yaw; pivot/sliding needs human correction','Run airborne trajectory retained; no gravity reconstruction','Elbow/torso source poses retained; no claim of corrected anatomy until visual review']})
write(OUT/'asset_manifest.json',{'schema_version':1,'asset_id':'harbor-courier-review','version':'0.1.0','source_commit':'8e877a07f19571436c2658a885db77206014a74c','model_file':'harbor-courier-review.glb','source_file':'harbor-courier-review.blend','unit':'meter','clips':[a.name for a in actions],'min_animation_count':7,'requirements':{'skins':True,'animated':True,'visual_review':True},'source':'Quaternius CC0 anatomy/hair/locomotion + PR137 original outfit; new review motion exporter','license_note':'Preserve sources/harbor-v02/THIRD_PARTY_NOTICES.md and CC0 notices','sha256':digest(OUT/'harbor-courier-review.glb'),'art_approved':False,'game_ready':False,'textures':images})
write(OUT/'report.json',{'blender':bpy.app.version_string,'bone_count':len(bones),'clips':list(reports),'art_approved':False,'game_ready':False,'candidate_clothing_changes':cloth_changes,'source_textures_downsampled':False,'source_files_overwritten':False,'source_motion_metrics':source})
print('HARBOR_REVIEW_EXPORTED',str(OUT))
