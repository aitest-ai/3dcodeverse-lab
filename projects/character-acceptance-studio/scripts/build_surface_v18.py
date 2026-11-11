"""Build from immutable V17: a localized MToon outline mask."""
import bpy,sys,os,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v06.motion_overlay import MotionOverlay
from v06.geometry_guard import geometry_signature
from v18.accessors import values
from v18.outline import png_mask,append as mask_append,MASK_NAME
OUT=Path(os.environ.get('STUDIO_V18_OUT',str(R/'work/v18-build')))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
for key,prev,ver in [('vivi','0.5.0','0.6.0'),('vita','0.4.0','0.5.0')]:
 base=R/'inputs-v18/library-v17'/('vroid-'+key+'-motion-review')/prev;meta=json.loads((base/'adaptation.json').read_text());dest=OUT/('vroid-'+key+'-motion-review')/ver
 if dest.exists():raise RuntimeError('Refuse overwrite '+str(dest))
 assert sha(base/'model.glb')==meta['model_sha256'] and sha(base/'model.blend')==meta['mother_sha256'];dest.mkdir(parents=True)
 bpy.ops.wm.open_mainfile(filepath=str(base/'model.blend'));body=bpy.data.objects['Body'];source_signature=geometry_signature();overlay=MotionOverlay(base/'model.glb');uv=values(overlay,overlay.doc['meshes'][1]['primitives'][0]['attributes']['TEXCOORD_0']);faces=json.loads((R/'scripts/v18/audited_shoulders.json').read_text())['entries'][key];png,mask=png_mask([[uv[i] for i in t['vertices']] for t in faces]);mask['audited_faces']=faces;mask.update(mask_append(overlay,png));(dest/'textures').mkdir();path=dest/'textures/shoulder-outline.png';path.write_bytes(png);im=bpy.data.images.load(str(path));im.name=MASK_NAME;im.colorspace_settings.name='Non-Color';im.pack();im.filepath='//textures/shoulder-outline.png';im.use_fake_user=True
 for m in body.data.materials:
  if 'Tops' in m.name:m['v18_outline_width_image']=MASK_NAME;m['v18_note']='MToon width multiplier; browser only. Geometric folds remain.'
 bpy.context.scene.frame_set(0);modelsha=overlay.save(dest/'model.glb');bpy.ops.wm.save_as_mainfile(filepath=str(dest/'model.blend'),compress=True)
 write(dest/'outline-mask.json',mask)
 write(dest/'adaptation.json',{'asset_id':'vroid-'+key+'-motion-review','version':ver,'base_model':str((base/'model.glb').relative_to(R)),'base_model_sha256':sha(base/'model.glb'),'base_mother':str((base/'model.blend').relative_to(R)),'base_mother_sha256':sha(base/'model.blend'),'model_sha256':modelsha,'mother_sha256':sha(dest/'model.blend'),'mask_sha256':sha(path),'source_geometry_signature':source_signature,'geometry_signature':geometry_signature(),'preserved_binary_prefix_bytes':overlay.prefix_bytes,'preserved_binary_prefix_sha256':overlay.prefix_sha256,'changed_clips':[],'preserved_clips':['Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight'],'preserved':'all geometry, topology, skin weights, morphs, UVs, normals, original images, rigs/rest and animation bytes; only local outline width mask added','geometry_defects':'Existing shoulder folds and skin self intersections remain; material mask does not fix geometry','blender_version':bpy.app.version_string,'art_approved':False,'game_ready':False})
 print('V18_BUILT',key,modelsha,flush=True)
