"""V30 real V29 source: replace two rigid towel strips with one skinned drape.
Unchanged body/face/hair and original action; floral color map preserved.
Actual Cycles before/after and fresh delivered GLB reimport, no art-pass claim.
"""
import os,sys,json,struct,hashlib,math
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent
for d in (HERE,HERE.parent/'taiwan_v20',HERE.parent/'taiwan_v21',HERE.parent/'taiwan_v24',HERE.parent/'taiwan_v28'):sys.path.insert(0,str(d))
from source_waist import coordinates,digest_mesh
from draped_towel import build
INPUT=Path(os.getenv('V30_INPUT','input/v29')).resolve();OUT=Path(os.getenv('V30_OUT','outputs/v30')).resolve()
for d in ('renders','qa','textures'):(OUT/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=INPUT/'shui.blend'
assert sha(source)=='2fa326259c75a87287d41e9a0dbe3cb8e864a7a1280ca9d19b3183853c54b43c'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
scene.frame_set(0);bpy.context.view_layer.update()
rig=bpy.data.objects['RootRig_shui'];body=bpy.data.objects['TrueMPFBBody_shui']
shirt=bpy.data.objects['OpenSourceCloth_shui_namuhekam_male_polo_shirt']
original=[o for o in scene.objects if o.type=='MESH']
old_towels=[o for o in original if o.get('accessory_group')=='shoulder_towel']
assert len(old_towels)==2
keep=[o for o in original if o not in old_towels];digests={o.name:digest_mesh(o) for o in keep}
assert len(body.data.vertices)==13380 and len(rig.data.bones)==53 and len(body.data.shape_keys.key_blocks)==15
assert not any(m.type=='MASK' for m in body.modifiers)
assert rig.animation_data and rig.animation_data.action
textures={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
bs=next(n for n in shirt.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
color=bs.inputs['Base Color'].links[0].from_node.image
shirt_image_name=color.name;shirt_image_hash=hashlib.sha256(color.packed_file.data).hexdigest()
h=float(coordinates(body)[:,2].max());camera=scene.camera
scene.render.engine='CYCLES';scene.cycles.samples=28;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.fps=24;scene.frame_start=0;scene.frame_end=60
images=[]

def render(label,angle=0,view='chest',frame=0):
    scene.frame_set(frame);bpy.context.view_layer.update()
    if view=='full':target=Vector((0,0,h*.53));scale=h*1.23
    elif view=='neck':target=Vector((0,0,h-.29));scale=.43
    else:target=Vector((0,0,h-.455));scale=.69
    a=math.radians(angle);camera.location=target+Vector((3*math.sin(a),-3*math.cos(a),0))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    p=OUT/'renders'/('shui_v30_'+label+'.png');scene.render.filepath=str(p)
    bpy.ops.render.render(write_still=True);images.append(p.name)

views=[('full',0,'full',0),('full_threequarter',35,'full',0),('chest',0,'chest',0),
 ('threequarter',35,'chest',0),('side',85,'chest',0),('neck_back',180,'neck',0),
 ('raise',0,'chest',12),('bend',35,'chest',24),('step',35,'full',36),('turn',0,'chest',48)]
for n,a,v,f in views:render('before_'+n,a,v,f)
scene.frame_set(0);bpy.context.view_layer.update()
removed=[{'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)} for o in old_towels]
for obj in old_towels:bpy.data.objects.remove(obj,do_unlink=True)
towel,design=build(body,shirt,rig,OUT/'textures')
for n,a,v,f in views:render('after_'+n,a,v,f)
scene.frame_set(0);bpy.context.view_layer.update()
assert all(digest_mesh(bpy.data.objects[n])==v for n,v in digests.items())
for im in bpy.data.images:
    if im.name in textures:assert im.packed_file and hashlib.sha256(im.packed_file.data).hexdigest()==textures[im.name]
assert hashlib.sha256(bpy.data.images[shirt_image_name].packed_file.data).hexdigest()==shirt_image_hash

# Local outer-surface visibility diagnostics, not cloth-physics collision proof.
def evaluated(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:
        p=np.asarray([tuple(ev.matrix_world@v.co) for v in me.vertices])
        nm=ev.matrix_world.to_3x3().inverted().transposed()
        n=np.asarray([tuple((nm@v.normal).normalized()) for v in me.vertices])
        faces=[tuple(f.vertices) for f in me.polygons]
        return p,n,faces
    finally:ev.to_mesh_clear()

def sample(obj,body,shirt):
    p,n,_=evaluated(obj);trees=[]
    for g in (body,shirt):
        gp,gn,gf=evaluated(g);trees.append(BVHTree.FromPolygons(gp.tolist(),gf))
    ids=list(range(0,design['rows']*design['columns'],9))
    front=0;maximum=0.;examples=[]
    for i in ids:
        point=Vector(p[i]);normal=Vector(n[i]);start=point+normal*.030;depth=[]
        for tree in trees:
            hit,_,_,distance=tree.ray_cast(start,-normal,.060)
            if hit is not None:depth.append(distance)
        if depth and min(depth)<.028:
            front+=1;maximum=max(maximum,.03-min(depth))
            if len(examples)<8:examples.append({'source_vertex':i,'depth_m':.03-min(depth)})
    return {'samples':len(ids),'original_clothing_in_front_samples':front,'maximum_depth_m':maximum,'examples':examples}
qa={};rest=evaluated(towel)[0];motion=0.
for frame in range(0,61,6):
    scene.frame_set(frame);bpy.context.view_layer.update()
    qa[str(frame)]=sample(towel,body,shirt)
    motion=max(motion,float(np.linalg.norm(evaluated(towel)[0]-rest,axis=1).max()))
    print('V30_TOWEL_FRAME',frame,qa[str(frame)],flush=True)
assert motion>.002
scene.frame_set(0);bpy.context.view_layer.update()
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
    doc=parse(path);assert len(doc['skins'])==1 and len(doc['skins'][0]['joints'])==53
    assert any(len(m.get('extras',{}).get('targetNames',[]))==14 for m in doc['meshes'])
    assert not any('V27_shui_Towel' in n.get('name','') for n in doc['nodes'])
    assert any(n.get('name')=='V30_shui_DrapedShoulderTowel' and 'skin' in n for n in doc['nodes'])
    assert any('V30_TerryCotton' in m.get('name','') and m.get('normalTexture') for m in doc['materials'])
    assert any('V30_Shui' in m.get('name','') and m.get('normalTexture') for m in doc['materials'])
    assert path.stat().st_size<6000000
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'animations':len(doc.get('animations',[])),
        'animation_channels':sum(len(a.get('channels',[])) for a in doc.get('animations',[]))}
neutral=export(OUT/'shui.glb',False);animated=export(OUT/'shui_stress.glb',True)
assert animated['animations']==1 and animated['animation_channels']==159
bpy.ops.file.pack_all();blend=OUT/'shui.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report={'version':'V30','character':'shui','input_blend_sha256':sha(source),'native_body_vertices':13380,'bones':53,'body_morphs':14,
 'removed_original_towel_objects':removed,'replacement_towel':design,'unchanged_original_meshes':list(digests),
 'original_packed_texture_bytes_preserved':list(textures),'original_shirt_color_sha256':shirt_image_hash,
 'shirt_material_change':'original flower albedo retained; subtle standard normal and increased roughness',
 'neutral_glb':neutral,'stress_glb':animated,'editable_blend':{'file':'shui.blend','sha256':sha(blend)},
 'source_11_time_samples':qa,'max_source_towel_motion_m':motion,'sampling_scope':'Outer-surface torso visibility at11 times, not full self-collision proof',
 'motion_scope':'Original0-2.5s test action unchanged, no cloth simulation or new locomotion',
 'art_approved':False,'renders':images}
(OUT/'qa/source_report.json').write_text(json.dumps(report,indent=2))
for o in list(scene.objects):
    if o.type in ('MESH','ARMATURE'):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/animated['file']))
rig=next(o for o in scene.objects if o.type=='ARMATURE');assert len(rig.data.bones)==53
fresh=bpy.data.objects['V30_shui_DrapedShoulderTowel']
scene.frame_set(0);bpy.context.view_layer.update();p0=evaluated(fresh)[0];moving=0.
for frame in range(0,61,6):
    scene.frame_set(frame);bpy.context.view_layer.update()
    moving=max(moving,float(np.linalg.norm(evaluated(fresh)[0]-p0,axis=1).max()))
assert moving>.002
render('delivered_full',0,'full',0);render('delivered_chest',0,'chest',0)
render('delivered_bend',35,'chest',24);render('delivered_neck_back',180,'neck',0)
bpy.ops.wm.open_mainfile(filepath=str(blend))
assert len(bpy.data.objects['TrueMPFBBody_shui'].data.vertices)==13380
assert len(bpy.data.objects['RootRig_shui'].data.bones)==53
packed=[]
for im in bpy.data.images:
    if im.source=='FILE':
        assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
        packed.append({'name':im.name,'size':list(im.size)})
report.update({'renders':images,'fresh_delivered_towel_motion_m':moving,'source_reopened_images':packed,
 'delivered_glb_rendered':True,'untouched_face_hair':True})
(OUT/'report.json').write_text(json.dumps(report,indent=2))
manifest={'schema_version':1,'asset_id':'shui','unit':'meter','format':'glTF2.0GLB',
 'source':'V29 native shui, original continuous sculpted shoulder towel and cotton normal maps',
 'model_file':'shui.glb','source_file':'shui.blend','clips':[],'min_animation_count':0,
 'requirements':{'skins':True,'animated':False,'visual_review':True},'additional_animation_file':'shui_stress.glb',
 'license_note':'Original towel geometry/texturesCC0-1.0; inherited MPFB/MakeHumanCC0 character; original floral albedo retained',
 'art_approved':False}
(OUT/'asset_manifest.json').write_text(json.dumps(manifest,indent=2))
print('V30_DONE',json.dumps({'neutral':neutral,'animated':animated,'renders':len(images),'source_motion_m':motion,'delivered_motion_m':moving}),flush=True)
