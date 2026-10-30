"""V19: fit an existing tucked waistband; preserve every non-pants buffer byte.
Requires numpy (included with Blender). No new faces, joints, weights or morphs.
"""
from __future__ import annotations
import copy, hashlib, json, struct
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

SOURCE_SHA256='6f492396c28469533a979897037f522182ccd3726643e29b83c58c02911c2384'

def quaternion_matrix(q):
    x,y,z,w=np.asarray(q,dtype=float)/np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                     [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                     [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])

class GLB:
    def __init__(self,path):
        self.path=Path(path);data=self.path.read_bytes()
        magic,version,total=struct.unpack_from('<4sII',data)
        if magic!=b'glTF' or version!=2 or total!=len(data):raise ValueError('Invalid GLB')
        length,kind=struct.unpack_from('<I4s',data,12)
        if kind!=b'JSON':raise ValueError('Missing JSON')
        self.doc=json.loads(data[20:20+length])
        binary_length,kind=struct.unpack_from('<I4s',data,20+length)
        if kind!=b'BIN\0':raise ValueError('Missing embedded binary')
        self.binary=bytearray(data[28+length:28+length+binary_length])
        self.original_binary=bytes(self.binary);self.original_doc=copy.deepcopy(self.doc)
        self.cache={};self.sha256=hashlib.sha256(data).hexdigest()
    def accessor(self,index):
        if index in self.cache:return self.cache[index]
        a=self.doc['accessors'][index]
        if 'sparse' in a or 'bufferView' not in a:raise ValueError('Unsupported requested sparse accessor')
        view=self.doc['bufferViews'][a['bufferView']]
        dt=np.dtype({5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']])
        width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
        stride=view.get('byteStride',width*dt.itemsize)
        data=np.ndarray((a['count'],width),dtype=dt,buffer=self.binary,
            offset=view.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,dt.itemsize)).copy()
        if a.get('normalized'):data=np.maximum(data/np.iinfo(dt).max,-1)
        self.cache[index]=data
        return data
    def global_matrices(self):
        nodes=self.doc['nodes'];local=[]
        for node in nodes:
            if 'matrix' in node:matrix=np.array(node['matrix']).reshape(4,4).T
            else:
                matrix=np.eye(4)
                matrix[:3,:3]=quaternion_matrix(node.get('rotation',[0,0,0,1]))@np.diag(node.get('scale',[1,1,1]))
                matrix[:3,3]=node.get('translation',[0,0,0])
            local.append(matrix)
        parents={c:i for i,node in enumerate(nodes) for c in node.get('children',[])};result={}
        def get(i):
            if i not in result:result[i]=(get(parents[i]) if i in parents else np.eye(4))@local[i]
            return result[i]
        for i in range(len(nodes)):get(i)
        return result
    def mesh(self,fragment):
        matches=[(i,n) for i,n in enumerate(self.doc['nodes']) if 'mesh' in n and fragment in n.get('name','')]
        if len(matches)!=1:raise ValueError('Ambiguous mesh '+fragment)
        ni,node=matches[0];mesh=self.doc['meshes'][node['mesh']]
        if len(mesh['primitives'])!=1:raise ValueError('Expected original single-material garment')
        pr=mesh['primitives'][0];attr=pr['attributes'];positions=self.accessor(attr['POSITION'])
        pos4=np.column_stack((positions,np.ones(len(positions))));globals=self.global_matrices()
        if 'skin' in node:
            skin=self.doc['skins'][node['skin']]
            ib=self.accessor(skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
            matrices=np.stack([globals[i]@m for i,m in zip(skin['joints'],ib)])
            joints=self.accessor(attr['JOINTS_0']).astype(int);weights=self.accessor(attr['WEIGHTS_0'])
            blended=(matrices[joints]*weights[:,:,None,None]).sum(axis=1)
            world=np.einsum('nij,nj->ni',blended,pos4)[:,:3]
        else:world=(globals[ni]@pos4.T).T[:,:3]
        world=world[:,[0,2,1]];world[:,1]*=-1
        faces=self.accessor(pr['indices']).ravel().astype(int).reshape(-1,3)
        return world,faces,pr
    def ring(self,fragment,mode):
        points,faces,pr=self.mesh(fragment)
        _,unique,inverse=np.unique(np.round(points,6),axis=0,return_index=True,return_inverse=True)
        welded=points[unique];triangles=inverse[faces]
        edges=Counter(tuple(sorted((int(a),int(b)))) for tr in triangles for a,b in zip(tr,np.roll(tr,-1)))
        adjacency=defaultdict(set)
        for (a,b),count in edges.items():
            if count==1:adjacency[a].add(b);adjacency[b].add(a)
        components=[];seen=set()
        for root in adjacency:
            if root in seen:continue
            pending=[root];seen.add(root);component=[]
            while pending:
                v=pending.pop();component.append(v)
                for n in adjacency[v]:
                    if n not in seen:seen.add(n);pending.append(n)
            if len(component)>=12 and np.ptp(welded[component,0])>.15:components.append(component)
        if not components:raise ValueError('Missing genuine wide garment opening')
        loop=(max if mode=='top' else min)(components,key=lambda ids:welded[ids,2].mean())
        if any(len(adjacency[i])!=2 for i in loop):raise ValueError('Boundary is not a closed loop')
        return welded,np.array(loop),pr
    def write_vec3(self,index,array,allowed):
        a=self.doc['accessors'][index];view=self.doc['bufferViews'][a['bufferView']]
        if a['componentType']!=5126 or a['type']!='VEC3':raise ValueError('Expected float VEC3')
        base=view.get('byteOffset',0)+a.get('byteOffset',0);stride=view.get('byteStride',12)
        target=np.ndarray((a['count'],3),dtype='<f4',buffer=self.binary,offset=base,strides=(stride,4))
        if array.shape!=target.shape or not np.isfinite(array).all():raise ValueError('Invalid update')
        target[:]=array
        for i in range(a['count']):allowed[base+i*stride:base+i*stride+12]=True
    def save(self,path):
        j=json.dumps(self.doc,separators=(',',':')).encode();j+=b' '*(-len(j)%4)
        b=bytes(self.binary);b+=b'\0'*(-len(b)%4)
        Path(path).write_bytes(struct.pack('<4sII',b'glTF',2,28+len(j)+len(b))+
            struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(b),b'BIN\0')+b)

def periodic(theta,values,targets):
    order=np.argsort(theta);t=theta[order];v=values[order]
    return np.interp(targets,np.r_[t[-1]-2*np.pi,t,t[0]+2*np.pi],np.r_[v[-1],v,v[0]])

def repair(source,destination):
    g=GLB(source)
    if g.sha256!=SOURCE_SHA256:raise ValueError('Unrecognized V18 source SHA256')
    if len(g.doc['skins'])!=1 or len(g.doc['skins'][0]['joints'])!=53:raise ValueError('Expected 53-joint character')
    if not g.doc.get('animations'):raise ValueError('Expected original V18 animation')
    p,ring,pr=g.ring('OpenSourceCloth_jie_cortu_cargo_pants','top')
    shirt,hem,_=g.ring('OpenSourceCloth_jie_toigo_basic_tucked_t-shirt','bottom')
    if len(p)!=211 or len(ring)!=16 or len(hem)!=36:raise ValueError('Unexpected source topology')
    center=np.array([0.,(shirt[hem,1].min()+shirt[hem,1].max())/2])
    def angle(points):return np.arctan2(points[:,1]-center[1],points[:,0]-center[0])
    theta=angle(p[ring]);stheta=angle(shirt[hem])
    floor=periodic(stheta,shirt[hem,2],theta)+.014
    target=np.maximum(p[ring,2],floor);order=np.argsort(theta);reverse=np.argsort(order)
    heights=target[order];lower=floor[order]
    for _ in range(50):heights=np.maximum(lower,.25*np.roll(heights,1)+.5*heights+.25*np.roll(heights,-1))
    dz=heights[reverse]-p[ring,2]
    radius=np.linalg.norm(p[ring,:2]-center,axis=1)
    shirt_radius=periodic(stheta,np.linalg.norm(shirt[hem,:2]-center,axis=1),theta)
    dr=np.maximum(radius,shirt_radius+.006)-radius
    points,faces,pr=g.mesh('OpenSourceCloth_jie_cortu_cargo_pants')
    angles=angle(points);rim_z=periodic(theta,p[ring,2],angles)
    fade=np.clip((points[:,2]-(rim_z-.16))/.16,0,1);fade=fade*fade*(3-2*fade)
    delta=np.zeros_like(points);delta[:,2]=periodic(theta,dz,angles)*fade
    radial=points[:,:2]-center;radial/=np.maximum(np.linalg.norm(radial,axis=1)[:,None],1e-9)
    delta[:,:2]=radial*periodic(theta,dr,angles)[:,None]*fade[:,None]
    maximum=float(np.linalg.norm(delta,axis=1).max())
    if maximum>.045:raise ValueError('Repair exceeds 45 mm geometry safety bound')
    attr=pr['attributes'];old=g.accessor(attr['POSITION'])
    neutral=points[:,[0,2,1]]*np.array([1,1,-1])
    if np.max(np.abs(old-neutral))>1e-5:raise ValueError('Unexpected neutral transform')
    changed=((points+delta)[:,[0,2,1]]*np.array([1,1,-1])).astype('<f4')
    _,wi,winverse=np.unique(np.round(changed,6),axis=0,return_index=True,return_inverse=True)
    tr=changed[faces];normals=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);smooth=np.zeros((len(wi),3))
    for k in range(3):np.add.at(smooth,winverse[faces[:,k]],normals)
    smooth/=np.maximum(np.linalg.norm(smooth,axis=1)[:,None],1e-12)
    allowed=np.zeros(len(g.binary),dtype=bool)
    g.write_vec3(attr['POSITION'],changed,allowed);g.write_vec3(attr['NORMAL'],smooth[winverse],allowed)
    pa=g.doc['accessors'][attr['POSITION']];pa['min']=changed.min(0).tolist();pa['max']=changed.max(0).tolist()
    before=np.frombuffer(g.original_binary,dtype='u1');after=np.frombuffer(g.binary,dtype='u1')
    if not np.array_equal(before[~allowed],after[~allowed]):raise AssertionError('Non-pants bytes changed')
    expected=copy.deepcopy(g.original_doc)
    expected['accessors'][attr['POSITION']]['min']=pa['min'];expected['accessors'][attr['POSITION']]['max']=pa['max']
    if expected!=g.doc:raise AssertionError('Unexpected scene, animation or material JSON change')
    g.save(destination)
    return {'source_sha256':g.sha256,'candidate_sha256':hashlib.sha256(Path(destination).read_bytes()).hexdigest(),
        'source_welded_pants_vertices':len(p),'glb_pants_vertices':len(points),
        'pants_waist_ring_vertices':len(ring),'shirt_hem_vertices':len(hem),
        'changed_glb_vertices':int((np.linalg.norm(delta,axis=1)>1e-7).sum()),
        'maximum_displacement_m':maximum,'overlap_target_m':.014,'radial_clearance_target_m':.006,
        'all_other_binary_bytes_identical':True,'animation_json_identical':True,
        'body_morphs_weights_uv_images_indices_unchanged':True,'topology_preserved':True,
        'interpretation':'Tucked shirt: trousers outside shirt at seam is expected, not an error.',
        'art_approved':False,'source_space':'V18 glTF; no claim of new source MPFB reconstruction'}
