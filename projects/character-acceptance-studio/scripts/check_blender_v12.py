"""Cold-open paired root/body actions; independently sample actual native evaluated geometry."""
import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.blender_utils import vertices
E=R/'evidence-v12';W=R/'work/v12-cold';W.mkdir(parents=True,exist_ok=True);E.mkdir(exist_ok=True);reports=[]
for key in ['horse-brown','horse-white']:
 if __import__('os').environ.get('STUDIO_HORSE') and __import__('os').environ['STUDIO_HORSE']!=key:continue
 F=R/'library-v12'/(key+'-walk-support-review')/'0.1.0';m=json.loads((F/'adaptation.json').read_text());assert hashlib.sha256((F/'model.blend').read_bytes()).hexdigest()==m['mother_sha256'];bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'));rig=bpy.data.objects['AnimalArmature'];root=bpy.data.objects['StudioTravelRoot_v11'];body=bpy.data.objects['Horse'];scale=m['display_calibration']['scale'];offset=m['display_calibration']['offset_y'];assert len(rig.data.bones)==50 and len(bpy.data.actions)==15
 for ob,name in [(rig,'WalkWorld'),(root,'WalkWorld_Root')]:
  ob.animation_data.action=bpy.data.actions[name]
  if ob.animation_data.action.slots:ob.animation_data.action_slot=ob.animation_data.action.slots[0]
 T=m['plan']['duration_s'];poses=[]
 for phase in [0,.125,.5,.875,1]:
  f=T*phase*24;bpy.context.scene.frame_set(int(f),subframe=f%1);poses.append({'phase':phase,'time_s':T*phase,'body':[[v.x*scale,v.z*scale+offset,-v.y*scale] for v in vertices(body)]})
 (W/(key+'.json')).write_text(json.dumps(poses));reports.append({'source_id':key,'model_sha256':m['model_sha256'],'mother_sha256':m['mother_sha256'],'bones':50,'editable_rig_actions':14,'paired_root_actions':1,'body_vertices':len(body.data.vertices),'cold_samples':5,'renders':'not-rendered in v12; actual browser multiview frames/video are separate','art_approved':False})
(E/'blender-cold.json').write_text(json.dumps({'blender':bpy.app.version_string,'entries':reports},indent=2)+'\n');print('V12_COLD_SURFACES_PASS')
