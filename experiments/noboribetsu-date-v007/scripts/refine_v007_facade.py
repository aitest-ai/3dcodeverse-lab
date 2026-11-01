#!/usr/bin/env python3
"""Noboribetsu Date V007 candidate: restrained photo-agnostic material legibility & noren relief.

The original V005 GLB and all collision/route files are never edited. This is
an artist-estimated visual calibration, NOT a photo-exact or surveyed building.
Requires trimesh, numpy, Pillow; no network/paid models/textures.
"""
from pathlib import Path
import argparse, hashlib, json, math
import numpy as np
from PIL import Image
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals

SOURCE_SHA = 'f2f579f398334473a5c93a55109e87fae6d175c1be5756c484a368ee07b20afb'
MATERIAL_ADJUSTMENTS={
  # warm/dark timber is too uniformly black against the plaster at close camera distance
  'wood_structure': {'rgb':(71,51,37),'rough':.93},
  'wood_aged': {'rgb':(51,39,30),'rough':.95},
  'wood_newer': {'rgb':(94,68,51),'rough':.91},
  'wood_edges': {'rgb':(102,77,57),'rough':.95},
  'tile_mid': {'rgb':(79,83,84),'rough':.94},
  'tile_dark': {'rgb':(65,69,69),'rough':.94},
  'tile_worn': {'rgb':(73,77,77),'rough':.96},
  'noren_blue': {'rgb':(69,87,93),'rough':.99},
  'plaster_lower': {'rgb':(163,151,134),'rough':1.0},
  'plaster_warm': {'rgb':(213,201,177),'rough':.99},
  'plaster_cool': {'rgb':(210,211,200),'rough':.99},
}
WOOD={'wood_structure','wood_aged','wood_newer','wood_edges'}
PLASTER={'plaster_warm','plaster_cool','plaster_lower'}

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for block in iter(lambda:f.read(2**20),b''):h.update(block)
 return h.hexdigest()

def texture(seed):
 """Original repeatable near-neutral, directional weathering texture; no copyrighted source."""
 rng=np.random.default_rng(seed)
 w,h=256,512
 fine=rng.normal(0,1,w)
 fine=np.convolve(np.pad(fine,(12,12),mode='wrap'),np.ones(25)/25,'valid')
 fine=(fine-np.mean(fine))/(np.std(fine)+1e-9)
 yy=np.arange(h)
 out=np.empty((h,w,3),dtype=np.uint8)
 for y in range(h):
  slow=0.75*np.sin((yy[y]+seed*7)/81.0)+0.45*np.sin((yy[y]+seed*3)/17.0)
  # Preserve average albedo (~0.966): low contrast by design; no big fake scratches.
  row=np.clip(246+1.85*fine+1.3*slow,238,252)
  out[y,:,:]=np.stack([row,row*0.995,row*.985],axis=1).astype(np.uint8)
 return Image.fromarray(out,'RGB')

def limewash(seed):
 """Locally authored mottled limewash; weak large-scale color noise, not a photo."""
 rng=np.random.default_rng(seed)
 blocks=rng.normal(0,1,(25,25)).astype(np.float32)
 # Bilinear scaling simulates slow pigment/weather variation, no hand-drawn stains.
 scaled=Image.fromarray(blocks,'F').resize((512,512),Image.Resampling.BILINEAR)
 field=np.asarray(scaled,dtype=float)
 field=(field-field.mean())/(field.std()+1e-9)
 yy,xx=np.mgrid[0:512,0:512]
 shade=np.clip(246+3.2*field+0.7*np.sin(xx/57+yy/81),234,252)
 out=np.stack([shade,shade*.996,shade*.989],axis=-1).astype(np.uint8)
 return Image.fromarray(out,'RGB')

def front_axes(manifest,osm_id):
 b=next(b for b in manifest['buildings'] if b['id']==osm_id)
 poly=np.array([(x,-north) for x,north in b['polygon']],dtype=float)
 cx,cz=poly.mean(axis=0)
 # Reuse construction convention from V005; selected front edge recorded in V005 manifest.
 ext=json.loads((root/'v005_manifest.json').read_text())
 bb=next(b for b in ext['known_buildings'] if b['osm_id']==osm_id)
 i=bb['basis']['front_edge'];a,bt=poly[i],poly[(i+1)%len(poly)]
 u=(bt-a)/np.linalg.norm(bt-a); normal=np.array([-u[1],u[0]])
 mid=(a+bt)/2
 v=normal if np.dot(np.array([cx,cz])-mid,normal)>0 else -normal
 return mid,u,v,float(b['base'])

def refine(rootdir:Path,outdir:Path):
 global root
 root=rootdir.resolve()
 source=root/'assets/v005_east_facades.glb'
 assert sha(source)==SOURCE_SHA, 'Frozen V005 façade GLB changed; refusing modification'
 outdir.mkdir(parents=True,exist_ok=True)
 dst=outdir/'v007_east_facades.glb'
 if dst.exists(): raise FileExistsError(dst)
 scene=trimesh.load(source,force='scene',process=False)
 scene_view=json.loads((root/'scene_view.json').read_text())
 old_summary={n:{'vertices':len(g.vertices),'faces':len(g.faces),'bounds':g.bounds.tolist()} for n,g in scene.geometry.items()}
 before_noren=scene.geometry['noren_blue'].vertices.copy()
 midpoint,u,v,base=front_axes(scene_view,'way/283905573')
 mat_records={}
 for name,geom in scene.geometry.items():
  if name not in MATERIAL_ADJUSTMENTS:continue
  opts=MATERIAL_ADJUSTMENTS[name]
  m=geom.visual.material
  original={'rgb':[int(x) for x in m.baseColorFactor[:3]],'roughness':float(m.roughnessFactor)}
  if name in WOOD:
   # Textures are very low contrast; UVs are explicit and do not change geometry.
   # Structural timbers mostly follow world vertical direction; local source was
   # built from repeated 8-vertex boxes with independent corners.
   pts=np.asarray(geom.vertices,dtype=float)
   uv=np.column_stack(((pts[:,0]*.49+pts[:,2]*.37),pts[:,1]*.62)).astype(np.float32)
   neutral=texture(101+sorted(WOOD).index(name)*137)
   geom.visual=TextureVisuals(uv=uv,material=PBRMaterial(name=name,
      baseColorFactor=[*opts['rgb'],255],baseColorTexture=neutral,
      roughnessFactor=opts['rough'],metallicFactor=0,doubleSided=True))
  elif name in PLASTER:
   pts=np.asarray(geom.vertices,dtype=float)
   uv=np.column_stack(((pts[:,0]*.24+pts[:,2]*.14),pts[:,1]*.34)).astype(np.float32)
   geom.visual=TextureVisuals(uv=uv,material=PBRMaterial(name=name,
      baseColorFactor=[*opts['rgb'],255],baseColorTexture=limewash(991+len(name)*11),
      roughnessFactor=opts['rough'],metallicFactor=0,doubleSided=True))
  else:
   m.baseColorFactor=np.array([*opts['rgb'],255],dtype=np.uint8)
   m.roughnessFactor=opts['rough']
  mat_records[name]={'before':original,'after':opts,'original_artist_estimate':True}

 # Subtle sag only in B candidate cloth, not A skeleton or real walk/collision.
 # The top edge is fixed; below, maximum 12 mm outward and 8 mm vertical.
 fabric=scene.geometry['noren_blue'];pts=fabric.vertices.copy()
 y_top=pts[:,1].max();y_bottom=pts[:,1].min();dy=max(1e-4,y_top-y_bottom)
 local=(pts[:,[0,2]]-np.array(midpoint)) @ u
 # The entry reused the V005 four-panel fabric. Avoid left/right giant sinusoid.
 for idx,p in enumerate(pts):
  t=np.clip((y_top-p[1])/dy,0,1)
  phase=local[idx]*2.7+0.8
  outward=.012*np.sin(phase)*t*t
  drop=.008*np.sin(phase*.66+1.1)*t*t
  pts[idx,0]-=v[0]*outward
  pts[idx,2]-=v[1]*outward
  pts[idx,1]-=drop
 fabric.vertices=pts
 displacement=np.linalg.norm(pts-before_noren,axis=1)
 max_disp=float(displacement.max())
 assert max_disp<.018, max_disp
 # The source is held independently, and every other mesh still has exact vertex/face counts.
 dst.write_bytes(scene.export(file_type='glb'))
 reread=trimesh.load(dst,force='scene',process=False)
 assert set(scene.geometry)==set(reread.geometry)
 for name,old in old_summary.items():
  a=reread.geometry[name]
  assert len(a.vertices)==old['vertices'] and len(a.faces)==old['faces'],name
  if name!='noren_blue':
   assert np.allclose(a.vertices,trimesh.load(source,force='scene',process=False).geometry[name].vertices,atol=1e-5),name
 # glTF vertices serialized to float32. Allow 5e-6 m for geometry quantization.
 delta=np.linalg.norm(reread.geometry['noren_blue'].vertices-before_noren,axis=1)
 assert max(delta)<.019
 report={'schema':'date-v007-facades-visual-only/1','status':'MODEL_EXPORTED_RELOADED_NOT_WEBGL_VERIFIED',
    'source':{'path':'assets/v005_east_facades.glb','sha256':SOURCE_SHA,'bytes':source.stat().st_size},
    'model':{'path':'assets/v007_east_facades.glb','sha256':sha(dst),'bytes':dst.stat().st_size},
    'mesh_count':len(scene.geometry),'total_triangles':int(sum(len(g.faces) for g in reread.geometry.values())),
    'unchanged_mesh_geometry_except_noren':True,'noren_max_displacement_m':float(delta.max()),
    'collision_changed':False,'route_changed':False,'new_buildings':0,'new_interiors':0,
    'visual_changes':'low-contrast authored material factors + 4 procedurally generated timber textures + 3 original muted limewash textures + restrained noren folds',
    'material_records':mat_records, 'authenticity':'artist-estimated, no site survey, no published photos embedded',
    'webgl2':'NOT_VERIFIED','android':'NOT_VERIFIED','blender_native':'NOT_EXECUTED'}
 (outdir/'v007_facade_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 return report

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('v006_dist',type=Path);ap.add_argument('v007_output',type=Path);args=ap.parse_args()
 r=refine(args.v006_dist,args.v007_output);print(json.dumps({k:r[k] for k in ['status','mesh_count','total_triangles','noren_max_displacement_m','model']},ensure_ascii=False))