"""V28 police wardrobe: original lace-up shoes, actual cloth surface separation.
Original body/face/rig/morph/animation stay intact. No hidden body deletion.
Footwear is our own CC0 geometry, not a claim of regulation-issued shoes.
"""
import math,sys
from pathlib import Path
import numpy as np
import bpy,bmesh
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
for d in ('taiwan_v20','taiwan_v24','taiwan_v21'):sys.path.insert(0,str(ROOT/d))
from source_waist import coordinates
from belt import WeightSource,mesh


def mat(name,color,roughness):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1.)
    p.inputs['Roughness'].default_value=roughness
    return m


def world_tree(obj):
    bpy.context.view_layer.update()
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:return BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons])
    finally:ev.to_mesh_clear()


def write_world(obj,new):
    old=coordinates(obj);delta=(new-old)@np.asarray(obj.matrix_world.inverted().to_3x3()).T
    local=np.asarray([tuple(v.co) for v in obj.data.vertices])
    keys=list(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else []
    snapshots=[np.asarray([tuple(v.co) for v in k.data]) for k in keys]
    obj.data.vertices.foreach_set('co',np.asarray(local+delta,dtype='f4').ravel())
    for k,a in zip(keys,snapshots):k.data.foreach_set('co',np.asarray(a+delta,dtype='f4').ravel())
    obj.data.update();obj.update_tag(refresh={'DATA'});bpy.context.view_layer.update()
    assert np.allclose(coordinates(obj),new,atol=2e-6)
    return {'moved_vertices':int((np.linalg.norm(new-old,axis=1)>1e-7).sum()),'max_shift_m':float(np.linalg.norm(new-old,axis=1).max())}


def fix_clothes(body,shirt,pants):
    bt=world_tree(body);p=coordinates(pants);q=p.copy()
    for i,v in enumerate(p):
        if v[2]>.52:continue
        hit,n,_,d=bt.find_nearest(Vector(v))
        if hit is None or d>.035:continue
        signed=(Vector(v)-hit).dot(n)
        shift=max(0.,.0055-signed)
        if shift>.022:continue
        if shift:q[i]+=np.asarray(n)*shift
    legs=write_world(pants,q)
    pt=world_tree(pants);p=coordinates(shirt);q=p.copy()
    lo=float(p[:,2].min());center=np.array([0.,-.025])
    for i,v in enumerate(p):
        if not(lo-.005<=v[2]<=lo+.19) or abs(v[0])>.27:continue
        radial=v[:2]-center;r=np.linalg.norm(radial)
        if r<.05:continue
        unit=radial/r;start=Vector((*(center+unit*.7),v[2]));direction=Vector((-unit[0],-unit[1],0))
        hit,_,_,_=pt.ray_cast(start,direction,.7)
        if hit is None:continue
        pr=float(np.linalg.norm(np.array(hit[:2])-center));need=pr+.008-r
        if .0003<need<.032:q[i,:2]+=unit*need
    hem=write_world(shirt,q)
    return {'pants_lower_leg':legs,'untucked_uniform_over_pants':hem,'topology_and_weights_edited':False}


def convex_hull(a):
    points=sorted(set(tuple(x) for x in np.round(a,7)))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    low=[]
    for p in points:
        while len(low)>=2 and cross(low[-2],low[-1],p)<=0:low.pop()
        low.append(p)
    up=[]
    for p in reversed(points):
        while len(up)>=2 and cross(up[-2],up[-1],p)<=0:up.pop()
        up.append(p)
    return np.asarray(low[:-1]+up[:-1])


def contour(points,margin=.006,n=64):
    hull=convex_hull(points);center=hull.mean(0)
    if len(hull)<4:raise RuntimeError('Foot slice has no valid outline')
    ring=[]
    for i in range(n):
        u=np.array([math.cos(2*math.pi*i/n),math.sin(2*math.pi*i/n)])
        radii=[]
        for a,b in zip(hull,np.roll(hull,-1,axis=0)):
            edge=b-a;system=np.column_stack((u,-edge))
            if abs(np.linalg.det(system))<1e-10:continue
            r,t=np.linalg.solve(system,a-center)
            if r>0 and -.0001<=t<=1.0001:radii.append(r)
        if not radii:raise RuntimeError('Unresolved foot outline ray')
        ring.append(center+u*(min(radii)+margin))
    ring=np.asarray(ring)
    smooth=.15*np.roll(ring,1,0)+.7*ring+.15*np.roll(ring,-1,0)
    delta=smooth-center;r=np.linalg.norm(delta,axis=1)
    original_r=np.linalg.norm(ring-center,axis=1)
    return center+delta*np.maximum(r,original_r)[:,None]/r[:,None]


def recalc(obj):
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()


def loft(name,rings,material,weights,caps=True):
    n=len(rings[0]);verts=[tuple(p) for row in rings for p in row];faces=[]
    for row in range(len(rings)-1):
        for j in range(n):faces.append((row*n+j,row*n+(j+1)%n,(row+1)*n+(j+1)%n,(row+1)*n+j))
    if caps:faces += [tuple(reversed(range(n))),tuple((len(rings)-1)*n+j for j in range(n))]
    ob=mesh(name,verts,faces,material);recalc(ob);weights.bind(ob)
    return ob


def cord(name,path,material,weights,radius=.0012):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=2
    curve.bevel_depth=radius;curve.bevel_resolution=2
    spline=curve.splines.new('POLY');spline.points.add(len(path)-1)
    for p,v in zip(spline.points,path):p.co=(*v,1.)
    ob=bpy.data.objects.new(name,curve);bpy.context.scene.collection.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target='MESH');ob=bpy.context.object;ob.data.materials.append(material)
    weights.bind(ob);return ob


def shoes(body,rig):
    weights=WeightSource(body,rig);pts=coordinates(body)
    leather=mat('V28_Shoe_Black_Leather',(.014,.016,.020),.34)
    sole=mat('V28_Shoe_MatteRubber',(.006,.007,.009),.82)
    stitch=mat('V28_Shoe_DarkStitch',(.032,.033,.035),.74)
    lace=mat('V28_Shoe_CharcoalLaces',(.018,.019,.021),.92)
    added=[];details=[]
    for side in ('l','r'):
        ankle=rig.matrix_world@rig.data.bones['foot_'+side].head_local
        sign=1 if ankle.x>0 else -1
        foot=pts[(pts[:,0]*sign>0)&(pts[:,2]<.155)]
        if len(foot)<100:raise RuntimeError('Source foot selection failed '+side)
        base=contour(foot[foot[:,2]<.095,:2],.010)
        zbase=float(foot[:,2].min())-.001
        sole_rings=[np.column_stack((base,np.full(len(base),z))) for z in (zbase,zbase+.006,zbase+.021)]
        added.append(loft('V28_cop_Shoe_'+side+'_Sole',sole_rings,sole,weights))
        upper=[]
        for level in (.021,.033,.052,.073,.094,.114,.137):
            if level<=.033:xy=base.copy()
            else:
                band=foot[(foot[:,2]>=level-.023)&(foot[:,2]<=level+.023)]
                if len(band)<12:band=foot[foot[:,2]>.085]
                xy=contour(band[:,:2],.007)
            upper.append(np.column_stack((xy,np.full(len(xy),zbase+level))))
        shell=loft('V28_cop_Shoe_'+side+'_Upper',upper,leather,weights,False);added.append(shell)
        top=upper[-1].copy();ctr=top[:,:2].mean(0);inside=top.copy()
        inside[:,:2]=ctr+(inside[:,:2]-ctr)*.94;inside[:,2]-=.003
        added.append(loft('V28_cop_Shoe_'+side+'_Collar',[top,inside],leather,weights,False))
        welt=np.column_stack((base,np.full(len(base),zbase+.0215)))
        added.append(cord('V28_cop_Shoe_'+side+'_Welt',list(welt)+[welt[0]],stitch,weights,.0008))
        ball=rig.matrix_world@rig.data.bones['ball_'+side].head_local
        forward=np.array([ball.x-ankle.x,ball.y-ankle.y]);forward/=np.linalg.norm(forward)
        lateral=np.array([-forward[1],forward[0]])
        origin=np.array([ankle.x,ankle.y]);st=world_tree(shell);lace_paths=[]
        for j in range(5):
            along=.027+j*.012
            endpoints=[]
            for d in (-1,1):
                xy=origin+forward*along+lateral*(.017*d)
                hit,_,_,_=st.ray_cast(Vector((*xy,.25)),Vector((0,0,-1)),.3)
                if hit is None:continue
                endpoints.append(np.array(hit)+[0,0,.002])
            if len(endpoints)==2:
                a,b=endpoints;mid=(a+b)/2;mid[2]+=.003
                path=[tuple(a),tuple(mid),tuple(b)]
                added.append(cord('V28_cop_Shoe_'+side+'_Lace_'+str(j),path,lace,weights,.0011));lace_paths.append(path)
        details.append({'side':side,'source_foot_points':len(foot),'source_bounds':[foot.min(0).tolist(),foot.max(0).tolist()],
          'sole_bottom_z':zbase,'upper_top_z':zbase+.137,'laces':len(lace_paths)})
    for ob in added:
        ob['source']='V28 original fitted black lace-up shoe';ob['geometry_license']='CC0-1.0'
    return added,{'design':'plain black lace-up uniform shoes, original CC0 geometry; no claimed official model',
      'shoes':details,'added_objects':[o.name for o in added],
      'skinning':'barycentric interpolation from original body triangles, top4 weights'}
