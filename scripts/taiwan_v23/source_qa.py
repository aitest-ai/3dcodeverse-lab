"""V23: edit pinned V22 native source, not a substitute character.
Paired real Cycles renders; same corrected waist semantics before/after;
actual delivered GLB in a fresh scene. No artistic approval from ray counts.
"""
import os,sys,json,hashlib,math
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent
for folder in (HERE,HERE.parent/'taiwan_v20',HERE.parent/'taiwan_v21',HERE.parent/'taiwan_v22'):sys.path.insert(0,str(folder))
from source_waist import coordinates,digest_mesh
from motion_qa import GLB,arm_faces,evaluated_bvh
from waist_fit import opening,periodic
from local_cloth import evaluated_points
from fly_audit import surface_audit
from inner_lip import apply
INPUT=Path(os.getenv('V23_INPUT','input/v22')).resolve()
OUT=Path(os.getenv('V23_OUT','outputs/v23')).resolve()
for d in ('blend','models','motion','renders','qa'): (OUT/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=INPUT/'blend/uncle_v22_source.blend'
assert sha(source)=='6fc8ae3d9fdded9dc64b44edd4881aba7376ba204dd4f7974cd1a4ab1f8bbf46'
base_report=json.loads((INPUT/'qa/uncle_v22_source_qa.json').read_text())
roi=base_report['fixed_roi_z'];center=np.asarray(base_report['center_xy'])
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;rig=bpy.data.objects['RootRig_uncle']
body=bpy.data.objects['TrueMPFBBody_uncle']
shirt=bpy.data.objects['OpenSourceCloth_uncle_toigo_basic_tucked_t-shirt']
pants=bpy.data.objects['OpenSourceCloth_uncle_toigo_wool_pants']
meshes=[o for o in scene.objects if o.type=='MESH']
assert len(body.data.vertices)==13380 and len(rig.data.bones)==53
assert len(body.data.shape_keys.key_blocks)==11
assert not any(m.type=='MASK' for m in body.modifiers)
assert rig.animation_data and rig.animation_data.action,'Keep the actual existing V22 animation'
scene.render.fps=24;scene.frame_start=0;scene.frame_end=48
scene.frame_set(0);bpy.context.view_layer.update()
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
camera=scene.camera;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
limbs=arm_faces(body,rig)

# Same-side seam measure from V22; do not resurrect the V21 far-side error.
def scan():
    trees=[evaluated_bvh(o) for o in (body,shirt,pants)]
    p,ids,_=opening(evaluated_points(pants),[list(f.vertices) for f in pants.data.polygons],True)
    theta=np.arctan2(p[ids,1]-center[1],p[ids,0]-center[0]);heights=p[ids,2]
    counts={'rays':8200,'waist_body_hits':0,'natural_limb_hits':0,'visible_skin':0,'shirt_outside_below_band':0,'legacy_far_side_tuck_count':0}
    for view in range(8):
        angle=view*math.pi/4;r=Vector((math.sin(angle),-math.cos(angle),0));t=Vector((math.cos(angle),math.sin(angle),0))
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
                if bd<min(sd,pd)-.0015:counts['visible_skin']+=1
                if math.isfinite(sd) and math.isfinite(pd) and sd<pd-.0015:
                    q=hits[2][0];a=math.atan2(q.y-center[1],q.x-center[0])
                    old_rim=float(periodic(theta,heights,np.asarray([a]))[0])
                    if z<old_rim-.008:counts['legacy_far_side_tuck_count']+=1
                    s=hits[1][0];a=math.atan2(s.y-center[1],s.x-center[0])
                    same_rim=float(periodic(theta,heights,np.asarray([a]))[0])
                    if z<same_rim-.008:counts['shirt_outside_below_band']+=1
    return counts

# An extended diagnostic includes the very top of the visible dark wedge.
# Both baseline and candidate are measured with identical region and sampling.
def extended_surface():
    ev=pants.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:
        me.calc_loop_triangles()
        points=np.asarray([tuple(ev.matrix_world@v.co) for v in me.vertices])
        faces=np.asarray([list(t.vertices) for t in me.loop_triangles],int)
    finally:ev.to_mesh_clear()
    t=points[faces];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ln=np.linalg.norm(n,axis=1)
    ok=(ln>1e-10)&(t[:,:,1].max(1)<-.10)&(t[:,:,0].min(1)<=.045)&(t[:,:,0].max(1)>=-.045)&(t[:,:,2].min(1)<=.977)&(t[:,:,2].max(1)>=.915)
    t,n=t[ok],n[ok];n/=np.linalg.norm(n,axis=1)[:,None]
    a=t[:,0,[0,2]];b=t[:,1,[0,2]];c=t[:,2,[0,2]]
    den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1]);ok=np.abs(den)>1e-12
    t,n,a,b,c,den=[x[ok] for x in (t,n,a,b,c,den)]
    rays=np.asarray([(x,z) for z in np.linspace(.915,.977,201) for x in np.linspace(-.045,.045,201)])
    covered=back=0
    for start in range(0,len(rays),256):
        q=rays[start:start+256]
        u=((b[:,1]-c[:,1])*(q[:,None,0]-c[:,0])+(c[:,0]-b[:,0])*(q[:,None,1]-c[:,1]))/den
        v=((c[:,1]-a[:,1])*(q[:,None,0]-c[:,0])+(a[:,0]-c[:,0])*(q[:,None,1]-c[:,1]))/den
        mask=(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)
        depth=u*t[:,0,1]+v*t[:,1,1]+(1-u-v)*t[:,2,1]
        selected=np.where(mask,depth,np.inf);indices=selected.argmin(axis=1)
        hit=np.isfinite(selected[np.arange(len(q)),indices]);covered+=int(hit.sum())
        back+=int((hit&(n[indices,1]>.2)).sum())
    return {'rays':len(rays),'covered':covered,'inward_nearest_surface_rays':back,
            'x_range':[-.045,.045],'z_range':[.915,.977],
            'scope':'Neutral pants only; no claim of full clothing visibility or all-pose self-collision'}

images=[]
def render(label,angle=0,kind='waist'):
    middle=(roi[0]+roi[1])/2;target=Vector((center[0],center[1],middle));scale=.53
    if kind=='full':
        h=max(coordinates(body)[:,2]);target=Vector((0,0,h*.52));scale=h*1.25
    elif kind=='fly':target=Vector((0,-.15,.95));scale=.18
    a=math.radians(angle);camera.location=target+Vector((math.sin(a)*3,-math.cos(a)*3,0))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    path=OUT/'renders'/('uncle_v23_'+label+'.png');scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True);images.append(path.name)

pose_names={0:'neutral',12:'arms_raise',24:'torso_bend',36:'step'}
times=[i*.5 for i in range(97)]
def all_frames(label,draw=True):
    data={}
    for f in times:
        scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();data[str(f)]=scan()
        print('V23_FRAME',label,f,data[str(f)]['visible_skin'],data[str(f)]['shirt_outside_below_band'],flush=True)
        if draw and f in pose_names:
            name=pose_names[f];render(label+'_'+name+'_front');render(label+'_'+name+'_back45',135)
    scene.frame_set(0);bpy.context.view_layer.update()
    if draw:
        render(label+'_full',kind='full')
        for angle,title in ((0,'front'),(-35,'left35'),(35,'right35')):render(label+'_fly_'+title,angle,kind='fly')
    return data

# Dump true native geometry for explicit source-index correspondence auditing.
(OUT/'qa/native_pants_before.json').write_text(json.dumps({'points':coordinates(pants).tolist(),'faces':[list(f.vertices) for f in pants.data.polygons]}))
old_surface=surface_audit(pants);old_extended=extended_surface();before=all_frames('before')
repair=apply(pants)
after=all_frames('after');new_surface=surface_audit(pants);new_extended=extended_surface()
changed=[o.name for o in meshes if digest_mesh(o)!=initial[o.name]]
assert changed==[pants.name],changed
assert all(structure(o)==structures[o.name] for o in meshes)
for im in bpy.data.images:
    if im.source=='FILE':
        old=next(t for t in textures if t['name']==im.name)
        assert hashlib.sha256(im.packed_file.data).hexdigest()==old['sha256']

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
neutral=export(OUT/'models/uncle_v23_source.glb',False)
animated=export(OUT/'motion/uncle_v23_stress.glb',True);assert animated['animations']==1
bpy.ops.file.pack_all();blend=OUT/'blend/uncle_v23_source.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
summary={'status':'INNER_LIP_CANDIDATE_NOT_ART_APPROVED','input_source_sha256':sha(source),'native_body_vertices':13380,'bones':53,'body_morphs':10,
 'changed_meshes':changed,'non_target_meshes_unchanged':True,'topology_uv_weights_unchanged':True,'textures_unchanged':True,
 'repair':repair,'old_region_before':old_surface,'old_region_after':new_surface,
 'extended_region_before':old_extended,'extended_region_after':new_extended,
 'fixed_roi_z':roi,'center_xy':center.tolist(),'grid':[8,41,25],'times_blender_frames':times,'fps':24,
 'before_97_times':before,'after_97_times':after,'neutral_glb':neutral,'stress_glb':animated,
 'source_blend':{'file':blend.name,'sha256':sha(blend)},'renders':images,'decoded_textures':textures,'art_approved':False,
 'scope':'Seven V22 native inner-lip points only; same 2-second stress clip at half-frame sampling, not extra motion types or a walk cycle'}
(OUT/'qa/uncle_v23_source_qa.json').write_text(json.dumps(summary,indent=2))

bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=24
bpy.ops.import_scene.gltf(filepath=str(OUT/'motion'/animated['file']))
rig=next(o for o in scene.objects if o.type=='ARMATURE');body=bpy.data.objects['TrueMPFBBody_uncle']
shirt=bpy.data.objects['OpenSourceCloth_uncle_toigo_basic_tucked_t-shirt'];pants=bpy.data.objects['OpenSourceCloth_uncle_toigo_wool_pants']
limbs=arm_faces(body,rig);delivered=all_frames('delivered',False)
export_surface=surface_audit(pants);export_extended=extended_surface()
bpy.ops.wm.open_mainfile(filepath=str(blend))
assert len(bpy.data.objects['TrueMPFBBody_uncle'].data.vertices)==13380
assert len(bpy.data.objects['RootRig_uncle'].data.bones)==53
for im in bpy.data.images:
    if im.source=='FILE':assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
sums=lambda d:{key:sum(v[key] for v in d.values()) for key in ('visible_skin','shirt_outside_below_band','legacy_far_side_tuck_count')}
quality={'baseline':sums(before),'candidate':sums(after),'delivered':sums(delivered),
 'new_skin_times':[f for f in after if after[f]['visible_skin']>before[f]['visible_skin']],
 'same_side_regression_times':[f for f in after if after[f]['shirt_outside_below_band']>before[f]['shirt_outside_below_band']],
 'old_region':{'before':old_surface,'after':new_surface,'delivered':export_surface},
 'extended_region':{'before':old_extended,'after':new_extended,'delivered':export_extended},
 'samples_per_pass':len(times)*8200,'art_approved':False}
(OUT/'qa/uncle_v23_roundtrip.json').write_text(json.dumps({'quality':quality,'times':delivered,'animation_sha256':animated['sha256'],'source_reopen_verified':True},indent=2))
print('V23_ACTUAL_RESULT',json.dumps(quality),flush=True)
