"""Blender 5.2.3 background per-character garment/posture candidate, never overwrite published assets.
STUDIO_CHARACTER=harbor-courier-review blender -b --python-exit-code 1 --python scripts/build_character_v03.py
Use a separate Blender process for each character. Default writes work/v03-build only.
"""
import bpy,math,json,os,sys,hashlib,shutil,copy,struct
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import garment_repairs_v03 as clothes
asset=os.environ.get('STUDIO_CHARACTER','harbor-courier-review');assert asset in ['harbor-courier-review','taiwan-oldman-review']
ROOT=Path(os.environ.get('STUDIO_V03_OUT',str(R/'work/v03-build'))).resolve()
if ROOT==R or any(ROOT==p or p in ROOT.parents for p in [R/'assets',R/'sources']):raise RuntimeError('Cannot build over immutable sources/published assets')
old=R/'assets'/asset/'0.2.0';out=ROOT/asset/'0.3.0';out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
mother=old/(asset+'.blend');before=sha(mother);bpy.ops.wm.open_mainfile(filepath=str(mother));sc=bpy.context.scene;rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');names=list(rig.pose.bones.keys());FPS=sc.render.fps
for tr in rig.animation_data.nla_tracks:tr.mute=True
native={}
for name in ['Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight']:
    action=bpy.data.actions[name];rig.animation_data.action=action
    if action.slots:rig.animation_data.action_slot=action.slots[0]
    N=round(action.frame_range[1]);frames=[]
    for i in range(N+1):
        sc.frame_set(i);frames.append({'location':list(rig.location),'rotation':list(rig.rotation_quaternion),'scale':list(rig.scale),'bones':{n:{'p':list(rig.pose.bones[n].location),'q':list(rig.pose.bones[n].rotation_quaternion),'s':list(rig.pose.bones[n].scale)} for n in names}})
    native[name]=frames
rig.animation_data_clear();rig.location=(0,0,0);rig.rotation_quaternion=(1,0,0,0)
for p in rig.pose.bones:p.location=(0,0,0);p.rotation_quaternion=(1,0,0,0);p.scale=(1,1,1)
bpy.context.view_layer.update();head='Head' if 'Head' in names else 'head'
def world(n):return rig.matrix_world@rig.pose.bones[n].matrix
def setq(n,q):
    m=world(n);rig.pose.bones[n].matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(m.translation,q,m.to_scale());bpy.context.view_layer.update()
rest_head_q=world(head).to_quaternion();body=bpy.data.objects['LinXi_Anatomy' if asset.startswith('harbor') else 'TrueMPFBBody_oldman'];body_before=clothes.digest(clothes.snapshot(body))
garments=clothes.harbor(rig) if asset.startswith('harbor') else clothes.oldman(rig);write(out/'garment-change-log.json',garments)
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
rig.animation_data_create();audit=json.loads((old/'motion-audit.json').read_text());profile=json.loads((old/'skeleton-profile.json').read_text());shoe=bpy.data.objects['Merged_Sneaker_rubber' if asset.startswith('harbor') else 'TrueMPFBBody_oldman.shoes03'];footids={s:[v.index for v in shoe.data.vertices if (shoe.matrix_world@v.co).x*(1 if s=='l' else -1)>0] for s in ['l','r']};posture={};actions=[]
def vertices(o):
    ob=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ob.to_mesh();ps=[ob.matrix_world@v.co for v in me.vertices];ob.to_mesh_clear();return ps
def lean(yaw):
    v=world('neck_01').translation-world('pelvis').translation;f=Vector((math.sin(yaw),-math.cos(yaw),0));return math.atan2(v.dot(f),v.z)
for name,frames in native.items():
    action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action;report=[]
    for i,f in enumerate(frames):
        sc.frame_set(i);rig.location=f['location'];rig.rotation_quaternion=f['rotation'];rig.scale=f['scale']
        for n,d in f['bones'].items():p=rig.pose.bones[n];p.location=d['p'];p.rotation_quaternion=d['q'];p.scale=d['s']
        bpy.context.view_layer.update();row=audit['clips'][name]['samples'][i];yaw=row['heading_rad'];initial=lean(yaw);cap=math.radians(12 if name=='Run' else 8);base=cap-math.radians(2);target=min(initial,base+math.radians(2)*math.tanh((initial-base)/math.radians(2))) if initial>base else initial
        axis=Vector((math.cos(yaw),math.sin(yaw),0))
        for _ in range(10):
            delta=lean(yaw)-target
            if abs(delta)<math.radians(.005):break
            setq('spine_01',Quaternion(axis,-delta*1.18)@world('spine_01').to_quaternion())
        q=world(head).to_quaternion();forward=q@rest_head_q.inverted()@Vector((0,-1,0));elev=math.atan2(forward.z,math.hypot(forward.x,forward.y));gaze_target=max(math.radians(-6),min(math.radians(2),elev));gaze_yaw=math.atan2(forward.x,-forward.y);gaze_axis=Vector((math.cos(gaze_yaw),math.sin(gaze_yaw),0));setq(head,Quaternion(gaze_axis,elev-gaze_target)@q)
        for prop in ['location','rotation_quaternion','scale']:rig.keyframe_insert(data_path=prop,frame=i)
        for p in rig.pose.bones:
            for prop in ['location','rotation_quaternion','scale']:p.keyframe_insert(data_path=prop,frame=i,group=p.name)
        after=lean(yaw);ps=vertices(shoe)
        for side,foot in row['feet'].items():
            pivot=foot['pivot'] if foot['contact'] else 'flat';ids=profile['neutral_foot_geometry'][side]['indices'][pivot];ref=sum((ps[j] for j in ids),Vector())/len(ids);foot['reference_m']=list(ref);foot['planar_error_m']=math.hypot(ref.x-foot['planned_reference_m'][0],ref.y-foot['planned_reference_m'][1]);foot['sole_z_m']=min(ps[j].z for j in footids[side])
        row['points']={n:list(world(n).translation) for n in row['points']};row['posture_v03']={'before_lean_deg':math.degrees(initial),'after_lean_deg':math.degrees(after),'target_lean_deg':math.degrees(target),'head_forward_elevation_before_deg':math.degrees(elev),'head_forward_target_elevation_deg':math.degrees(gaze_target)};report.append(row['posture_v03'])
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
    rig.animation_data.action=None;actions.append(action);posture[name]=report;clip=audit['clips'][name];clip['minimum_sole_z_m']=min(f['sole_z_m'] for row in clip['samples'] for f in row['feet'].values());clip['max_contact_planar_error_m']=max(f['planar_error_m'] for row in clip['samples'] for f in row['feet'].values() if f['contact']);print(asset,name,'lean range',min(x['after_lean_deg'] for x in report),max(x['after_lean_deg'] for x in report),flush=True)
for a in actions:
    tr=rig.animation_data.nla_tracks.new();tr.name=a.name;st=tr.strips.new(a.name,0,a)
    if a.slots:st.action_slot=a.slots[0]
sc.frame_set(0);audit['version']='0.3.0';audit['method']='Original v0.2 world contacts/root preserved; actual pelvis-to-neck lean solved on spine01; editable local garment repairs; 60Hz evaluated footwear references remeasured';profile['version']='0.3.0';profile['posture_revision']='spine01 subtree tilt measured against pelvis-neck axis; head-forward pitch bounded -6..2 degrees; not eye tracking';write(out/'motion-audit.json',audit);write(out/'posture-audit.json',posture);write(out/'skeleton-profile.json',profile)
shutil.copytree(old/'textures',out/'textures',dirs_exist_ok=True);shutil.copyfile(old/'height-plan.json',out/'height-plan.json')
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type in ['MESH','ARMATURE']:o.select_set(True)
bpy.context.view_layer.objects.active=rig;bpy.ops.wm.save_as_mainfile(filepath=str(out/(asset+'.blend')));model=out/(asset+'.glb');bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',use_selection=True,export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_animations=True,export_skins=True,export_morph=True)
if asset.startswith('taiwan'):
    raw=model.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);tail=raw[20+n:]
    for m in doc['materials']:
        if m['name']=='TrueMPFBBody_oldman.shoes03':m['alphaMode']='MASK';m['alphaCutoff']=.5
    js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*(-len(js)%4);model.write_bytes(struct.pack('<4sII',b'glTF',2,12+8+len(js)+len(tail))+struct.pack('<I4s',len(js),b'JSON')+js+tail)
assert sha(mother)==before;assert clothes.digest(clothes.snapshot(body))==body_before
manifest=json.loads((old/'asset_manifest.json').read_text());manifest.update(version='0.3.0',sha256=sha(model),source='Exact 0.2.0 character + project-authored editable garment/posture correction; upstream licenses unchanged');write(out/'asset_manifest.json',manifest)
write(out/'report.json',{'blender':bpy.app.version_string,'source_blend':str(mother.relative_to(R)),'source_sha256':before,'source_unchanged':True,'body_geometry_weights_unchanged':True,'raw_original_topology_available_in':'0.2.0','garment_changes':'garment-change-log.json','posture_changes':'posture-audit.json','root_and_lower_body_channels_preserved':True,'packed_images_changed':False,'art_approved':False,'game_ready':False,'limitations':['No physical cloth simulation','No all-body collision guarantee','Human art and physical phone untested','Head-forward axis constraint is not pupil gaze correction']});print('V03_COMPLETE',asset,sha(model),flush=True)
