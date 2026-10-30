"""Real Blender QA for V19. Same source/candidate animation, views and lights.
Not a cloth simulator, walk cycle, whole-body approval or image retouch.
"""
import os,sys,json,math,hashlib,shutil
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from waist_core import GLB,repair,periodic

OUT=Path(os.environ.get('V19_OUT','outputs/v19_waist')).resolve();OUT.mkdir(parents=True,exist_ok=True)
SOURCE=Path(os.environ.get('V19_SOURCE','input/jie_v18_poses_not_walk_cycle.glb')).resolve()
CANDIDATE=OUT/'jie_v19_tucked_waist_PILOT.glb'
repair_report=repair(SOURCE,CANDIDATE)
# Regression unit tests for periodic interpolation and the original asset.
assert np.allclose(periodic(np.array([-2.,0.,2.]),np.ones(3),np.array([-math.pi,math.pi])),1)
assert repair_report['all_other_binary_bytes_identical']
doc=GLB(CANDIDATE).doc
assert len(doc['skins'][0]['joints'])==53
assert sum(len(a['channels']) for a in doc['animations'])==159
assert any(len(m.get('extras',{}).get('targetNames',[]))==10 for m in doc['meshes'])

KEY_POSES=[('neutral',0.),('arms_raise',.5),('torso_bend',1.),('step',1.5)]
TEST_POSES=KEY_POSES+[(f'between_{i}',t) for i,t in enumerate((.25,.75,1.25,1.75))]
# These fixed bounds are unchanged across versions/poses. They exclude the neck.
ZMIN,ZMAX=.94,1.13
NX,NZ,VIEWS=41,25,8
TOLERANCE=.0015


def setup(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.render.fps=24
    bpy.ops.import_scene.gltf(filepath=str(path))
    rig=next(o for o in scene.objects if o.type=='ARMATURE')
    body=next(o for o in scene.objects if o.type=='MESH' and o.name=='TrueMPFBBody_jie')
    shirt=next(o for o in scene.objects if o.type=='MESH' and 'OpenSourceCloth_jie_toigo_basic_tucked_t-shirt' in o.name)
    pants=next(o for o in scene.objects if o.type=='MESH' and 'OpenSourceCloth_jie_cortu_cargo_pants' in o.name)
    assert len(rig.data.bones)==53
    # Use the actual bone hierarchy, including all fingers, rather than an
    # incomplete list of names which mistakes fingers for exposed waist skin.
    arm_names=set()
    for side in ('l','r'):
        root=rig.data.bones['upperarm_'+side]
        arm_names.add(root.name);arm_names.update(b.name for b in root.children_recursive)
    group_names={g.index:g.name for g in body.vertex_groups}
    scores=[sum(g.weight for g in v.groups if group_names.get(g.group) in arm_names) for v in body.data.vertices]
    limb_faces=[sum(scores[i] for i in p.vertices)/len(p.vertices)>.5 for p in body.data.polygons]
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.device='CPU'
    scene.render.threads_mode='FIXED';scene.render.threads=8
    scene.render.resolution_x=640;scene.render.resolution_y=520;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.world=bpy.data.worlds.new('V19_IdenticalWorld');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.15,.18,.21,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.56
    camera_data=bpy.data.cameras.new('V19_IdenticalCamera');camera=bpy.data.objects.new('V19_IdenticalCamera',camera_data)
    scene.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO'
    for name,xyz,power in (('Key',(3,-4,4),440),('Fill',(-3,-3,3),260),('Rim',(-2,3,4),260)):
        light=bpy.data.lights.new(name,'AREA');obj=bpy.data.objects.new(name,light);scene.collection.objects.link(obj)
        obj.location=xyz;obj.rotation_euler=(Vector((0,0,1.1))-obj.location).to_track_quat('-Z','Y').to_euler()
        light.energy=power;light.size=3.3
    return scene,rig,body,shirt,pants,limb_faces


def evaluated_bvh(obj):
    deps=bpy.context.evaluated_depsgraph_get();evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh()
    try:
        if len(mesh.polygons)!=len(obj.data.polygons):raise RuntimeError('Unexpected evaluated topology change')
        points=[evaluated.matrix_world@v.co for v in mesh.vertices]
        polygons=[list(p.vertices) for p in mesh.polygons]
        return BVHTree.FromPolygons(points,polygons,all_triangles=False)
    finally:evaluated.to_mesh_clear()


def hit(bvh,origin,direction):
    p,normal,face,distance=bvh.ray_cast(origin,direction,2.0)
    return (float(distance),face) if p is not None else (float('inf'),-1)


def scan(body,shirt,pants,limb_faces):
    bvh_b=evaluated_bvh(body);bvh_s=evaluated_bvh(shirt);bvh_p=evaluated_bvh(pants)
    rows=[]
    for view in range(VIEWS):
        angle=2*math.pi*view/VIEWS
        radial=Vector((math.sin(angle),-math.cos(angle),0));tangent=Vector((math.cos(angle),math.sin(angle),0))
        direction=-radial
        row={'angle_degrees':45*view,'rays':NX*NZ,'waist_body_hits':0,
             'visible_waist_skin':0,'natural_arm_or_finger_occlusion':0,
             'both_garments_hit':0,'pants_outer_expected_for_tucked_shirt':0,
             'shirt_outer_in_overlap_for_manual_review':0,'skin_sample_positions':[]}
        for iz in range(NZ):
            z=ZMIN+(ZMAX-ZMIN)*iz/(NZ-1)
            for ix in range(NX):
                x=-.18+.36*ix/(NX-1)
                origin=radial+tangent*x+Vector((0,-.035,z))
                b,face=hit(bvh_b,origin,direction);s,_=hit(bvh_s,origin,direction);p,_=hit(bvh_p,origin,direction)
                if math.isfinite(s) and math.isfinite(p):
                    row['both_garments_hit']+=1
                    if p<s-TOLERANCE:row['pants_outer_expected_for_tucked_shirt']+=1
                    elif s<p-TOLERANCE:row['shirt_outer_in_overlap_for_manual_review']+=1
                if face<0:continue
                if limb_faces[face]:row['natural_arm_or_finger_occlusion']+=1;continue
                row['waist_body_hits']+=1
                if b<min(s,p)-TOLERANCE:
                    row['visible_waist_skin']+=1
                    if len(row['skin_sample_positions'])<20:row['skin_sample_positions'].append(list(origin+direction*b))
        rows.append(row)
    return {'views':rows,'total_rays':NX*NZ*VIEWS,
            'visible_waist_skin':sum(r['visible_waist_skin'] for r in rows),
            'waist_body_hits':sum(r['waist_body_hits'] for r in rows)}


def frame(scene,seconds):
    f=seconds*scene.render.fps/scene.render.fps_base
    scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()


def render(scene,version,pose,view):
    camera=scene.camera;z=1.04
    if view=='front45':camera.location=(1.5,-2.1,z);scale=.47
    elif view=='back45':camera.location=(1.5,2.1,z);scale=.47
    elif view=='full':camera.location=(0,-4.,.88);z=.88;scale=2.15
    else:raise ValueError(view)
    camera.rotation_euler=(Vector((0,-.035,z))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=scale
    name=f'jie_{version}_{pose}_{view}.png';scene.render.filepath=str(OUT/name)
    bpy.ops.render.render(write_still=True)
    return name

all_results={};rendered=[];wrist_proof={}
for version,path in [('before',SOURCE),('after',CANDIDATE)]:
    scene,rig,body,shirt,pants,limb=setup(path);results={}
    for name,seconds in TEST_POSES:
        frame(scene,seconds)
        results[name]=scan(body,shirt,pants,limb)
        if name in ('neutral','arms_raise'):
            wrist_proof[version+'_'+name]=list(rig.matrix_world@rig.pose.bones['hand_l'].head)
        if name in dict(KEY_POSES):
            for view in ('front45','back45'):rendered.append(render(scene,version,name,view))
        print('V19_WAIST_SCAN',version,name,results[name]['visible_waist_skin'],flush=True)
    if version=='after':
        frame(scene,0.);rendered.append(render(scene,version,'neutral','full'))
    all_results[version]=results

for pose in dict(TEST_POSES):
    if all_results['after'][pose]['visible_waist_skin']>all_results['before'][pose]['visible_waist_skin']:
        regression=True;break
else:regression=False
before_total=sum(r['visible_waist_skin'] for r in all_results['before'].values())
after_total=sum(r['visible_waist_skin'] for r in all_results['after'].values())
report={'status':'PILOT_STATIC_WAIST_REPAIR_WITH_ORIGINAL_STRESS_ANIMATION',
        'repair':repair_report,'qa_bounds':{'z':[ZMIN,ZMAX],'width':.36,'radial_center_y':-.035,
            'views':VIEWS,'grid':[NX,NZ],'depth_tolerance_m':TOLERANCE,'times':dict(TEST_POSES)},
        'measurements':all_results,'rendered_images':rendered,'actual_wrist_world_positions':wrist_proof,
        'sampled_regression':regression,'sum_before':before_total,'sum_after':after_total,
        'legacy_warning':'V18 counts included exposed neck skin. Pants ahead of a tucked T-shirt is not inherently wrong.',
        'limits':['Discrete rays and 8 sampled times, not proof for every pose.',
                  'No new source MPFB reconstruction; original body buffer remains identical.',
                  'No new walk cycle or cloth simulation. Art and 8-character release remain unapproved.'],
        'art_approved':False}
(OUT/'v19_waist_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
(OUT/'README_繁體中文.txt').write_text('V19 外送員腰部修補候選\n\n只調整原褲裝頂點與法線。人體、臉部表情、骨架權重、貼圖、UV、網格面與原動畫資料均逐位元組保留。\n原始服裝是紮入式 T 恤，褲頭遮住衣服不是錯誤；本版改以八方向的腰部露膚檢查驗證，排除領口與手指遮擋。\n修補包含側腰與後腰，仍需看實際渲染圖判定是否自然。這是四姿態加四個中間時間點的壓力測試，不是走路循環。\n未通過正式美術驗收，並非八人正式角色包。完整數值與檔案 SHA256 請見 JSON。\n\n來源：3dcodeverse-lab V18 Actions 41140731630 / Artifact 13018858363。服裝沿用專案已有的 toigo_basic_tucked_t-shirt（MargaretToigo）及 cortu_cargo_pants（Cortu）；來源 V17 報告標示 CC0。本輪沒有新增外部素材。\n',encoding='utf-8')
if regression or before_total<=0 or after_total>=before_total*.7:
    raise RuntimeError('Waist regression/improvement gate failed; see actual report')
assert abs(wrist_proof['after_arms_raise'][2]-wrist_proof['after_neutral'][2])>.30
assert all(np.allclose(wrist_proof['before_'+p],wrist_proof['after_'+p],atol=1e-6) for p in ('neutral','arms_raise'))
print('V19_COMPLETE',before_total,after_total,repair_report,flush=True)
