"""v0.2 world contact solver, 60fps baked root motion and true two-step turns.
Starts from exact v0.1 per-character mothers, not incompatible source animation arrays.
Default output is work/v02-build, preserving all delivered assets and original mothers.
STUDIO_V02_OUT=/isolated/path STUDIO_CHARACTER=harbor-courier-review blender -b --python ...
"""
import bpy,math,json,os,sys,hashlib,struct,statistics
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from gait_plan_v02 import Planner,smooth,lerp,rot
ROOT=Path(os.environ.get('STUDIO_V02_OUT',str(R/'work/v02-build'))).resolve();FPS=60;GROUND=.003
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cyclic(values,phase,quaternion=False):
    n=len(values)-1;f=(phase%1)*n;i=int(f);u=f-i;v=[list(values[k%n]) for k in [i-1,i,i+1,i+2]]
    if quaternion:
        for j in [0,2,3]:
            if sum(a*b for a,b in zip(v[1],v[j]))<0:v[j]=[-x for x in v[j]]
    out=[.5*((2*b)+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u) for a,b,c,d in zip(*v)]
    return Quaternion(out).normalized() if quaternion else Vector(out)
def run(asset):
    old=R/'assets'/asset/'0.1.0';out=ROOT/asset/'0.2.0';out.mkdir(parents=True,exist_ok=True)
    filename='harbor-courier-review' if asset.startswith('harbor') else 'oldman-retarget-candidate';mother=old/(filename+'.blend')
    before=sha(mother);bpy.ops.wm.open_mainfile(filepath=str(mother));sc=bpy.context.scene;rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');original_scale=rig.scale.copy();bone_names=[b.name for b in rig.data.bones];source_fps=sc.render.fps
    shoe=bpy.data.objects['Merged_Sneaker_rubber' if asset.startswith('harbor') else 'TrueMPFBBody_oldman.shoes03'];source={}
    for tr in rig.animation_data.nla_tracks:tr.mute=True
    for name in ['Idle','Walk','Run']:
        action=bpy.data.actions[name];rig.animation_data.action=action
        if action.slots:rig.animation_data.action_slot=action.slots[0]
        duration=float(action.frame_range[1])/source_fps;count=round(duration*30);frames=[]
        for i in range(count+1):
            f=i/count*duration*source_fps;sc.frame_set(int(f),subframe=f%1)
            frames.append({'loc':list(rig.location),'bones':{n:{'p':list(rig.pose.bones[n].location),'q':list(rig.pose.bones[n].rotation_quaternion),'s':list(rig.pose.bones[n].scale)} for n in bone_names}})
        source[name]={'duration':duration,'frames':frames}
    rig.animation_data_clear()
    for a in list(bpy.data.actions):bpy.data.actions.remove(a)
    rig.animation_data_create();rig.rotation_mode='QUATERNION';rig.rotation_quaternion=(1,0,0,0);rig.location=(0,0,0)
    for p in rig.pose.bones:p.location=(0,0,0);p.rotation_mode='QUATERNION';p.rotation_quaternion=(1,0,0,0);p.scale=(1,1,1)
    bpy.context.view_layer.update()
    shoe_changes={'modified_vertices':0}
    if asset.startswith('taiwan'):
        from shoe_weights_v02 import repair as repair_shoe_weights
        shoe_changes=repair_shoe_weights(shoe,rig);write(out/'shoe-weight-changes.json',shoe_changes);bpy.context.view_layer.update()
    ids={s:[v.index for v in shoe.data.vertices if (shoe.matrix_world@v.co).x*(1 if s=='l' else -1)>0] for s in ['l','r']}
    def vertices():
        ob=shoe.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ob.to_mesh();points=[ob.matrix_world@v.co for v in me.vertices];ob.to_mesh_clear();return points
    def bone_world(n):return rig.matrix_world@rig.pose.bones[n].matrix
    def set_bone(n,pos,q):
        pb=rig.pose.bones[n];pb.matrix=Matrix.LocRotScale(rig.matrix_world.inverted()@pos,rig.matrix_world.to_quaternion().inverted()@q,Vector((1,1,1)));bpy.context.view_layer.update()
    def qworld(n):return rig.matrix_world.to_quaternion()@rig.pose.bones[n].matrix.to_quaternion()
    # Flatten actual sole heel/toe regions, rather than assuming the foot-bone axis is a sole plane.
    rest_q={s:qworld('foot_'+s) for s in ['l','r']};flat_q={};sets={};offsets={};neutral_geometry={}
    for s in ['l','r']:
        raw=vertices();ys=sorted(raw[i].y for i in ids[s]);lo,hi=ys[len(ys)//4],ys[len(ys)*3//4];regions={'heel':[i for i in ids[s] if raw[i].y>=hi],'toe':[i for i in ids[s] if raw[i].y<=lo]}
        q=rest_q[s].copy()
        for _ in range(3):
            p=bone_world('foot_'+s).translation;set_bone('foot_'+s,p,q);rig.pose.bones['ball_'+s].rotation_quaternion=(1,0,0,0);bpy.context.view_layer.update();vs=vertices();h=min(vs[i].z for i in regions['heel']);f=min(vs[i].z for i in regions['toe']);dy=statistics.mean(vs[i].y for i in regions['heel'])-statistics.mean(vs[i].y for i in regions['toe']);angle=math.atan2(f-h,dy);q=Quaternion(Vector((1,0,0)),angle)@q
        set_bone('foot_'+s,bone_world('foot_'+s).translation,q);flat_q[s]=q.copy();vs=vertices();floor=min(vs[i].z for i in ids[s]);sets[s]={'flat':[i for i in ids[s] if vs[i].z<floor+.004]}
        for k,region in regions.items():
            low=min(vs[i].z for i in region);sets[s][k]=[i for i in region if vs[i].z<low+.004]
        means={k:sum((vs[i] for i in group),Vector())/len(group) for k,group in sets[s].items()};offsets[s]={k:list(means[k]-means['flat']) for k in ['heel','toe']};neutral_geometry[s]={'indices':sets[s],'offsets':offsets[s],'flat_world_quaternion':list(q),'ankle_height_m':bone_world('foot_'+s).translation.z-floor+GROUND,'sole_heel_toe_difference_m':min(vs[i].z for i in regions['toe'])-min(vs[i].z for i in regions['heel'])}
    leg=sum((bone_world(a).translation-bone_world(b).translation).length for a,b in [('calf_l','thigh_l'),('foot_l','calf_l')]);width=abs(bone_world('foot_l').translation.x);planner=Planner(leg,width,source['Walk']['duration'],source['Run']['duration']);reach_margin=.004
    def pose(clip,phase):
        arr=source[clip]['frames'];return {'loc':cyclic([f['loc'] for f in arr],phase),'bones':{n:{k:cyclic([f['bones'][n][k] for f in arr],phase,k=='q') for k in ['p','q','s']} for n in bone_names}}
    def apply(plan,t,name):
        moving=pose(plan['body'],plan['phase']);idle=pose('Idle',0 if name in ['Start','Stop'] else t/2.5)
        blend=plan['walk_blend'] if name in ['Start','Stop'] else 1
        for n in bone_names:
            p=rig.pose.bones[n];a,b=idle['bones'][n],moving['bones'][n];p.location=a['p'].lerp(b['p'],blend);p.rotation_quaternion=a['q'].slerp(b['q'],blend);p.scale=a['s'].lerp(b['s'],blend)
        rig.location=idle['loc'].lerp(moving['loc'],blend);rig.location.x=plan['root'][0];rig.location.y=plan['root'][1];rig.rotation_quaternion=Quaternion(Vector((0,0,1)),plan['yaw']);rig.scale=original_scale
        bpy.context.view_layer.update()
        # Smooth character-specific hip height replaces the old per-frame root
        # shove. Retain the upper-body pose, and scale the authored jog bounce.
        ankle_height=statistics.mean(v['ankle_height_m'] for v in neutral_geometry.values())
        idle_h=ankle_height+.985*leg;walk_h=ankle_height+.985*leg-.006*math.cos(plan['phase']*math.tau*2)
        run_h=ankle_height+.92*leg+.030*(1+math.cos((plan['phase']-.40)*math.tau*2))/2
        height=run_h if name=='Run' else walk_h if name=='Walk' else idle_h+(walk_h-idle_h)*blend if name in ['Start','Stop'] else idle_h
        active=[s for s,f in plan['feet'].items() if f['contact']]
        shift=Vector();axis=Vector(rot((1,0,0),plan['yaw']))
        if len(active)==1 and name!='Run':
            swing=next(f for f in plan['feet'].values() if not f['contact']);amount=smooth(min(1,swing['clearance']/.025));center=Vector(plan['feet'][active[0]]['P']);pelvis=bone_world('pelvis').translation;side=(center-pelvis).dot(axis);limit=.045 if name.startswith('Turn') else .035;shift=axis*max(-limit,min(limit,side))*amount
        if name.startswith('Turn'):height-=.012*max(f['clearance']/.065 for f in plan['feet'].values())
        hips=(bone_world('thigh_l').translation.z+bone_world('thigh_r').translation.z)/2;shift.z=height-hips
        set_bone('pelvis',bone_world('pelvis').translation+shift,qworld('pelvis'))
        # Restrained upright torso cap, preserving the original oscillation under the cap.
        v=bone_world('neck_01').translation-bone_world('pelvis').translation;forward=Vector(rot((0,-1,0),plan['yaw']));lean=math.atan2(v.dot(forward),v.z);cap=math.radians(15 if name=='Run' else 8);excess=max(0,lean-cap)
        if excess:
            original={n:qworld(n) for n in ['spine_01','spine_02','spine_03']};axis=Vector(rot((1,0,0),plan['yaw']))
            # Positive X pitches forward -Y; rotate back by the excess.
            for n,w in [('spine_01',.25),('spine_02',.6),('spine_03',1)]:set_bone(n,bone_world(n).translation,Quaternion(axis,-excess*w)@original[n])
        return math.degrees(lean),math.degrees(excess)
    def solve(side,target,q,heading):
        th,ca,fo=['thigh_'+side,'calf_'+side,'foot_'+side];H,K,A=[bone_world(n).translation.copy() for n in [th,ca,fo]];Q=[qworld(n) for n in [th,ca]];l1=(K-H).length;l2=(A-K).length;vec=target-H;d=min(max(vec.length,.0001),l1+l2-.00001);u=vec.normalized();a=(l1*l1-l2*l2+d*d)/(2*d)
        pole=Vector(rot((.08 if side=='l' else -.08,-1,0),heading));bend=pole-u*pole.dot(u)
        if bend.length<.00001:bend=Vector((1,0,0))-u*u.x
        nk=H+u*a+bend.normalized()*math.sqrt(max(0,l1*l1-a*a));na=H+u*d
        set_bone(th,H,(K-H).rotation_difference(nk-H)@Q[0]);set_bone(ca,nk,(A-K).rotation_difference(na-nk)@Q[1]);set_bone(fo,na,q)
        return (na-target).length
    def targets(plan):
        target={};qs={};references={};points=vertices()
        for side,f in plan['feet'].items():
            yaw=Quaternion(Vector((0,0,1)),f['yaw']);pitch=Quaternion(Vector((1,0,0)),f['pitch']);qs[side]=yaw@pitch@flat_q[side]
            pivot=f['pivot'] if f['contact'] else 'flat';group=sets[side][pivot];current=sum((points[i] for i in group),Vector())/len(group);desired=Vector(f['P'])
            if f['contact']:desired+=yaw@Vector(offsets[side].get(pivot,[0,0,0]))
            else:
                off=Vector(lerp(offsets[side]['toe'],offsets[side]['heel'],f['pivot_blend']));desired+=yaw@(off-pitch@off)
            low=min(points[i].z for i in ids[side]);err=Vector((desired.x-current.x,desired.y-current.y,GROUND+f['clearance']-low));target[side]=bone_world('foot_'+side).translation+err;references[side]=(group,desired)
        return target,qs,references
    def prepare_feet(plan):
        for side,f in plan['feet'].items():
            for n in ['ball_'+side,'ball_leaf_'+side]:
                if n in rig.pose.bones:rig.pose.bones[n].rotation_quaternion=(1,0,0,0)
            set_bone('foot_'+side,bone_world('foot_'+side).translation,Quaternion(Vector((0,0,1)),f['yaw'])@Quaternion(Vector((1,0,0)),f['pitch'])@flat_q[side])
    sc.render.fps=FPS;reports={};actions=[];raw_lower={};envelopes={}
    # Plan height before baking: conservative smooth envelopes avoid a reactive
    # vertical jerk, and keep the linked clip endpoint corrections identical.
    for name,D in planner.duration.items():
        count=round(D*FPS);planner.duration[name]=count/FPS;values=[]
        for i in range(count+1):
            sc.frame_set(i);plan=planner.sample(name,i/FPS);apply(plan,i/FPS,name);prepare_feet(plan);wanted,_,_=targets(plan);lower=0
            for side,target in wanted.items():
                H=bone_world('thigh_'+side).translation;K=bone_world('calf_'+side).translation;A=bone_world('foot_'+side).translation;length=(H-K).length+(K-A).length-reach_margin;h=math.hypot(H.x-target.x,H.y-target.y)
                if h<length:lower=max(lower,H.z-target.z-math.sqrt(max(0,length*length-h*h)))
            values.append(max(0,min(.12,lower)))
        raw_lower[name]=values
    for name in ['Idle','Walk','Run']:
        values=raw_lower[name];N=len(values)-1
        envelopes[name]=[max(v*math.exp(-.5*(min(abs(i-j),N-abs(i-j))/FPS/.12)**2) for j,v in enumerate(values[:-1])) for i in range(N+1)]
    for name in ['Start','Stop','TurnLeft','TurnRight']:
        values=raw_lower[name];N=len(values)-1;start=envelopes['Walk'][0] if name=='Stop' else envelopes['Idle'][0];end=envelopes['Walk'][0] if name=='Start' else envelopes['Idle'][0];base=[start+(end-start)*smooth(i/N) for i in range(N+1)];envelope=base.copy()
        for j in range(1,N):
            residual=max(0,values[j]-base[j]);radius=min(.16*FPS,j*.45,(N-j)*.45)
            if residual and radius:
                for i in range(max(0,math.ceil(j-radius)),min(N,math.floor(j+radius))+1):envelope[i]=max(envelope[i],base[i]+residual*math.cos((i-j)/radius*math.pi/2)**2)
        envelopes[name]=envelope
    write(out/'height-plan.json',{'fps':FPS,'raw_reach_correction':raw_lower,'smooth_conservative_correction':envelopes,'method':'Periodic Gaussian upper envelope for cycles; endpoint-constrained compact cosine upper envelope for linked transitions. Never uses a previous run as input.'})
    for name,D in planner.duration.items():
        count=round(D*FPS);D=count/FPS;planner.duration[name]=D;action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action;rows=[]
        for i in range(count+1):
            t=i/FPS;sc.frame_set(i);plan=planner.sample(name,t);lean,correction=apply(plan,t,name)
            prepare_feet(plan)
            lower=envelopes[name][i];rig.location.z-=lower;bpy.context.view_layer.update();clamp=0
            for _ in range(9):
                wanted,qs,refs=targets(plan);final_clamp=0
                for side in ['l','r']:final_clamp=max(final_clamp,solve(side,wanted[side],qs[side],plan['yaw']))
                clamp=max(clamp,final_clamp)
                check=vertices();residual=0
                for side,f in plan['feet'].items():
                    group,desired=refs[side];p=sum((check[j] for j in group),Vector())/len(group);low=min(check[j].z for j in ids[side]);residual=max(residual,abs(p.x-desired.x),abs(p.y-desired.y),abs(low-GROUND-f['clearance']))
                if residual<.000015:break
            points=vertices();measure={}
            for side,f in plan['feet'].items():
                group,desired=refs[side];p=sum((points[j] for j in group),Vector())/len(group);error=math.hypot(p.x-desired.x,p.y-desired.y)
                measure[side]={'contact':f['contact'],'pivot':f['pivot'],'contact_id':f['contact_id'],'reference_m':list(p),'planned_reference_m':list(desired),'planar_error_m':error,'sole_z_m':min(points[j].z for j in ids[side]),'clearance_m':f['clearance'],'foot_q':list(qworld('foot_'+side))}
            for prop in ['location','rotation_quaternion','scale']:rig.keyframe_insert(data_path=prop,frame=i)
            for pb in rig.pose.bones:
                for prop in ['location','rotation_quaternion','scale']:pb.keyframe_insert(data_path=prop,frame=i,group=pb.name)
            pointnames=['pelvis','spine_03','neck_01','Head' if 'Head' in rig.pose.bones else 'head','thigh_l','calf_l','thigh_r','calf_r','foot_l','foot_r','upperarm_l','lowerarm_l','hand_l','upperarm_r','lowerarm_r','hand_r']
            positions={n:bone_world(n).translation.copy() for n in pointnames};knee={}
            for side in ['l','r']:
                H,K,A=[positions[n+'_'+side] for n in ['thigh','calf','foot']];knee[side]=180-math.degrees((H-K).angle(A-K))
            rows.append({'frame':i,'time_s':t,'root_m':list(rig.location),'heading_rad':plan['yaw'],'feet':measure,'points':{n:list(p) for n,p in positions.items()},'knee_flex_deg':knee,'reach_lowering_m':lower,'ik_clamp_m':clamp,'final_ik_clamp_m':final_clamp,'source_torso_lean_deg':lean,'posture_correction_deg':correction})
        rig.animation_data.action=None;actions.append(action)
        slip=[]
        for side in ['l','r']:
            for a,b in zip(rows,rows[1:]):
                aa,bb=a['feet'][side],b['feet'][side]
                if aa['contact'] and bb['contact'] and aa['contact_id']==bb['contact_id'] and aa['pivot']==bb['pivot']:slip.append(math.dist(aa['reference_m'][:2],bb['reference_m'][:2])*FPS)
        reports[name]={'duration_s':D,'fps':FPS,'frames':len(rows),'speed_mps':planner.strides.get(name,0)/D if name in ['Walk','Run'] else 0,'root_end_m':rows[-1]['root_m'],'heading_end_deg':math.degrees(rows[-1]['heading_rad']),'minimum_sole_z_m':min(f['sole_z_m'] for r in rows for f in r['feet'].values()),'max_contact_planar_error_m':max(f['planar_error_m'] for r in rows for f in r['feet'].values() if f['contact']),'stance_reference_speed_mean_mps':statistics.mean(slip) if slip else None,'stance_reference_speed_max_mps':max(slip) if slip else None,'max_reach_lowering_m':max(r['reach_lowering_m'] for r in rows),'max_ik_clamp_m':max(r['ik_clamp_m'] for r in rows),'max_final_ik_clamp_m':max(r['final_ik_clamp_m'] for r in rows),'samples':rows,'art_approved':False}
        print(asset,name,'ground',reports[name]['minimum_sole_z_m'],'contact error',reports[name]['max_contact_planar_error_m'],'lower',reports[name]['max_reach_lowering_m'],flush=True)
    for a in actions:
        tr=rig.animation_data.nla_tracks.new();tr.name=a.name;st=tr.strips.new(a.name,0,a)
        if a.slots:st.action_slot=a.slots[0]
    sc.frame_set(0);bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.objects:
        if o.type in ['MESH','ARMATURE']:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    blend=out/(asset+'.blend');model=out/(asset+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',use_selection=True,export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_animations=True,export_skins=True,export_morph=True)
    if asset.startswith('taiwan'):
        data=model.read_bytes();size=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+size])
        for m in doc['materials']:
            if m['name']=='TrueMPFBBody_oldman.shoes03':m['alphaMode']='MASK';m['alphaCutoff']=.5
        payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4);rest=data[20+size:];model.write_bytes(struct.pack('<4sII',b'glTF',2,20+len(payload)+len(rest))+struct.pack('<I4s',len(payload),b'JSON')+payload+rest)
    images=[];tex=out/'textures';tex.mkdir(exist_ok=True)
    for im in bpy.data.images:
        if im.packed_file and im.size[0]:
            name=im.name if im.name.endswith('.png') else im.name+'.png';p=tex/name;p.write_bytes(im.packed_file.data);images.append({'file':'textures/'+name,'dimensions':list(im.size),'sha256':sha(p)})
    oldprofile=json.loads((old/'skeleton-profile.json').read_text());oldprofile['version']='0.2.0';oldprofile['root_motion']='Baked world translation and yaw; use per-clip trajectory for follow view. Foot support anchors are world-space heel/flat/toe geometry constraints.';oldprofile['footwear_nodes']=[shoe.name];oldprofile['neutral_foot_geometry']=neutral_geometry
    oldprofile['semantic']={'root':'root' if 'root' in bone_names else 'Root','hips':'pelvis','spineLower':'spine_01','spineMiddle':'spine_02','spineUpper':'spine_03','neck':'neck_01','head':'Head' if 'Head' in bone_names else 'head'}
    for side,prefix in [('l','left'),('r','right')]:
        for label,b in [('Shoulder','clavicle'),('UpperArm','upperarm'),('Forearm','lowerarm'),('Hand','hand'),('UpperLeg','thigh'),('LowerLeg','calf'),('Foot','foot'),('Toe','ball')]:oldprofile['semantic'][prefix+label]=b+'_'+side
    oldprofile['neutral_foot_index_space']='Editable Blender shoe mesh vertex indices; glTF may split UV/normal vertices. Do not reuse these indices blindly in runtime.';oldprofile['animated_root_node']=rig.name
    write(out/'skeleton-profile.json',oldprofile);write(out/'motion-audit.json',{'asset_id':asset,'version':'0.2.0','method':'Actual evaluated footwear support regions, 60fps, world-space root motion and numerical two-bone contact lock; not continuous full-body collision or human art acceptance','clips':reports,'art_approved':False})
    write(out/'asset_manifest.json',{'schema_version':1,'asset_id':asset,'version':'0.2.0','model_file':model.name,'source_file':blend.name,'unit':'meter','clips':list(reports),'min_animation_count':7,'requirements':{'skins':True,'animated':True,'visual_review':True},'source':'Exact v0.1 character-specific baked motions/rig and authored v0.2 world-contact plans; original Quaternius/MakeHuman/MRT sources retained','license_note':'Unchanged third-party source license; see root THIRD_PARTY_NOTICES.md','sha256':sha(model),'art_approved':False,'game_ready':False,'textures':images})
    write(out/'report.json',{'blender':bpy.app.version_string,'source_blend':str(mother.relative_to(R)),'source_sha256':before,'source_unchanged':sha(mother)==before,'bones':len(bone_names),'fps':FPS,'leg_length_m':leg,'half_stance_width_m':width,'topology_uv_positions_changed':False,'shoe_vertices_reweighted':shoe_changes['modified_vertices'],'texture_resolution_changed':False,'art_approved':False,'game_ready':False,'known_limitations':['Full garment/body collisions not solved','Root/contact paths are authored candidates, not captured or trained motion','Human art and physical phone not tested','Toe/heel contact uses selected actual shoe vertices; not physical ground reaction forces']})
    print('V02_COMPLETE',asset,sha(model),flush=True)
characters=[os.environ['STUDIO_CHARACTER']] if 'STUDIO_CHARACTER' in os.environ else ['harbor-courier-review','taiwan-oldman-review']
for character in characters:run(character)
