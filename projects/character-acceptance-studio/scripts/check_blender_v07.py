"""Cold-open frozen mothers, compare actual surfaces to build audit, and save native browser-parity probes."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.blender_utils import *
E=R/'evidence-v07';E.mkdir(exist_ok=True);W=R/'work/v07-qa';W.mkdir(parents=True,exist_ok=True);report=[]
for key,ver in [('vivi','0.3.0'),('vita','0.1.0')]:
 F=R/'library-v07'/('vroid-'+key+'-motion-review')/ver;meta=json.loads((F/'adaptation.json').read_text());audit=json.loads((F/'motion-audit.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'));rig=bpy.data.objects['Armature'];root=bpy.data.objects['StudioRootMotion_v05'];body=bpy.data.objects['Body'];assert not any(p.constraints for p in rig.pose.bones)
 for name,data in audit['clips'].items():
  for o in [rig,root]:
   for tr in o.animation_data.nla_tracks:tr.mute=True
   a=bpy.data.actions[name if o==rig else name+'_Root'];o.animation_data.action=a
   if a.slots:o.animation_data.action_slot=a.slots[0]
  worst=0;low=1e9
  for row in data['samples']:
   bpy.context.scene.frame_set(round(row['t']*60));v=vertices(body)
   for s,f in row['feet'].items():
    ids=meta['contact_sets'][s][f['pivot'] if f['contact'] else 'flat'];point=sum((v[i] for i in ids),Vector())/len(ids);minimum=min(v[i].z for i in meta['foot_vertex_ids'][s]);low=min(low,minimum);worst=max(worst,(point-Vector(f['reference_m'])).length,abs(minimum-f['minimum_z_m']))
  assert worst<.00001,(key,name,worst);bpy.context.scene.frame_set(18);probe={o.name:[[v.x,v.z,-v.y] for v in vertices(o)] for o in bpy.data.objects if o.type=='MESH' and o.name!='Icosphere'};(W/(key+'-'+name+'-cold.json')).write_text(json.dumps(probe));report.append({'key':key,'clip':name,'frames':len(data['samples']),'maximum_build_vs_cold_surface_error_m':worst,'minimum_sole_z_m':low,'mother_sha256':hashlib.sha256((F/'model.blend').read_bytes()).hexdigest()});print(key,name,worst,flush=True)
(E/'blender-cold.json').write_text(json.dumps({'blender':bpy.app.version_string,'entries':report,'offline_art_render':'not performed; actual evaluated surfaces only','human_art':'not-tested'},indent=2)+'\n')
