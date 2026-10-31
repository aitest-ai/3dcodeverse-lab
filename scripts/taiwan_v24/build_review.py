"""V24 wardrobe design: original skinned belt over untouched V23 clothing.
The goal is visual coherence at game distance, not zero every seam statistic.
Reports sample occlusions honestly; never call CI an art approval.
"""
import os,sys,json,hashlib,math
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent
for folder in (HERE,HERE.parent/'taiwan_v20',HERE.parent/'taiwan_v21'):sys.path.insert(0,str(folder))
from source_waist import coordinates,digest_mesh
from motion_qa import GLB,arm_faces,evaluated_bvh
from belt import build
INPUT=Path(os.getenv('V24_INPUT','input/v23')).resolve()
OUT=Path(os.getenv('V24_OUT','outputs/v24')).resolve()
for d in ('renders','qa'): (OUT/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=INPUT/'blend/uncle_v23_source.blend'
assert sha(source)=='dd227bd4b6183c0d5d9013e555dee6576ffc840a38d6e34935680e0212bffbd3'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;rig=bpy.data.objects['RootRig_uncle']
body=bpy.data.objects['TrueMPFBBody_uncle']
shirt=bpy.data.objects['OpenSourceCloth_uncle_toigo_basic_tucked_t-shirt']
pants=bpy.data.objects['OpenSourceCloth_uncle_toigo_wool_pants']
original=[o for o in scene.objects if o.type=='MESH']
assert len(body.data.vertices)==13380 and len(rig.data.bones)==53
assert len(body.data.shape_keys.key_blocks)==11
assert rig.animation_data and rig.animation_data.action
scene.render.fps=24;scene.frame_start=0;scene.frame_end=48
scene.frame_set(0);bpy.context.view_layer.update()
baseline={o.name:digest_mesh(o) for o in original}
textures={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.source=='FILE' and im.packed_file}
base_materials=[m.name for m in bpy.data.materials]
camera=scene.camera
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=720;scene.render.resolution_y=840;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
# Preserve the previous scene light; change only camera framing consistently.
height=max(coordinates(body)[:,2]);waist=.967
added,design=build(pants,shirt,rig)
assert all(digest_mesh(o)==baseline[o.name] for o in original),'Original mesh changed'
for im in bpy.data.images:
    if im.name in textures:assert hashlib.sha256(im.packed_file.data).hexdigest()==textures[im.name]
for ob in added:
    for v in ob.data.vertices:
        assert 1<=len(v.groups)<=4
        assert abs(sum(g.weight for g in v.groups)-1)<2e-6

views=[('full_front',0,0,'full'),('full_threequarter',0,35,'full'),
       ('waist_front',0,0,'waist'),('waist_threequarter',0,35,'waist'),('waist_back',0,180,'waist'),
       ('raise_full',12,0,'full'),('bend_full',24,35,'full'),('bend_waist',24,0,'waist'),
       ('bend_back',24,150,'waist'),('step_full',36,35,'full')]
images=[]
def render(name,frame,angle,kind):
    scene.frame_set(frame);bpy.context.view_layer.update()
    target=Vector((0,0,height*.51)) if kind=='full' else Vector((0,-.03445,waist))
    a=math.radians(angle);camera.location=target+Vector((math.sin(a)*3,-math.cos(a)*3,0))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=height*1.22 if kind=='full' else .52
    path=OUT/'renders'/('uncle_v24_'+name+'.png');scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True);images.append(path.name)
for stage in ('before','after'):
    for ob in added:ob.hide_render=(stage=='before')
    for name,frame,angle,kind in views:render(stage+'_'+name,frame,angle,kind)
for ob in added:ob.hide_render=False
scene.frame_set(0);bpy.context.view_layer.update()

# Sample outer leather at the top/middle/bottom of every other belt section.
# Original garments only; intentional belt loops and buckle are excluded.
# Counts are local visibility diagnostics, not globally watertight collision proof.
def evaluated_coords(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:return np.array([tuple(ev.matrix_world@v.co) for v in me.vertices])
    finally:ev.to_mesh_clear()

def sample_belt(ob,garments):
    p=evaluated_coords(ob);N=design['circumference_segments']
    assert len(p)==N*8
    trees=[evaluated_bvh(g) for g in garments]
    result={'samples':0,'garment_in_front_of_outer_leather':0,'max_front_depth_m':0.,'examples':[]}
    for i in range(0,N,2):
        lower=p[i*8+3];upper=p[i*8+4]
        normal=Vector((p[i*8+3]-p[i*8]+p[i*8+4]-p[i*8+7])*.5).normalized()
        for t in (.15,.5,.85):
            point=Vector(lower*(1-t)+upper*t);start=point+normal*.03
            result['samples']+=1
            ds=[]
            for tree in trees:
                hit,_,_,dist=tree.ray_cast(start,-normal,.06)
                if hit is not None:ds.append(dist)
            if ds and min(ds)<.0285:
                overlap=.03-min(ds);result['garment_in_front_of_outer_leather']+=1
                result['max_front_depth_m']=max(result['max_front_depth_m'],overlap)
                if len(result['examples'])<8:result['examples'].append({'section':i,'height':t,'front_m':overlap})
    return result
belt=bpy.data.objects['V24_Belt_Leather']
qa={};rest=evaluated_coords(belt);motion_max=0.
for frame in range(49):
    scene.frame_set(frame);bpy.context.view_layer.update()
    qa[str(frame)]=sample_belt(belt,[pants,shirt])
    motion_max=max(motion_max,float(np.linalg.norm(evaluated_coords(belt)-rest,axis=1).max()))
    print('V24_BELT_SAMPLE',frame,qa[str(frame)]['garment_in_front_of_outer_leather'],flush=True)
assert motion_max>.001,'New belt did not follow animated rig'
scene.frame_set(0);bpy.context.view_layer.update()
assert all(digest_mesh(o)==baseline[o.name] for o in original)

def export(path,animated):
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig,*original,*added]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_skins=True,export_morph=True,
        export_animations=animated,export_morph_normal=False,export_cameras=False,export_lights=False)
    doc=GLB(path).doc
    assert len(doc['skins'])==1 and len(doc['skins'][0]['joints'])==53
    assert any(len(m.get('extras',{}).get('targetNames',[]))==10 for m in doc['meshes'])
    assert path.stat().st_size<6000000
    for node in doc['nodes']:
        if node.get('name','').startswith('V24_') and 'mesh' in node:assert 'skin' in node,node
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'animations':len(doc.get('animations',[])),
        'mesh_count':len(doc['meshes']),'animation_channels':sum(len(a.get('channels',[])) for a in doc.get('animations',[]))}
neutral=export(OUT/'uncle_v24_belt.glb',False)
animation=export(OUT/'uncle_v24_belt_stress.glb',True);assert animation['animations']==1
# Friendly starting camera and original editable source with embedded textures.
scene.frame_set(0);bpy.context.view_layer.update()
target=Vector((0,0,height*.51));camera.location=(1.5,-3,height*.51)
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=height*1.22
bpy.ops.file.pack_all();blend=OUT/'uncle_v24_belt.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report={'status':'WARDROBE_DESIGN_PILOT_VISUAL_REVIEW_REQUIRED','source_blend_sha256':sha(source),'design':design,
 'source_body_vertices':13380,'bones':53,'body_morphs':10,'existing_meshes_unchanged':list(baseline),
 'existing_texture_bytes_unchanged':list(textures),'new_accessory_only':True,
 'neutral_glb':neutral,'stress_glb':animation,'source_blend':{'file':blend.name,'sha256':sha(blend)},
 'renders':images,'source_49_frame_belt_samples':qa,'max_belt_motion_m':motion_max,
 'sampling_note':'192 outer-leather points per frame, original pants/shirt visibility only; not all-pose collision proof',
 'motion_scope':'Unchanged original 0-2s FK stress clip, no new walk/run/squat','art_approved':False}
(OUT/'qa/source_report.json').write_text(json.dumps(report,indent=2))

# Clean-scene reimport checks actual delivered skinning and real images.
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=24
bpy.ops.import_scene.gltf(filepath=str(OUT/animation['file']))
rig=next(o for o in scene.objects if o.type=='ARMATURE')
assert len(rig.data.bones)==53
new=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('V24_')]
assert len(new)==len(added)
# UV/normal seams can split exported vertices: compare position motion instead
# of assuming source cross-section indices still apply after glTF reimport.
belt=bpy.data.objects['V24_Belt_Leather'];scene.frame_set(0);bpy.context.view_layer.update()
p0=evaluated_coords(belt);delta=0.
for frame in (0,6,12,18,24,30,36,42,48):
    scene.frame_set(frame);bpy.context.view_layer.update()
    delta=max(delta,float(np.linalg.norm(evaluated_coords(belt)-p0,axis=1).max()))
assert delta>.001
imported={'bones':53,'added_skinned_meshes':[o.name for o in new],'max_delivered_belt_motion_m':delta,
 'source_vs_delivered_motion_max_difference_m':abs(delta-motion_max),
 'note':'Source sampled49 frames, reload9 frames; max differences need not be zero',
 'verified_animation_sha256':animation['sha256']}
# Reuse source lighting by reopening the saved scene, replacing all model objects
# with the exported animated GLB, then render matched full and bent waist views.
bpy.ops.wm.open_mainfile(filepath=str(blend));scene=bpy.context.scene;camera=scene.camera
for o in list(scene.objects):
    if o.type in ('MESH','ARMATURE'):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/animation['file']))
render('delivered_full_front',0,0,'full');render('delivered_bend_waist',24,0,'waist')
bpy.ops.wm.open_mainfile(filepath=str(blend))
assert len(bpy.data.objects['TrueMPFBBody_uncle'].data.vertices)==13380
assert len(bpy.data.objects['RootRig_uncle'].data.bones)==53
for im in bpy.data.images:
    if im.source=='FILE':assert im.packed_file and len(im.pixels)>0 and max(im.size)<=512
(OUT/'qa/roundtrip.json').write_text(json.dumps(imported,indent=2))
manifest={'schema_version':1,'asset_id':'uncle_v24_belt','format':'glTF 2.0 GLB','unit':'meter',
 'source':'V23 native character plus original procedural skinned leather belt and metal buckle',
 'model_file':neutral['file'],'source_file':blend.name,'clips':[],'min_animation_count':0,
 'requirements':{'skins':True,'animated':False,'visual_review':True},
 'license_note':'Original accessory geometry CC0-1.0; inherited MPFB/MakeHuman CC0 character provenance retained',
 'additional_animation_file':animation['file']}
(OUT/'asset_manifest.json').write_text(json.dumps(manifest,indent=2))
report['renders']=images;report['delivered_reimport']=imported
(OUT/'report.json').write_text(json.dumps(report,indent=2))
print('V24_COMPLETED',json.dumps({'neutral':neutral,'animation':animation,'new_objects':len(added),'render_count':len(images),'source_unchanged':True}),flush=True)
