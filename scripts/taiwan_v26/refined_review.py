"""V26 refinement entry point.
Runs the existing review suite unchanged, but wraps its accessory-construction
stage with evaluated-body arm envelopes. This is model geometry refinement,
not retouching rendered images. Original V20 source objects are never edited.
"""
from pathlib import Path
import sys,runpy,math
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent
for p in (HERE,HERE.parent/'taiwan_v25',HERE.parent/'taiwan_v24',HERE.parent/'taiwan_v21',HERE.parent/'taiwan_v20'):sys.path.insert(0,str(p))
import wardrobe
from apron import finalize
from belt import WeightSource,mesh

_base_build=wardrobe.build

def refined_build(role,body,shirt,pants,hair,rig):
    added,design=_base_build(role,body,shirt,pants,hair,rig)
    bpy.context.view_layer.update()
    ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());data=ev.to_mesh()
    try:
        points=[ev.matrix_world@v.co for v in data.vertices]
        faces=[tuple(p.vertices) for p in data.polygons]
    finally:ev.to_mesh_clear()
    if len(points)!=len(body.data.vertices):raise RuntimeError('Evaluated body topology changed')
    names={g.index:g.name for g in body.vertex_groups}
    weights_source=WeightSource(body,rig)
    outer=next(o for o in added if o.name.endswith('HoodedLayer_Base'))
    loops=wardrobe.source_boundaries(outer);op=wardrobe.coordinates(outer)
    diagnostics=[]
    def replace(name,verts,faces,mat,uv):
        old=bpy.data.objects[name];idx=added.index(old);properties=dict(old.items())
        old.name=name+'_REPLACED_TEMP'
        ob=finalize(mesh(name,verts,faces,mat,uv),rig,weights_source.at)
        for key,value in properties.items():ob[key]=value
        added[idx]=ob;bpy.data.objects.remove(old,do_unlink=True)
        return ob
    for sign,side in ((1,'l'),(-1,'r')):
        arm=rig.data.bones['upperarm_'+side]
        arm_names={arm.name,*[b.name for b in arm.children_recursive]}
        strength=[sum(g.weight for g in v.groups if names[g.group] in arm_names) for v in body.data.vertices]
        selected=[f for f in faces if max(strength[i] for i in f)>.25]
        arm_tree=BVHTree.FromPolygons(points,selected)
        candidates=[q for q in loops if sign*op[q,0].mean()>.17]
        if not candidates:raise RuntimeError('Original sleeve seam missing')
        ring=op[max(candidates,key=lambda q:sign*op[q,0].mean())]
        # Three-to-four subdivision points per existing edge preserve the
        # original opening, rather than bridging it with a guessed round seam.
        divisions=max(3,48//len(ring));dense=[]
        for i,p in enumerate(ring):
            for t in np.linspace(0,1,divisions,endpoint=False):dense.append(p*(1-t)+ring[(i+1)%len(ring)]*t)
        dense=np.asarray(dense);n=len(dense);start=dense.mean(0)
        wrist=np.asarray(rig.matrix_world@rig.pose.bones['hand_'+side].head)
        elbow=np.asarray(rig.matrix_world@rig.pose.bones['lowerarm_'+side].head)
        axis=Vector(wrist-start).normalized();v=Vector((0,1,0));v=(v-axis*v.dot(axis)).normalized();w=axis.cross(v)
        angles=np.arctan2((dense-start)@np.asarray(w),(dense-start)@np.asarray(v))
        base_radius=np.linalg.norm(dense-start,axis=1)
        bend=float(np.clip(np.linalg.norm(elbow-start)/np.linalg.norm(wrist-start),.15,.85))
        def center(t):
            if t<=bend:return start+(elbow-start)*(t/bend)
            return elbow+(wrist-elbow)*((t-bend)/(1-bend))
        misses=0
        def section(t,cuff=False):
            nonlocal misses
            c=center(t);row=[]
            for i,a in enumerate(angles):
                direction=np.asarray(v)*math.cos(a)+np.asarray(w)*math.sin(a)
                radius=(1-min(t,1))*base_radius[i]+min(t,1)*.037
                origin=Vector(c+direction*.23)
                hit,_,_,_=arm_tree.ray_cast(origin,Vector(-direction),.26)
                if hit is not None:
                    body_radius=float((np.asarray(hit)-c)@direction)
                    if 0<body_radius<.13:radius=max(radius,body_radius+(.012 if cuff else .010))
                    else:misses+=1
                else:misses+=1
                row.append(tuple(c+direction*radius))
            return row
        verts=[];uv=[];rows=24
        for j,t in enumerate(np.linspace(0,1,rows)):
            row=[tuple(p) for p in dense] if j==0 else section(float(t))
            verts.extend(row);uv.extend([(i/n,float(t)) for i in range(n)])
        polys=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(rows-1) for i in range(n)]
        prefix='V26_'+role+'_'
        sleeve=bpy.data.objects[prefix+'Sleeve_'+side];mat=sleeve.data.materials[0]
        replace(prefix+'Sleeve_'+side,verts,polys,mat,uv)
        cv=[];cu=[];cr=4
        for t in np.linspace(.94,1.025,cr):
            cv.extend(section(float(t),True));cu.extend([(i/n,float(t)) for i in range(n)])
        cf=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(cr-1) for i in range(n)]
        cuffmat=bpy.data.objects[prefix+'Cuff_'+side].data.materials[0]
        replace(prefix+'Cuff_'+side,cv,cf,cuffmat,cu)
        diagnostics.append({'side':side,'native_seam_vertices':len(ring),'resampled_seam_vertices':n,
            'longitudinal_sections':rows,'arm_filtered_faces':len(selected),'bounded_ray_misses':misses,
            'method':'actual evaluated arm radial envelope along elbow/wrist centerline'})

    # Shape only the upper helmet crown; keep the established rim and straps.
    # Crown becomes lower/wider rather than the rejected pointed outline.
    if role=='jie':
        shell=bpy.data.objects['V26_jie_Helmet_Shell']
        hp=wardrobe.coordinates(hair);cx=float((hp[:,0].min()+hp[:,0].max())/2);cy=float((hp[:,1].min()+hp[:,1].max())/2)
        h=float(wardrobe.coordinates(body)[:,2].max());cz=h-.092
        maximum=max(v.co.z for v in shell.data.vertices);height=maximum-cz
        for vertex in shell.data.vertices:
            t=max(0.,min(1.,(vertex.co.z-cz)/height))
            if t<=0:continue
            vertex.co.x=cx+(vertex.co.x-cx)*(1+.07*t)
            vertex.co.y=cy+(vertex.co.y-cy)*(1+.04*t)
            vertex.co.z-=.008*t*t
        shell.data.update()
        design['helmet_crown_refinement']='upper crown widened up to7% and lowered up to8mm; rim retained'
    design['sleeve_construction']=diagnostics
    design['objects']=[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'group':o['accessory_group']} for o in added]
    design['refinement']='Evaluated-body envelope, not image edits; source character unchanged'
    return added,design

wardrobe.build=refined_build
runpy.run_path(str(HERE/'build_review.py'),run_name='__main__')
