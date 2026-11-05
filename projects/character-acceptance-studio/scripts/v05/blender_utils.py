import bpy,math,json,struct
from mathutils import Matrix,Vector,Quaternion
from .overlay import read
B=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)));G=B.inverted()
def trs(m):
 p,q,s=m.decompose();return {'translation':list(p),'rotation':[q.x,q.y,q.z,q.w],'scale':list(s)}
def local_matrix(n):
 if 'matrix' in n:return Matrix([n['matrix'][i:i+4] for i in range(0,16,4)]).transposed()
 p=Vector(n.get('translation',[0,0,0]));r=n.get('rotation',[0,0,0,1]);q=Quaternion((r[3],r[0],r[1],r[2]));return Matrix.LocRotScale(p,q,Vector(n.get('scale',[1,1,1])))
def rest_graph(doc):
 nodes=doc['nodes'];parent={c:i for i,n in enumerate(nodes) for c in n.get('children',[])};world={}
 def get(i):
  if i not in world:world[i]=(get(parent[i]) if i in parent else Matrix.Identity(4))@local_matrix(nodes[i])
  return world[i]
 for i in range(len(nodes)):get(i)
 return parent,{i:B@m@G for i,m in world.items()}
class Capture:
 def __init__(self,rig,source):
  self.rig=rig;self.doc,binary=read(source);self.parents,self.rest=rest_graph(self.doc)
  # Node defaults can be a posed frame (native Shiba is); bind matrices, not node defaults, define skin rest space.
  for skin in self.doc.get('skins',[]):
   if 'inverseBindMatrices' not in skin:continue
   a=self.doc['accessors'][skin['inverseBindMatrices']];v=self.doc['bufferViews'][a['bufferView']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',64)
   for j,i in enumerate(skin['joints']):
    m=Matrix([list(struct.unpack_from('<4f',binary,offset+j*stride+k*16)) for k in range(4)]).transposed().inverted();self.rest[i]=B@m@G
  self.map={i:n['name'] for i,n in enumerate(self.doc['nodes']) if n.get('name') in rig.pose.bones};self.wrapper=len(self.doc['nodes'])
 def frame(self,rootmatrix):
  posed={};rig=self.rig
  def get(i):
   if i not in posed:
    if i in self.map:
     pb=rig.pose.bones[self.map[i]];posed[i]=pb.matrix@pb.bone.matrix_local.inverted()@self.rest[i]
    else:posed[i]=(get(self.parents[i]) if i in self.parents else Matrix.Identity(4))@B@local_matrix(self.doc['nodes'][i])@G
   return posed[i]
  out={}
  for i in self.map:
   m=(get(self.parents[i]).inverted() if i in self.parents else Matrix.Identity(4))@get(i);out[i]=trs(G@m@B)
  out[self.wrapper]=trs(G@rootmatrix@B);return out

def bone_world(rig,n):return rig.matrix_world@rig.pose.bones[n].matrix
def set_world(rig,n,m):rig.pose.bones[n].matrix=rig.matrix_world.inverted()@m;bpy.context.view_layer.update()
def set_q(rig,n,q):
 m=bone_world(rig,n);set_world(rig,n,Matrix.LocRotScale(m.translation,q,m.to_scale()))
def vertices(obj):
 ob=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ob.to_mesh();out=[ob.matrix_world@v.co for v in me.vertices];ob.to_mesh_clear();return out

def pose_basis(rig):
 result={}
 for p in rig.pose.bones:
  kw={'parent_matrix':p.parent.matrix,'parent_matrix_local':p.parent.bone.matrix_local} if p.parent else {};m=p.bone.convert_local_to_pose(p.matrix,p.bone.matrix_local,invert=True,**kw);loc,q,s=m.decompose();result[p.name]={'p':list(loc),'q':list(q),'s':list(s)}
 return result

def restore_basis(rig,frame):
 for n,d in frame.items():p=rig.pose.bones[n];p.rotation_mode='QUATERNION';p.location=d['p'];p.rotation_quaternion=d['q'];p.scale=d['s']
 bpy.context.view_layer.update()

def bake_actions(rig,root,clips,fps=60):
 rig.animation_data_clear();root.animation_data_clear()
 for p in rig.pose.bones:
  for c in list(p.constraints):p.constraints.remove(c)
 for a in list(bpy.data.actions):bpy.data.actions.remove(a)
 rig.animation_data_create();root.animation_data_create();actions=[]
 for name,data in clips.items():
  a=bpy.data.actions.new(name);r=bpy.data.actions.new(name+'_Root');a.use_fake_user=r.use_fake_user=True;rig.animation_data.action=a;root.animation_data.action=r
  for i,f in enumerate(data):
   restore_basis(rig,f['bones']);root.location=f['root']['p'];root.rotation_mode='QUATERNION';root.rotation_quaternion=f['root']['q'];root.scale=f['root']['s']
   for p in rig.pose.bones:
    for k in ['location','rotation_quaternion','scale']:p.keyframe_insert(data_path=k,frame=i,group=p.name)
   for k in ['location','rotation_quaternion','scale']:root.keyframe_insert(data_path=k,frame=i)
  for action in [a,r]:
   for layer in action.layers:
    for strip in layer.strips:
     for bag in strip.channelbags:
      for fc in bag.fcurves:
       for kp in fc.keyframe_points:kp.interpolation='LINEAR'
  rig.animation_data.action=root.animation_data.action=None;actions.append((name,a,r))
 for name,a,r in actions:
  for ob,action in [(rig,a),(root,r)]:
   tr=ob.animation_data.nla_tracks.new();tr.name=name;tr.mute=name!='Idle';st=tr.strips.new(name,0,action)
   if action.slots:st.action_slot=action.slots[0]
 bpy.context.scene.render.fps=fps;bpy.context.scene.frame_set(0)

def sync_runtime_weights(obj,rig,source,mesh_index,identity=False):
 """Repair an EDITABLE COPY to exactly match source GLB weights; source GLB and native master stay immutable.
 Blender's VRM import can overwrite duplicate joint entries rather than summing them; native animal masters can
 have >4 influences while their original runtime GLB has four. This makes the solved surface equal the runtime.
 """
 from mathutils.kdtree import KDTree
 d,b=read(source);mesh=d['meshes'][mesh_index];skin=d['skins'][next(n['skin'] for n in d['nodes'] if n.get('mesh')==mesh_index and 'skin' in n)]
 def values(index):
  a=d['accessors'][index];v=d['bufferViews'][a['bufferView']];count={'VEC3':3,'VEC4':4}[a['type']];fmt={5121:'B',5123:'H',5126:'f'}[a['componentType']];size=struct.calcsize(fmt)*count;start=v.get('byteOffset',0)+a.get('byteOffset',0);step=v.get('byteStride',size)
  return [struct.unpack_from('<'+str(count)+fmt,b,start+i*step) for i in range(a['count'])]
 tree=KDTree(len(obj.data.vertices))
 for v in obj.data.vertices:tree.insert(obj.matrix_world@v.co,v.index)
 tree.balance();expected={};maps=[];maxerror=0;conflicts=0;duplicate=0
 for pi,primitive in enumerate(mesh['primitives']):
  attr=primitive['attributes'];positions=values(attr['POSITION']);groups=[(values(attr['JOINTS_'+str(k)]),values(attr['WEIGHTS_'+str(k)])) for k in [0,1] if 'JOINTS_'+str(k) in attr];ids=[]
  for j,pos in enumerate(positions):
   if identity:
    assert len(positions)==len(obj.data.vertices);i=j
   else:
    _,i,dist=tree.find(Vector((pos[0],-pos[2],pos[1])));maxerror=max(maxerror,dist)
   ids.append(i);weights={}
   for joints,ws in groups:
    for joint,w in zip(joints[j],ws[j]):
     if w<=0:continue
     name=d['nodes'][skin['joints'][joint]]['name'];duplicate+=int(name in weights);weights[name]=weights.get(name,0)+w
   if i in expected:
    if any(abs(weights.get(k,0)-expected[i].get(k,0))>1e-6 for k in set(weights)|set(expected[i])):conflicts+=1
   else:expected[i]=weights
  maps.append({'mesh_name':'Cube'+('_'+str(pi) if pi else '') if not identity else 'Bodybaked','native_ids':ids})
 assert maxerror<1e-5 and conflicts==0,(maxerror,conflicts)
 changed=0;maximum=0
 for i,weights in expected.items():
  old={obj.vertex_groups[g.group].name:g.weight for g in obj.data.vertices[i].groups if obj.vertex_groups[g.group].name in rig.data.bones};error=max([abs(weights.get(k,0)-old.get(k,0)) for k in set(weights)|set(old)] or [0]);maximum=max(maximum,error);changed+=int(error>1e-6)
  for n in old:obj.vertex_groups[n].remove([i])
  for n,w in weights.items():
   g=obj.vertex_groups.get(n) or obj.vertex_groups.new(name=n);g.add([i],w,'REPLACE')
 bpy.context.view_layer.update();return {'edited_copy_vertices_changed':changed,'maximum_weight_difference':maximum,'duplicate_joint_entries_summed_in_original_primitives':duplicate,'source_runtime_weight_bytes':'unchanged','native_master':'unchanged','rest_mapping_max_error':maxerror,'maps':maps}
