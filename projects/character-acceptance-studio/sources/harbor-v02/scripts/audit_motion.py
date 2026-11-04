"""Sample evaluated skinned soles and bone trajectories, no image-only or static proxy checks."""
import bpy,json,math,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'assets/harbor-courier-v02.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');soles=[o for o in bpy.data.objects if o.type=='MESH' and any(m and m.name=='Sneaker_rubber' for m in o.data.materials)]
assert soles,'Real skinned outsole mesh missing'
for track in rig.animation_data.nla_tracks:track.mute=True
sc=bpy.context.scene;fps=sc.render.fps;report={'status':'MEASURED_NOT_ART_APPROVED','fps':fps,'clips':{},'scope':'Every integer animation frame; evaluated skinned outsole vertices and ball bone trajectories. Does not prove complete cloth/body non-intersection.'}
for name in ['Idle','Walk','Run','Turn','Talk','Interact','Celebrate']:
 action=bpy.data.actions[name];rig.animation_data.action=action;a,b=map(int,action.frame_range);samples=[];foot={'l':[],'r':[]}
 for frame in range(a,b+1):
  sc.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();low=math.inf
  for o in soles:
   ob=o.evaluated_get(deps);mesh=ob.to_mesh()
   low=min(low,min((ob.matrix_world@v.co).z for v in mesh.vertices));ob.to_mesh_clear()
  for side in ['l','r']:
   p=rig.matrix_world@rig.pose.bones['ball_'+side].matrix.translation;foot[side].append([float(p.x),float(p.y),float(p.z)])
  samples.append({'frame':frame,'minimum_sole_z_m':low})
 speeds=[]
 for side,points in foot.items():
  floor=min(v[2] for v in points)
  for p,q in zip(points,points[1:]):
   if max(p[2],q[2])<floor+.025:
    v=(q[1]-p[1])*fps
    if v>.1:speeds.append(v)
 report['clips'][name]={'frames':len(samples),'min_sole_z_m':min(s['minimum_sole_z_m'] for s in samples),'max_lowest_sole_z_m':max(s['minimum_sole_z_m'] for s in samples),'frames_below_minus_5mm':sum(s['minimum_sole_z_m']<-.005 for s in samples),'estimated_stance_forward_speed_mps':statistics.median(speeds) if speeds and name in ['Walk','Run'] else None,'stance_velocity_samples':len(speeds),'samples':samples}
(R/'evidence/motion-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:{x:v for x,v in d.items() if x!='samples'} for k,d in report['clips'].items()},indent=2))
