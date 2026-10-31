"""V28 bounded quality pass on actual V27 native files, not new identities.
Police: original black shoes and visible cloth fit. Elders: skin-surface study.
Before/after use identical lighting; final delivered GLB is reimported/rendered.
"""
import os,sys,json,hashlib,math,struct
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent
for d in (HERE,HERE.parent/'taiwan_v20'):sys.path.insert(0,str(d))
from source_waist import coordinates,digest_mesh
from motion_qa import evaluated_bvh
from cop_polish import fix_clothes,shoes
import age_material
CID=os.environ['V28_ID'];assert CID in ('cop','oldman','shui')
INPUT=Path(os.getenv('V28_INPUT','input/v27')).resolve();OUT=Path(os.getenv('V28_OUT','outputs/v28/'+CID)).resolve()
for d in ('renders','qa','textures'):(OUT/d).mkdir(parents=True,exist_ok=True)
expected={'cop':'8270fdccc2f53c0d7d771f4bbd282b8dead220757f46cab3edb99b059786e389',
 'oldman':'9c86a51a21cace621cb650e84b3b655f92fb0cb93a1b6b78b7bebd9df7c23728',
 'shui':'b147ae88ef1444a864c51cf85e664f491be6522344bad2533bae3f761f120469'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=INPUT/(CID+'.blend');assert sha(source)==expected[CID]
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;scene.frame_set(0);bpy.context.view_layer.update()
rig=bpy.data.objects['RootRig_'+CID];body=bpy.data.objects['TrueMPFBBody_'+CID]
assert len(body.data.vertices)==13380 and len(rig.data.bones)==53 and len(body.data.shape_keys.key_blocks)==15
assert rig.animation_data and rig.animation_data.action
original=[o for o in scene.objects if o.type=='MESH'];digests={o.name:digest_mesh(o) for o in original}
body_digest=digest_mesh(body);old_names=[o.name for o in original]
shirt=next(o for o in original if o.name.startswith('OpenSourceCloth_'+CID) and 'pants' not in o.name)
pants=next(o for o in original if o.name.startswith('OpenSourceCloth_'+CID) and 'pants' in o.name)
headwear=[o for o in original if o.get('accessory_group') in ('baseball_cap','peaked_cap','straw_hat','white_headband','glasses')]
h=float(coordinates(body)[:,2].max());camera=scene.camera
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.fps=24
scene.frame_start=0;scene.frame_end=60
images=[]

def set_expression(values):
    for o in scene.objects:
        if o.type=='MESH' and o.data.shape_keys:
            for k in o.data.shape_keys.key_blocks[1:]:k.value=values.get(k.name,0.)
    bpy.context.view_layer.update()


def render(label,angle=0,view='full',frame=0,uncovered=False,expression=None):
    scene.frame_set(frame);set_expression(expression or {})
    if view=='face':target=Vector((0,0,h-.135));scale=.43
    elif view=='shoes':target=Vector((0,-.065,.105));scale=.58
    elif view=='waist':target=Vector((0,-.02,h*.56));scale=.56
    else:target=Vector((0,0,h*.53));scale=h*1.23
    for o in headwear:
        if o.name in bpy.data.objects:o.hide_render=uncovered
    a=math.radians(angle);camera.location=target+Vector((3*math.sin(a),-3*math.cos(a),0))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    path=OUT/'renders'/(CID+'_'+label+'.png');scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True);images.append(path.name)
    for o in headwear:
        if o.name in bpy.data.objects:o.hide_render=False
    set_expression({})


def police_visibility():
    s=evaluated_bvh(shirt);p=evaluated_bvh(pants);counts={'back_rays':0,'pants_over_untucked_shirt':0}
    low=float(coordinates(shirt)[:,2].min())
    for iz in range(25):
        z=low+.19*iz/24
        for ix in range(41):
            origin=Vector((-.22+.44*ix/40,.65,z));direction=Vector((0,-1,0))
            a=s.ray_cast(origin,direction,1.3);b=p.ray_cast(origin,direction,1.3)
            counts['back_rays']+=1
            if a[0] is not None and b[0] is not None and b[3]<a[3]-.0015:counts['pants_over_untucked_shirt']+=1
    return counts

if CID=='cop':
    views=[('front',0,'full',0),('back',180,'full',0),('threequarter',35,'full',0),
      ('shoes',0,'shoes',0),('shoes_side',65,'shoes',0),('waist_back',180,'waist',0),
      ('bend_back',160,'waist',24),('step_shoes',35,'shoes',36)]
    before_motion={}
    for f in (0,12,24,36,48,60):scene.frame_set(f);bpy.context.view_layer.update();before_motion[str(f)]=police_visibility()
    for name,a,v,f in views:render('before_'+name,a,v,f)
    scene.frame_set(0);bpy.context.view_layer.update()
    cloth_report=fix_clothes(body,shirt,pants)
    old_shoes=bpy.data.objects.get('TrueMPFBBody_cop.shoes03')
    if old_shoes is None:raise RuntimeError('Original temporary sandals absent')
    removed=old_shoes.name;bpy.data.objects.remove(old_shoes,do_unlink=True)
    new,shoe_report=shoes(body,rig)
    for name,a,v,f in views:render('after_'+name,a,v,f)
    after_motion={}
    for f in (0,12,24,36,48,60):scene.frame_set(f);bpy.context.view_layer.update();after_motion[str(f)]=police_visibility()
    changes={'cloth_fit':cloth_report,'shoe_design':shoe_report,'removed_temporary_sandal_object':removed,
      'before_six_pose_back_samples':before_motion,'after_six_pose_back_samples':after_motion,
      'scope':'Back overlap sampling only; no all-angle zero-clipping claim'}
    unchanged=[n for n in old_names if n not in (removed,shirt.name,pants.name)]
else:
    views=[('front',0,'full',False,{}),('face',0,'face',True,{}),('face_threequarter',35,'face',True,{}),
      ('face_with_hat',0,'face',False,{}),('smile',0,'face',True,{'mouthSmile':.7}),
      ('blink',0,'face',True,{'eyeBlinkLeft':.92,'eyeBlinkRight':.92})]
    for name,a,v,u,e in views:render('before_'+name,a,v,0,u,e)
    eyes=bpy.data.objects['TrueMPFBBody_'+CID+'.high-poly']
    changes=age_material.apply(body,eyes,CID,OUT/'textures')
    for name,a,v,u,e in views:render('after_'+name,a,v,0,u,e)
    unchanged=old_names;new=[]
scene.frame_set(0);set_expression({});bpy.context.view_layer.update()
assert digest_mesh(body)==body_digest,'Body geometry/morphs were altered'
assert all(digest_mesh(bpy.data.objects[n])==digests[n] for n in unchanged),'Out-of-scope source geometry changed'
meshes=[o for o in scene.objects if o.type=='MESH']

def parse(path):
    b=Path(path).read_bytes();magic,version,length=struct.unpack_from('<4sII',b)
    n,kind=struct.unpack_from('<I4s',b,12)
    assert magic==b'glTF' and version==2 and length==len(b) and kind==b'JSON'
    return json.loads(b[20:20+n])


def export(path,animated):
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig,*meshes]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_skins=True,
      export_animations=animated,export_morph=True,export_morph_normal=False,export_cameras=False,export_lights=False,export_extras=True)
    d=parse(path);assert len(d['skins'])==1 and len(d['skins'][0]['joints'])==53
    assert any(len(m.get('extras',{}).get('targetNames',[]))==14 for m in d['meshes'])
    assert path.stat().st_size<6000000
    if CID!='cop':assert any(m.get('normalTexture') for m in d['materials']),'Standard exported normal texture absent'
    for node in d['nodes']:
        if node.get('name','').startswith('V28_cop_Shoe_') and 'mesh' in node:assert 'skin' in node
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'animations':len(d.get('animations',[])),
      'animation_channels':sum(len(a.get('channels',[])) for a in d.get('animations',[]))}
neutral=export(OUT/(CID+'.glb'),False);animated=export(OUT/(CID+'_stress.glb'),True);assert animated['animations']==1
bpy.ops.file.pack_all();blend=OUT/(CID+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report={'character':CID,'version':'V28','source_blend_sha256':sha(source),'native_body_vertices':13380,'bones':53,'body_morph_count':14,
 'body_geometry_and_morphs_unchanged':True,'unchanged_original_meshes':unchanged,'changes':changes,
 'neutral_glb':neutral,'stress_glb':animated,'editable_blend':{'file':blend.name,'bytes':blend.stat().st_size,'sha256':sha(blend)},
 'scope':'Source-preserving quality candidate, not a new MPFB rebuild; same inherited 2.5-second stress action',
 'art_approved':False,'renders':images}
(OUT/'qa/source_report.json').write_text(json.dumps(report,indent=2))
# Reuse exact lights but replace ALL character objects with actual exported GLB.
for o in list(scene.objects):
    if o.type in ('MESH','ARMATURE'):bpy.data.objects.remove(o,do_unlink=True)
headwear=[]
bpy.ops.import_scene.gltf(filepath=str(OUT/animated['file']))
rig=next(o for o in scene.objects if o.type=='ARMATURE');assert len(rig.data.bones)==53
headwear=[o for o in scene.objects if o.type=='MESH' and o.get('accessory_group') in ('baseball_cap','peaked_cap','straw_hat','glasses')]
render('delivered_front',0,'full')
if CID=='cop':
    render('delivered_shoes',35,'shoes');render('delivered_bend_back',160,'waist',24)
    reps=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('V28_cop_Shoe_') and o.name.endswith('_Upper')]
    assert len(reps)==2
    def evaluated(o):
        e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
        try:return np.array([tuple(e.matrix_world@v.co) for v in m.vertices])
        finally:e.to_mesh_clear()
    scene.frame_set(0);bpy.context.view_layer.update();rest={o.name:evaluated(o) for o in reps};moved={n:0. for n in rest}
    for f in (0,12,24,36,48,60):
        scene.frame_set(f);bpy.context.view_layer.update()
        for o in reps:moved[o.name]=max(moved[o.name],float(np.linalg.norm(evaluated(o)-rest[o.name],axis=1).max()))
    assert all(x>.001 for x in moved.values()),'Shoes are static instead of skinned'
    report['delivered_shoe_motion_m']=moved
else:
    render('delivered_face',0,'face',0,True)
    render('delivered_smile',0,'face',0,True,{'mouthSmile':.7})
bpy.ops.wm.open_mainfile(filepath=str(blend))
assert len(bpy.data.objects['TrueMPFBBody_'+CID].data.vertices)==13380
assert len(bpy.data.objects['TrueMPFBBody_'+CID].data.shape_keys.key_blocks)==15
assert len(bpy.data.objects['RootRig_'+CID].data.bones)==53
loaded=[]
for im in bpy.data.images:
    if im.source=='FILE':
        assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
        loaded.append({'name':im.name,'dimensions':list(im.size)})
report['renders']=images;report['delivered_glb_rendered']=True;report['source_reopened_images']=loaded
(OUT/'report.json').write_text(json.dumps(report,indent=2))
manifest={'schema_version':1,'asset_id':CID,'format':'glTF 2.0 GLB','unit':'meter','source':'V27 native character, V28 bounded visual quality changes',
 'model_file':CID+'.glb','source_file':CID+'.blend','clips':[],'min_animation_count':0,
 'requirements':{'skins':True,'animated':False,'visual_review':True},'additional_animation_file':CID+'_stress.glb',
 'license_note':'Original MakeHuman CC0 character; CC0 procedural shoe/normal; source-skin albedo derivative retains CC0 provenance','art_approved':False}
(OUT/'asset_manifest.json').write_text(json.dumps(manifest,indent=2))
print('V28_SOURCE_AND_EXPORT_VERIFIED',CID,json.dumps({'neutral':neutral,'animated':animated,'renders':len(images),'art_approved':False}),flush=True)
