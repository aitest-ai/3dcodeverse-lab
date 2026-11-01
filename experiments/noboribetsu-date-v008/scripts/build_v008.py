#!/usr/bin/env python3
"""Add non-destructive, author-estimated waraji-ya architectural detail on frozen V007 GLB.

Photo provenance: edo-trip.jp old official Waraji-ya photo uploaded 2018/04.
Structural cues only; 2025 refit means current sign/awning colors must NOT be assumed.
No third-party images or photo textures are put in the model.
"""
import argparse,hashlib,json,math, pathlib,random
import numpy as np,trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals

EXPECTED_SOURCE_SHA = '077e900be4a0591909625b7e1c7b2d8eaa441eb855717da0b9c6b87b7d90b34e'
REFERENCE_URL='https://edo-trip.jp/wp/wp-content/uploads/2018/04/f0272006b776b4fd294606a2d4a80622-800x600.jpg'
BID='way/283905573'

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def axes(view):
 b=next(x for x in view['buildings'] if x['id']==BID)
 poly=np.array([(x,-north) for x,north in b['polygon']],dtype=float)
 # Authoring V005 uses front edge 1, verified from frozen V005 manifest.
 i=1;a=poly[i];c=poly[(i+1)%len(poly)];mid=(a+c)*0.5
 u=(c-a)/np.linalg.norm(c-a);v=np.array([-u[1],u[0]])
 if np.dot(poly.mean(axis=0)-mid,v)<0:v=-v
 return mid,u,v,float(b['base']),float(np.linalg.norm(c-a))

def oriented_box(mid,u,v,center_u,center_v,y,width,depth,height):
 # Local axes: side runs across store, depth runs inside, y is up; no axis alignment assumption.
 verts=[]
 for yy in (-1,1):
  for vv in (-1,1):
   for uu in (-1,1):
    p=mid + u*(center_u+uu*width/2) +v*(center_v+vv*depth/2)
    verts.append((float(p[0]),float(y+yy*height/2),float(p[1])))
 # trimesh oriented local conventional box corners, compute convex hull for winding
 mesh=trimesh.Trimesh(vertices=np.array(verts),faces=trimesh.convex.convex_hull(np.array(verts)).faces,process=False)
 return mesh

def tinted_mesh(parts,hexcolor,name):
 m=trimesh.util.concatenate(parts)
 m.visual=TextureVisuals(material=PBRMaterial(name=name,baseColorFactor=[*hexcolor,255],roughnessFactor=.96,metallicFactor=0,doubleSided=True))
 return m

def main(src,viewpath,outdir):
 assert sha(src)==EXPECTED_SOURCE_SHA,'V007 authoritative GLB hash changed; fail closed'
 outdir.mkdir(parents=True,exist_ok=True)
 dst=outdir/'v008_waraji_architecture.glb'
 if dst.exists(): raise FileExistsError('Refusing to overwrite '+str(dst))
 srcscene=trimesh.load(src,force='scene',process=False)
 frozen={name:{'verts':len(g.vertices),'faces':len(g.faces),'bounds':np.array(g.bounds).tolist()} for name,g in srcscene.geometry.items()}
 assert len(frozen)==17
 view=json.loads(viewpath.read_text());mid,u,v,base,front_w=axes(view)
 # 2018 official photo backs a bright upper-story sash, exposed rafter tips, and stone edging.
 # All dimensions below are artist estimates; preserve existing V007 geo and route/collision.
 
 # 10 restrained off-white paper/window backing panels, placed BEHIND preserved upper wooden lattice.
 # Upper slat front plane ~ -0.42 m; old opaque black plane ~ -0.35 m. Use depth=-0.385 m to show sash through slats.
 inner=front_w-1.00;count=10;gap=.075;bw=(inner-(count-1)*gap)/count
 paper_a=[];paper_b=[]
 for i in range(count):
  s=-inner/2 + bw/2 + i*(bw+gap)
  p=oriented_box(mid,u,v,s,-.385,base+3.94,bw,.026,.70)
  (paper_a if i%2==0 else paper_b).append(p)
 for name,arr,rgb in [('v008_waraji_upper_paper_ochre',paper_a,(199,193,177)),('v008_waraji_upper_paper_cool',paper_b,(210,206,190))]:
  srcscene.add_geometry(tinted_mesh(arr,rgb,name),geom_name=name,node_name=name)
 # 20 exposed eave-bracket ends, close to upper roof line. Render only, not collision geometry.
 rafter=[];n=20
 for i in range(n):
  s=-front_w*.48 + i*(front_w*.96)/(n-1)
  rafter.append(oriented_box(mid,u,v,s,-.44,base+4.64,.09,.31,.14))
 srcscene.add_geometry(tinted_mesh(rafter,(175,169,151),'v008_waraji_eave_bracket_ends'),
                       geom_name='v008_waraji_eave_bracket_ends',node_name='v008_waraji_eave_bracket_ends')
 # 22 uneven, low-profile river stones along the INSIDE footprint edge, not in the walking center.
 rng=random.Random(20261101);stones=[]
 for i in range(22):
  s=-(front_w-.42)/2 +(front_w-.42)*(i+.5)/22+rng.uniform(-.022,.022)
  z=-.44+rng.uniform(-.012,.012)
  stone=trimesh.creation.icosphere(subdivisions=1,radius=1)
  stone.apply_scale((.17+rng.random()*.035,.11+rng.random()*.045,.085+rng.random()*.02))
  stone.apply_translation((mid[0]+u[0]*s+v[0]*z,base+.10,mid[1]+u[1]*s+v[1]*z))
  # trimesh spheres use x,y,z: y should be vertical; fix vertical/depth scaling explicitly
  vert=stone.vertices.copy()
  # above scaled y ~ 0.12, z ~0.09, acceptable low stone plinth
  stones.append(stone)
 srcscene.add_geometry(tinted_mesh(stones,(111,112,106),'v008_waraji_stone_toe'),
                       geom_name='v008_waraji_stone_toe',node_name='v008_waraji_stone_toe')
 glb=srcscene.export(file_type='glb');dst.write_bytes(glb)
 loaded=trimesh.load(dst,force='scene',process=False)
 assert len(loaded.geometry)==21,(len(loaded.geometry),list(loaded.geometry))
 for name,old in frozen.items():
  cur=loaded.geometry[name];orig=trimesh.load(src,force='scene',process=False).geometry[name]
  assert len(cur.vertices)==old['verts'] and len(cur.faces)==old['faces'],name
  assert np.allclose(cur.vertices,orig.vertices,atol=8e-6) and np.array_equal(cur.faces,orig.faces),name
 # New components must stay close to the original Waraji footprint, not Utsuroi or road tail.
 inv=np.column_stack((u,v))
 additions=[]
 for name,mesh in loaded.geometry.items():
  if not name.startswith('v008_'):continue
  q=(mesh.vertices[:,[0,2]]-mid)@inv
  assert np.max(np.abs(q[:,0]))<front_w/2+.25,name
  assert q[:,1].min()>-.9 and q[:,1].max()<.4,name
  assert mesh.vertices[:,1].min()>=base-.08 and mesh.vertices[:,1].max()<base+5.3,name
  additions.append({'name':name,'vertices':len(mesh.vertices),'triangles':len(mesh.faces),'bounds':mesh.bounds.round(4).tolist()})
 assert sum(x['triangles'] for x in additions)<10000
 report={'schema':'date-v008-photo-guided-structural-candidate/1','status':'REAL_GLB_EXPORTED_RELOADED_GEO_VERIFIED',
    'source_v007_sha256':EXPECTED_SOURCE_SHA,'v008_glb_sha256':sha(dst),'bytes':dst.stat().st_size,
    'original_mesh_count':len(frozen),'original_triangles':sum(g['faces'] for g in frozen.values()),
    'new_mesh_count':len(additions),'new_triangles':sum(a['triangles'] for a in additions),
    'total_triangles':sum(len(g.faces) for g in loaded.geometry.values()),'new_geometry':additions,
    'building_id':BID,'footprint_front_edge_m':front_w,'reference_url':REFERENCE_URL,
    'reference_age':'official image path /2018/04/; site imagery may be older than 2025 renovation',
    'reality_limit':'window backing, bracket spacing and stone sizes are author-estimated; not photogrammetry or verified 2026 color',
    'preservation':{'v007_geometry_unchanged':True,'v007_original_file_unchanged':True,'all_roads_unchanged':True,'collision_unchanged':True,'A_stage_unchanged':True},
    'blender_native':'not_run','webgl2':'not_tested','android':'not_tested'}
 (outdir/'v008_model_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:report[k] for k in ('status','bytes','original_triangles','new_triangles','total_triangles','v008_glb_sha256')},ensure_ascii=False))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('v007_glb',type=pathlib.Path);ap.add_argument('scene_view',type=pathlib.Path);ap.add_argument('outdir',type=pathlib.Path);a=ap.parse_args()
 main(a.v007_glb,a.scene_view,a.outdir)