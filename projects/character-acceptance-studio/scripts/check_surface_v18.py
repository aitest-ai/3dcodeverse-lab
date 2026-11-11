"""Cold-open exact original surfaces, deterministic mask export, safe edit guard."""
import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v06.motion_overlay import MotionOverlay
from v18.native_guard import geometry_signature,state_signature
from v18.outline import png_mask,MASK_NAME
from v05.blender_utils import vertices
from v17.sleeves import activate as activate_shape
from export_surface_v18 import export
E=R/'evidence-v18';W=R/'work/v18-qa';E.mkdir(exist_ok=True);W.mkdir(parents=True,exist_ok=True)
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def activate(clip):
 activate_shape(bpy.data.objects['Body'],clip)
 for name,a in [('Armature',clip),('StudioRootMotion_v05',clip+'_Root')]:
  ob=bpy.data.objects[name]
  for t in ob.animation_data.nla_tracks:t.mute=True
  action=bpy.data.actions[a];ob.animation_data.action=action
  if action.slots:ob.animation_data.action_slot=action.slots[0]
rows=[]
for key,ver in [('vivi','0.6.0'),('vita','0.5.0')]:
 F=R/'library-v18'/('vroid-'+key+'-motion-review')/ver;meta=json.loads((F/'adaptation.json').read_text());a=MotionOverlay(R/meta['base_model']);b=MotionOverlay(F/'model.glb');assert b.binary[:len(a.binary)]==a.binary
 for prop in ['animations','nodes','skins','materials','meshes','scenes','accessors']:assert a.doc[prop]==b.doc[prop],prop
 assert b.doc['images'][:-1]==a.doc['images'] and b.doc['textures'][:-1]==a.doc['textures']
 # Only the single material's outline texture property may differ among original extensions.
 import copy
 ext=copy.deepcopy(b.doc['extensions']);changed=[]
 for i,m in enumerate(ext['VRM']['materialProperties']):
  if 'Tops' in m['name']:changed.append(m['textureProperties'].pop('_OutlineWidthTexture'))
 assert len(changed)==1 and ext==a.doc['extensions']
 bpy.ops.wm.open_mainfile(filepath=str(R/meta['base_mother']));bpy.context.scene.frame_set(0);source=state_signature();bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'));bpy.context.scene.frame_set(0);assert state_signature()==source
 im=bpy.data.images[MASK_NAME];assert tuple(im.size)==(2048,2048) and hashlib.sha256(im.packed_file.data).hexdigest()==meta['mask_sha256'];cold={}
 for clip in ['Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight']:
  activate(clip);bpy.context.scene.frame_set(18);cold[clip]={o.name:[[v.x,v.z,-v.y] for v in vertices(o)] for o in bpy.data.objects if o.type=='MESH' and o.name!='Icosphere'}
 write(W/(key+'-cold.json'),cold);receipt=export(key,None,W/(key+'-reexport.glb'));assert receipt['sha256']==meta['model_sha256']
 # White mask is an intentionally changed diagnostic file, never a catalog asset.
 white,_=png_mask([]);im=bpy.data.images[MASK_NAME];im.pack(data=white,data_len=len(white));edited=W/(key+'-mask-edit.blend');bpy.ops.wm.save_as_mainfile(filepath=str(edited),compress=True);positive=export(key,edited,W/(key+'-mask-edit.glb'));assert positive['sha256']!=meta['model_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'));bpy.data.objects['Body'].data.vertices[0].co.x+=.001;bad=W/(key+'-unsupported.blend');bpy.ops.wm.save_as_mainfile(filepath=str(bad),compress=True)
 try:export(key,bad,W/(key+'-must-not-exist.glb'));raise AssertionError('Guard accepted geometry edit')
 except RuntimeError as e:assert 'Only the packed outline' in str(e)
 row={'key':key,'version':ver,'model_sha256':meta['model_sha256'],'original_binary_prefix_exact':True,'all_geometry_topology_weights_morphs_uv_normals_exact':True,'seven_animations_rigs_original_images_exact':True,'only_original_extension_change':'Tops _OutlineWidthTexture','native_state_except_new_mask_exact':True,'cold_reexport_byte_exact':True,'editable_mask_export_accepted':True,'unsupported_vertex_edit_rejected':True,'blender':bpy.app.version_string,'geometry_collision_status':'unchanged, not repaired'};rows.append(row);write(E/'blender-checks.json',{'entries':rows,'offline_render':'not-tested; native evaluated surfaces only','human_art':'not-tested'});print(key,'passed',flush=True)
print('V18_NATIVE_PASS')
