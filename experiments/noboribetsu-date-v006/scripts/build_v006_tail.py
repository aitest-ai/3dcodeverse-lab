#!/usr/bin/env python3
"""V006 R1: append final two vertices of frozen V002 OSM main-path route.

Author-estimated 6m road only; no new building identities or claims of surveyed surfaces.
Writes separate model/collision/manifest, never modifies V005 assets. Requires numpy/scipy/trimesh.
"""
from pathlib import Path
import hashlib,json,math,os,random
import numpy as np
from scipy.spatial import cKDTree
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals

ROOT=Path(os.environ.get('DATE_V006_ROOT', Path(__file__).resolve().parent.parent)).resolve()
DIST=ROOT/'dist'; ASSETS=DIST/'assets'
ORIG=ROOT/'baseline/scene_view_v005.json'
SCENE=ROOT/'baseline/scene_geometry.json'
EXPECTED_SCENE='75d672d5296ac28bef25b03423da395027c4b29cf804652239f40e9fc73d408a'
if hashlib.sha256(SCENE.read_bytes()).hexdigest()!=EXPECTED_SCENE: raise RuntimeError('V002 geometry hash mismatch')
base=json.loads(ORIG.read_text()); source=json.loads(SCENE.read_text())
assert base['version']=='V005-east-candidate-r1'
assert len(source['raw_osm_route_enu'])>=8
assert math.dist([base['route'][-1][q] for q in ('x','z')],[source['raw_osm_route_enu'][5][0],-source['raw_osm_route_enu'][5][1]])<.001
assert abs(base['route'][-1]['s']-197.72393408812707)<1e-6

DEM=np.asarray(source['terrain']['vertices'],dtype=np.float64)
F=np.asarray(source['terrain']['triangles'],dtype=np.int32)
TREE=cKDTree(DEM[F][:,:,:2].mean(axis=1))
def height(x,z):
    _,ids=TREE.query((x,-z),k=min(100,len(F)))
    for j in np.atleast_1d(ids):
        a,b,c=DEM[F[int(j)]];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-12:continue
        u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(-z-c[1]))/den
        v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(-z-c[1]))/den
        w=1-u-v
        if min(u,v,w)>-1e-7:return float(u*a[2]+v*b[2]+w*c[2])
    raise ValueError(f'V002 DEM not covering x={x}, z={z}')

# Interpolate the last two OSM centerline legs (NOT a direct shortcut or new surveyed path).
raw=source['raw_osm_route_enu']
turns=[(p[0],-p[1]) for p in raw[5:8]]
vec=[np.array(v,dtype=float) for v in turns]
segments=[];positions=[]
for k,(a,b) in enumerate(zip(vec,vec[1:])):
    L=float(np.linalg.norm(b-a)); n=math.ceil(L/.42)
    segments.append({'start_enu':raw[5+k],'end_enu':raw[6+k],'length_m':L,'sections':n})
    for i in range(n+1):
        if k and i==0:continue
        t=i/n
        positions.append(a+(b-a)*t)

# Mitered transverse sections prevent open wedges on the sharp second bend.
centers=np.asarray(positions);count=len(centers)
assert count>60
normals=[];transverse=[];route=list(base['route']);offsets=[-3.,-2.,-1.,0.,1.,2.,3.]
for i,c in enumerate(centers):
    pre=centers[max(i-1,0)];nxt=centers[min(i+1,count-1)]
    u1=c-pre if i>0 else nxt-c
    u2=nxt-c if i<count-1 else c-pre
    u1=u1/np.linalg.norm(u1);u2=u2/np.linalg.norm(u2)
    n1=np.array([-u1[1],u1[0]]);n2=np.array([-u2[1],u2[0]])
    m=n1+n2; m/=np.linalg.norm(m)
    m=m/max(.65,float(np.dot(m,n1)))
    normals.append(m)
    strip=[height(*(c+m*v)) for v in offsets]
    transverse.append(strip)
    y=height(*c) if i>0 else base['route'][-1]['y']
    if i>0:
        d=float(np.linalg.norm(c-centers[i-1]))
        route.append({'x':float(c[0]),'y':y,'z':float(c[1]),'s':route[-1]['s']+d})
assert 230<route[-1]['s']<235

rnd=random.Random(2026110106)
verts=[];mat_faces={'V006_road_earth':[],'V006_gravel_edge':[],'V006_aged_stones':[]}
def face(mat,points):
    idx=len(verts);verts.extend(points)
    mat_faces[mat].extend(((idx,idx+1,idx+2),(idx,idx+2,idx+3)))
# Mesh surfaces and DEM-barycentric collision use identical x/z, differing only by render clearance.
walk_v=[];walk_f=[]
for i in range(count-1):
    corners=[];coll=[]
    for j in (i,i+1):
        c=centers[j];n=normals[j]
        vtx=[]
        for v in offsets:
            q=c+n*v
            h=transverse[j][offsets.index(v)]
            vtx.append((float(q[0]),max(h,route[-(count-j)]['y']-.4)+.042,float(q[1])))
        corners.append(vtx)
        # Collision uses centerline DEM cross-profile for coherent stepping.
        l=height(*(c+n*3));r=height(*(c-n*3));
        coll.append([(float((c+n*3)[0]),l,float((c+n*3)[1])),(float((c-n*3)[0]),r,float((c-n*3)[1]))])
    for k in range(len(offsets)-1):
        # Road faces double-sided only in the shader; triangles remain single count here.
        face('V006_road_earth',(corners[0][k],corners[0][k+1],corners[1][k+1],corners[1][k]))
    for k in (0,len(offsets)-2):
        # Low-contrast edge strips, author's visual interpretation, never called a curb/drain.
        p=corners[0][k];q=corners[0][k+1];s=corners[1][k+1];t=corners[1][k]
        p=(p[0],p[1]+.008,p[2]);q=(q[0],q[1]+.008,q[2]);s=(s[0],s[1]+.008,s[2]);t=(t[0],t[1]+.008,t[2])
        face('V006_gravel_edge',(p,q,s,t))
    k=len(walk_v);walk_v.extend((coll[0][0],coll[0][1],coll[1][0],coll[1][1]));walk_f.extend(((k,k+1,k+2),(k+2,k+1,k+3)))

# Physical GLB groups stay separated for editing. Do not create decorative unverified buildings.
material_rgba={'V006_road_earth':([94,88,80,255],.98),'V006_gravel_edge':([104,99,87,255],.96),'V006_aged_stones':([111,105,94,255],.98)}
model=trimesh.Scene();stats={}
for key,ff in mat_faces.items():
    if not ff:continue
    # Each output geometry owns only the vertices that its triangles need.
    indices=np.asarray(ff,dtype=np.int64)
    used,inv=np.unique(indices,return_inverse=True)
    vv=np.asarray(verts,dtype=np.float32)[used]; mesh=trimesh.Trimesh(vertices=vv,faces=inv.reshape(-1,3),process=False)
    rgba,rough=material_rgba[key]
    mesh.visual=TextureVisuals(material=PBRMaterial(name=key,baseColorFactor=rgba,metallicFactor=0,roughnessFactor=rough,doubleSided=True))
    model.add_geometry(mesh,geom_name=key,node_name=key)
    stats[key]={'triangles':len(mesh.faces),'vertices':len(mesh.vertices)}
ASSETS.mkdir(parents=True,exist_ok=True)
name='v006_tail_road.glb'; p=ASSETS/name;p.write_bytes(model.export(file_type='glb'))
again=trimesh.load(p,force='scene',process=False)
if sum(len(m.faces) for m in again.geometry.values())!=sum(x['triangles'] for x in stats.values()):raise RuntimeError('GLB read-back geometry mismatch')

collision={'schema':'noboribetsu-date-v006-final-frozen-osm-path/1','axes':'Three EUS','walkable':[{'id':'V006_OSM_tail_legs_6_7','stage':'both','vertices':walk_v,'triangles':walk_f,'source':'Frozen V002 OSM last two main-path legs; V002 GSI DEM cross sections; width 6m is estimated'}],'obstacles':[],'not_surveyed':True}
(DIST/'v006_collision.json').write_text(json.dumps(collision,ensure_ascii=False,separators=(',',':'))+'\n')
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
model_info={name:{'path':'assets/'+name,'bytes':p.stat().st_size,'sha256':sha(p)}}
manifest={'schema':'noboribetsu-date-v006-tail/1','base_version':'V005-east-candidate-r1','version':'V006-tail-candidate-r1','status':'SOURCE_AND_COLLISION_QA_ONLY',
 'previous_route_end_m':base['route'][-1]['s'],'route_end_m':route[-1]['s'],'added_length_m':route[-1]['s']-base['route'][-1]['s'],
 'last_osm_waypoints_enu':raw[5:8],'osm_segments':segments,'unidentified_new_buildings':0,'new_buildings':0,
 'model':model_info[name],'geometry':stats,'collision':{'path':'v006_collision.json','sha256':sha(DIST/'v006_collision.json'),'triangles':len(walk_f)},
 'provenance':{'OSM':'OpenStreetMap © contributors, ODbL, frozen 2026-10-31 V002','elevations':'Frozen V002 GSI DEM, visual-only; road width unknown and assumed 6 m','new_structure':'none','site_photos':'not redistributed'},
 'Blender_native':'NOT_RUN','Three_js_webgl2':'NOT_VERIFIED','Android':'NOT_VERIFIED','private_preview':'UNCHANGED'}
(DIST/'v006_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
view=json.loads(ORIG.read_text());view['version']='V006-tail-candidate-r1';view['base_version']='V005-east-candidate-r1';view['route']=route
view['extension_v006']={'manifest':'v006_manifest.json','collision':'v006_collision.json','model':model_info[name], 'status':'last two frozen OSM legs only; no confirmed new building footprints'}
view['scope']='V005 preserved; continuous route to final two frozen V002 OSM waypoints; DEM-aligned visual road only'
(DIST/'scene_view.json').write_text(json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n')
qa={'status':'CANDIDATE_NON_BROWSER','route_previous_m':base['route'][-1]['s'],'route_end_m':route[-1]['s'],'added_m':route[-1]['s']-base['route'][-1]['s'],'route_points':len(route),'triangles':stats,'collision_triangles':len(walk_f),'new_buildings':0,'model':model_info[name]}
(DIST/'v006_build_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(qa,ensure_ascii=False,indent=2))