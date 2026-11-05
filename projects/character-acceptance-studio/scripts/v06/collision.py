"""Bounded triangle-crossing diagnostics, not cloth simulation/full-body solid collision certification."""
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

def regions(obj):
 me=obj.data;me.calc_loop_triangles();weighted=lambda v,key:sum(g.weight for g in v.groups if key in obj.vertex_groups[g.group].name)
 skirt={v.index for v in me.vertices if weighted(v,'Skirt')>.01};cloth=[tuple(f.vertices) for f in me.loop_triangles if f.material_index==1 and any(i in skirt for i in f.vertices)];legs=[tuple(f.vertices) for f in me.loop_triangles if f.material_index==0 and all(.28<me.vertices[i].co.z<.78 for i in f.vertices)];hands={}
 for s in ['L','R']:
  total={v.index for v in me.vertices if any(weighted(v,'J_Bip_'+s+'_'+part)>.01 for part in ['Hand','Index','Middle','Ring','Little','Thumb'])};tris=[tuple(f.vertices) for f in me.loop_triangles if f.material_index==0 and all(i in total for i in f.vertices)];hands[s]=tris
 skin_hands={};nails={}
 for side,tris in hands.items():
  parent={i:i for t in tris for i in t}
  def find(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  def union(a,b):parent[find(a)]=find(b)
  positions={}
  for i in parent:
   key=tuple(round(x,6) for x in me.vertices[i].co)
   if key in positions:union(i,positions[key])
   else:positions[key]=i
  for t in tris:union(t[0],t[1]);union(t[1],t[2])
  groups={}
  for i in parent:groups.setdefault(find(i),set()).add(i)
  nail_ids=set();pieces=[]
  for ids in groups.values():
   names={obj.vertex_groups[g.group].name for i in ids for g in me.vertices[i].groups if g.weight>.00001}
   if len(ids)==32 and len(names)==1 and next(iter(names)).endswith('3'):
    nail_ids.update(ids);pieces.append({'bone':next(iter(names)),'vertices':sorted(ids)})
  nails[side]=pieces;skin_hands[side]=[t for t in tris if not any(i in nail_ids for i in t)]
 return {'cloth_vertices':sorted(skirt),'cloth_triangles':cloth,'leg_triangles':legs,'hand_triangles_all':hands,'hand_triangles':skin_hands,'original_isolated_nail_components':nails}

def proper_cross(v,a,b):
 if set(a)&set(b):return False
 # UV/normal seams may duplicate vertex IDs at the same physical point. Do not count those as self crossings.
 if any((v[i]-v[j]).length_squared<1e-12 for i in a for j in b):return False
 for first,second in [(a,b),(b,a)]:
  tri=[v[i] for i in second]
  for j in range(3):
   p,q=v[first[j]],v[first[(j+1)%3]];d=q-p
   if d.length_squared<1e-14:continue
   hit=intersect_ray_tri(*tri,d,p,True)
   if hit is not None and 1e-5<(hit-p).dot(d)/d.length_squared<1-1e-5:return True
 return False

def crossings(v,first,second=None):
 self_test=second is None;second=first if self_test else second;a=BVHTree.FromPolygons(v,first,all_triangles=True);b=a if self_test else BVHTree.FromPolygons(v,second,all_triangles=True);return [(i,j) for i,j in a.overlap(b) if (not self_test or i<j) and proper_cross(v,first[i],second[j])]
