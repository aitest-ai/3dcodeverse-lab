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
 for im in sorted((im for im in bpy.data.images if im.name!='V18_Shoulder_Outline_Width'),key=lambda im:im.name):data['images'].append((im.name,None if im.packed_file else bpy.path.abspath(im.filepath),hashlib.sha256(im.packed_file.data).hexdigest() if im.packed_file else None))
 # matrix rows are mathutils.Vector; convert recursively via JSON default.
 return hashlib.sha256(json.dumps(data,sort_keys=True,default=lambda x:list(x)).encode()).hexdigest()

def state_signature():
 body=bpy.data.objects['Body'];geom=geometry_signature()
 uv=[(o.name,[(u.name,[list(p.uv) for p in u.data]) for u in o.data.uv_layers]) for o in bpy.data.objects if o.type=='MESH']
 actions=[]
 for a in sorted(bpy.data.actions,key=lambda x:x.name):
  for layer in a.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:actions.append((a.name,fc.data_path,fc.array_index,[(list(k.co),k.interpolation,list(k.handle_left),list(k.handle_right)) for k in fc.keyframe_points]))
 setup=[]
 for o in sorted(bpy.data.objects,key=lambda x:x.name):
  if o.constraints or (o.type=='ARMATURE' and any(b.constraints for b in o.pose.bones)) or (o.animation_data and o.animation_data.drivers):raise RuntimeError('Unsupported constraints/drivers')
  mods=[]
  for m in o.modifiers:
   props={}
   for p in m.bl_rna.properties:
    if p.is_readonly or p.identifier=='rna_type':continue
    v=getattr(m,p.identifier)
    if p.type in ['BOOLEAN','INT','FLOAT','STRING','ENUM']:props[p.identifier]=list(v) if getattr(p,'is_array',False) else sorted(v) if isinstance(v,set) else v
    elif p.type=='POINTER':props[p.identifier]=getattr(v,'name',None)
   mods.append((m.name,m.type,props))
  animation=[]
  for data in [o.animation_data,getattr(getattr(o.data,'shape_keys',None),'animation_data',None)]:
   if data:
    animation.append((data.action.name if data.action else None,[(t.name,t.mute,t.is_solo,[(s.name,s.action.name if s.action else None,s.frame_start,s.frame_end,s.action_frame_start,s.action_frame_end,s.scale,s.repeat,s.blend_type,s.extrapolation,s.mute,s.influence) for s in t.strips]) for t in data.nla_tracks]))
  setup.append((o.name,o.parent.name if o.parent else None,mods,animation))
 shape=body.data.shape_keys
 if shape.animation_data and shape.animation_data.drivers:raise RuntimeError('Unsupported shape drivers')
 return hashlib.sha256(json.dumps([geom,uv,actions,setup,bpy.context.scene.render.fps,bpy.context.scene.render.fps_base],sort_keys=True).encode()).hexdigest()
