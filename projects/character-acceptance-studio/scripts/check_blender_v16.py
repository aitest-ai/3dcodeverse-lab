"""Cold-open mother, inspect native preservation, compare reproducible export tracks."""
import bpy,json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import vertices
from v06.geometry_guard import geometry_signature
from v06.motion_overlay import MotionOverlay
from export_hands_v16 import activate,other_animation_signature,export
E=R/'evidence-v16';W=R/'work/v16-qa';E.mkdir(exist_ok=True);W.mkdir(parents=True,exist_ok=True);rows=[]
for key,ver in [('vivi','0.4.0'),('vita','0.3.0')]:
 F=R/'library-v16'/('vroid-'+key+'-motion-review')/ver;meta=json.loads((F/'adaptation.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/meta['base_mother']));base_geom=geometry_signature();base_actions=other_animation_signature();action_names=sorted(bpy.data.actions.keys());bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'))
 assert geometry_signature()==base_geom==meta['geometry_signature'];assert other_animation_signature()==base_actions;assert sorted(bpy.data.actions.keys())==action_names
 rig=bpy.data.objects['Armature'];root=bpy.data.objects['StudioRootMotion_v05'];activate(rig,root,'Run');bpy.context.scene.frame_set(18)
 probe={o.name:[[v.x,v.z,-v.y] for v in vertices(o)] for o in bpy.data.objects if o.type=='MESH' and o.name!='Icosphere'};(W/(key+'-cold.json')).write_text(json.dumps(probe))
 dst=W/(key+'-reexport.glb');receipt=export(key,None,dst);a=MotionOverlay(F/'model.glb');b=MotionOverlay(dst);ca=next(c for c in a.doc['animations'] if c['name']=='Run');cb=next(c for c in b.doc['animations'] if c['name']=='Run');worst=0
 for sa,sb in zip(ca['samplers'],cb['samplers']):
  av,bv=a.values(sa['output']),b.values(sb['output']);assert len(av)==len(bv);worst=max(worst,max(abs(x-y) for v,w in zip(av,bv) for x,y in zip(v,w)))
 assert worst<2e-6,worst
 row={'key':key,'version':ver,'model_sha256':meta['model_sha256'],'mother_sha256':meta['mother_sha256'],'native_geometry_rest_weights_materials_textures_unchanged':True,'all_native_non_target_animation_data_unchanged':True,'native_actions':len(action_names),'reexport_maximum_component_error':worst,'reexport':receipt,'blender':bpy.app.version_string};rows.append(row);print(key,worst,flush=True)
 (F/'report.json').write_text(json.dumps({'generation':'Blender '+bpy.app.version_string+' background CPU','validation':row,'human_art':'not-tested','full_cloth_collision':'not-tested','art_approved':False,'game_ready':False},indent=2)+'\n')
(E/'blender-cold.json').write_text(json.dumps({'entries':rows,'offline_render':'not performed; native evaluated surface probes only','human_art':'not-tested'},indent=2)+'\n')
