"""Rebuild quarantined cuff trial; never adds it to the reusable catalog."""
import bpy,bmesh,sys,json,math,collections,os,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));OUT=Path(os.environ.get('STUDIO_V19_OUT',str(R/'experiments-v19')));OUT.mkdir(parents=True,exist_ok=True);assert not any(p.name!=".gitignore" for p in OUT.iterdir()), "Refuse existing experiment overwrite"
from v06.motion_overlay import MotionOverlay
from v18.experimental.body_export import append,values
from v05.blender_utils import B
from bootstrap_inputs_v19 import LOCK
rows=[]
for key,ver in [('vivi','0.6.0'),('vita','0.5.0')]:
 base=R/'inputs-v19/library-v18'/('vroid-'+key+'-motion-review')/ver;assert all(hashlib.sha256((base/n).read_bytes()).hexdigest()==sha for n,sha in LOCK['vroid-'+key+'-motion-review/'+ver].items());bpy.ops.wm.open_mainfile(filepath=str(base/'model.blend'));o=bpy.data.objects['Body'];me=o.data;me.calc_loop_triangles();rig=bpy.data.objects['Armature'];ov=MotionOverlay(base/'model.glb');oldN=[B.to_3x3()@Vector(n) for n in values(ov,ov.doc['meshes'][1]['primitives'][0]['attributes']['NORMAL'])];rest=[v.co.copy() for v in me.vertices];shapes={k.name:[v.co.copy() for v in k.data] for k in me.shape_keys.key_blocks};selected_faces=next(e['source_faces'] for e in json.loads((R/'docs/CUFF_SELECTION_V19.json').read_text())['entries'] if e['key']==key);source_faces=[(list(t.vertices),t.material_index,me.polygons[t.polygon_index].use_smooth) for t in me.loop_triangles]
 def point(i):return tuple(round(x,7) for x in rest[i])
 def ek(a,b):return tuple(sorted((point(a),point(b))))
 edgekeys={ek(t.vertices[j],t.vertices[(j+1)%3]) for t in me.loop_triangles if t.index in selected_faces for j in range(3)};normals=collections.defaultdict(list)
 for t in me.loop_triangles:
  if t.material_index==1:
   for i in t.vertices:normals[point(i)].append(oldN[i])
 avgN={p:sum(ns,Vector()).normalized() for p,ns in normals.items()};bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();count=len(rest);edges=[];info=[]
 for e in bm.edges:
  a,b=[v.index for v in e.verts]
  if ek(a,b) not in edgekeys or not any(f.material_index==1 for f in e.link_faces):continue
  mid=(rest[a]+rest[b])*.5;Na,Nb=avgN[point(a)],avgN[point(b)];delta=-.25*((mid-rest[a]).dot(Na)*Na+(mid-rest[b]).dot(Nb)*Nb)
  limit=min(.0025,.15*(rest[a]-rest[b]).length)
  if delta.length>limit:delta*=limit/delta.length
  edges.append(e);info.append({'parents':[a,b],'mid':mid,'delta':delta})
 bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=False,smooth=0);bm.verts.index_update();mapping=[]
 for v in bm.verts:
  if v.index<count:continue
  neighbors={e.other_vert(v).index for e in v.link_edges};candidates=[e for e in info if (v.co-e['mid']).length<1e-6 and set(e['parents'])<=neighbors];assert candidates
  # UV seams can yield identical midpoint positions; parent group/materials remain equivalent for spatial correction.
  e=candidates[0];delta=e['delta'];v.co+=delta
  for layer in bm.verts.layers.shape.values():v[layer]+=delta
  mapping.append({'vertex':v.index,'parents':e['parents'],'curvature_offset_m':list(delta)})
 uv_layer=bm.loops.layers.uv.active;uvs={loop.vert.index:loop[uv_layer].uv.copy() for f in bm.faces for loop in f.loops};edge_mid={tuple(sorted(r['parents'])):r['vertex'] for r in mapping};bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index==1],context='FACES_ONLY');bm.verts.ensure_lookup_table()
 for ids,material,smooth in source_faces:
  if material!=1:continue
  a,b,c=ids;ab,bc,ca=[edge_mid.get(tuple(sorted(e))) for e in [(a,b),(b,c),(c,a)]]
  if all(x is not None for x in [ab,bc,ca]):children=[[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]]
  elif all(x is None for x in [ab,bc,ca]):children=[ids]
  else:
   boundary=[]
   for i,mid in [(a,ab),(b,bc),(c,ca)]:
    boundary.append(i)
    if mid is not None:boundary.append(mid)
   pivot=next(i for i,v in enumerate(boundary) if v>=count);boundary=boundary[pivot:]+boundary[:pivot];children=[[boundary[0],boundary[j],boundary[j+1]] for j in range(1,len(boundary)-1)]
  for child in children:
   f=bm.faces.new([bm.verts[i] for i in child]);f.material_index=material;f.smooth=smooth
   for loop in f.loops:loop[uv_layer].uv=uvs[loop.vert.index]
 bmesh.ops.delete(bm,geom=[e for e in bm.edges if e.is_wire],context='EDGES');bm.verts.index_update()
 bm.to_mesh(me);bm.free();me.update();assert all((me.vertices[i].co-rest[i]).length<1e-8 for i in range(count));assert all(all((k.data[i].co-shapes[k.name][i]).length<1e-8 for i in range(count)) for k in me.shape_keys.key_blocks)
 normal_rows=oldN+[ (oldN[r['parents'][0]]+oldN[r['parents'][1]]).normalized() for r in sorted(mapping,key=lambda r:r['vertex'])];me.normals_split_custom_set_from_vertices(normal_rows)
 metadata={'status':'rejected-not-for-reuse','baseline_sha256':hashlib.sha256((base/'model.glb').read_bytes()).hexdigest(),'key':key,'old_vertices':count,'new_vertices':len(me.vertices),'new_vertex_mapping':mapping,'source_faces':selected_faces};rows.append(metadata);(OUT/'mapping.json').write_text(json.dumps(rows,indent=2)+'\n');meta=append(ov,o,mapping);sha=ov.save(OUT/(key+'-rejected.glb'));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(key+'-rejected.blend')),compress=True);print(key,'source faces',len(selected_faces),'added vertices',len(mapping),'max displacement',max(Vector(m['curvature_offset_m']).length for m in mapping),'sha',sha,flush=True)
