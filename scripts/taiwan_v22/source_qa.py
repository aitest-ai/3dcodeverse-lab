"""V22 original .blend local candidate, paired Cycles renders and full clip QA.
Baseline/candidate share V21 FK calibrations and fixed waist ROI. Corrected
same-side boundary semantics retain legacy false-positive counts separately.
"""
import os,sys,json,hashlib,math
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent
for folder in (HERE,HERE.parent/'taiwan_v20',HERE.parent/'taiwan_v21'):sys.path.insert(0,str(folder))
from source_waist import coordinates,digest_mesh
from motion_qa import GLB,arm_faces,evaluated_bvh
from waist_fit import opening,periodic
from local_cloth import evaluated_points,separate_fly,fit_tucked_hem
from fly_audit import surface_audit
INPUT=Path(os.getenv('V22_INPUT','input/v21')).resolve()
OUT=Path(os.getenv('V22_OUT','outputs/v22')).resolve()
for d in ('blend','models','motion','renders','qa'): (OUT/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=INPUT/'blend/uncle_v21_source.blend'
assert sha(source)=='9f73943d5b7e413c2a9c879213295d77f59ab547f94d0252c7c87d198bab9390'
baseline=json.loads((INPUT/'qa/uncle_v21_source_qa.json').read_text())
roi=baseline['roi_z'];center=np.asarray(baseline['center_xy'])
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;rig=bpy.data.objects['RootRig_uncle']
body=bpy.data.objects['TrueMPFBBody_uncle']
shirt=bpy.data.objects['OpenSourceCloth_uncle_toigo_basic_tucked_t-shirt']
pants=bpy.data.objects['OpenSourceCloth_uncle_toigo_wool_pants']
meshes=[o for o in scene.objects if o.type=='MESH']
assert len(body.data.vertices)==13380 and len(rig.data.bones)==53
assert len(body.data.shape_keys.key_blocks)==11
assert not any(m.type=='MASK' for m in body.modifiers)
for o in meshes:
    if o.data.shape_keys:
        for k in o.data.shape_keys.key_blocks[1:]:k.value=0.
initial={o.name:digest_mesh(o) for o in meshes}

def structure(o):
    h=hashlib.sha256()
    for face in o.data.polygons:h.update(np.asarray(face.vertices[:],dtype='<i4').tobytes())
    for vertex in o.data.vertices:
        for g in vertex.groups:h.update(np.asarray([g.group,g.weight],dtype='<f8').tobytes())
    for uv in o.data.uv_layers:h.update(np.asarray([tuple(v.uv) for v in uv.data],dtype='<f4').tobytes())
    return h.hexdigest()
structures={o.name:structure(o) for o in meshes}
textures=[]
for im in bpy.data.images:
    if im.source=='FILE':
        assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
        textures.append({'name':im.name,'size':list(im.size),'sha256':hashlib.sha256(im.packed_file.data).hexdigest()})
camera=scene.camera;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.fps=24;scene.frame_start=0;scene.frame_end=48
cal=baseline['calibration']
raised={cal['raise_'+s]['bone']:cal['raise_'+s]['rotation_xyz'] for s in ('l','r')}
bend={cal['bend']['bone']:cal['bend']['rotation_xyz']}
step={cal['step_'+s]['bone']:cal['step_'+s]['rotation_xyz'] for s in ('l','r')}
poses={'neutral':(0,{}),'arms_raise':(12,raised),'torso_bend':(24,bend),'step':(36,step),'reset':(48,{})}
rig.animation_data_clear()
for name,(frame,angles) in poses.items():
    scene.frame_set(frame)
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4);b.rotation_mode='XYZ'
    for name,rot in angles.items():rig.pose.bones[name].rotation_euler=rot
    bpy.context.view_layer.update()
    for b in rig.pose.bones:b.keyframe_insert(data_path='rotation_euler',frame=frame,group=b.name)
scene.frame_set(0);bpy.context.view_layer.update()
limbs=arm_faces(body,rig)

def scan():
    trees=[evaluated_bvh(o) for o in (body,shirt,pants)]
    p,ids,_=opening(evaluated_points(pants),[list(f.vertices) for f in pants.data.polygons],True)
    theta=np.arctan2(p[ids,1]-center[1],p[ids,0]-center[0]);heights=p[ids,2]
    counts={'rays':8200,'waist_body_hits':0,'natural_limb_hits':0,'visible_skin':0,'shirt_outside_below_band':0,'legacy_far_side_tuck_count':0,'legacy_pants_behind_body':0}
    views=[]
    for view in range(8):
        angle=view*math.pi/4;r=Vector((math.sin(angle),-math.cos(angle),0));t=Vector((math.cos(angle),math.sin(angle),0))
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
                    # Retain legacy signal; do not compare front shirt to rear band.
                    q=hits[2][0];old_angle=math.atan2(q.y-center[1],q.x-center[0])
                    old_rim=float(periodic(theta,heights,np.asarray([old_angle]))[0])
                    if z<old_rim-.008:
                        counts['legacy_far_side_tuck_count']+=1
                        if pd>bd+.0015:counts['legacy_pants_behind_body']+=1
                    s=hits[1][0];local_angle=math.atan2(s.y-center[1],s.x-center[0])
                    local_rim=float(periodic(theta,heights,np.asarray([local_angle]))[0])
                    if z<local_rim-.008:counts['shirt_outside_below_band']+=1;row['shirt_below_band']+=1
        views.append(row)
    return {**counts,'views':views}

images=[]
def render(label,angle=0,kind='waist'):
    middle=(roi[0]+roi[1])/2;target=Vector((center[0],center[1],middle));scale=.53
    if kind=='full':
        h=max(coordinates(body)[:,2]);target=Vector((0,0,h*.52));scale=h*1.25
    elif kind=='fly':target=Vector((0,-.15,.95));scale=.18
    a=math.radians(angle);camera.location=target+Vector((math.sin(a)*3,-math.cos(a)*3,0))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    path=OUT/'renders'/('uncle_v22_'+label+'.png');scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True);images.append(path.name)

def all_frames(label,draw=True):
    data={}
    for f in range(49):
        scene.frame_set(f);bpy.context.view_layer.update();data[str(f)]=scan()
        print('V22_FRAME',label,f,data[str(f)]['visible_skin'],data[str(f)]['shirt_outside_below_band'],data[str(f)]['legacy_far_side_tuck_count'],flush=True)
        if draw:
            for name,(keyframe,_) in poses.items():
                if keyframe==f and name!='reset':
                    render(label+'_'+name+'_front');render(label+'_'+name+'_back45',135)
    scene.frame_set(0);bpy.context.view_layer.update()
    if draw:render(label+'_full',kind='full');render(label+'_fly',kind='fly')
    return data

fly_before=surface_audit(pants)
before=all_frames('before')
fly=separate_fly(pants)
training_frames=[0,6,12,18,24,30,36,42,48]
tuck=fit_tucked_hem(body,shirt,pants,rig,center,limbs,training_frames)
after=all_frames('after');fly_after=surface_audit(pants)
changes=[o.name for o in meshes if digest_mesh(o)!=initial[o.name]]
assert set(changes)<=set([shirt.name,pants.name])
assert all(structure(o)==structures[o.name] for o in meshes)
for im in bpy.data.images:
    if im.source=='FILE':
        original=next(t for t in textures if t['name']==im.name)
        assert hashlib.sha256(im.packed_file.data).hexdigest()==original['sha256']

def export(path,animated):
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig,*meshes]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_skins=True,export_morph=True,
        export_animations=animated,export_morph_normal=False,export_cameras=False,export_lights=False)
    d=GLB(path).doc
    assert len(d['skins'])==1 and len(d['skins'][0]['joints'])==53
    assert any(len(m.get('extras',{}).get('targetNames',[]))==10 for m in d['meshes'])
    assert path.stat().st_size<6000000
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'animations':len(d.get('animations',[]))}
scene.frame_set(0);bpy.context.view_layer.update()
neutral=export(OUT/'models/uncle_v22_source.glb',False)
animated=export(OUT/'motion/uncle_v22_stress.glb',True)
assert animated['animations']==1
bpy.ops.file.pack_all();blend=OUT/'blend/uncle_v22_source.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
summary={'status':'LOCAL_CANDIDATE_NOT_ART_APPROVED','input_source_sha256':sha(source),'native_body_vertices':13380,'bones':53,'body_morphs':10,
 'changed_meshes':changes,'non_target_meshes_unchanged':True,'topology_uv_weights_unchanged':True,'textures_unchanged':True,
 'fly':fly,'fly_surface_before':fly_before,'fly_surface_after':fly_after,'tuck':tuck,
 'metric_revision':'V22 same-side waist height at shirt hit; raw V21 far-side count retained separately',
 'calibration':cal,'fixed_roi_z':roi,'center_xy':center.tolist(),'grid':[8,41,25],
 'before_49_frames':before,'after_49_frames':after,'neutral_glb':neutral,'stress_glb':animated,
 'source_blend':{'file':blend.name,'sha256':sha(blend)},'renders':images,'decoded_textures':textures,'art_approved':False,
 'scope':'Local V21 source edits, no full four-person rebuild; same stress clip, not a walk cycle'}
(OUT/'qa/uncle_v22_source_qa.json').write_text(json.dumps(summary,indent=2))

bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=24
bpy.ops.import_scene.gltf(filepath=str(OUT/'motion'/animated['file']))
rig=next(o for o in scene.objects if o.type=='ARMATURE');body=bpy.data.objects['TrueMPFBBody_uncle']
shirt=bpy.data.objects['OpenSourceCloth_uncle_toigo_basic_tucked_t-shirt'];pants=bpy.data.objects['OpenSourceCloth_uncle_toigo_wool_pants']
limbs=arm_faces(body,rig);roundtrip=all_frames('delivered',False);fly_delivered=surface_audit(pants)
bpy.ops.wm.open_mainfile(filepath=str(blend))
assert len(bpy.data.objects['TrueMPFBBody_uncle'].data.vertices)==13380
assert len(bpy.data.objects['RootRig_uncle'].data.bones)==53
for im in bpy.data.images:
    if im.source=='FILE':assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
sums=lambda d:{key:sum(v[key] for v in d.values()) for key in ('visible_skin','shirt_outside_below_band','legacy_far_side_tuck_count','legacy_pants_behind_body')}
quality={'baseline':sums(before),'candidate':sums(after),'delivered':sums(roundtrip)}
quality['new_skin_hit_frames']=[f for f in after if after[f]['visible_skin']>before[f]['visible_skin']]
quality['tuck_regression_frames']=[f for f in after if after[f]['shirt_outside_below_band']>before[f]['shirt_outside_below_band']]
quality['heldout_frames']=[f for f in range(49) if f not in training_frames]
quality['art_approved']=False
quality['fly_surface']={'baseline':fly_before,'candidate':fly_after,'delivered':fly_delivered}
quality['metric_revision']='Corrected same-side boundary comparison, not a 83-to-0 repair claim'
(OUT/'qa/uncle_v22_roundtrip.json').write_text(json.dumps({'quality':quality,'frames':roundtrip,'animation_sha256':animated['sha256'],'source_reopen_verified':True},indent=2))
print('V22_ACTUAL_RESULT',json.dumps(quality),flush=True)
