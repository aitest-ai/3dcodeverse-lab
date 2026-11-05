"""Cold-open the new FK mother, retain contact phases, and measure actual corrected mesh coordinates."""
import bpy,json,sys,os,hashlib,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.blender_utils import *
from v06.collision import regions
F=Path(os.environ.get('STUDIO_V06_MODEL',str(R/'work/v06-build/vroid-vivi-motion-review/0.2.0')));E=R/'evidence-v06';E.mkdir(exist_ok=True);W=R/'work/v06-qa';W.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'));rig=bpy.data.objects['Armature'];root=bpy.data.objects['StudioRootMotion_v05'];o=bpy.data.objects['Body'];base=R/'library-v05/vroid-vivi-motion-review/0.1.0';meta=json.loads((base/'adaptation.json').read_text());audit=json.loads((base/'motion-audit.json').read_text());report=[]
assert not any(p.constraints for p in rig.pose.bones)
(E/'collision-regions.json').write_text(json.dumps(regions(o)))
for name,data in audit['clips'].items():
 for ob in [rig,root]:
  for tr in ob.animation_data.nla_tracks:tr.mute=True
  a=bpy.data.actions[name if ob==rig else name+'_Root'];ob.animation_data.action=a
  if a.slots:ob.animation_data.action_slot=a.slots[0]
 low=1e9;changed=0
 for row in data['samples']:
  bpy.context.scene.frame_set(round(row['t']*60));v=vertices(o)
  for k,f in row['feet'].items():
   ids=meta['foot_vertex_ids'][k];selected=meta['contact_sets'][k][f['pivot'] if f['contact'] else 'flat'];point=sum((v[i] for i in selected),Vector())/len(selected);floor=min(v[i].z for i in ids);low=min(low,floor);changed=max(changed,(point-Vector(f['reference_m'])).length);f['reference_m']=list(point);f['minimum_z_m']=floor
  row['root']=list(root.location);row['points']={n:list(bone_world(rig,n).translation) for n in row['points']}
 bpy.context.scene.frame_set(18);probe={ob.name:[[v.x,v.z,-v.y] for v in vertices(ob)] for ob in bpy.data.objects if ob.type=='MESH' and ob.name!='Icosphere'};(W/(name+'-cold.json')).write_text(json.dumps(probe));report.append({'clip':name,'frames':len(data['samples']),'minimum_sole_z_m':low,'maximum_contact_reference_change_from_v01_m':changed});print(name,report[-1],flush=True)
audit.update(method='Cold-open v0.2 baked FK surface, v0.1 contact phase labels retained; new turn twist and final 15% pose settling are measured. Not art approval.',model_sha256=hashlib.sha256((F/'model.glb').read_bytes()).hexdigest());(W/'motion-audit.json').write_text(json.dumps(audit,indent=2)+'\n');
if F.resolve().is_relative_to((R/'work').resolve()):(F/'motion-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
(E/'blender-cold.json').write_text(json.dumps({'blender':bpy.app.version_string,'mother_sha256':hashlib.sha256((F/'model.blend').read_bytes()).hexdigest(),'entries':report,'offline_render':'not performed; evaluated mesh coordinates only','human_art':'not-tested'},indent=2)+'\n')
