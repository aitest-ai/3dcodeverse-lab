"""Cold mother verification for newly baked Shiba arcs; source geometry is checked independently."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.blender_utils import *
E=R/'evidence-v09';W=R/'work/v09-qa';W.mkdir(parents=True,exist_ok=True);F=R/'library-v09/quaternius-shibainu-grounded-review/0.2.0';meta=json.loads((F/'adaptation.json').read_text());audit=json.loads((F/'motion-audit.json').read_text());report=[]
for variant in ['baseline','model']:
 bpy.ops.wm.open_mainfile(filepath=str(F/(variant+'.blend')));rig=bpy.data.objects['AnimalArmature'];root=bpy.data.objects['StudioRootMotion_v05'];ob=bpy.data.objects['ShibaInu'];assert not any(p.constraints for p in rig.pose.bones)
 for name,data in audit['baseline_clips' if variant=='baseline' else 'clips'].items():
  for o in [rig,root]:
   for tr in o.animation_data.nla_tracks:tr.mute=True
   a=bpy.data.actions[name if o==rig else name+'_Root'];o.animation_data.action=a
   if a.slots:o.animation_data.action_slot=a.slots[0]
  worst=0
  for row in data['samples']:
   bpy.context.scene.frame_set(round(row['t']*60));vs=vertices(ob)
   for k,f in row['feet'].items():
    p=meta['paws'][k];point=sum((vs[i] for i in p['flat']),Vector())/len(p['flat']);low=min(vs[i].z for i in p['ids']);worst=max(worst,(point-Vector(f['reference_m'])).length,abs(low-f['minimum_z_m']))
  assert worst<.00001,(variant,name,worst);bpy.context.scene.frame_set(37);v=vertices(ob);(W/(variant+'-'+name+'-cold.json')).write_text(json.dumps([[p.x,p.z,-p.y] for p in v]));report.append({'variant':variant,'clip':name,'frames':len(data['samples']),'maximum_cold_vs_build_error_m':worst,'mother_sha256':hashlib.sha256((F/(variant+'.blend')).read_bytes()).hexdigest()});print(variant,name,worst,flush=True)
(E/'blender-cold.json').write_text(json.dumps({'blender':bpy.app.version_string,'entries':report,'offline_art_render':'not-performed','human_art':'not-tested'},indent=2)+'\n')
