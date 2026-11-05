"""Blender background: cold-open corrected mothers and verify baked FK surfaces against build audits."""
import bpy,json,sys,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.blender_utils import *
E=R/'evidence-v05';E.mkdir(exist_ok=True);report=[]
for key,asset,obj,probe in [('vivi','vroid-vivi-motion-review','Body','Run'),('shiba','quaternius-shibainu-grounded-review','ShibaInu','Gallop')]:
 folder=R/'library-v05'/asset/'0.1.0';bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');root=bpy.data.objects['StudioRootMotion_v05'];ob=bpy.data.objects[obj];meta=json.loads((folder/'adaptation.json').read_text());audit=json.loads((folder/'motion-audit.json').read_text());entries=[]
 assert not any(p.constraints for p in rig.pose.bones),'FK working copy still has live constraints'
 for name,data in audit['clips'].items():
  for o in [rig,root]:
   for tr in o.animation_data.nla_tracks:tr.mute=True
   action=bpy.data.actions[name if o==rig else name+'_Root'];o.animation_data.action=action
   if action.slots:o.animation_data.action_slot=action.slots[0]
  error=0;floor=1e9
  for row in data['samples']:
   bpy.context.scene.frame_set(round(row['t']*60));v=vertices(ob)
   for k,f in row['feet'].items():
    ids=meta['foot_vertex_ids'][k] if key=='vivi' else meta['paws'][k]['ids'];selected=meta['contact_sets'][k][f['pivot'] if f['contact'] else 'flat'] if key=='vivi' else meta['paws'][k]['flat'];point=sum((v[i] for i in selected),Vector())/len(selected);low=min(v[i].z for i in ids);floor=min(floor,low);error=max(error,(point-Vector(f['reference_m'])).length,abs(low-f['minimum_z_m']))
  assert error<1e-5,(key,name,error);entries.append({'clip':name,'samples':len(data['samples']),'maximum_build_vs_cold_bake_error_m':error,'minimum_sole_z_m':floor})
  if name==probe:
   bpy.context.scene.frame_set(18);out={o.name:[[v.x,v.z,-v.y] for v in vertices(o)] for o in bpy.data.objects if o.type=='MESH' and o.name!='Icosphere'};(E/(key+'-cold-geometry.json')).write_text(json.dumps(out))
 report.append({'id':asset,'blender_sha256':hashlib.sha256((folder/'model.blend').read_bytes()).hexdigest(),'clips':entries})
(E/'blender-cold.json').write_text(json.dumps({'version':bpy.app.version_string,'status':'COLD_BAKED_SURFACES_MATCH_BUILD_AUDIT','entries':report,'offline_render':'not performed; these are evaluated native mesh checks, not images','human_art':'not-tested'},indent=2)+'\n');print('COLD_BAKE_PASS',sum(len(x['clips']) for x in report),flush=True)
