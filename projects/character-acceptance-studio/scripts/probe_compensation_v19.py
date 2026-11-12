"""Optional numerical-only experiment. No compensated GLB is produced or accepted."""
import bpy,sys,json,math
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];(R/'work/v19').mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import vertices
from v17.sleeves import activate as activate_shape
from v06.motion_overlay import MotionOverlay
from v06.collision import crossings
from v19.visibility import SurfaceAlpha,triangles,alpha_bounds
rows=[]
for key,ver in [('vivi','0.6.0'),('vita','0.5.0')]:
 base=R/'inputs-v19/library-v18'/('vroid-'+key+'-motion-review')/ver;bpy.ops.wm.open_mainfile(filepath=str(R/'experiments-v19'/(key+'-rejected.blend')));body=bpy.data.objects['Body'];rig=bpy.data.objects['Armature'];root=bpy.data.objects['StudioRootMotion_v05'];fit=next(r for r in json.loads((R/'experiments-v19/mapping.json').read_text()) if r['key']==key);mapping=fit['new_vertex_mapping'];inv={n:rig.data.bones[n].matrix_local.inverted() for n in rig.pose.bones.keys()};D=[];samples=[];cache=[]
 before=MotionOverlay(base/'model.glb');after=MotionOverlay(R/'experiments-v19'/(key+'-rejected.glb'));oldtri=[t['vertices'] for t in triangles(before)];newtri=[t['vertices'] for t in triangles(after)];lookup={tuple(sorted(t)):i for i,t in enumerate(oldtri)};parents={r['vertex']:set(r['parents']) for r in mapping};mapped=[lookup[tuple(sorted(set().union(*(parents.get(i,{i}) for i in t))))] for t in newtri];osa,nsa=SurfaceAlpha(before),SurfaceAlpha(after);oa,na=alpha_bounds(before),alpha_bounds(after);nc=[i for i,t in enumerate(newtri) if any(j>=6648 for j in t) and na[i]['potentially_visible']];nv=[i for i,a in enumerate(na) if a['potentially_visible']];oc=sorted({mapped[i] for i in nc if oa[mapped[i]]['potentially_visible']});ov=[i for i,a in enumerate(oa) if a['potentially_visible']]
 for clip in ['Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight']:
  activate_shape(body,clip)
  for ob,name in [(rig,clip),(root,clip+'_Root')]:
   for t in ob.animation_data.nla_tracks:t.mute=True
   action=bpy.data.actions[name];ob.animation_data.action=action
   if action.slots:ob.animation_data.action_slot=action.slots[0]
  for frame in range(round(rig.animation_data.action.frame_range[1])+1):
   bpy.context.scene.frame_set(frame);vs=vertices(body);deltas=[];targets=[]
   for row in mapping:
    i=row['vertex'];a,b=row['parents'];J=Matrix(((0,0,0),(0,0,0),(0,0,0)))
    for g in body.data.vertices[i].groups:
     n=body.vertex_groups[g.group].name
     if n in rig.pose.bones:J+=(rig.pose.bones[n].matrix@inv[n]).to_3x3()*g.weight
    J=rig.matrix_world.to_3x3()@J@rig.matrix_world.inverted().to_3x3()@body.matrix_world.to_3x3();curve=Vector(row['curvature_offset_m']);delta=J.inverted_safe()@((vs[a]+vs[b])*.5-vs[i])+curve;deltas.extend(delta);targets.append(((vs[a]+vs[b])*.5,J@curve))
   D.append(deltas);samples.append({'clip':clip,'frame':frame})
   if frame%2==0:
    oldpairs={(oc[x],ov[y]) for x,y in crossings(vs,[oldtri[i] for i in oc],[oldtri[i] for i in ov])};oldpairs={p for p in oldpairs if osa.crossing_visible(vs,*p)};cache.append((clip,frame,vs,targets,oldpairs))
 print(key,'cached',len(D),'max original skinning midpoint error',max(np.linalg.norm(np.array(D).reshape(len(D),-1,3),axis=2).flat),flush=True)
 matrix=np.array(D);U,S,V=np.linalg.svd(matrix,full_matrices=False);ranks=[]
 for r in range(1,17):
  err=float(np.max(np.linalg.norm((matrix-(U[:,:r]*S[:r])@V[:r]).reshape(len(D),-1,3),axis=2)));ranks.append({'rank':r,'maximum_local_residual_m':err})
 print(key,'ranks',ranks,flush=True)
 tests=[]
 for scale in [1,.5,.25,0]:
  bad=0;maximum=0;byclip={}
  for clip,frame,vs0,targets,oldpairs in cache:
   vs=[v.copy() for v in vs0]
   for row,(mid,curve) in zip(mapping,targets):vs[row['vertex']]=mid+scale*curve
   newraw={(nc[x],nv[y]) for x,y in crossings(vs,[newtri[i] for i in nc],[newtri[i] for i in nv])};ps={(mapped[a],mapped[b]) for a,b in newraw if mapped[a]!=mapped[b] and not set(oldtri[mapped[a]])&set(oldtri[mapped[b]]) and nsa.crossing_visible(vs,a,b)};added=ps-oldpairs;maximum=max(maximum,len(added));bad+=bool(added);byclip[clip]=max(byclip.get(clip,0),len(added))
  tests.append({'curve_scale':scale,'new_crossing_frames':bad,'maximum_new_pairs':maximum,'per_clip':byclip});print(key,tests[-1],flush=True)
 np.savez(R/'work/v19'/(key+'-compensation.npz'),matrix=matrix,U=U,S=S,V=V);rows.append({'key':key,'samples':samples,'ranks':ranks,'tests':tests});(R/'work/v19/compensation-probe.json').write_text(json.dumps(rows,indent=2)+'\n')
