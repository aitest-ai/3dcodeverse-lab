"""V29 real V28 source edit, original-relative morph preservation and export QA.
Two elder characters only. Same lighting, poses, camera and inherited action.
Not a new eight-person rebuild or completed art/animation approval.
"""
import os,sys,json,hashlib,math,struct
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent
for d in (HERE,HERE.parent/'taiwan_v20',HERE.parent/'taiwan_v21',HERE.parent/'taiwan_v28'):sys.path.insert(0,str(d))
from source_waist import coordinates,digest_mesh
from elder_form import face_form,hair_form,hair_maps
CID=os.environ['V29_ID'];assert CID in ('oldman','shui')
INPUT=Path(os.getenv('V29_INPUT','input/v28')).resolve();OUT=Path(os.getenv('V29_OUT','outputs/v29/'+CID)).resolve()
for d in ('renders','qa','textures'):(OUT/d).mkdir(parents=True,exist_ok=True)
expected={'oldman':'5a62bfd2351477bba1668852c9c5de32334311ae1c207190fb5b1a866f4ded71',
 'shui':'abab8ae8bbb3862db85f044eafe8f55df81e8ed88c4b0cc2a75544db4f59999d'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=INPUT/(CID+'.blend');assert sha(source)==expected[CID]
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;scene.frame_set(0);bpy.context.view_layer.update()
rig=bpy.data.objects['RootRig_'+CID];body=bpy.data.objects['TrueMPFBBody_'+CID]
eyes=bpy.data.objects['TrueMPFBBody_'+CID+'.high-poly']
hair=bpy.data.objects['HairFitted_'+CID]
assert len(body.data.vertices)==13380 and len(rig.data.bones)==53
assert len(body.data.shape_keys.key_blocks)==15 and rig.animation_data and rig.animation_data.action
assert not any(m.type=='MASK' for m in body.modifiers)
original=[o for o in scene.objects if o.type=='MESH'];digests={o.name:digest_mesh(o) for o in original}

def invariant(obj):
    h=hashlib.sha256()
    for f in obj.data.polygons:h.update(np.asarray(f.vertices[:],dtype='<i4').tobytes())
    for v in obj.data.vertices:
        for g in v.groups:h.update(np.asarray([g.group,g.weight],dtype='<f8').tobytes())
    for uv in obj.data.uv_layers:h.update(np.asarray([tuple(v.uv) for v in uv.data],dtype='<f4').tobytes())
    return h.hexdigest()
structures={o.name:invariant(o) for o in original}
texture_hashes={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
headwear=[o for o in original if o.get('accessory_group') in ('baseball_cap','straw_hat','glasses')]
h=float(coordinates(body)[:,2].max());camera=scene.camera
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.fps=24
scene.frame_start=0;scene.frame_end=60
images=[]

def expression(values):
    for o in scene.objects:
        if o.type=='MESH' and o.data.shape_keys:
            for k in o.data.shape_keys.key_blocks[1:]:k.value=values.get(k.name,0.)
    bpy.context.view_layer.update()

def render(label,angle=0,view='face',frame=0,uncovered=True,expr=None):
    scene.frame_set(frame);expression(expr or {})
    if view=='face':target=Vector((0,0,h-.135));scale=.43
    else:target=Vector((0,0,h*.53));scale=h*1.23
    for o in headwear:
        if o.name in bpy.data.objects:o.hide_render=uncovered
    a=math.radians(angle);camera.location=target+Vector((3*math.sin(a),-3*math.cos(a),0))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    p=OUT/'renders'/(CID+'_'+label+'.png');scene.render.filepath=str(p)
    bpy.ops.render.render(write_still=True);images.append(p.name)
    for o in headwear:
        if o.name in bpy.data.objects:o.hide_render=False
    expression({})

views=[('full',0,'full',0,False,{}),('face',0,'face',0,True,{}),
 ('threequarter',35,'face',0,True,{}),('side',85,'face',0,True,{}),
 ('with_hat',0,'face',0,False,{}),('smile',0,'face',0,True,{'mouthSmile':.7}),
 ('blink',0,'face',0,True,{'eyeBlinkLeft':.92,'eyeBlinkRight':.92}),
 ('jaw_open',0,'face',0,True,{'mouthOpen':.65}),('turn',0,'face',48,False,{})]
for n,a,v,f,u,e in views:render('before_'+n,a,v,f,u,e)
scene.frame_set(0);expression({})
face_report=face_form(body,eyes,CID)
hair_shape_report=hair_form(hair,body,eyes,CID)
hair_texture_report=hair_maps(hair,eyes,CID,OUT/'textures')
for n,a,v,f,u,e in views:render('after_'+n,a,v,f,u,e)
scene.frame_set(0);expression({})
assert all(invariant(o)==structures[o.name] for o in original),'Source topology/UV/weights changed'
unchanged=[o.name for o in original if o not in (body,hair)]
assert all(digest_mesh(bpy.data.objects[n])==digests[n] for n in unchanged)
for im in bpy.data.images:
    if im.name in texture_hashes:assert im.packed_file and hashlib.sha256(im.packed_file.data).hexdigest()==texture_hashes[im.name]
assert len(body.data.vertices)==13380 and len(body.data.shape_keys.key_blocks)==15
assert face_report['changed_source_vertices']>20
assert face_report['relative_morph_max_error_m']<4e-7
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
    assert any('V29_GrayHair' in m.get('name','') and m.get('normalTexture') for m in d['materials'])
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'animations':len(d.get('animations',[])),
      'animation_channels':sum(len(a.get('channels',[])) for a in d.get('animations',[]))}
neutral=export(OUT/(CID+'.glb'),False);animated=export(OUT/(CID+'_stress.glb'),True)
assert animated['animations']==1 and animated['animation_channels']==159
bpy.ops.file.pack_all();blend=OUT/(CID+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report={'character':CID,'version':'V29','input_blend_sha256':sha(source),'native_body_vertices':13380,'bones':53,'body_morph_count':14,
 'body_form':face_report,'hair_form':hair_shape_report,'hair_material':hair_texture_report,
 'topology_uv_weights_unchanged':True,'unchanged_original_meshes':unchanged,
 'source_image_bytes_preserved':list(texture_hashes),'neutral_glb':neutral,'stress_glb':animated,
 'editable_blend':{'file':blend.name,'bytes':blend.stat().st_size,'sha256':sha(blend)},
 'scope':'V28 native elder source update; bounded face and hair form plus source-UV strand maps; same 2.5s action',
 'not_claimed':['complete chronological-age likeness','individual hair simulation','all-angle expression or collision approval','new walk/run/squat'],
 'art_approved':False,'renders':images}
(OUT/'qa/source_report.json').write_text(json.dumps(report,indent=2))
for o in list(scene.objects):
    if o.type in ('MESH','ARMATURE'):bpy.data.objects.remove(o,do_unlink=True)
headwear=[];bpy.ops.import_scene.gltf(filepath=str(OUT/animated['file']))
rig=next(o for o in scene.objects if o.type=='ARMATURE');assert len(rig.data.bones)==53
headwear=[o for o in scene.objects if o.type=='MESH' and o.get('accessory_group') in ('baseball_cap','straw_hat','glasses')]
render('delivered_full',0,'full',0,False)
render('delivered_face');render('delivered_threequarter',35)
render('delivered_smile',expr={'mouthSmile':.7})
render('delivered_blink',expr={'eyeBlinkLeft':.92,'eyeBlinkRight':.92})
render('delivered_jaw_open',expr={'mouthOpen':.65})
bpy.ops.wm.open_mainfile(filepath=str(blend))
assert len(bpy.data.objects['TrueMPFBBody_'+CID].data.vertices)==13380
assert len(bpy.data.objects['TrueMPFBBody_'+CID].data.shape_keys.key_blocks)==15
assert len(bpy.data.objects['RootRig_'+CID].data.bones)==53
loaded=[]
for im in bpy.data.images:
    if im.source=='FILE':
        assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
        loaded.append({'name':im.name,'dimensions':list(im.size)})
report.update({'renders':images,'delivered_glb_rendered':True,'source_reopened_images':loaded})
(OUT/'report.json').write_text(json.dumps(report,indent=2))
manifest={'schema_version':1,'asset_id':CID,'format':'glTF 2.0 GLB','unit':'meter',
 'source':'V28 native elder; V29 bounded artistic cheek/jowl form and gray hair clump maps',
 'model_file':CID+'.glb','source_file':CID+'.blend','clips':[],'min_animation_count':0,
 'requirements':{'skins':True,'animated':False,'visual_review':True},'additional_animation_file':CID+'_stress.glb',
 'license_note':'MakeHuman CC0 character; source-texture derivative and authored normal-field CC0-1.0','art_approved':False}
(OUT/'asset_manifest.json').write_text(json.dumps(manifest,indent=2))
print('V29_SOURCE_AND_EXPORT',CID,json.dumps({'neutral':neutral,'animated':animated,'images':len(images),'face':face_report,'hair':hair_shape_report}),flush=True)
