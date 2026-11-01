#!/usr/bin/env python3
"""V009 Utsuroi-kan non-destructive corrective exterior candidate.

Rebuild from frozen V008 GLB.  Remove ONLY the 20 wall-side repeated grids by
exact V005 box detection, replacing them with restrained weatherboards and
spaced posts. No unverified windows, dimensions, roof or interior are claimed.
No external photos/textures are bundled. Official use reference: edo-trip.jp.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np,trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals

BASE_SHA='ff6725b1ecb22b455203c69dd4dd194f68c2b356ce17364ad89e09941d4ca4ea'
VIEW_VERSION='V008-structure-candidate-r1'
BID='way/283905580'
REFERENCE='https://edo-trip.jp/facility/utsuroi-kan/'

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def geom_frame(view,manifestpath:Path):
 b=next(b for b in view['buildings'] if b['id']==BID)
 m=next(x for x in json.loads(manifestpath.read_text())['known_buildings'] if x['osm_id']==BID)
 idx=m['basis']['front_edge']; poly=np.array([(x,-north) for x,north in b['polygon']],float)
 a,c=poly[idx],poly[(idx+1)%len(poly)]
 mid=(a+c)/2;L=np.linalg.norm(c-a);u=(c-a)/L
 v=np.array([-u[1],u[0]])
 if np.dot(poly.mean(axis=0)-mid,v)<0:v=-v
 depth=max(np.dot(pt-mid,v) for pt in poly)
 assert abs(L-9.653519662452663)<1e-4 and abs(depth-8.671631647032438)<1e-4
 return mid,u,v,float(b['base']),L,depth

def coords(pts,mid,u,v):
 return (np.asarray(pts)[:,[0,2]]-mid)@np.column_stack((u,v))

def make_box(mid,u,v,s,t,y,width,depth,height):
 verts=[]
 for zz in (-1,1):
  for yy in (-1,1):
   for xx in (-1,1):
    p=mid+u*(s+xx*width/2)+v*(t+zz*depth/2)
    verts.append((p[0],y+yy*height/2,p[1]))
 # indices according to vertex order: 0(-,-,-),1(+,-,-),2(-,+,-),3(+,+,-) etc.
 faces=np.array([[0,2,3],[0,3,1], [4,5,7],[4,7,6], [0,1,5],[0,5,4], [2,6,7],[2,7,3], [0,4,6],[0,6,2], [1,3,7],[1,7,5]],dtype=np.int64)
 return trimesh.Trimesh(vertices=np.array(verts,dtype=np.float64),faces=faces,process=False)

def texture(parts,rgba,name):
 obj=trimesh.util.concatenate(parts)
 obj.visual=TextureVisuals(material=PBRMaterial(name=name,baseColorFactor=[*rgba,255],roughnessFactor=.96,metallicFactor=0.,doubleSided=True))
 return obj

def build(src:Path,viewpath:Path,out:Path):
 assert sha(src)==BASE_SHA, 'Frozen V008 model SHA mismatch'
 view=json.loads(viewpath.read_text());assert view['version']==VIEW_VERSION
 mid,u,v,Y,L,D=geom_frame(view,viewpath.with_name('v005_manifest.json'))
 source=trimesh.load(src,force='scene',process=False)
 assert len(source.geometry)==21
 frozen={n:(len(g.vertices),len(g.faces),g.vertices.copy(),g.faces.copy()) for n,g in source.geometry.items()}
 old=source.geometry['wood_structure']; verts=old.vertices;faces=old.faces
 assert len(verts)==1184 and len(faces)==1776
 assert len(verts)%8==0 and len(faces)%12==0
 keep_vertices=[];keep_faces=[];removed=[];retained=[]
 for i in range(len(verts)//8):
  bv=verts[8*i:8*i+8];bf=faces[12*i:12*i+12]
  if bf.min()<i*8 or bf.max()>=i*8+8:
   raise RuntimeError('Frozen V008 box mesh packing changed; refusing changes')
  loc=coords(bv,mid,u,v);cent=loc.mean(axis=0);extent=np.ptp(loc,axis=0)
  height=np.ptp(bv[:,1]);
  side_grid=(abs(abs(cent[0])-(L/2+.105))<.012 and .35<cent[1]<D-.28
             and abs(extent[0]-.15)<.006 and abs(extent[1]-.065)<.006
             and abs(height-4.42)<.006 and abs(bv[:,1].mean()-(Y+2.36))<.008)
  if side_grid:
   removed.append({'original_box':i,'side':'left' if cent[0]<0 else 'right','depth_m':round(float(cent[1]),4)})
   continue
  retained.append(i)
  n=len(keep_vertices)
  keep_vertices.extend(bv)
  keep_faces.extend(bf-i*8+n)
 assert len(removed)==20,(len(removed),removed)
 assert sorted(x['original_box'] for x in removed)==list(range(88,98))+list(range(101,111))
 assert len(retained)==128
 new_original=trimesh.Trimesh(vertices=np.asarray(keep_vertices),faces=np.asarray(keep_faces),process=False)
 new_original.visual=old.visual.copy()
 del source.geometry['wood_structure']
 source.add_geometry(new_original,geom_name='wood_structure',node_name='wood_structure')
 # Slightly reduced side spacing and smaller posts; lower side boards are surface-only.
 posts=[];a=[];b=[];sills=[]
 for side in [-1,1]:
  loc=side*(L/2+.103)
  for k in range(4):
   t=.30+(D-.6)*k/3
   # 4 structural posts per side rather than 10, completely within source wall envelope.
   posts.append(make_box(mid,u,v,loc,t,Y+2.63,.12,.13,4.05))
  for k in range(9):
   h=.79+.117*k
   # Never overstate weathering; two muted wood colors and very shallow relief.
   # For a side wall, U is wall thickness and V runs along the depth.
   m=make_box(mid,u,v,side*(L/2+.085),D/2,Y+h,.035,D-.21,.100)
   (a if (k+int(side>0))%3 else b).append(m)
  sills.append(make_box(mid,u,v,side*(L/2+.103),D/2,Y+1.85,.085,D-.18,.092))
 source.add_geometry(texture(posts,(76,57,43),'v009_utsuroi_spaced_side_posts'),geom_name='v009_utsuroi_spaced_side_posts')
 source.add_geometry(texture(a,(108,86,67),'v009_utsuroi_side_board_mid'),geom_name='v009_utsuroi_side_board_mid')
 source.add_geometry(texture(b,(95,76,58),'v009_utsuroi_side_board_dark'),geom_name='v009_utsuroi_side_board_dark')
 source.add_geometry(texture(sills,(78,60,46),'v009_utsuroi_side_sill'),geom_name='v009_utsuroi_side_sill')
 assert len(source.geometry)==25
 out.mkdir(parents=True,exist_ok=False)
 dst=out/'v009_utsuroi_facade.glb';dst.write_bytes(source.export(file_type='glb'))
 new=trimesh.load(dst,force='scene',process=False)
 assert len(new.geometry)==25
 # All source geometry other than the single deliberately repaired side-wood group remains bit-identical in coordinates.
 untouched={}
 for n,(nv,nf,v0,f0) in frozen.items():
  if n=='wood_structure':continue
  g=new.geometry[n]
  assert len(g.vertices)==nv and len(g.faces)==nf and np.array_equal(g.faces,f0) and np.allclose(g.vertices,v0,atol=8e-6),n
 # Match the kept boxes after glTF float32 round trip.
 newwood=new.geometry['wood_structure']
 assert len(newwood.faces)==1536 and len(newwood.vertices)==1024
 assert np.array_equal(newwood.faces,new_original.faces)
 assert np.allclose(newwood.vertices,new_original.vertices,atol=8e-6)
 for n,g in new.geometry.items():
  if not n.startswith('v009_'):continue
  p=coords(g.vertices,mid,u,v)
  assert np.max(np.abs(p[:,0]))<L/2+.25,n
  assert p[:,1].min()>=-.02 and p[:,1].max()<=D+.02,n
  assert g.vertices[:,1].min()>Y+.59 and g.vertices[:,1].max()<Y+4.81,n
 qa={'schema':'noboribetsu-v009-utsuroi-sidewall-candidate/1','status':'GLB_RELOADED_STRUCTURAL_REPAIR_VERIFIED',
     'base_v008_sha256':BASE_SHA,'glb_v009_sha256':sha(dst),'bytes':dst.stat().st_size,
     'known_location':'OSM way/283905580','facility_use':'costume photography and rental (official)',
     'exterior_photo':'No verified full-façade photograph; author-estimated side-wall treatment, NOT an as-built reconstruction',
     'external_reference':REFERENCE,
     'original_meshes':21,'original_triangles':sum(nf for nv,nf,v0,f0 in frozen.values()),
     'removed_triangles':len(removed)*12,'removed_side_grid_boxes':len(removed),
     'new_geometry':{n:{'triangles':len(g.faces),'vertices':len(g.vertices),'bounds':g.bounds.round(4).tolist()}
                     for n,g in new.geometry.items() if n.startswith('v009_')},
     'total_meshes':len(new.geometry),'total_triangles':sum(len(g.faces) for g in new.geometry.values()),
     'all_other_20_original_meshes_unchanged':True,
     'wood_structure_retained_box_count':len(retained),
     'route_changed':False,'collision_changed':False,'A_stage_changed':False,
     'waraji_original_geometry_unchanged':True,'waraji_v008_detail_geometry_unchanged':True,
     'blender_native_executed':False,'webgl2_verified':False,'android_verified':False}
 (out/'v009_model_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:qa[k] for k in ('status','original_triangles','removed_triangles','total_triangles','glb_v009_sha256')},ensure_ascii=False))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('v008_glb',type=Path);ap.add_argument('scene_view',type=Path);ap.add_argument('output_new_directory',type=Path);q=ap.parse_args()
 build(q.v008_glb,q.scene_view,q.output_new_directory)