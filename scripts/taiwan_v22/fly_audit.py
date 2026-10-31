"""Neutral fly-surface audit from evaluated Blender triangles.
Only pants surfaces in the fixed front X/Z rectangle. Not a hole count.
"""
import numpy as np
import bpy


def surface_audit(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:
        me.calc_loop_triangles()
        points=np.asarray([tuple(ev.matrix_world@v.co) for v in me.vertices])
        faces=np.asarray([list(t.vertices) for t in me.loop_triangles],int)
    finally:ev.to_mesh_clear()
    t=points[faces];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ln=np.linalg.norm(n,axis=1)
    valid=(ln>1e-10)&(t[:,:,1].max(1)<-.1)&(t[:,:,0].max(1)>=-.04)&(t[:,:,0].min(1)<=.04)&(t[:,:,2].max(1)>=.915)&(t[:,:,2].min(1)<=.968)
    t,n=t[valid],n[valid];n/=np.linalg.norm(n,axis=1)[:,None]
    a=t[:,0,[0,2]];b=t[:,1,[0,2]];c=t[:,2,[0,2]]
    den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1])
    ok=np.abs(den)>1e-12;t,n,a,b,c,den=[x[ok] for x in (t,n,a,b,c,den)]
    rays=np.asarray([(x,z) for z in np.linspace(.915,.968,121) for x in np.linspace(-.04,.04,161)])
    covered=back=near=0
    for start in range(0,len(rays),256):
        q=rays[start:start+256]
        u=((b[:,1]-c[:,1])*(q[:,None,0]-c[:,0])+(c[:,0]-b[:,0])*(q[:,None,1]-c[:,1]))/den
        v=((c[:,1]-a[:,1])*(q[:,None,0]-c[:,0])+(a[:,0]-c[:,0])*(q[:,None,1]-c[:,1]))/den
        mask=(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)
        depth=u*t[:,0,1]+v*t[:,1,1]+(1-u-v)*t[:,2,1]
        outward=np.min(np.where(mask&(n[:,1]<-.2),depth,np.inf),axis=1)
        inward=np.min(np.where(mask&(n[:,1]>.2),depth,np.inf),axis=1)
        cover=np.isfinite(np.minimum(outward,inward));covered+=int(cover.sum())
        with np.errstate(invalid='ignore'):
            delta=inward-outward
            back+=int((cover&(inward<outward-.0001)).sum())
            near+=int((cover&np.isfinite(delta)&(np.abs(delta)<.0001)).sum())
    return {'rays':len(rays),'covered':covered,'inward_surface_in_front_over_0_1mm':back,
        'inner_outer_within_0_1mm':near,'x_range_m':[-.04,.04],'z_range_m':[.915,.968],
        'scope':'Pants only, neutral front projection, not a complete-clothing visibility or hole count'}
