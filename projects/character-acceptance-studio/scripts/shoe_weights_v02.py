"""Stabilize a real shoe's lower sole, retaining editable topology/UV and upper-shoe flexibility."""
import math
from mathutils import Vector
def repair(shoe,rig):
    groups={g.index:g.name for g in shoe.vertex_groups};bones=set(rig.data.bones.keys());points=[shoe.matrix_world@v.co for v in shoe.data.vertices];changes=[]
    for side,sign in [('l',1),('r',-1)]:
        ids=[v.index for v in shoe.data.vertices if points[v.index].x*sign>0];lo=min(points[i].y for i in ids);hi=max(points[i].y for i in ids);bins={}
        for i in ids:
            key=min(31,int((points[i].y-lo)/max(.0001,hi-lo)*32));bins[key]=min(bins.get(key,math.inf),points[i].z)
        for i in ids:
            key=min(31,int((points[i].y-lo)/max(.0001,hi-lo)*32));height=points[i].z-bins[key]
            if height>=.024:continue
            w=1 if height<=.012 else 1-(height-.012)/.012
            w=w*w*(3-2*w);v=shoe.data.vertices[i];old={groups[g.group]:g.weight for g in v.groups if groups[g.group] in bones};new={n:value*(1-w) for n,value in old.items()};foot='foot_'+side;new[foot]=new.get(foot,0)+w
            new={n:value for n,value in sorted(new.items(),key=lambda kv:kv[1],reverse=True)[:4] if value>1e-8};total=sum(new.values());new={n:value/total for n,value in new.items()}
            if sum(abs(old.get(n,0)-new.get(n,0)) for n in set(old)|set(new))<1e-7:continue
            for n in old:shoe.vertex_groups[n].remove([i])
            for n,value in new.items():
                group=shoe.vertex_groups.get(n) or shoe.vertex_groups.new(name=n);group.add([i],value,'REPLACE')
            changes.append({'vertex':i,'side':side,'height_above_local_sole_m':height,'before':old,'after':new})
    return {'method':'32 longitudinal bins per actual foot; lower12mm sole rigid to foot bone,12-24mm blended to original top4 normalized weights; upper shoe unchanged','mesh':shoe.name,'modified_vertices':len(changes),'topology_uv_positions_unchanged':True,'changes':changes}
