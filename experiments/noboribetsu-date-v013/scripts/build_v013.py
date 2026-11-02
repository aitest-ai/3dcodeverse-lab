#!/usr/bin/env python3
"""V013 only adds *non-surveyed* transparent shoulder color where old stone/edges are absent.

Usage: python build_v013.py V002_Complete.zip V012_runtime_dir output.json
Never modifies DEM, underlying roads, buildings or collisions.
"""
from pathlib import Path
import sys,json,hashlib,zipfile,math
import numpy as np
import trimesh
from scipy.spatial import cKDTree

SCHEMA='noboribetsu-date-v013-adaptive-merchant-shoulder/1'
SEGMENTS=[('V004',82.877,130.01465,'v004_merchant_road.glb','stone_warm_grey','v004_merchant_facades.glb'),
          ('V005',130.01465,197.72393408812707,'v005_east_road.glb','road_cobbles','v005_east_facades.glb')]
OFFSETS=(3.39,3.53,3.69,3.82)
PALETTE=((.33,.288,.212),(.336,.315,.238),(.304,.349,.267),(.305,.37,.295))
ALPHA=(.22,.21,.12,0.)

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read_v002(p):
 with zipfile.ZipFile(p) as z:
  files=[n for n in z.namelist() if n.endswith('/data/scene_geometry.json')]
  if len(files)!=1:raise ValueError('missing/ambiguous frozen geometry')
  return json.loads(z.read(files[0]))

def do(v002,rt,target):
 rt=Path(rt);dist=rt/'dist';target=Path(target)
 view=json.loads((dist/'scene_view.json').read_bytes());route=view['route']
 assert abs(route[-1]['s']-231.56641497226084)<.01 and len(route)==472
 assert 'transition_v012' in view and 'terrain_gap_v011' in view
 terrain=read_v002(v002)
 assert terrain['axes']=='Blender ENU; GLB EUS'
 elevations={(round(float(x),3),round(float(-y),3)):float(h) for x,y,h in terrain['terrain']['vertices']}
 def sample_dem(x,z):
  x0=2*math.floor(x/2);z0=2*math.floor(z/2);u=(x-x0)/2;v=(z-z0)/2
  hs=[elevations.get((float(xx),float(zz))) for xx,zz in ((x0,z0),(x0+2,z0),(x0,z0+2),(x0+2,z0+2))]
  if any(h is None for h in hs):return None
  return (1-u)*(1-v)*hs[0]+u*(1-v)*hs[1]+(1-u)*v*hs[2]+u*v*hs[3]
 parts=[];overall_pos=[];overall_colors=[];overall_idx=[];total_gap=0;max_height_diff=0
 for label,s_start,s_end,road_file,stone,facade_file in SEGMENTS:
  points=[p for p in route if s_start-1e-4<=p['s']<=s_end+1e-4]
  if len(points)<25:raise ValueError('incomplete merchant route '+label)
  road_path=dist/'assets'/road_file
  road=trimesh.load(road_path,force='scene',process=False)
  stone_tree=cKDTree(road.geometry[stone].vertices[:,[0,2]])
  patina_name=('road_patinated_edge' if label=='V004' else 'edge_patina')
  patina_tree=cKDTree(road.geometry[patina_name].vertices[:,[0,2]])
  fscene=trimesh.load(dist/'assets'/facade_file,force='scene',process=False)
  # Fixed architectural foundation is immutable. Do not overlay it with painted earth.
  foundation_names=['stone_foot','stone_warm_grey'] if label=='V004' else ['foundation_stone']
  fv=np.concatenate([fscene.geometry[n].vertices[:,[0,2]] for n in foundation_names if n in fscene.geometry],axis=0)
  foundation_tree=cKDTree(fv)
  series=[];rejections={k:0 for k in ('stone_edge','near_facade','steep_dem','no_dem','old_edge_overlap')}
  for i,p in enumerate(points):
   lo=points[max(0,i-1)];hi=points[min(len(points)-1,i+1)]
   dx=hi['x']-lo['x'];dz=hi['z']-lo['z'];mag=math.hypot(dx,dz)
   if mag<1e-9:raise ValueError('degenerate route station '+str(i))
   series.append((p,-dz/mag,dx/mag))
  accepted=[[],[]]
  for side_i,side in enumerate((-1,1)):
   for i,(p,nx,nz) in enumerate(series):
    inner=(p['x']+side*nx*OFFSETS[0],p['z']+side*nz*OFFSETS[0]);outer=(p['x']+side*nx*OFFSETS[-1],p['z']+side*nz*OFFSETS[-1]);near_old=(p['x']+side*nx*3.19,p['z']+side*nz*3.19)
    reason=None
    if stone_tree.query(inner)[0]<.14:reason='stone_edge'
    elif patina_tree.query(inner)[0]<.12:reason='old_edge_overlap'
    elif foundation_tree.query(outer)[0]<.26:reason='near_facade'
    vals=[]
    if not reason:
     for ring,off in enumerate(OFFSETS):
      wave=0 if ring==0 else (math.sin(i*.57+side*.8)*.008+math.sin(i*1.17+1.2)*.006)*min(ring,2)/2
      x=p['x']+side*nx*(off+wave);z=p['z']+side*nz*(off+wave)
      h=sample_dem(x,z)
      if h is None:reason='no_dem';break
      dev=abs(h-p['y']);max_height_diff=max(max_height_diff,dev)
      if dev>.35:reason='steep_dem';break
      t=ring/3
      y=p['y']*(1-t)+h*t+(.020-.006*t)
      vals.append((x,y,z))
    if reason:rejections[reason]+=1;accepted[side_i].append(None)
    else:accepted[side_i].append(vals)
  # Only connected neighboring stations survive. This leaves existing historical stone edging untouched.
  begin=len(overall_pos)//3;tri_before=len(overall_idx)//3;active_segments=0
  for side_i,side in enumerate((-1,1)):
   local_nodes={}
   for i,vals in enumerate(accepted[side_i]):
    if vals is None:continue
    local_nodes[i]=len(overall_pos)//3
    p=points[i];distance_to_limit=min(p['s']-s_start,s_end-p['s']);ramp=max(0.,min(1.,distance_to_limit/1.5))
    for ring,(x,y,z) in enumerate(vals):
     overall_pos.extend(round(float(w),5) for w in (x,y,z))
     mult=1+.025*math.sin(i*.37+ring*.8+side)
     overall_colors.extend([*[round(min(1.,color*mult),5) for color in PALETTE[ring]],round(ALPHA[ring]*ramp,5)])
   for i in range(len(points)-1):
    if i not in local_nodes or i+1 not in local_nodes:continue
    a=local_nodes[i];b=local_nodes[i+1];active_segments+=1
    for j in range(3):
     x=a+j;y=b+j
     if side==1:overall_idx.extend([x,y,x+1,y,y+1,x+1])
     else:overall_idx.extend([x,x+1,y,y,x+1,y+1])
  part={'section':label,'s_start':s_start,'s_end':s_end,'stations':len(points),'accepted_station_sides':sum(v is not None for ss in accepted for v in ss),'active_segment_sides':active_segments,'triangles':len(overall_idx)//3-tri_before,'vertices':len(overall_pos)//3-begin,'rejections':rejections,'source_road_sha256':digest(road_path),'preexisting_edge_materials':list(road.geometry.keys()),'skip_existing_stone':True}
  if part['triangles']<50:raise ValueError('Insufficient new visual shoulders '+label+' '+str(part))
  parts.append(part)
 patch={'schema':SCHEMA,'version':'V013-R1','stage':'B','collision_enabled':False,'author_estimated':True,'not_surveyed':True,'previous_v012_unchanged':True,'previous_v011_gap_unchanged':True,'parts':parts,'triangles':len(overall_idx)//3,'vertices':len(overall_pos)//3,'positions':overall_pos,'colors':overall_colors,'indices':overall_idx,'render_material':{'type':'MeshStandardMaterial','vertexColors':True,'transparent':True,'depthWrite':False,'side':'DoubleSide','roughness':1.0,'metalness':0.0},'description':'Selective low-alpha roadside soil/moss tint OUTSIDE preserved preexisting V004/V005 patinated and stone edge areas'}
 assert patch['triangles']>0 and patch['triangles']==len(overall_idx)//3
 target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(patch,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 qa={'schema':'noboribetsu-date-v013-source-geometry/1','status':'PASS_SOURCE_ONLY','triangle_count':patch['triangles'],'vertex_count':patch['vertices'],'section_checks':parts,'max_abs_terrain_height_difference_m':max_height_diff,'collision_changed':False,'v011_gap_changed':False,'webgl_tested':False}
 (target.parent/'V013_geometry_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(qa,ensure_ascii=False,indent=2))
 return qa

if __name__=='__main__':
 if len(sys.argv)!=4:raise SystemExit('Usage: build_v013.py V002_COMPLETE.zip V012_RUNTIME_DIR V013_PATCH.json')
 do(*sys.argv[1:])