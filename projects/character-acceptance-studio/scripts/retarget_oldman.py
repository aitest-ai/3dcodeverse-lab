"""Rest/axis aware Quaternius65 -> MPFB53 review retarget, followed by evaluated-shoe grounding.
Requires the immutable V29 source + build_harbor.py's evaluated source-motion.json.
Exports a visible before/after pair. No source animation arrays, bind matrices or bone lengths copied.
"""
import bpy, json, math, hashlib, statistics,struct,os
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
R=Path(__file__).resolve().parents[1];BUILD_ROOT=Path(os.environ.get('STUDIO_BUILD_ROOT',str(R/'work/rebuilt-assets'))).resolve();OUT=BUILD_ROOT/'taiwan-oldman-review/0.1.0';OUT.mkdir(parents=True,exist_ok=True)
source=json.loads((BUILD_ROOT/'harbor-courier-review/0.1.0/source-motion.json').read_text());FPS=30
bpy.ops.wm.open_mainfile(filepath=str(R/'sources/oldman-v29/oldman.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');bones=list(rig.data.bones);sc=bpy.context.scene;sc.render.fps=FPS
rig.animation_data_clear()
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
for o in bpy.data.objects:
    if o.type=='MESH' and o.data.shape_keys:
        o.data.shape_keys.animation_data_clear()
        for k in o.data.shape_keys.key_blocks:k.value=0
shoes=bpy.data.objects['TrueMPFBBody_oldman.shoes03'];ids={s:[v.index for v in shoes.data.vertices if (shoes.matrix_world@v.co).x*(1 if s=='l' else -1)>0] for s in ['l','r']}
rig.animation_data_create();object_location=rig.location.copy();scale=rig.scale.x
S={n:Matrix(m) for n,m in source['bone_rest'].items()};T={b.name:b.matrix_local.copy() for b in bones}
mapping={b.name:('root' if b.name=='Root' else 'Head' if b.name=='head' else b.name) for b in bones}
assert all(n in S for n in mapping.values())
ratio=(bones['thigh_l'].length+bones['calf_l'].length) if isinstance(bones,dict) else (rig.data.bones['thigh_l'].length+rig.data.bones['calf_l'].length)
ratio/=sum((S[n].translation-S[p].translation).length for n,p in [('calf_l','thigh_l'),('foot_l','calf_l')])
correction={}
for tn,sn in mapping.items():
    rs,rt=S[sn].to_quaternion(),T[tn].to_quaternion()
    align=(rt@Vector((0,1,0))).rotation_difference(rs@Vector((0,1,0)))
    correction[tn]=rs.inverted()@align@rt
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def export_alpha_mask(path):
    # Sandal cutouts use genuine texture alpha. Use MASK with depth writes in glTF,
    # preserving both the original image and the editable source shader alpha link.
    data=path.read_bytes();size=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+size]);changed=[]
    for material in doc['materials']:
        if material['name']=='TrueMPFBBody_oldman.shoes03':material['alphaMode']='MASK';material['alphaCutoff']=.5;changed.append(material['name'])
    payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4);rest=data[20+size:]
    result=struct.pack('<4sII',b'glTF',2,12+8+len(payload)+len(rest))+struct.pack('<I4s',len(payload),b'JSON')+payload+rest;path.write_bytes(result)
    return changed
def soles():
    ob=shoes.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ob.to_mesh();v={s:min((ob.matrix_world@me.vertices[i].co).z for i in ids[s]) for s in ids};ob.to_mesh_clear();return v
def reset():
    rig.location=object_location
    for p in rig.pose.bones:p.location=(0,0,0);p.rotation_mode='QUATERNION';p.rotation_quaternion=(1,0,0,0);p.scale=(1,1,1)
    bpy.context.view_layer.update()
def apply(f):
    reset()
    for b in bones:
        pb=rig.pose.bones[b.name];sn=mapping[b.name];head=pb.matrix.translation.copy()
        if b.name=='Root':q=Quaternion(f['q'][sn])@S[sn].to_quaternion().inverted()@T[b.name].to_quaternion()
        else:q=Quaternion(f['q'][sn])@correction[b.name]
        if b.name=='pelvis':head+=(Vector(f['p'][sn])-S[sn].translation)*ratio
        pb.matrix=Matrix.LocRotScale(head,q,Vector((1,1,1)));bpy.context.view_layer.update()
def record(i):
    rig.keyframe_insert(data_path='location',frame=i)
    for pb in rig.pose.bones:
        for k in ['location','rotation_quaternion','scale']:pb.keyframe_insert(data_path=k,frame=i,group=pb.name)
def ik(side,target):
    th,ca,fo=[rig.pose.bones[n+'_'+side] for n in ['thigh','calf','foot']]
    H,K,A=[p.matrix.translation.copy() for p in [th,ca,fo]];qs=[p.matrix.to_quaternion().copy() for p in [th,ca,fo]]
    l1=(K-H).length;l2=(A-K).length;u=(target-H).normalized();d=min(max((target-H).length,.001),l1+l2-.00001);a=(l1*l1-l2*l2+d*d)/(2*d);bend=K-H-u*(K-H).dot(u)
    if bend.length<.0001:bend=Vector((0,-1,0))-u*u.dot(Vector((0,-1,0)))
    nk=H+u*a+bend.normalized()*math.sqrt(max(0,l1*l1-a*a));na=H+u*d
    for pb,old,new,pos,q in [(th,K-H,nk-H,H,qs[0]),(ca,A-K,na-nk,nk,qs[1])]:
        pb.matrix=Matrix.LocRotScale(pos,old.rotation_difference(new)@q,Vector((1,1,1)));bpy.context.view_layer.update()
    fo.matrix=Matrix.LocRotScale(na,qs[2],Vector((1,1,1)));bpy.context.view_layer.update();return (na-target).length*scale
baseline={}
for name,motion in source['motions'].items():
    arr=[]
    for f in motion['samples']:
        apply(f);arr.append({'sole':soles(),'p':{n:list(rig.pose.bones[n].matrix.translation) for n in ['foot_l','foot_r']}})
    speed=[]
    for side in ['l','r']:
        floor=min(v['sole'][side] for v in arr)
        for a,b in zip(arr,arr[1:]):
            v=(b['p']['foot_'+side][1]-a['p']['foot_'+side][1])*FPS*scale
            if max(a['sole'][side],b['sole'][side])<floor+.025 and v>.1:speed.append(v)
    baseline[name]={'frames':arr,'speed_mps':statistics.median(speed) if speed and name!='Idle' else 0,'floor':min(min(f['sole'].values()) for f in arr)}
reports={};opaque_repairs=[]
for variant in ['baseline','candidate']:
    if variant=='candidate':
        # Existing V29 exported opaque skin/eyes/teeth as BLEND, so WebGL sorted
        # inner mouth/eyes in front of the face. Keep original images byte-identical;
        # disconnect alpha only on surfaces which are anatomically opaque.
        for name in ['TrueMPFBBody_oldman','TrueMPFBBody_oldman.high-poly','TrueMPFBBody_oldman.teeth_base','TrueMPFBBody_oldman.tongue01']:
            for mat in bpy.data.objects[name].data.materials:
                if not mat or not mat.use_nodes:continue
                for node in mat.node_tree.nodes:
                    if node.type=='BSDF_PRINCIPLED':
                        alpha=node.inputs['Alpha']
                        for link in list(alpha.links):mat.node_tree.links.remove(link)
                        alpha.default_value=1.0
                opaque_repairs.append(mat.name)
    rig.animation_data.action=None
    for tr in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(tr)
    for a in list(bpy.data.actions):bpy.data.actions.remove(a)
    reports[variant]={};actions=[]
    for name,motion in source['motions'].items():
        action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action;actions.append(action);samples=[];clamped=0
        arr=baseline[name]['frames'];speed=baseline[name]['speed_mps'];period=len(arr)-1
        for i,f in enumerate(motion['samples']):
            sc.frame_set(i);apply(f)
            if variant=='candidate':
                low=min(soles().values());delta=.004-low if name!='Run' else .004-baseline[name]['floor'];rig.location.z+=delta;bpy.context.view_layer.update()
                if name in ['Walk','Run']:
                    for side in ['l','r']:
                        floor=min(v['sole'][side] for v in arr);idx=i%period
                        vel=(arr[(idx+1)%period]['p']['foot_'+side][1]-arr[idx]['p']['foot_'+side][1])*FPS*scale
                        if arr[idx]['sole'][side]<floor+.023 and vel>.1:
                            j=idx
                            for _ in range(period-1):
                                prev=(j-1)%period;pv=(arr[(prev+1)%period]['p']['foot_'+side][1]-arr[prev]['p']['foot_'+side][1])*FPS*scale
                                if arr[prev]['sole'][side]>=floor+.023 or pv<=.1:break
                                j=prev
                            p=rig.pose.bones['foot_'+side].matrix.translation.copy();target=p.copy();target.x=arr[j]['p']['foot_'+side][0];target.y=arr[j]['p']['foot_'+side][1]+speed/scale*((idx-j)%period)/FPS
                            w=min(1,max(0,(.023-(arr[idx]['sole'][side]-floor))/.009));clamped+=ik(side,p.lerp(target,w))>.001
                if name in ['Walk','Idle']:rig.location.z+=.004-min(soles().values());bpy.context.view_layer.update()
            record(i);points={n:list(rig.matrix_world@rig.pose.bones[n].matrix.translation) for n in ['pelvis','spine_03','head','upperarm_l','lowerarm_l','hand_l','upperarm_r','lowerarm_r','hand_r','foot_l','foot_r','ball_l','ball_r']}
            samples.append({'frame':i,'time_s':i/FPS,'soles':soles(),'points':points})
        reports[variant][name]={'frames':len(samples),'duration_s':period/FPS,'minimum_sole_z_m':min(min(s['soles'].values()) for s in samples),'max_lowest_sole_z_m':max(min(s['soles'].values()) for s in samples),'speed_mps':speed,'ik_target_clamps':clamped,'samples':samples}
        rig.animation_data.action=None
    for a in actions:
        tr=rig.animation_data.nla_tracks.new();tr.name=a.name;st=tr.strips.new(a.name,0,a)
        if a.slots:st.action_slot=a.slots[0]
    reset();sc.frame_set(0);bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.objects:
        if o.type in ['MESH','ARMATURE']:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'oldman-retarget-{variant}.blend'))
    bpy.ops.export_scene.gltf(filepath=str(OUT/f'oldman-retarget-{variant}.glb'),export_format='GLB',use_selection=True,export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_animations=True,export_skins=True,export_morph=True)
    if variant=='candidate':export_alpha_mask(OUT/f'oldman-retarget-{variant}.glb')
textures=OUT/'textures';textures.mkdir(exist_ok=True);images=[]
for im in bpy.data.images:
    if im.packed_file and im.size[0]:
        p=textures/(im.name if im.name.endswith('.png') else im.name+'.png');p.write_bytes(im.packed_file.data);images.append({'name':im.name,'dimensions':list(im.size),'file':'textures/'+p.name,'sha256':digest(p)})
profile={'schema_version':1,'id':'mpfb53-oldman-v29','source_asset':'taiwan-oldman-V29','unit':'meter','authoring_up':'+Z','authoring_forward':'-Y','runtime_up':'+Y','runtime_forward':'+Z','reference_pose':'MPFB source A-pose; preserved per-bone roll','object_matrix':[list(row) for row in rig.matrix_world],'bone_mapping_to_quaternius':mapping,'rest_alignment_quaternions':{n:list(q) for n,q in correction.items()},'leg_scale_ratio':ratio,'root_motion':'in-place, pelvis translation scaled by actual leg lengths; per-clip vertical shoe correction','bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'length_m':b.length*scale,'rest_matrix':[list(row) for row in b.matrix_local]} for b in bones],'method':'Align target rest Y to source rest Y, preserve residual roll; source global pose rotation plus this roll correction -> target pose. Target hierarchy/lengths/bind/geometry unchanged. Bake target local pose. Two-bone stance correction uses evaluated real shoe mesh.','warnings':['Human elbow/knee/twist and all garment regions need visual review','Original mobile phone is still attached to hand; grip not adapted','No transfer of fingers beyond existing semantic matches','Run foot flight and phase may need manual editing']}
write(OUT/'skeleton-profile.json',profile);write(OUT/'motion-audit.json',{'variants':reports,'art_approved':False})
write(OUT/'asset_manifest.json',{'schema_version':1,'asset_id':'taiwan-oldman-review','version':'0.1.0','model_file':'oldman-retarget-candidate.glb','source_file':'oldman-retarget-candidate.blend','clips':['Idle','Walk','Run'],'min_animation_count':3,'unit':'meter','requirements':{'skins':True,'animated':True,'visual_review':True},'source':'V29 original oldman MPFB/MRT CC0; motion retarget from Quaternius CC0','license_note':'Preserve sources/oldman-v29/LICENSE-SOURCE-HEADERS.txt and Quaternius notices','sha256':digest(OUT/'oldman-retarget-candidate.glb'),'art_approved':False,'game_ready':False,'textures':images})
write(OUT/'report.json',{'blender':bpy.app.version_string,'bones':len(bones),'body_morphs':len(bpy.data.objects['TrueMPFBBody_oldman'].data.shape_keys.key_blocks)-1,'leg_scale_ratio':ratio,'source_files_overwritten':False,'geometry_uv_weights_changed':False,'source_textures_downsampled':False,'material_alpha_repairs':opaque_repairs,'material_repair_reason':'Source V29 opaque anatomy exported as alpha BLEND; internal mouth/eyes incorrectly sorted over face in WebGL. Candidate removes alpha connection only for skin/eyes/teeth/tongue; original image bytes and transparent hair/brow/lash retained. Sandal texture alpha preserved; explicit glTF MASK .5 export conversion, implemented in export_alpha_mask().','art_approved':False,'game_ready':False,'missing':['Target-specific garment sculpt/weight polish','Start/Stop/Turn retarget not produced','Human art acceptance','Phone grip animation'],'source_blend_sha256':digest(R/'sources/oldman-v29/oldman.blend')})
print('OLDMAN_RETARGET_EXPORTED',OUT)
