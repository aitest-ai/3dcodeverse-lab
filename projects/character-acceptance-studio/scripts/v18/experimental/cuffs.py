"""Subdivide only the two audited 12-edge cuff openings; retain all original vertices."""
import bmesh,collections
from mathutils import Vector
def subdivide(o):
 me=o.data;me.calc_loop_triangles();count=len(me.vertices);rest=[v.co.copy() for v in me.vertices];shapes={k.name:[v.co.copy() for v in k.data] for k in me.shape_keys.key_blocks};weld={};represent={};cloth=[t for t in me.loop_triangles if t.material_index!=0];ids={i for t in cloth for i in t.vertices}
 for i in ids:weld[i]=represent.setdefault(tuple(round(x,6) for x in rest[i]),i)
 edges=collections.Counter()
 for t in cloth:
  a,b,c=[weld[i] for i in t.vertices]
  for x,y in [(a,b),(b,c),(c,a)]:edges[tuple(sorted((x,y)))]+=1
 adj=collections.defaultdict(set)
 for (a,b),n in edges.items():
  if n==1:adj[a].add(b);adj[b].add(a)
 seen=set();loops=[]
 for start in sorted(adj):
  if start in seen:continue
  pending=[start];component=set()
  while pending:
   i=pending.pop()
   if i in component:continue
   component.add(i);pending.extend(adj[i]-component)
  seen.update(component);center=sum((rest[i] for i in component),Vector())/len(component)
  if len(component)==12 and abs(center.x)>.35 and center.z>.9:
   assert all(len(adj[i])==2 for i in component);loops.append(component)
 assert len(loops)==2
 boundary={tuple(sorted((a,b))) for loop in loops for a in loop for b in adj[a]};bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();original=list(bm.verts);original_indices={v:i for i,v in enumerate(original)};selected=[];edge_info=[]
 for e in bm.edges:
  a,b=[v.index for v in e.verts]
  if a not in weld or b not in weld or tuple(sorted((weld[a],weld[b]))) not in boundary:continue
  pa,pb=weld[a],weld[b];prev=next(i for i in adj[pa] if i!=pb);nxt=next(i for i in adj[pb] if i!=pa);mid=(rest[a]+rest[b])*.5;target=(rest[a]+rest[b])*(9/16)-(rest[prev]+rest[nxt])*(1/16);selected.append(e);edge_info.append({'ends':[a,b],'mid':mid,'target':target})
 print('cuffs','edges',len(selected),'shapelayers',list(bm.verts.layers.shape.keys()),flush=True)
 bmesh.ops.subdivide_edges(bm,edges=selected,cuts=1,use_grid_fill=False,smooth=0)
 bm.verts.index_update();new=[v for v in bm.verts if v.index>=count];mapping=[]
 for v in new:
  edge=min(edge_info,key=lambda e:(v.co-e['mid']).length_squared);assert (v.co-edge['mid']).length<1e-6,(len(new),v.index,list(v.co),(v.co-edge['mid']).length,list(edge['mid']));delta=edge['target']-v.co;v.co+=delta
  for layer in bm.verts.layers.shape.values():v[layer]+=delta
  mapping.append({'vertex':v.index,'parents':edge['ends'],'curvature_offset_m':list(delta)})
 bm.to_mesh(me);bm.free();me.update();assert len(me.vertices)==count+24;assert all((me.vertices[i].co-rest[i]).length<1e-8 for i in range(count));assert all(len(k.data)==len(me.vertices) for k in me.shape_keys.key_blocks)
 for k in me.shape_keys.key_blocks:assert all((k.data[i].co-shapes[k.name][i]).length<1e-8 for i in range(count)),k.name
 print('cuffs','new',len(mapping),'shape lengths',[(k.name,len(k.data)) for k in me.shape_keys.key_blocks], 'new weights max',max(len(me.vertices[x['vertex']].groups) for x in mapping),flush=True)
 return {'old_vertices':count,'new_vertices':len(me.vertices),'new_vertex_mapping':mapping,'cuff_segments_before':12,'cuff_segments_after':24}
