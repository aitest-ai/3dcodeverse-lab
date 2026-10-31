"""V27 accessory construction followed by explicit visual-review corrections.
Keeps the first source implementation inspectable in accessories_base.py.
Refines only the just-created original cap/headband, before export or animation.
"""
import math
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from native import coordinates
from accessories_base import build as initial_build


def assign_world(obj,points):
    inverse=obj.matrix_world.inverted()
    if len(points)!=len(obj.data.vertices):raise RuntimeError('Accessory topology mismatch')
    for v,p in zip(obj.data.vertices,points):v.co=inverse@Vector(p)
    obj.data.update();bpy.context.view_layer.update()


def build(cid,body,rig,shirt,pants,attached):
    added,report=initial_build(cid,body,rig,shirt,pants,attached)
    h=report['head_fit']['body_top'];cy=report['head_fit']['center_y']
    rx=report['head_fit']['radius_x'];ry=report['head_fit']['radius_y'];base=h-.065
    changes=[]
    if cid in ('oldman','cop'):
        crown=next(o for o in added if o.name=='V27_'+cid+'_CapCrown')
        points=coordinates(crown);n=72;rows=14
        assert len(points)==n*rows
        for i,p in enumerate(points):
            phi=.008+(math.pi/2-.008)*(i//n)/(rows-1)
            p[2]=base+(.080*math.cos(phi) if cid=='oldman' else .085*(1-math.sin(phi)**4))
        assign_world(crown,points)
        visor=next(o for o in added if o.name=='V27_'+cid+'_CapVisor')
        points=coordinates(visor);assert len(points)==4*41
        over=1.1 if cid=='cop' else 1.
        for i,p in enumerate(points):
            v=(i//41)/3;u=-1+2*(i%41)/40
            inner=cy-ry*over*math.sqrt(max(0.,1-(u*.92)**2))
            outer=cy-ry*over-(.055 if cid=='cop' else .070)*(1-.35*u*u)
            p[0]=rx*over*.96*u*(1-.08*v)
            p[1]=(1-v)*inner+v*outer
            p[2]=base-.008-.013*v+.005*u*u
        assign_world(visor,points)
        if cid=='oldman':
            for ob in added:
                if 'CapPanelSeam' in ob.name:
                    points=coordinates(ob);points[:,2]=base+(points[:,2]-base)*(.080/.105)
                    assign_world(ob,points)
        changes.append({'part':'cap','change':'narrowed real visor and lower baseball crown / flatter peaked crown',
                        'topology_and_weights_preserved':True})
    if cid=='bro':
        band=next(o for o in added if o.name=='V27_bro_WhiteHeadband')
        points=coordinates(band);assert len(points)==144
        bvh=BVHTree.FromPolygons([body.matrix_world@v.co for v in body.data.vertices],
             [tuple(f.vertices) for f in body.data.polygons])
        old=points.copy()
        for i,p in enumerate(points):
            z=h-.067+((i//72)-.5)*.035;t=2*math.pi*(i%72)/72
            radial=Vector((math.cos(t),math.sin(t),0));center=Vector((0,cy,z))
            hit,_,_,_=bvh.ray_cast(center+radial*.35,-radial,.35)
            if hit is None:raise RuntimeError('Cannot fit headband to actual forehead '+str(i))
            points[i]=np.asarray(hit+radial*.003)
        assign_world(band,points)
        z=h-.067;origin=Vector((0,cy+.35,z))
        hit,_,_,_=bvh.ray_cast(origin,Vector((0,-1,0)),.35)
        if hit is None:raise RuntimeError('Cannot fit rear headband knot')
        shift=hit.y-(cy+ry)
        for ob in added:
            if ob.name=='V27_bro_HeadbandKnot' or 'V27_bro_HeadbandTail_' in ob.name:
                p=coordinates(ob);p[:,1]+=shift;assign_world(ob,p)
        changes.append({'part':'headband','change':'actual source head surface +3mm, rear knot follows measured back of head',
                        'max_correction_m':float(np.linalg.norm(points-old,axis=1).max()),'topology_and_weights_preserved':True})
    report['visual_review_corrections']=changes
    return added,report
