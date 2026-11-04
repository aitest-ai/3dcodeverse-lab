"""Bounded editable repair on a new Harbor review copy. Never edits immutable source files.
Replace the jagged sleeve boundary/cuffs and poorly weighted diagonal strap using the actual jacket.
Original topology survives in sources/; topology changes here are explicit and recorded.
"""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.geometry import barycentric_transform
from mathutils.bvhtree import BVHTree
def repair(rig):
    jacket=bpy.data.objects['Original_Tailored_Jacket'];counts={'jacket_vertices_before':len(jacket.data.vertices)}
    bm=bmesh.new();bm.from_mesh(jacket.data)
    for x in [-.550,.550]:bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(x,0,0),plane_no=(1,0,0),dist=.000001,clear_inner=False,clear_outer=False)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if abs(f.calc_center_median().x)>.550001],context='FACES')
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(jacket.data);bm.free();jacket.data.update()
    cuffs=bpy.data.objects['Merged_Shirt_oat_canvas'];bm=bmesh.new();bm.from_mesh(cuffs.data);bmesh.ops.delete(bm,geom=[v for v in bm.verts if abs(v.co.x)>.45],context='VERTS');bm.to_mesh(cuffs.data);bm.free()
    def mesh(name,verts,faces,material):
        me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.parent=rig;o.data.materials.append(material);m=o.modifiers.new('Editable_skin','ARMATURE');m.object=rig
        for p in me.polygons:p.use_smooth=True
        return o
    for side,label in [(1,'l'),(-1,'r')]:
        verts=[];faces=[];rings=[(.539,.053,.052),(.551,.051,.050),(.580,.044,.044),(.614,.041,.041)]
        for x,ry,rz in rings:
            for k in range(32):
                a=math.tau*k/32;verts.append((side*x,.052+math.cos(a)*ry,1.418+math.sin(a)*rz))
        for j in range(len(rings)-1):
            for k in range(32):faces.append((j*32+k,j*32+(k+1)%32,(j+1)*32+(k+1)%32,(j+1)*32+k))
        if side<0:faces=[tuple(reversed(f)) for f in faces]
        o=mesh('Review_continuous_cuff_'+label,verts,faces,bpy.data.materials['Shirt_oat_canvas']);lower=o.vertex_groups.new(name='lowerarm_'+label);hand=o.vertex_groups.new(name='hand_'+label)
        for v in o.data.vertices:
            w=min(.22,max(0,(abs(v.co.x)-.58)/.034*.22));lower.add([v.index],1-w,'REPLACE');hand.add([v.index],w,'REPLACE')
        m=o.modifiers.new('Editable_cotton_thickness','SOLIDIFY');m.thickness=.002;m.offset=0
    # Remove only the old connected strap pieces, retaining the original pouch.
    sat=bpy.data.objects['Merged_Satchel_cognac'];bm=bmesh.new();bm.from_mesh(sat.data);seen=set();remove=[]
    for v in bm.verts:
        if v in seen:continue
        component=set([v]);queue=[v];seen.add(v)
        while queue:
            p=queue.pop()
            for edge in p.link_edges:
                q=edge.other_vert(p)
                if q not in seen:seen.add(q);component.add(q);queue.append(q)
        if max(v.co.z for v in component)-min(v.co.z for v in component)>.3:remove.extend(component)
    bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(sat.data);bm.free()
    jacket.data.calc_loop_triangles();tri=list(jacket.data.loop_triangles);coords=[v.co.copy() for v in jacket.data.vertices];tree=BVHTree.FromPolygons(coords,[list(t.vertices) for t in tri],all_triangles=True)
    group_names={g.index:g.name for g in jacket.vertex_groups};misses=0
    for back in [False,True]:
        verts=[];faces=[];weights=[]
        for i in range(45):
            t=i/44;x=-.14+t*.24;z=1.448-t*.414
            for dx in [-.011,.011]:
                hit=tree.ray_cast(Vector((x+dx,1 if back else -1,z)),Vector((0,-1 if back else 1,0)))
                if hit[0] is None:raise RuntimeError(f'Jacket strap surface not found: back={back} row={i} x={x+dx} z={z}')
                pos,normal,idx,_=hit;pos=pos+Vector((0,.007 if back else -.007,0));verts.append(tuple(pos));indices=tri[idx].vertices;A,B,C=[coords[k] for k in indices]
                uv=barycentric_transform(hit[0],A,B,C,Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)));row={}
                for vi,w in zip(indices,uv):
                    for g in jacket.data.vertices[vi].groups:row[group_names[g.group]]=row.get(group_names[g.group],0)+g.weight*max(0,w)
                row=sorted(row.items(),key=lambda kv:kv[1],reverse=True)[:4];total=sum(v for _,v in row);weights.append([(n,v/total) for n,v in row])
        for i in range(44):faces.append((i*2,i*2+1,i*2+3,i*2+2))
        if back:faces=[tuple(reversed(f)) for f in faces]
        o=mesh('Review_jacket_fitted_strap_'+('back' if back else 'front'),verts,faces,bpy.data.materials['Satchel_cognac']);groups={}
        for i,row in enumerate(weights):
            for n,w in row:
                if n not in groups:groups[n]=o.vertex_groups.new(name=n)
                groups[n].add([i],w,'REPLACE')
        m=o.modifiers.new('Editable_leather_thickness','SOLIDIFY');m.thickness=.002;m.offset=0
    counts.update({'jacket_vertices_after':len(jacket.data.vertices),'old_strap_vertices_removed':len(remove),'new_cuff_vertices':256,'new_strap_vertices':180,'topology_changed':True,'weights':'cuff forearm/hand blend; strap barycentric transfer from actual jacket, normalized top4','texture_bytes_changed':False,'status':'visual_candidate_not_approved','not_fixed':['Strap/pouch sewn attachment needs review','Chest tightness and neckline silhouette','Hem/hips/pants deformation','All-pose cloth/body collision']})
    return counts
