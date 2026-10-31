"""Original V24 accessory, not a body replacement or hidden repair shell.
Fits a 38mm leather belt to existing waist surfaces. Transfers normalized
four-bone weights from nearest actual pants triangles; buckle uses one
common blend so it does not fold like fabric. All geometry authored here.
"""
import math
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from source_waist import coordinates
from waist_fit import opening,periodic


def material(name,color,roughness,metallic=0.):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1.)
    bs.inputs['Roughness'].default_value=roughness
    bs.inputs['Metallic'].default_value=metallic
    return m


class WeightSource:
    def __init__(self,pants,rig):
        pants.data.calc_loop_triangles()
        self.points=[pants.matrix_world@v.co for v in pants.data.vertices]
        self.triangles=[tuple(t.vertices) for t in pants.data.loop_triangles]
        self.tree=BVHTree.FromPolygons(self.points,self.triangles,all_triangles=True)
        groups={g.index:g.name for g in pants.vertex_groups}
        self.weights=[{groups[g.group]:g.weight for g in v.groups if groups[g.group] in rig.data.bones and g.weight>0.} for v in pants.data.vertices]
        self.rig=rig

    def at(self,point):
        hit,_,idx,_=self.tree.find_nearest(Vector(point))
        if hit is None:raise RuntimeError('No source pants triangle')
        ids=self.triangles[idx];a,b,c=[np.array(self.points[i]) for i in ids]
        ab=b-a;ac=c-a;ap=np.array(hit)-a
        d00=ab@ab;d01=ab@ac;d11=ac@ac;d20=ap@ab;d21=ap@ac
        den=d00*d11-d01*d01
        if abs(den)<1e-16:coeff=np.array([1.,0.,0.])
        else:
            v=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den
            coeff=np.maximum([1-v-w,v,w],0.);coeff/=sum(coeff)
        weights={}
        for i,k in zip(ids,coeff):
            for bone,w in self.weights[i].items():weights[bone]=weights.get(bone,0.)+float(k)*w
        weights=dict(sorted(weights.items(),key=lambda x:x[1],reverse=True)[:4])
        total=sum(weights.values())
        if total<1e-8:raise RuntimeError('Source face has no deforming bones')
        return {k:v/total for k,v in weights.items()}

    def bind(self,obj,common=None):
        obj.parent=self.rig
        obj.matrix_parent_inverse=self.rig.matrix_world.inverted()
        modifier=obj.modifiers.new('V24_SourceMatched_Skin','ARMATURE');modifier.object=self.rig
        for vertex in obj.data.vertices:
            weights=common if common is not None else self.at(obj.matrix_world@vertex.co)
            for name,value in weights.items():
                group=obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
                group.add([vertex.index],float(value),'REPLACE')
        return obj


def mesh(name,verts,faces,mat,uv=None):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for p in data.polygons:p.use_smooth=True
    if uv:
        layer=data.uv_layers.new(name='BeltUV')
        for p in data.polygons:
            for li in p.loop_indices:layer.data[li].uv=uv[data.loops[li].vertex_index]
    return ob


def rounded_rectangle(hw,hh,radius,steps=6):
    result=[]
    for cx,cz,start in ((hw-radius,hh-radius,0),(-hw+radius,hh-radius,90),(-hw+radius,-hh+radius,180),(hw-radius,-hh+radius,270)):
        for j in range(steps+1):
            a=math.radians(start+j*90/steps)
            result.append((cx+radius*math.cos(a),cz+radius*math.sin(a)))
    return result


def tube(name,path,radius,mat,sides=8):
    verts=[];faces=[];n=len(path)
    for i,p in enumerate(path):
        tangent=(Vector(path[(i+1)%n])-Vector(path[(i-1)%n])).normalized()
        axis=Vector((0,1,0));second=tangent.cross(axis).normalized()
        for j in range(sides):
            a=2*math.pi*j/sides
            verts.append(tuple(Vector(p)+radius*(axis*math.cos(a)+second*math.sin(a))))
    for i in range(n):
        for j in range(sides):faces.append((i*sides+j,i*sides+(j+1)%sides,((i+1)%n)*sides+(j+1)%sides,((i+1)%n)*sides+j))
    return mesh(name,verts,faces,mat)


def build(pants,shirt,rig):
    source=WeightSource(pants,rig)
    points=coordinates(pants)
    p,ids,_=opening(points,[list(f.vertices) for f in pants.data.polygons],True)
    rim=p[ids];center=np.array([0.,-.03445388749241829])
    a=np.arctan2(rim[:,1]-center[1],rim[:,0]-center[0])
    N=128;angles=-math.pi/2+np.arange(N)*2*math.pi/N
    heights=periodic(a,rim[:,2],angles)
    for _ in range(3):heights=.25*np.roll(heights,1)+.5*heights+.25*np.roll(heights,-1)
    # Belt top extends 6mm above the visible waistband, bottom 32mm below.
    centers=heights-.013
    bvh=[]
    for obj in (pants,shirt):
        verts=[obj.matrix_world@v.co for v in obj.data.vertices]
        bvh.append(BVHTree.FromPolygons(verts,[tuple(f.vertices) for f in obj.data.polygons]))
    def radius(theta,z):
        unit=Vector((math.cos(theta),math.sin(theta),0));origin=Vector((*center,z))+unit*.7
        radii=[]
        for tree in bvh:
            hit,_,_,_=tree.ray_cast(origin,-unit,.7)
            if hit is not None:radii.append(float((hit-Vector((*center,z))).length))
        if not radii:raise RuntimeError('No wardrobe surface under belt')
        value=max(radii)
        if not .09<value<.27:raise RuntimeError('Unexpected belt fit radius '+str(value))
        return value
    # Choose the greatest underlying radius across width, then conservative smoothing.
    radii=np.array([max(radius(t,z+d) for d in (-.019,-.009,0,.009,.019)) for t,z in zip(angles,centers)])
    smooth=radii.copy()
    for _ in range(3):smooth=.25*np.roll(smooth,1)+.5*smooth+.25*np.roll(smooth,-1)
    radii=np.maximum(radii,smooth)+.0042
    leather=material('V24_DeepBrown_Leather',(.055,.022,.010),.72)
    edges=material('V24_Leather_Edge',(.025,.010,.005),.82)
    metal=material('V24_BrushedSteel',(.30,.32,.33),.30,.88)
    loopmat=material('V24_Charcoal_Cloth_Loops',(.032,.034,.035),.92)
    # Rounded rectangular leather cross-section: (radial,z). Closed actual thickness.
    cross=[(-.0018,-.0177),(-.0012,-.019),(.0012,-.019),(.0018,-.0177),
           (.0018,.0177),(.0012,.019),(-.0012,.019),(-.0018,.0177)]
    verts=[];faces=[];uv=[]
    for i,(t,r,z) in enumerate(zip(angles,radii,centers)):
        for radial,dz in cross:
            verts.append((center[0]+(r+radial)*math.cos(t),center[1]+(r+radial)*math.sin(t),z+dz))
            uv.append((i/N,(dz+.019)/.038))
    for i in range(N):
        for j in range(8):faces.append((8*i+j,8*((i+1)%N)+j,8*((i+1)%N)+(j+1)%8,8*i+(j+1)%8))
    belt=mesh('V24_Belt_Leather',verts,faces,leather,uv);source.bind(belt)
    added=[belt]
    # Small rounded metal frame, pin, and keeper at the front; not a giant plate.
    z=float(centers[0]);front_y=float(center[1]-radii[0]-.0065)
    outline=rounded_rectangle(.024,.0205,.004,6)
    buckle=tube('V24_Belt_Buckle_Frame',[(x,front_y,z+v) for x,v in outline],.0022,metal)
    common=source.at((0,front_y,z));source.bind(buckle,common);added.append(buckle)
    # Box pin with real bevel geometry, baked before binding.
    def box(name,location,scale,mat,bevel=.001,weights=None):
        bpy.ops.mesh.primitive_cube_add(size=1,location=location)
        ob=bpy.context.object;ob.name=name;ob.dimensions=scale
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        mod=ob.modifiers.new('BakedRoundedEdges','BEVEL');mod.width=bevel;mod.segments=2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        # Freeze object transform into vertex coordinates before armature binding.
        ob.data.transform(ob.matrix_world);ob.matrix_world.identity()
        ob.data.materials.append(mat)
        for f in ob.data.polygons:f.use_smooth=True
        source.bind(ob,weights);added.append(ob);return ob
    box('V24_Belt_Buckle_Pin',(0,front_y-.001,z),(.042,.0032,.0034),metal,.001,common)
    # Leather keeper, fitted by belt parameter rather than floating in front.
    t=-math.pi/2+.24;ix=int(round(.24/(2*math.pi/N)))
    path=[]
    rr=float(radii[ix]);zz=float(centers[ix])
    for radial,dz in ((-.001,-.022),(.006,-.022),(.006,.022),(-.001,.022)):
        path.append((center[0]+(rr+radial)*math.cos(t),center[1]+(rr+radial)*math.sin(t),zz+dz))
    # A small band crossing the belt, modeled as closed strip around it.
    vs=[]
    tangent=Vector((-math.sin(t),math.cos(t),0))
    for q in path:
        for s in (-.004,.004):vs.append(tuple(Vector(q)+tangent*s))
    fs=[(2*i,2*((i+1)%4),2*((i+1)%4)+1,2*i+1) for i in range(4)]
    keeper=mesh('V24_Belt_Leather_Keeper',vs,fs,leather);source.bind(keeper);added.append(keeper)
    # Four functional cloth loops give the belt a plausible attachment to trousers.
    for k,t in enumerate((-math.pi/2-.65,-math.pi/2+.75,math.pi/2-.62,math.pi/2+.62)):
        idx=int(round(((t+math.pi/2)%(2*math.pi))/(2*math.pi/N)))%N
        r=float(radii[idx]);zz=float(centers[idx]);tangent=Vector((-math.sin(t),math.cos(t),0))
        points=[]
        for dz,extra in ((-.025,-.002),(-.020,.006),(.020,.006),(.025,-.002)):
            p=Vector((center[0]+(r+extra)*math.cos(t),center[1]+(r+extra)*math.sin(t),zz+dz))
            for s in (-.0035,.0035):points.append(tuple(p+tangent*s))
        f=[(2*j,2*j+1,2*(j+1)+1,2*(j+1)) for j in range(3)]
        ob=mesh('V24_BeltLoop_'+str(k+1),points,f,loopmat);source.bind(ob);added.append(ob)
    for ob in added:
        ob['source']='Original procedural V24 belt styling; no third-party accessory'
        ob['license']='CC0-1.0'
    # Mesh winding is corrected from consistent outward volume orientation.
    for ob in added:
        bpy.context.view_layer.objects.active=ob
        import bmesh
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    return added,{'belt_width_m':.038,'leather_thickness_m':.0036,'circumference_segments':N,
        'center_xy':center.tolist(),'center_z_range':[float(min(centers)),float(max(centers))],
        'buckle_frame_width_m':.0524,'buckle_frame_height_m':.0454,
        'weights':'nearest original pants triangles, barycentric interpolation, top4 normalized',
        'buckle_weights':common,'objects':[{'name':o.name,'verts':len(o.data.vertices),'faces':len(o.data.polygons)} for o in added]}
