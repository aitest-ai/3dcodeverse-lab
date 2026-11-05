import bpy,json,hashlib
def geometry_signature():
 def val(x):
  if isinstance(x,(str,int,float,bool)) or x is None:return x
  try:return list(x)
  except TypeError:return str(type(x))
 data={'meshes':[],'rigs':[],'materials':[],'images':[]}
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if o.type=='MESH':data['meshes'].append({'name':o.name,'matrix':list(o.matrix_basis),'vertices':[list(v.co) for v in o.data.vertices],'faces':[(list(p.vertices),p.material_index) for p in o.data.polygons],'groups':[g.name for g in o.vertex_groups],'weights':[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices],'shapes':{k.name:[list(v.co) for v in k.data] for k in o.data.shape_keys.key_blocks} if o.data.shape_keys else {},'materials':[m.name if m else None for m in o.data.materials]})
  if o.type=='ARMATURE':data['rigs'].append([(b.name,b.parent.name if b.parent else None,[list(r) for r in b.matrix_local],list(b.tail_local)) for b in o.data.bones])
 for m in sorted(bpy.data.materials,key=lambda m:m.name):
  nodes=[];links=[]
  if m.node_tree:
   nodes=[(n.name,n.type,[(i.name,val(i.default_value)) for i in n.inputs if hasattr(i,'default_value')],getattr(getattr(n,'image',None),'name',None)) for n in m.node_tree.nodes];links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]
  data['materials'].append((m.name,list(m.diffuse_color),nodes,links))
 for im in sorted(bpy.data.images,key=lambda im:im.name):data['images'].append((im.name,None if im.packed_file else bpy.path.abspath(im.filepath),hashlib.sha256(im.packed_file.data).hexdigest() if im.packed_file else None))
 # matrix rows are mathutils.Vector; convert recursively via JSON default.
 return hashlib.sha256(json.dumps(data,sort_keys=True,default=lambda x:list(x)).encode()).hexdigest()
