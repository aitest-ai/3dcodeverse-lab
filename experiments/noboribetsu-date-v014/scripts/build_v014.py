#!/usr/bin/env python3
"""Produce optional, non-surveyed central stone inlay for V004 merchant street.

The existing V004/V005/V011–V013 models and collision files are read-only.
This does NOT claim historical paving alignment or dimensions.
Usage: python build_v014.py V013_RUNTIME_DIR output/v014_central_stone.json
"""
import sys,math,json,hashlib
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree

SCHEMA='noboribetsu-date-v014-v004-centre-stones/1'
RANGE=(89.5,124.5)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(rt,out):
 rt=Path(rt);dist=rt/'dist';out=Path(out)
 view=json.loads((dist/'scene_view.json').read_text());route=view['route']
 assert abs(route[-1]['s']-231.56641497226084)<.01
 assert 'transition_v013' in view and 'terrain_gap_v011' in view and 'transition_v012' in view
 roadfile=dist/'assets/v004_merchant_road.glb'
 scene=trimesh.load(roadfile,force='scene',process=False)
 assert set(['road_asphalt','stone_warm_grey','road_patinated_edge']).issubset(scene.geometry)
 stone=cKDTree(scene.geometry['stone_warm_grey'].vertices[:,[0,2]])
 patina=cKDTree(scene.geometry['road_patinated_edge'].vertices[:,[0,2]])
 road=cKDTree(scene.geometry['road_asphalt'].vertices[:,[0,2]])
 points=[p for p in route if 82.876<p['s']<130.015]
 def interp(s):
  for a,b in zip(points,points[1:]):
   if a['s']<=s<=b['s']:
    t=(s-a['s'])/(b['s']-a['s']);return np.array([a[k]*(1-t)+b[k]*t for k in ('x','y','z')])
  raise ValueError('Missing V004 centerline station '+str(s))
 verts=[];colors=[];indices=[];rejections=[];samples=[]
 # Gaps leave the original road visible; no full-length false ``historical ditch'' claim.
 stations=np.arange(90.0,124.0,0.69)
 for index,s in enumerate(stations):
  p=interp(float(s));fore=interp(float(s)+.18);back=interp(float(s)-.18)
  tangent=fore-back;tangent[1]=0;tangent/=np.linalg.norm(tangent)
  normal=np.array([-tangent[2],0,tangent[0]])
  # Individual stones are separated and subtly varied but kept within ~40cm.
  half_len=.255+(.018*math.sin(index*1.97))
  half_width=.188+(.012*math.sin(index*2.07+.8))
  lateral=.018*math.sin(index*.73)
  center=p+normal*lateral
  # Avoid previous curb/edge anywhere near the stones, and do not cross segment ends.
  if stone.query(center[[0,2]])[0]<.80 or patina.query(center[[0,2]])[0]<.80:
   rejections.append({'station':round(float(s),3),'why':'existing stone or patina too close'});continue
  # The old road is triangulated wide quads; its local centerline y is route y + 0.018m.
  # Put visual-only stones 1.1cm above that surface; never set a new collision height.
  corners=[]
  for ax,cx in [(-1,-1),(1,-1),(1,1),(-1,1)]:
   v=center+ax*half_len*tangent+cx*half_width*normal
   v[1]+=0.029
   corners.append(v)
  if any(not np.isfinite(c).all() for c in corners):raise ValueError('Nonfinite stone')
  off=len(verts)//3
  for c in corners:
   verts.extend([round(float(k),5) for k in c]);
   tint=.93+.055*(.5+.5*math.sin(index*1.61))
   # Subtle warm grey stone on charcoal road; each tile separate, no repeated texture pixels.
   colors.extend([round(.90*tint,4),round(.87*tint,4),round(.79*tint,4)])
  indices.extend([off,off+1,off+2,off,off+2,off+3]);samples.append(float(s))
 assert len(samples)>=35, f'Not enough isolated paving stones ({len(samples)})'
 obj={'schema':SCHEMA,'version':'V014-R1','stage':'B','visual_only':True,'collision_changed':False,
      'not_surveyed':True,'author_estimated':True,'asset_source':{'v004_road_sha256':sha(roadfile)},
      'coverage_m':[RANGE[0],RANGE[1]],'stone_count':len(samples),'triangles':len(indices)//3,
      'vertices':len(verts)//3,'positions':verts,'colors':colors,'indices':indices,
      'skipped_existing_curb':rejections,'unchanged':['V011 terrain gap','V012 edge','V013 selective shoulder','road/obstacle collision','A-stage','original V004 GLB'],
      'material':{'type':'MeshStandardMaterial','vertexColors':True,'roughness':.99,'metalness':0.0,'polygonOffset':True},
      'provenance':'Optional photo-informed centrally placed slab design study; no claim the exact real paving is here or this width'}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 qa={'stone_count':len(samples),'triangles':obj['triangles'],'vertices':obj['vertices'],'existing_stone_skipped':len(rejections),'min_old_stone_distance_m':min(stone.query(np.array(verts).reshape(-1,3)[:,[0,2]])[0]).item(), 'road_geometry_untouched':True,'collision_unchanged':True,'webgl_tested':False,'status':'SOURCE_GEOMETRY_PASS'}
 (out.parent/'V014_geometry_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(qa,ensure_ascii=False))
 return qa
if __name__=='__main__':run(*sys.argv[1:])