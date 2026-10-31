"""Original V25 wardrobe: orange-yellow wrap apron and tied headscarf.
Add-only, preserving original body/face/clothing data. This is skinned cloth,
not cloth physics. The first candidate was visually rejected because waist
rays hit sleeves; this revision explicitly excludes arm-weighted faces.
"""
import math
import numpy as np
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from belt import WeightSource,material,mesh


def tree(obj,rig=None,exclude_arms=False):
    verts=[obj.matrix_world@v.co for v in obj.data.vertices]
    faces=[tuple(f.vertices) for f in obj.data.polygons]
    if exclude_arms:
        names=set()
        for side in ('l','r'):
            bone=rig.data.bones['upperarm_'+side]
            names.add(bone.name);names.update(b.name for b in bone.children_recursive)
        groups={g.index:g.name for g in obj.vertex_groups}
        arms=[sum(g.weight for g in v.groups if groups[g.group] in names) for v in obj.data.vertices]
        faces=[f for f in faces if max(arms[i] for i in f)<.20]
        if len(faces)<100:raise RuntimeError('Insufficient verified torso faces')
    return BVHTree.FromPolygons(verts,faces)


def finalize(obj,rig,weights):
    obj.parent=rig;obj.matrix_parent_inverse=rig.matrix_world.inverted()
    mod=obj.modifiers.new('V25_RigBinding','ARMATURE');mod.object=rig
    for vertex in obj.data.vertices:
        ws=weights(obj.matrix_world@vertex.co) if callable(weights) else weights
        total=sum(ws.values());assert total>0 and len(ws)<=4
        for name,w in ws.items():
            assert name in rig.data.bones
            group=obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
            group.add([vertex.index],float(w/total),'REPLACE')
    obj['asset_role']='V25 original boss wardrobe accessory';obj['geometry_license']='CC0-1.0'
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    return obj


def grid_sheet(name,points,rows,cols,mat,rig,weights,uv=None,thickness=.0014):
    points=[tuple(p) for p in points];count=len(points)
    verts=points+[(x,y+thickness,z) for x,y,z in points];faces=[]
    for j in range(rows-1):
        for i in range(cols-1):
            a=j*cols+i;b=a+1;c=a+cols+1;d=a+cols
            faces.extend([(a,d,c,b),(a+count,b+count,c+count,d+count)])
    edge=list(range(cols))+[j*cols+cols-1 for j in range(1,rows)]+list(range(count-2,count-cols-1,-1))+[j*cols for j in range(rows-2,0,-1)]
    for a,b in zip(edge,edge[1:]+edge[:1]):faces.append((a,b,b+count,a+count))
    return finalize(mesh(name,verts,faces,mat,(uv+uv) if uv else None),rig,weights)


def ribbon(name,path,width,mat,rig,weights):
    points=[Vector(p) for p in path];verts=[];faces=[]
    for i,p in enumerate(points):
        tangent=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
        normal=Vector((p.x,p.y+.015,0))
        if normal.length<.005:normal=Vector((0,-1,0))
        normal.normalize();across=tangent.cross(normal)
        if across.length<1e-5:across=Vector((1,0,0))
        across.normalize();verts.extend([tuple(p-across*width*.5),tuple(p+across*width*.5)])
        if i:faces.append((2*i-2,2*i-1,2*i+1,2*i))
    return finalize(mesh(name,verts,faces,mat),rig,weights)


def cord(name,path,mat,rig,weights,radius=.0008):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D'
    data.bevel_depth=radius;data.bevel_resolution=1;data.resolution_u=1
    spline=data.splines.new('POLY');spline.points.add(len(path)-1)
    for p,co in zip(spline.points,path):p.co=(*co,1.)
    ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target='MESH');ob=bpy.context.object;ob.data.materials.append(mat)
    return finalize(ob,rig,weights)


def build(body,shirt,pants,hair,rig):
    body_tree=tree(body,rig,True);shirt_tree=tree(shirt,rig,True);pants_tree=tree(pants)
    weights_source=WeightSource(shirt,rig)
    def torso_weights(point):
        if point.z<.89:return {'pelvis':1.}
        if point.z<.97:
            t=(point.z-.89)/.08;ws=weights_source.at(point)
            out={k:t*v for k,v in ws.items()};out['pelvis']=out.get('pelvis',0.)+1-t
            out=dict(sorted(out.items(),key=lambda p:p[1],reverse=True)[:4]);s=sum(out.values())
            return {k:v/s for k,v in out.items()}
        return weights_source.at(point)
    def surface(x,z,back=False):
        origin=Vector((x,1. if back else -1.,z));direction=Vector((0,-1 if back else 1,0));hits=[]
        for bvh in (shirt_tree,pants_tree,body_tree):
            p,_,_,_=bvh.ray_cast(origin,direction,2.)
            if p is not None:hits.append(p.y)
        if not hits:return .06 if back else -.13
        return max(hits) if back else min(hits)
    apronmat=material('V25_Apron_OrangeYellow_Cotton',(.70,.22,.035),.90)
    trim=material('V25_Apron_Seam_DarkerOchre',(.38,.125,.028),.91)
    thread=material('V25_Apron_Stitch_WarmCream',(.60,.43,.22),.92)
    scarfmat=material('V25_Headscarf_WarmCream',(.64,.48,.28),.89)
    added=[];rows,cols=34,29;bottom,top=.58,1.215
    stations=[(.58,.235),(.72,.237),(.84,.218),(.945,.184),(1.015,.155),(1.10,.127),(1.215,.103)]
    def width(z):return float(np.interp(z,[v[0] for v in stations],[v[1] for v in stations]))
    row_z=np.linspace(bottom,top,rows);row_base=[]
    for z in row_z:
        if z<.91:row_base.append(min(-.205,surface(0,z)-.018))
        else:row_base.append(min(surface(float(x),float(z)) for x in np.linspace(-.10,.10,9))-.015)
    row_base=np.asarray(row_base)
    for _ in range(3):row_base[1:-1]=.25*row_base[:-2]+.5*row_base[1:-1]+.25*row_base[2:]
    def front(x,z):
        u=x/width(z);y=float(np.interp(z,row_z,row_base))+.024*u*u
        y+=.0038*math.sin(5*math.pi*u)*max(0.,(.94-z)/.36)
        return min(y,surface(x,z)-.011)
    points=[];uv=[]
    for j,z in enumerate(row_z):
        for i,u in enumerate(np.linspace(-1,1,cols)):
            x=width(z)*u;zz=z+.004*u*u*max(0.,(.80-z)/.22)
            points.append((float(x),front(float(x),float(zz)),float(zz)));uv.append((i/(cols-1),j/(rows-1)))
    panel=grid_sheet('V25_Apron_Main',points,rows,cols,apronmat,rig,torso_weights,uv);added.append(panel)
    for side in (-1,1):
        path=[]
        for z in row_z:
            x=side*(width(z)-.004);path.append((x,front(x,z)-.001,z+.002))
        added.append(cord('V25_Apron_SideSeam_'+str(side),path,trim,rig,torso_weights))
    added.append(cord('V25_Apron_Hem',[(x,front(x,bottom+.006)-.001,bottom+.006) for x in np.linspace(-.229,.229,35)],trim,rig,torso_weights))
    pocket=[];puv=[];pr,pc=9,17
    for j,z in enumerate(np.linspace(.79,.90,pr)):
        for i,x in enumerate(np.linspace(-.102,.102,pc)):
            bulge=.0025+.003*math.sin(math.pi*i/(pc-1))*math.sin(math.pi*j/(pr-1))
            pocket.append((float(x),front(x,z)-bulge-.003,float(z)));puv.append((i/(pc-1),j/(pr-1)))
    added.append(grid_sheet('V25_Apron_FrontPocket',pocket,pr,pc,apronmat,rig,torso_weights,puv,.001))
    path=[(-.098,front(-.098,z)-.006,z) for z in np.linspace(.897,.794,12)]
    path += [(x,front(x,.794)-.006,.794) for x in np.linspace(-.098,.098,23)]
    path +=[(.098,front(.098,z)-.006,z) for z in np.linspace(.794,.897,12)]
    added.append(cord('V25_Apron_PocketStitch',path,thread,rig,torso_weights,.0006))
    added.append(cord('V25_Apron_PocketDivider',[(0,front(0,z)-.009,z) for z in np.linspace(.793,.897,15)],trim,rig,torso_weights,.00065))

    # Extend a legitimate wrap apron around hips/back instead of hiding source
    # trouble with an unrelated patch. Existing clothing remains intact beneath.
    center=np.asarray([0.,-.025]);wrap=[];wuv=[];wr,wc=24,65
    for j,z in enumerate(np.linspace(bottom,.945,wr)):
        w=width(z);edge=(front(-w,z)+front(w,z))*.5+.001
        back=max(.135,surface(0,z,True)+.015)
        knots=[0,.15,.35,.50,.65,.85,1.]
        xs=[-w,-w,-.70*w,0,.70*w,w,w]
        ys=[edge,0,back*.92,back,back*.92,0,edge]
        for i,u in enumerate(np.linspace(0,1,wc)):
            x=float(np.interp(u,knots,xs));y=float(np.interp(u,knots,ys));q=Vector((x,y,z))
            radial=Vector((x-center[0],y-center[1],0));length=radial.length;radial.normalize()
            origin=Vector((*center,z))+radial*.6
            for bvh in (body_tree,shirt_tree,pants_tree):
                hit,_,_,_=bvh.ray_cast(origin,-radial,.6)
                if hit is not None:
                    needed=(hit-Vector((*center,z))).length+.011
                    if needed>length:q+=radial*(needed-length);length=needed
            wrap.append(tuple(q));wuv.append((u,j/(wr-1)))
    # Double-sided original cloth surface, a standard skinned apron piece.
    faces=[]
    for j in range(wr-1):
        for i in range(wc-1):
            a=j*wc+i;faces.append((a,a+1,a+wc+1,a+wc))
    added.append(finalize(mesh('V25_Apron_WrapSidesBack',wrap,faces,apronmat,wuv),rig,torso_weights))
    added.append(cord('V25_Apron_BackHem',wrap[:wc],trim,rig,torso_weights,.0008))

    # Seat upper strap bends on actual shoulders using downward torso rays.
    def shoulder(x,y):
        q,_,_,_=body_tree.ray_cast(Vector((x,y,1.315)),Vector((0,0,-1)),.15)
        if q is None:raise RuntimeError('Cannot prove real shoulder surface')
        return (x,y,q.z+.005)
    p=[(-.089,front(-.089,top)-.001,top),(-.102,surface(-.102,1.25)-.007,1.25),
       shoulder(-.094,-.015),(-.078,surface(-.078,1.268,True)+.007,1.268),
       (0,surface(0,1.268,True)+.008,1.268),(.078,surface(.078,1.268,True)+.007,1.268),
       shoulder(.094,-.015),(.102,surface(.102,1.25)-.007,1.25),(.089,front(.089,top)-.001,top)]
    dense=[]
    for a,b in zip(p,p[1:]):
        for t in np.linspace(0,1,5,endpoint=False):dense.append(tuple(Vector(a).lerp(Vector(b),float(t))))
    dense.append(p[-1]);added.append(ribbon('V25_Apron_NeckStrap',dense,.018,apronmat,rig,torso_weights))

    # Torso-only waist rays must never bind the tie to sleeves or wrists.
    waist_z=.947;ring=[]
    for t in np.linspace(-math.pi/2,3*math.pi/2,97):
        r=Vector((math.cos(t),math.sin(t),0));origin=Vector((*center,waist_z))+r*.6;hits=[]
        for bvh in (body_tree,shirt_tree,pants_tree):
            q,_,_,_=bvh.ray_cast(origin,-r,.6)
            if q is not None:hits.append(q)
        if not hits:raise RuntimeError('Missing torso surface under apron tie')
        q=max(hits,key=lambda q:(q-Vector((*center,waist_z))).length)+r*.013
        if (q-Vector((*center,waist_z))).length>.285:raise RuntimeError('Waist tie found non-torso surface')
        if math.sin(t)<-.35:q.y=min(q.y,front(q.x,waist_z)-.001)
        ring.append(tuple(q))
    if max(abs(p[0]) for p in ring)>.27:raise RuntimeError('Tie reaches toward sleeves')
    added.append(ribbon('V25_Apron_WaistTie',ring,.028,apronmat,rig,torso_weights))
    back_y=max(.135,surface(0,waist_z,True)+.018)+.006
    for side in (-1,1):
        bow=[(side*.035*(1-math.cos(t)),back_y+.008*math.sin(t),waist_z+.014*math.sin(t)) for t in np.linspace(0,2*math.pi,25)]
        added.append(ribbon('V25_Apron_BowLoop_'+str(side),bow,.012,apronmat,rig,torso_weights))
        tail=[(side*(.01+.024*t),back_y+.004*math.sin(t*math.pi),waist_z-.095*t) for t in np.linspace(0,1,12)]
        added.append(ribbon('V25_Apron_TieTail_'+str(side),tail,.017,apronmat,rig,torso_weights))

    # Actual upper-scalp-fitting headscarf, retaining original hair underneath.
    hair_tree=tree(hair);headcenter=Vector((0,-.018,1.405));verts=[];faces=[];uv=[];n=64;nr=14
    def headpoint(phi,theta):
        v=Vector((.086*math.sin(phi)*math.cos(theta),.112*math.sin(phi)*math.sin(theta),.095*math.cos(phi))).normalized()
        origin=headcenter+v*.34;hits=[]
        for bvh in (body_tree,hair_tree):
            q,_,_,_=bvh.ray_cast(origin,-v,.40)
            if q is not None:hits.append(q)
        if not hits:raise RuntimeError('Headscarf ray missed actual head')
        q=max(hits,key=lambda q:(q-headcenter).dot(v));return q+v*.004
    verts.append(tuple(headpoint(0,0)));uv.append((.5,1))
    for j in range(1,nr+1):
        for i in range(n):
            t=-math.pi/2+2*math.pi*i/n;phi_end=1.51-.28*max(0.,-math.sin(t))**4
            verts.append(tuple(headpoint(phi_end*j/nr,t)));uv.append((i/n,1-j/nr))
    for i in range(n):faces.append((0,1+i,1+(i+1)%n))
    for j in range(nr-1):
        for i in range(n):
            a=1+j*n+i;b=1+j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
    added.append(finalize(mesh('V25_Headscarf_Crown',verts,faces,scarfmat,uv),rig,{'head':1.}))
    border=[verts[1+(nr-1)*n+i] for i in range(n)]+[verts[1+(nr-1)*n]]
    added.append(cord('V25_Headscarf_Border',border,apronmat,rig,{'head':1.},.0012))
    back=Vector(verts[1+(nr-1)*n+n//2]);back.y+=.007
    for side in (-1,1):
        path=[tuple(back+Vector((side*.048*t,.004*math.sin(t*math.pi),-.055*t))) for t in np.linspace(0,1,12)]
        added.append(ribbon('V25_Headscarf_Tail_'+str(side),path,.028,scarfmat,rig,{'head':1.}))
    for obj in added:obj['wardrobe_group']='headscarf' if 'Headscarf' in obj.name else 'apron'
    return added,{'revision':'torso-only tie and legitimate wrap apron after rejected first render',
        'apron_color':'orange-yellow ochre','headscarf_color':'warm cream with ochre edge',
        'apron_height_m':top-bottom,'apron_panel_width_range_m':[.206,.474],'apron_thickness_m':.0014,
        'wrap_sides_back':True,'torso_only_waist_fit':True,'waist_tie_max_abs_x_m':max(abs(p[0]) for p in ring),
        'pocket_present':True,'waist_ties_and_neck_loop':True,
        'source_hair_retained':'ponytail01; original short-curly brief still pending',
        'skinning':'upper apron original sweater weights, lower skirt pelvis, headscarf head joint',
        'cloth_simulation':False,'new_external_assets':False,
        'objects':[{'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)} for o in added]}
