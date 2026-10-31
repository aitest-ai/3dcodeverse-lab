"""Reconstruct only the malformed original lower polo band.
Keep the original upper garment, body, material and skeleton. Native source
cloth topology below the cut is deliberately changed and reported, not hidden.
"""
import math
import numpy as np
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from belt import WeightSource
from motion_qa import arm_faces
from source_waist import coordinates


def rebuild(shirt,body,pants,rig):
    if shirt.data.shape_keys and len(shirt.data.shape_keys.key_blocks)>1:
        raise RuntimeError('Do not remesh a garment with relative morph keys')
    donor=WeightSource(shirt,rig)
    old_uv=shirt.data.uv_layers.active
    uv_tri=[np.asarray([tuple(old_uv.data[i].uv) for i in t.loops]) for t in shirt.data.loop_triangles]
    source_faces=len(shirt.data.polygons);source_vertices=len(shirt.data.vertices)
    def uv_at(point):
        hit,_,idx,_=donor.tree.find_nearest(Vector(point));ids=donor.triangles[idx]
        a,b,c=[np.asarray(donor.points[i]) for i in ids];ab=b-a;ac=c-a;ap=np.asarray(hit)-a
        d00=ab@ab;d01=ab@ac;d11=ac@ac;d20=ap@ab;d21=ap@ac;den=d00*d11-d01*d01
        if abs(den)<1e-15:return uv_tri[idx][0]
        v=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den
        return (1-v-w)*uv_tri[idx][0]+v*uv_tri[idx][1]+w*uv_tri[idx][2]
    limbs=arm_faces(body,rig);obstacles=[]
    for ob in (body,pants):
        pts=coordinates(ob);faces=[tuple(p.vertices) for i,p in enumerate(ob.data.polygons) if ob is not body or not limbs[i]]
        obstacles.append(BVHTree.FromPolygons(pts.tolist(),faces))
    if shirt.data.shape_keys:shirt.shape_key_clear() # only a redundant Basis, not facial morphs
    bm=bmesh.new();bm.from_mesh(shirt.data)
    cut=.920;mat=shirt.matrix_world.copy();inv=mat.inverted()
    plane_co=inv@Vector((0,0,cut));plane_no=(mat.to_3x3().transposed()@Vector((0,0,1))).normalized()
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,
        plane_co=plane_co,plane_no=plane_no,clear_inner=True,clear_outer=False)
    edges=[e for e in bm.edges if e.is_boundary and all(abs((mat@v.co).z-cut)<2e-5 for v in e.verts)]
    adj={}
    for e in edges:
        a,b=e.verts;adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
    if len(adj)<20 or any(len(n)!=2 for n in adj.values()):raise RuntimeError('Lower cut is not one usable closed boundary')
    start=next(iter(adj));ring=[start];previous=None;cur=start
    while True:
        nxt=next(v for v in adj[cur] if v is not previous)
        if nxt is start:break
        if nxt in ring:raise RuntimeError('Ambiguous lower boundary')
        ring.append(nxt);previous,cur=cur,nxt
    if len(ring)!=len(adj):raise RuntimeError('Multiple disconnected cut loops')
    uv_layer=bm.loops.layers.uv.active;deform=bm.verts.layers.deform.verify()
    group_ids={g.name:g.index for g in shirt.vertex_groups}
    center=np.asarray([0.,-.012]);starts=np.asarray([tuple(mat@v.co) for v in ring])
    radial=starts[:,:2]-center;radii=np.linalg.norm(radial,axis=1);directions=radial/radii[:,None]
    new_faces=[];new_count=0;top=ring
    def add_vert(q):
        nonlocal new_count
        v=bm.verts.new(inv@Vector(q));weights=donor.at(q)
        for name,w in weights.items():
            if name not in group_ids:group_ids[name]=shirt.vertex_groups.new(name=name).index
            v[deform][group_ids[name]]=w
        new_count+=1;return v
    for layer in range(1,8):
        t=layer/7;lower=[]
        for i,direction in enumerate(directions):
            z=cut*(1-t)+(.844+.003*(abs(starts[i,0])/.20)**2)*t
            radius=radii[i]+.003*t+.0015*math.sin(t*math.pi)
            origin=Vector((*(center+direction*.42),z));ray=Vector((-direction[0],-direction[1],0))
            for obstacle in obstacles:
                hit,_,_,_=obstacle.ray_cast(origin,ray,.42)
                if hit is not None:radius=max(radius,float(np.linalg.norm(np.asarray(hit[:2])-center))+.007)
            lower.append(add_vert((*(center+direction*radius),z)))
        for i in range(len(ring)):
            j=(i+1)%len(ring);f=bm.faces.new((top[i],top[j],lower[j],lower[i]));f.smooth=True;new_faces.append(f)
        top=lower
    # A 1.6mm turned edge, not the old ~4cm folded/intersecting band.
    inner=[]
    for v in top:
        q=np.array(tuple(mat@v.co),dtype=float);d=q[:2]-center;d/=np.linalg.norm(d);q[:2]-=d*.0016;q[2]+=.0015
        inner.append(add_vert(q))
    for i in range(len(ring)):
        j=(i+1)%len(ring);f=bm.faces.new((top[i],top[j],inner[j],inner[i]));f.smooth=True;new_faces.append(f)
    for f in new_faces:
        f.material_index=0
        for loop in f.loops:loop[uv_layer].uv=uv_at(mat@loop.vert.co)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(shirt.data);bm.free()
    shirt.data.update();shirt.update_tag(refresh={'DATA'});bpy.context.view_layer.update()
    return {'method':'Remove malformed lower band below0.920m; connected7-row untucked hem plus1.6mm turned edge',
      'source_vertices_before':source_vertices,'source_faces_before':source_faces,
      'source_vertices_after':len(shirt.data.vertices),'source_faces_after':len(shirt.data.polygons),
      'cut_ring_vertices':len(ring),'created_vertices':new_count,'created_faces':len(new_faces),
      'topology_changed_below_cut':True,'original_upper_material_and_color_image_preserved':True,
      'new_uvs_and_top4_weights':'nearest original shirt triangle barycentric transfer',
      'not_body_remesh':True,'not_occlusion_shell':True}
