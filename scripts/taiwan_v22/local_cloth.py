"""V22: local cloth candidate; no new faces, masks, weights, or materials.
Uses actual original front-facing panel connectivity, and verifies LBS against
Blender evaluated coordinates before mapping pose-space corrections to rest.
"""
from collections import defaultdict
import math
import numpy as np
import bpy
from mathutils import Vector
from source_waist import coordinates
from waist_fit import opening,periodic
from motion_qa import evaluated_bvh


def evaluated_points(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:return np.asarray([tuple(ev.matrix_world@v.co) for v in me.vertices])
    finally:ev.to_mesh_clear()


def write_world(obj,target):
    before=coordinates(obj);world_delta=target-before
    delta=world_delta@np.asarray(obj.matrix_world.inverted().to_3x3()).T
    local=np.asarray([tuple(v.co) for v in obj.data.vertices])
    keys=list(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else []
    old=[np.asarray([tuple(v.co) for v in k.data]) for k in keys]
    obj.data.vertices.foreach_set('co',np.asarray(local+delta,dtype='f4').ravel())
    for key,value in zip(keys,old):key.data.foreach_set('co',np.asarray(value+delta,dtype='f4').ravel())
    obj.data.update();obj.update_tag(refresh={'DATA'});bpy.context.view_layer.update()
    if not np.allclose(coordinates(obj),target,atol=2e-6):raise RuntimeError('Source write failed')


def separate_fly(pants):
    pts=coordinates(pants);faces=[list(f.vertices) for f in pants.data.polygons]
    # Face normals, not a guessed flat rectangular set of vertices.
    eligible=set();edges=defaultdict(list)
    for i,face in enumerate(faces):
        q=pts[face];n=np.cross(q[1]-q[0],q[2]-q[0]);length=np.linalg.norm(n)
        if length<1e-10:continue
        if n[1]/length<-.20 and q[:,2].mean()>.86:
            eligible.add(i)
            for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted((a,b)))].append(i)
    adj=defaultdict(set)
    for row in edges.values():
        for f in row:adj[f].update(set(row)-{f})
    seen=set();components=[]
    for root in eligible:
        if root in seen:continue
        seen.add(root);queue=[root];comp=[]
        while queue:
            f=queue.pop();comp.append(f)
            for other in adj[f]:
                if other not in seen:seen.add(other);queue.append(other)
        ids=sorted(set(v for f in comp for v in faces[f]));q=pts[ids]
        components.append((comp,ids,q))
    # The right outer front panel wraps left of the fly; the underlap stays put.
    candidates=[c for c in components if len(c[0])>12 and c[2][:,0].min()<-.01
                and c[2][:,0].max()>.10 and c[2][:,1].mean()<-.04]
    if len(candidates)!=1:raise RuntimeError('Ambiguous native outer fly panel')
    comp,ids,q=candidates[0];new=pts.copy();changed=[]
    for i in ids:
        x,y,z=pts[i]
        if y>=-.12 or z<=.905 or abs(x)>=.055:continue
        w=max(0,1-abs(x)/.055);w=w*w*(3-2*w)
        vertical=np.clip((z-.905)/.018,0,1);vertical=vertical*vertical*(3-2*vertical)
        d=.0030*w*vertical
        if d<1e-7:continue
        new[i,1]-=d;changed.append(i)
    if not changed:raise RuntimeError('No real fly vertices selected')
    write_world(pants,new)
    return {'method':'connected original right front panel, local 3mm fly separation',
      'component_faces':len(comp),'changed_vertex_ids':changed,'max_shift_m':float(np.linalg.norm(new-pts,axis=1).max()),
      'vertical_change_m':float(np.abs(new[:,2]-pts[:,2]).max()),'no_topology_change':True}


def skin_matrices(obj,rig):
    active=[m for m in obj.modifiers if m.show_viewport]
    if any(m.type!='ARMATURE' for m in active):raise RuntimeError('Unsupported active modifier')
    if any(m.use_deform_preserve_volume for m in active):raise RuntimeError('LBS cannot model preserve volume')
    rw=np.asarray(rig.matrix_world);ow=np.asarray(obj.matrix_world)
    inverse=np.linalg.inv(rw)
    groups={g.index:g.name for g in obj.vertex_groups}
    transforms={b.name:rw@np.asarray(b.matrix)@np.linalg.inv(np.asarray(b.bone.matrix_local))@inverse@ow for b in rig.pose.bones}
    matrices=[]
    for vertex in obj.data.vertices:
        pairs=[(g.weight,transforms[groups[g.group]]) for g in vertex.groups if groups[g.group] in transforms and g.weight>0]
        total=sum(w for w,m in pairs)
        matrices.append(sum(w*m for w,m in pairs)/total if total>1e-9 else ow)
    mats=np.asarray(matrices)
    local=np.asarray([tuple(v.co) for v in obj.data.vertices])
    predicted=np.einsum('nij,nj->ni',mats,np.column_stack((local,np.ones(len(local)))))[:,:3]
    error=float(np.abs(predicted-evaluated_points(obj)).max())
    if error>4e-5:raise RuntimeError('LBS/depsgraph disagreement '+str(error))
    return mats,error


def fit_tucked_hem(body,shirt,pants,rig,center,limbs,sample_frames):
    original=coordinates(shirt);current=original.copy();faces=[list(f.vertices) for f in shirt.data.polygons]
    neighbors=[set() for _ in original]
    for face in faces:
        for a,b in zip(face,face[1:]+face[:1]):neighbors[a].add(b);neighbors[b].add(a)
    # Never touch the visible upper torso, sleeve or neckline.
    permitted=(original[:,2]<1.006)&(np.abs(original[:,0])<.25)
    inv_world=np.asarray(shirt.matrix_world.inverted().to_3x3())
    world_linear=np.asarray(shirt.matrix_world.to_3x3())
    rows=[];max_error=0.;capped=set()
    for iteration in range(3):
        proposals=np.zeros_like(original);strength=np.zeros(len(original));unresolved=0;hits=0
        for frame in sample_frames:
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
            sp=evaluated_points(shirt);pp=evaluated_points(pants)
            q,rim,_=opening(pp,[list(f.vertices) for f in pants.data.polygons],True)
            a=np.arctan2(q[rim,1]-center[1],q[rim,0]-center[0])
            bvh_p=evaluated_bvh(pants);bvh_b=evaluated_bvh(body)
            matrices,error=skin_matrices(shirt,rig);max_error=max(max_error,error)
            for i in np.where(permitted)[0]:
                point=sp[i];vec=point[:2]-center;r=np.linalg.norm(vec)
                if r<.01:continue
                direction=vec/r;theta=math.atan2(vec[1],vec[0])
                edge=float(periodic(a,q[rim,2],np.array([theta]))[0])
                if point[2]>edge-.006:continue
                start=Vector((*(center+direction),point[2]));ray=Vector((-direction[0],-direction[1],0))
                ph,_,_,_=bvh_p.ray_cast(start,ray,1.)
                if ph is None:continue
                pr=np.linalg.norm(np.array(ph[:2])-center)
                wanted=pr-.003
                if r<=wanted+.0005:continue
                origin=start.copy();bh=None
                for _ in range(12):
                    bh,_,face,_=bvh_b.ray_cast(origin,ray,1.)
                    if bh is None:break
                    if limbs[face]:origin=bh+ray*.0001;continue
                    break
                else:bh=None
                if bh is None:continue
                br=np.linalg.norm(np.array(bh[:2])-center)
                if br+.0015>wanted:
                    unresolved+=1;continue  # Never tuck cloth into the actual body.
                amount=min(r-wanted,.008)
                displacement=np.array([-direction[0]*amount,-direction[1]*amount,0.])
                local_delta=np.linalg.solve(matrices[i,:3,:3],displacement)
                rest_delta=world_linear@local_delta
                size=np.linalg.norm(rest_delta)
                if size>strength[i]:strength[i]=size;proposals[i]=rest_delta
                hits+=1
        # Smooth the local displacement field, not the mesh itself.
        field=proposals.copy()
        for _ in range(2):
            nxt=field.copy()
            for i in np.where(permitted)[0]:
                n=list(neighbors[i])
                if n:nxt[i]=.75*field[i]+.25*field[n].mean(0)
            field=nxt
        candidate=current+field*.85
        total=candidate-original;norm=np.linalg.norm(total,axis=1)
        for i in np.where(norm>.012)[0]:
            total[i]*=.012/norm[i];capped.add(int(i))
        current=original+total;write_world(shirt,current)
        rows.append({'iteration':iteration,'vertex_pose_corrections':hits,'no_safe_gap_skipped':unresolved})
    return {'method':'multi-pose radial cloth clearance, inverse verified LBS and local smooth field',
      'sample_frames':sample_frames,'iterations':rows,'changed_vertices':int((np.linalg.norm(current-original,axis=1)>1e-7).sum()),
      'max_source_shift_m':float(np.linalg.norm(current-original,axis=1).max()),'capped_vertex_ids':sorted(capped),
      'max_lbs_vs_blender_error_m':max_error,'body_clearance_m':.0015,'pants_clearance_m':.003,
      'shirt_displacement_limit_m':.012,'no_body_or_weight_edits':True}
