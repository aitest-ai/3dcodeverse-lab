"""Local Run-only elbow skin and garment corrective. Original base vertices, UVs and skin weights stay intact.

Solve bounded cloth/arm crossings in evaluated poses, map the displacement back
through each vertex's native linear-skinning Jacobian, and retain a shape key.
This is a deterministic pose fitting pass, not cloth simulation or solid collision.
"""
import bpy,math
from mathutils import Vector,Matrix
from v05.blender_utils import vertices
from v06.collision import crossings
KEY='Run_ElbowSleeveCorrective';ACTION='Run_ElbowSleeveCorrectiveAction'
def fit(body,rig,regions):
 assert body.data.shape_keys is None,'Expected original Body without morphs'
 rest=[v.co.copy() for v in body.data.vertices];cloth=[t for p in regions['arms'].values() for t in p['sleeve_triangles']];skin=[t for p in regions['arms'].values() for t in p['skin_triangles']];skin_ids={i for t in skin for i in t};ids={i for t in cloth+skin for i in t}
 weights={i:[(body.vertex_groups[g.group].name,g.weight) for g in body.data.vertices[i].groups if body.vertex_groups[g.group].name in rig.pose.bones and g.weight>0] for i in ids};invrest={n:rig.data.bones[n].matrix_local.inverted() for n in rig.pose.bones.keys()};body.shape_key_add(name='Basis');shape=body.shape_key_add(name=KEY);shape.value=1;deltas={i:Vector() for i in ids};history=[]
 for iteration in range(20):
  worst=worst_self=worst_skin_self=updates=0
  for sample in range(85):
   frame=sample/2;bpy.context.scene.frame_set(math.floor(frame),subframe=frame%1);vs=vertices(body);pairs=crossings(vs,skin,cloth);worst=max(worst,len(pairs));constraints={}
   for a,b in pairs:
    A,B,C=[vs[j] for j in skin[a]];normal=(B-A).cross(C-A).normalized()
    for i in cloth[b]:
     signed=(vs[i]-A).dot(normal)
     if signed<.002:constraints.setdefault(i,[]).append(normal*min(.003,.002-signed))
   self_pairs=crossings(vs,cloth);worst_self=max(worst_self,len(self_pairs))
   def mobility(tri):return sum(w*(1 if 'LowerArm' in n else .5 if 'UpperArm' in n else .1 if 'Hand' in n else 0) for i in tri for n,w in weights[i])
   baseline_pairs={tuple(p) for p in regions['baseline_arm_skin_pairs_120hz'][sample]};skin_pairs=[p for p in crossings(vs,skin) if tuple(p) not in baseline_pairs];worst_skin_self=max(worst_skin_self,len(skin_pairs))
   for a,b in skin_pairs:
    fixed,moving=(skin[a],skin[b]) if mobility(skin[a])<=mobility(skin[b]) else (skin[b],skin[a]);A,B,C=[vs[j] for j in fixed];normal=(B-A).cross(C-A).normalized()
    for i in moving:
     signed=(vs[i]-A).dot(normal)
     if signed<.0005:constraints.setdefault(i,[]).append(normal*min(.001,.0005-signed))
   for a,b in self_pairs:
    fixed,moving=(cloth[a],cloth[b]) if mobility(cloth[a])<=mobility(cloth[b]) else (cloth[b],cloth[a]);A,B,C=[vs[j] for j in fixed];normal=(B-A).cross(C-A).normalized()
    for i in moving:
     signed=(vs[i]-A).dot(normal)
     if signed<.001:constraints.setdefault(i,[]).append(normal*min(.002,.001-signed))
   for i,ds in constraints.items():
    worldDelta=sum(ds,Vector())/len(ds);M=Matrix(((0,0,0),(0,0,0),(0,0,0)))
    for n,w in weights[i]:M+=(rig.pose.bones[n].matrix@invrest[n]).to_3x3()*w
    J=rig.matrix_world.to_3x3()@M@rig.matrix_world.inverted().to_3x3()@body.matrix_world.to_3x3();deltas[i]+=(J.inverted_safe()@worldDelta)*.7;shape.data[i].co=rest[i]+deltas[i];updates+=1
  history.append({'iteration':iteration,'maximum_crossing_pairs':worst,'maximum_sleeve_self_pairs':worst_self,'maximum_arm_skin_self_pairs':worst_skin_self,'vertex_updates':updates,'maximum_offset_m':max(v.length for v in deltas.values())})
  if worst==0 and worst_self==0 and worst_skin_self==0:break
 assert max(v.length for v in deltas.values())<.02,'Reject excessive local correction'
 assert max(deltas[i].length for i in skin_ids)<.008,'Reject excessive skin corrective: '+str(max(deltas[i].length for i in skin_ids))
 checks=[]
 for frame in range(43):
  bpy.context.scene.frame_set(frame);vs=vertices(body);pairs=crossings(vs,skin);baseline_pairs={tuple(p) for p in regions['baseline_arm_skin_pairs_120hz'][frame*2]};checks.append({'frame':frame,'sleeve_skin':len(crossings(vs,skin,cloth)),'sleeve_self':len(crossings(vs,cloth)),'arm_skin_self':len(pairs),'new_arm_skin_self':len([p for p in pairs if tuple(p) not in baseline_pairs])})
 assert max(x['sleeve_skin'] for x in checks)==max(x['sleeve_self'] for x in checks)==max(x['new_arm_skin_self'] for x in checks)==0, 'Unresolved arm/sleeve crossing: '+str(checks)
 data=body.data.shape_keys;data.animation_data_create();a=bpy.data.actions.new(ACTION);a.use_fake_user=True;data.animation_data.action=a
 for frame in [0,42]:shape.value=1;shape.keyframe_insert(data_path='value',frame=frame)
 for layer in a.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
 return {'key':KEY,'action':ACTION,'activation':'Run only; zero for reference pose and the six unchanged clips','method':'Local crossed-face separating planes, inverse native LBS Jacobian and 0.7 relaxation; arm skin margin 0.5 mm, cloth self margin 1 mm, cloth/skin margin 2 mm. Original base topology/skin weights retained; no cloth simulation.','history':history,'checks_60hz':checks,'skin_vertex_ids':sorted(i for i in skin_ids if (shape.data[i].co-rest[i]).length>1e-8),'maximum_skin_offset_m':max(deltas[i].length for i in skin_ids),'offsets_local_m':{str(i):list(shape.data[i].co-rest[i]) for i in sorted(ids) if (shape.data[i].co-rest[i]).length>1e-8},'art_approved':False}
def activate(body,name):
 data=body.data.shape_keys
 if data and KEY in data.key_blocks:
  data.animation_data_create();data.animation_data.action=bpy.data.actions.get(ACTION) if name=='Run' else None
  if data.animation_data.action and data.animation_data.action.slots:data.animation_data.action_slot=data.animation_data.action.slots[0]
  data.key_blocks[KEY].value=1 if name=='Run' else 0
