"""V20 native four-character integration. Runs the existing MPFB source builder
in the SAME Blender process, then edits original source meshes before export.
No reimported GLB is used to construct a character. The V19 GLB is only a
geometry/motion reference and test fixture. This remains an art-unapproved pilot.
"""
import os, sys, json, runpy, hashlib
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from source_waist import apply_native, coordinates, digest_mesh
from motion_qa import ReferenceMotion, arm_faces, scan8, GLB

ID = os.environ['FACE_ID']
if ID not in ('you','boss','uncle','jie'): raise ValueError('Unknown character')
OUT = Path(os.getenv('V20_OUT','outputs/v20')).resolve()
for name in ('models','blend','renders','qa','motion'):
    (OUT/name).mkdir(parents=True, exist_ok=True)
base = ROOT/'scripts/taiwan_characters/face_v17_knit_layer_qa.py'
raw = base.read_bytes()
blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
if blob != '97ce03edff0385da7f21a6fbd135adfcf25de855':
    raise RuntimeError('Unreviewed source MPFB builder change: '+blob)
os.environ['FACE_OUT'] = str(ROOT/'.tmp_v20'/ID)
os.environ['FACE_EXPORT_GLB'] = '1'
os.environ['FACE_HAIR_CHOICE'] = 'ponytail01'
# A real source rebuild: inherits mature V17 phenotype, CC0 assets and helpers removal.
g = runpy.run_path(str(base), run_name='__v20_original_mpfb_build__')
body, rig = g['body'], g['rig']
shirt, pants = g['garment_items']
meshes = [body, *g['attached']]
assert len(body.data.vertices) == 13380
assert len(rig.data.bones) == 53
assert len(body.data.shape_keys.key_blocks) == 11
assert not any(m.type == 'MASK' for m in body.modifiers)
initial = {ob.name: digest_mesh(ob) for ob in meshes}
scene, camera = bpy.context.scene, g['camera']
scene.render.fps = 24
scene.render.threads_mode = 'FIXED'; scene.render.threads = 8
scene.cycles.samples = 24
scene.render.resolution_x = 640; scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
images = []


def render(name, position, target, scale):
    camera.location = position
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale = scale
    path = OUT/'renders'/(ID+'_v20_'+name+'.png')
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    images.append(path.name)
    return path.name


def waist_render(version, pose, view):
    xyz = (1.5,-2.1,1.04) if view == 'front45' else (1.5,2.1,1.04)
    return render(version+'_'+pose+'_'+view, xyz, (0,-.035,1.04), .47)


def reset_pose():
    rig.animation_data_clear()
    scene.frame_set(0)
    for b in rig.pose.bones: b.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()


def export(path, animate=False):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in [rig, *meshes]: ob.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB',
        use_selection=True, export_skins=True, export_morph=True,
        export_animations=animate, export_morph_normal=False,
        export_cameras=False, export_lights=False, export_extras=True)
    doc = GLB(path).doc
    assert len(doc['skins']) == 1 and len(doc['skins'][0]['joints']) == 53
    assert any(len(m.get('extras',{}).get('targetNames',[])) == 10 for m in doc['meshes'])
    assert path.stat().st_size < 6000000
    return {'file':path.name,'bytes':path.stat().st_size,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'animations':len(doc.get('animations',[]))}


motion = None; repair = None; before = {}; after = {}; parity = None; pose_error = 0.
key_poses = {'neutral':0., 'arms_raise':.5, 'torso_bend':1., 'step':1.5}
if ID == 'jie':
    refs = list(Path(os.environ['V19_REFERENCE_DIR']).rglob('jie_v19_tucked_waist_PILOT.glb'))
    if len(refs) != 1: raise RuntimeError('Expected exactly one pinned V19 fixture')
    ref = refs[0]
    if hashlib.sha256(ref.read_bytes()).hexdigest() != 'da08048709cdb4bfa8da5b02a92b0d92396ba7f6e9bf9e96b09c28bb14f4b377':
        raise ValueError('V19 reference SHA256 mismatch')
    motion = ReferenceMotion(ref)
    limbs = arm_faces(body, rig)
    for name, seconds in key_poses.items():
        pose_error = max(pose_error, motion.native_pose(rig, seconds, round(seconds*24)))
        before[name] = scan8(body, shirt, pants, limbs)
        for view in ('front45','back45'): waist_render('before', name, view)
    reset_pose()
    repair = apply_native(shirt, pants)
    # Compare the fresh source geometry with the verified V19 shape, not vertex IDs.
    expected = motion.g.mesh('OpenSourceCloth_jie_cortu_cargo_pants')[0]
    actual = coordinates(pants)
    distance = np.linalg.norm(actual[:,None,:]-expected[None,:,:],axis=2)
    parity = float(max(distance.min(axis=0).max(),distance.min(axis=1).max()))
    if parity > 2e-5: raise AssertionError('Native source differs from V19 reference: '+str(parity))

changed = [ob.name for ob in meshes if digest_mesh(ob) != initial[ob.name]]
assert changed == ([pants.name] if ID == 'jie' else []), changed
body_signature = digest_mesh(body)
rig['v20_status'] = 'SOURCE_INTEGRATION_PILOT_ART_UNAPPROVED'
rig['v20_native_body_vertices'] = 13380
neutral_glb = export(OUT/'models'/(ID+'_v20_source.glb'))
# Final views and true source expression renders for all four independently rebuilt people.
for name, (pos,target,scale) in g['views'].items(): render(name,pos,target,scale)
keyobjects = [o for o in meshes if o.data.shape_keys]
for name, weights in g['presets'].items():
    for ob in keyobjects:
        for key in ob.data.shape_keys.key_blocks[1:]: key.value = weights.get(key.name,0.)
    bpy.context.view_layer.update()
    render(name,(0,-3,g['headcenter']),(0,0,g['headcenter']),.50)
for ob in keyobjects:
    for key in ob.data.shape_keys.key_blocks[1:]: key.value = 0.
bpy.context.view_layer.update()
# Editable native source, with packed maps, before adding the audit-only animation.
bpy.ops.file.pack_all()
blend = OUT/'blend'/(ID+'_v20_source.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)

stress_glb = None
if ID == 'jie':
    scene.frame_start = 0; scene.frame_end = 48
    wrist = {}
    for frame in range(49):
        seconds = frame/24
        pose_error = max(pose_error, motion.native_pose(rig, seconds, frame, insert_keys=True))
        row = scan8(body, shirt, pants, limbs)
        after[str(frame)] = {'seconds':seconds, **row}
        print('V20_SOURCE_WAIST_FRAME',frame,row['visible_waist_skin'],flush=True)
        if seconds in key_poses.values():
            name = next(n for n,t in key_poses.items() if t == seconds)
            wrist[name] = list(rig.matrix_world @ rig.pose.bones['hand_l'].head)
            for view in ('front45','back45'): waist_render('after',name,view)
    (OUT/'qa'/'jie_v20_native_motion.json').write_text(json.dumps(
        {'before_key_poses':before,'after_49_frames':after,'pose_matrix_max_error':pose_error,
         'bounds_z':[.94,1.13],'grid':[8,41,25],'tolerance_m':.0015,
         'scope':'Waist-only sampled reference stress clip, not general motion approval'}, indent=2))
    if sum(r['visible_waist_skin'] for r in before.values()) <= 0:
        raise AssertionError('Source baseline did not reproduce a waist defect')
    if any(r['visible_waist_skin'] for r in after.values()):
        raise AssertionError('Source motion waist coverage still fails; inspect saved report')
    if wrist['arms_raise'][2]-wrist['neutral'][2] < .30:
        raise AssertionError('Reference motion did not actually raise source wrist')
    scene.frame_set(0); bpy.context.view_layer.update()
    stress_glb = export(OUT/'motion'/'jie_v20_source_stress.glb', animate=True)
    if stress_glb['animations'] != 1: raise AssertionError('Missing actual stress animation')
    reset_pose()
assert digest_mesh(body) == body_signature
assert len(body.data.vertices) == 13380
report = {'character':ID, 'status':'SOURCE_PIPELINE_INTEGRATED_NOT_ART_APPROVED',
    'native_body_vertices':len(body.data.vertices), 'bones':len(rig.data.bones),
    'body_shape_keys':list(body.data.shape_keys.key_blocks.keys())[1:],
    'helper_geometry_physically_removed':not any(m.type=='MASK' for m in body.modifiers),
    'body_source_digest':body_signature, 'changed_meshes':changed,
    'non_target_mesh_data_unchanged':all(digest_mesh(o)==initial[o.name] for o in meshes if ID!='jie' or o!=pants),
    'repair':repair, 'v19_geometry_bidirectional_error_m':parity,
    'native_source_builder_git_blob':blob,
    'build_commit':os.getenv('GITHUB_SHA'), 'blender':bpy.app.version_string,
    'neutral_glb':neutral_glb, 'stress_glb':stress_glb,
    'editable_blend':{'file':blend.name,'bytes':blend.stat().st_size},
    'renders':images, 'face_asset_report':g['report'],
    'native_motion_frames':len(after),
    'native_motion_rays':sum(r['rays'] for r in after.values()),
    'native_motion_visible_waist_hits':sum(r['visible_waist_skin'] for r in after.values()),
    'art_approved':False, 'characters_completed':4, 'characters_requested':8}
(OUT/'qa'/(ID+'_v20_build.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('V20_SOURCE_BUILD_COMPLETE',ID,json.dumps(report),flush=True)
