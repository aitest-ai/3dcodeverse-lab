"""Reproduce quarantined failures at 60 Hz, preserve raw and alpha-filtered results.
Intersection alpha is not camera visibility, penetration volume, or game physics.
"""
import bpy,sys,json,hashlib,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v06.motion_overlay import MotionOverlay
from v06.collision import crossings
from v05.blender_utils import vertices
from v17.sleeves import activate as shape_activate
from v19.visibility import triangles,alpha_bounds,SurfaceAlpha
from v18.experimental.body_export import append,values
from v19.check_alpha import run as check_alpha
check_alpha()
E=R/'evidence-v19';E.mkdir(exist_ok=True);W=R/'work/v19-qa';W.mkdir(parents=True,exist_ok=True)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def activate(clip):
 shape_activate(bpy.data.objects['Body'],clip)
 for name,a in [('Armature',clip),('StudioRootMotion_v05',clip+'_Root')]:
  ob=bpy.data.objects[name]
  for t in ob.animation_data.nla_tracks:t.mute=True
  action=bpy.data.actions[a];ob.animation_data.action=action
  if action.slots:ob.animation_data.action_slot=action.slots[0]
def canon(a,b):return tuple(sorted((a,b)))
rows=[]
for key,ver in [('vivi','0.6.0'),('vita','0.5.0')]:
 base=R/'inputs-v19/library-v18'/('vroid-'+key+'-motion-review')/ver;trial=R/'experiments-v19'/(key+'-rejected');before=MotionOverlay(base/'model.glb');after=MotionOverlay(trial.with_suffix('.glb'));oldtris=[t['vertices'] for t in triangles(before)];newtris=[t['vertices'] for t in triangles(after)];fit=next(r for r in json.loads((R/'experiments-v19/mapping.json').read_text()) if r['key']==key)
 assert after.binary[:len(before.binary)]==before.binary
 for p in ['animations','nodes','skins','materials','extensions','images','textures','samplers']:assert before.doc.get(p)==after.doc.get(p),p
 for a,b in zip(before.doc['meshes'][1]['primitives'],after.doc['meshes'][1]['primitives']):
  for k,i in a['attributes'].items():assert values(before,i)==values(after,b['attributes'][k])[:6648],k
  for ta,tb in zip(a['targets'],b['targets']):
   for k,i in ta.items():assert values(before,i)==values(after,tb[k])[:6648]
  if 'Tops' not in before.doc['materials'][a['material']]['name']:assert a['indices']==b['indices']
 for i in [0,2]:assert before.doc['meshes'][i]==after.doc['meshes'][i]
 bpy.ops.wm.open_mainfile(filepath=str(trial.with_suffix('.blend')));body=bpy.data.objects['Body'];oldalpha=alpha_bounds(before);newalpha=alpha_bounds(after);old_surface=SurfaceAlpha(before);new_surface=SurfaceAlpha(after)
 # These helpers intentionally support this pinned UV tile, unit color alpha and cutout/opaque/blended setup.
 for surf in [old_surface,new_surface]:
  assert ((surf.uv>=0)&(surf.uv<=1)).all()
  for mi,(blend,cutoff,im) in surf.materials.items():assert blend in [0,1,2] and before.doc['extensions']['VRM']['materialProperties'][mi]['vectorProperties']['_Color'][3]==1
 parents={r['vertex']:set(r['parents']) for r in fit['new_vertex_mapping']};lookup={tuple(sorted(t)):i for i,t in enumerate(oldtris)};mapped=[lookup[tuple(sorted(set().union(*(parents.get(i,{i}) for i in t))))] for t in newtris]
 changed=[i for i,t in enumerate(newtris) if any(v>=6648 for v in t)];visiblechanged=[i for i in changed if newalpha[i]['potentially_visible']];visible=[i for i,a in enumerate(newalpha) if a['potentially_visible']];oldchanged=sorted({mapped[i] for i in changed});oldvisible=[i for i,a in enumerate(oldalpha) if a['potentially_visible']];oldvchanged=[i for i in oldchanged if oldalpha[i]['potentially_visible']];report=[];bookmarks=[];cold={}
 for clip in ['Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight']:
  activate(clip);end=round(bpy.data.actions[clip].frame_range[1]);samples=[];worst=None
  for frame in range(end+1):
   bpy.context.scene.frame_set(frame);v=vertices(body)
   # Raw counts retain fully transparent geometry. Alpha-filtered counts test the actual intersection segment.
   oldraw={canon(oldchanged[x],y) for x,y in crossings(v,[oldtris[j] for j in oldchanged],oldtris)}
   newraw={(changed[x],y) for x,y in crossings(v,[newtris[j] for j in changed],newtris)}
   newraw={(a,b) for a,b in newraw if mapped[a]!=mapped[b] and not set(oldtris[mapped[a]])&set(oldtris[mapped[b]])}
   oldpairs={p for p in oldraw if oldalpha[p[0]]['potentially_visible'] and oldalpha[p[1]]['potentially_visible'] and old_surface.crossing_visible(v,*p)}
   filtered=[(a,b) for a,b in sorted(newraw) if newalpha[a]['potentially_visible'] and newalpha[b]['potentially_visible'] and new_surface.crossing_visible(v,a,b)]
   newpairs={canon(mapped[a],mapped[b]) for a,b in filtered};added=newpairs-oldpairs;flips=[]
   for i in visiblechanged:
    a,b,c=[v[j] for j in newtris[i]];A,B,C=[v[j] for j in oldtris[mapped[i]]]
    if (b-a).cross(c-a).normalized().dot((B-A).cross(C-A).normalized())<-.01:flips.append(i)
   sample={'frame':frame,'time_s':frame/60,'baseline_raw_parent_pairs':len(oldraw),'trial_raw_parent_pairs':len({canon(mapped[a],mapped[b]) for a,b in newraw}),'baseline_alpha_pairs':len(oldpairs),'trial_alpha_pairs':len(newpairs),'added_alpha_parent_pairs':sorted(added),'flipped_children':flips};samples.append(sample)
   if added and (worst is None or len(added)>worst['added_parent_pairs']):
    a,b=next((a,b) for a,b in filtered if canon(mapped[a],mapped[b]) in added);p,q=mapped[a],mapped[b];vs=[v[i] for i in newtris[a]];side='left' if sum(x.x for x in vs)<0 else 'right'
    worst={'id':key+'-'+clip,'clip':clip,'frame':frame,'time_s':frame/60,'added_parent_pairs':len(added),'source_parent_pair':[p,q],'trial_triangle_pair':[a,b],'source_vertices':[oldtris[p],oldtris[q]],'trial_vertices':[newtris[a],newtris[b]],'view':side+'Hand','kind':'new alpha-supported intersection sample; NOT art or visibility approval'}
   if frame==18:cold[clip]={o.name:[[x.x,x.z,-x.y] for x in vertices(o)] for o in bpy.data.objects if o.type=='MESH' and o.name!='Icosphere'}
  report.append({'clip':clip,'samples':samples,'new_crossing_frames':sum(bool(s['added_alpha_parent_pairs']) for s in samples),'maximum_new_parent_pairs':max(len(s['added_alpha_parent_pairs']) for s in samples)});
  if worst:bookmarks.append(worst)
  print(key,clip,report[-1]['new_crossing_frames'],report[-1]['maximum_new_parent_pairs'],flush=True)
 # Cold mother export, deterministic GLB. No fitted numerical/PCA experiment is baked into this file.
 again=MotionOverlay(base/'model.glb');append(again,body,fit['new_vertex_mapping']);dst=W/(key+'-cold-export.glb');sha=again.save(dst);assert sha==h(trial.with_suffix('.glb'))
 write(W/(key+'-cold.json'),cold)
 row={'key':key,'baseline_version':ver,'baseline_sha256':h(base/'model.glb'),'trial_sha256':sha,'trial_mother_sha256':h(trial.with_suffix('.blend')),'status':'rejected-not-for-reuse','sampling_hz':60,'sample_count':sum(len(c['samples']) for c in report),'old_vertices_unchanged':6648,'added_vertices':len(parents),'original_animations_rig_texture_bytes_exact':True,'cold_reexport_byte_exact':True,'clips':report,'bookmarks':bookmarks};rows.append(row);write(E/'surface-diagnostics.json',{'schema_version':1,'status':'rejected trials, diagnostic evidence only','method':'All 7 clips at 60Hz. Changed cuff triangles versus Body, excluding source-adjacent parents; canonical parent-pair comparison. Raw counts include transparent template geometry. Alpha supports intersection segment at <=0.25 base texel spacing, not occlusion/LOD or penetration depth. Does not cover Hair/Face, containment or physics.','entries':rows,'blender':bpy.app.version_string,'human_art':'not-tested','physical_mobile':'not-tested'})
 assert any(c['new_crossing_frames'] for c in report),'Expected rejection not reproduced; investigate rather than promote'
print('V19_FAILURE_REPRODUCED_AND_NATIVE_EXPORT_PASS')
