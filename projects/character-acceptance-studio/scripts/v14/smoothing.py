"""Short native wrap correction with dense sampling only near wrap boundaries.
Outside the last/first 1.5% of native Walk, source poses are untouched before IK.
"""
from v10.horse_solver import sample_native,align,hermite
from mathutils import Quaternion

class CyclicWalk:
    def __init__(self,rig,action):
        self.rig,self.action=rig,action
        self.duration=float(action.frame_range[1])/24
        self.window=self.duration*.015
        self.step=1/2400
        a,b,dt=self.duration-self.window,self.window,self.step
        samples=[sample_native(rig,action,t) for t in [a-dt,a,a+dt,b-dt,b,b+dt]]
        self.seam=sample_native(rig,action,0)
        self.bridge={}
        for name in samples[0]:
            out={}
            for prop in ['p','q','s']:
                vals=[s[name][prop] for s in samples]
                if prop=='q':vals=[align(v,vals[1]) for v in vals]
                out[prop]=(vals[1],vals[4],[(c-d)/(2*dt) for c,d in zip(vals[2],vals[0])],[(c-d)/(2*dt) for c,d in zip(vals[5],vals[3])])
            self.bridge[name]=out

    def pose(self,t):
        D,w=self.duration,self.window
        # Inclusive interval avoids extrapolating the exact D-w boundary.
        if w<=t<=D-w:return sample_native(self.rig,self.action,t)
        u=(((t-D) if t>=D-w else t)+w)/(2*w)
        out={name:{k:hermite(*args,u,2*w) for k,args in props.items()} for name,props in self.bridge.items()}
        # Preserve the original seam pose with a zero-endpoint/zero-end-slope quartic correction.
        bell=16*u*u*(1-u)*(1-u)
        for name,pose in out.items():
            for prop,values in pose.items():
                center=hermite(*self.bridge[name][prop],.5,2*w)
                target=align(self.seam[name][prop],center) if prop=='q' else self.seam[name][prop]
                pose[prop]=[a+bell*(b-c) for a,b,c in zip(values,target,center)]
            pose['q']=list(Quaternion(pose['q']).normalized())
        return out

def sample_times(duration,period):
    hz=2400;period_ticks=round(period*hz);N=round(duration*hz)
    assert abs(period_ticks/hz-period)<1e-9 and abs(N/hz-duration)<1e-9
    guard=round((period*.015+1/240)*hz)
    return [i/hz for i in range(N+1) if i%10==0 or min(i%period_ticks,period_ticks-i%period_ticks)<=guard]
