"""V21 wool-pants waistband candidate, editing existing source coordinates only.
The wool trouser waist has an open fly seam. It is not the cargo closed ring.
"""
from collections import Counter, defaultdict
import numpy as np


def periodic(theta, values, targets):
    order=np.argsort(theta); t=np.asarray(theta)[order]; v=np.asarray(values)[order]
    return np.interp(targets,np.r_[t[-1]-2*np.pi,t,t[0]+2*np.pi],np.r_[v[-1],v,v[0]])


def opening(points, faces, upper):
    pts=np.asarray(points,float)
    _,first,inv=np.unique(np.round(pts,6),axis=0,return_index=True,return_inverse=True)
    p=pts[first]; counts=Counter()
    for f in faces:
        ids=inv[np.asarray(f,int)]
        for a,b in zip(ids,np.roll(ids,-1)):
            if a!=b: counts[tuple(sorted((int(a),int(b))))]+=1
    adj=defaultdict(set)
    for (a,b),n in counts.items():
        if n==1: adj[a].add(b);adj[b].add(a)
    seen=set(); candidates=[]
    for root in adj:
        if root in seen: continue
        seen.add(root); pending=[root]; component=[]
        while pending:
            v=pending.pop();component.append(v)
            for n in adj[v]:
                if n not in seen: seen.add(n);pending.append(n)
        if len(component)>=12 and np.ptp(p[component,0])>.15:
            candidates.append(component)
    if not candidates: raise ValueError('No broad original garment opening')
    ids=np.array((max if upper else min)(candidates,key=lambda c:p[c,2].mean()))
    degree=[len(adj[int(i)]) for i in ids]
    if max(degree)>2 or degree.count(1) not in (0,2):
        raise ValueError('Unsupported branching opening; do not invent a closed rim')
    return p,ids,{'boundary_vertices':len(ids),'open_endpoints':degree.count(1),
                 'topology':'open-fly path' if degree.count(1) else 'closed ring'}


def candidate(pants,pant_faces,shirt,shirt_faces):
    points=np.asarray(pants,float)
    p,rim,topology=opening(points,pant_faces,True)
    s,hem,_=opening(shirt,shirt_faces,False)
    center=np.array([0.,(s[hem,1].min()+s[hem,1].max())/2])
    angle=lambda q:np.arctan2(q[:,1]-center[1],q[:,0]-center[0])
    a=angle(p[rim]); b=angle(s[hem]); order=np.argsort(a); reverse=np.argsort(order)
    lower=periodic(b,s[hem,2],a)+.018
    target=np.maximum(p[rim,2],lower)[order]
    for _ in range(50):
        target=np.maximum(lower[order],.25*np.roll(target,1)+.5*target+.25*np.roll(target,-1))
    rise=target[reverse]-p[rim,2]
    radius=np.linalg.norm(p[rim,:2]-center,axis=1)
    shirt_radius=periodic(b,np.linalg.norm(s[hem,:2]-center,axis=1),a)
    grow=np.maximum(0,shirt_radius+.008-radius)
    theta=angle(points); local_top=periodic(a,p[rim,2],theta)
    fade=np.clip((points[:,2]-(local_top-.16))/.16,0,1)
    fade=fade*fade*(3-2*fade)
    radial=points[:,:2]-center
    radial/=np.maximum(np.linalg.norm(radial,axis=1)[:,None],1e-9)
    delta=np.zeros_like(points)
    delta[:,:2]=radial*periodic(a,grow,theta)[:,None]*fade[:,None]
    delta[:,2]=periodic(a,rise,theta)*fade
    if not np.isfinite(delta).all() or np.max(np.linalg.norm(delta,axis=1))>.055:
        raise ValueError('Waist fit exceeds 55mm safety limit')
    return delta,center,fade,{'pants_opening':topology,'shirt_hem_vertices':len(hem),
        'roi_z':[float(s[hem,2].min()-.065),float(p[rim,2].max()+.10)],
        'overlap_m':.018,'radial_clearance_m':.008,'falloff_m':.16}
