"""Restart and gentle walking turns. Blender X/Y metres; forward -Y, native L is +X."""
import math
from v13.plan import smooth,distance,foot_target as finite_foot,schedule as finite_schedule

def rotate(p,a):
    c,s=math.cos(a),math.sin(a)
    return [c*p[0]-s*p[1],s*p[0]+c*p[1]]

def heading(t,plan,sign):
    T=plan['duration_s']
    return sign*math.radians(15)*smooth((t-T)/(3*T))

class TurnPath:
    def __init__(self,plan,sign):
        self.plan,self.sign=plan,sign;self.duration=5*plan['duration_s'];self.hz=2400
        self.points=[[0.,0.]]
        h=1/self.hz
        for i in range(round(self.duration*self.hz)):
            a,b,c=[self.velocity((i+u)*h) for u in [0,.5,1]]
            self.points.append([v+h*(x+4*y+z)/6 for v,x,y,z in zip(self.points[-1],a,b,c)])
    def velocity(self,t):
        a=heading(t,self.plan,self.sign);v=self.plan['candidate_speed_m_s']
        return [v*math.sin(a),-v*math.cos(a)]
    def at(self,t):
        if t<0:return [0.,-self.plan['candidate_speed_m_s']*t],0.
        if t>self.duration:
            return [p+(t-self.duration)*v for p,v in zip(self.points[-1],self.velocity(self.duration))],heading(self.duration,self.plan,self.sign)
        i=min(len(self.points)-1,int(t*self.hz));a=i/self.hz;h=t-a
        velocity=[self.velocity(a+u*h) for u in [0,.5,1]]
        return [p+h*(x+4*y+z)/6 for p,x,y,z in zip(self.points[i],*velocity)],heading(t,self.plan,self.sign)
    def anchor(self,foot,k):
        p=self.plan['feet'][foot];T=self.plan['duration_s'];mid=(k+p['phase']+p['duty']/2)*T
        pos,yaw=self.at(mid);offset=rotate(p['source_stance_mean_m'][:2],yaw)
        return [a+b for a,b in zip(pos,offset)],yaw
    def foot(self,t,foot):
        p=self.plan['feet'][foot];T=self.plan['duration_s'];k=math.floor(t/T-p['phase']);phase=t/T-p['phase']-k
        a,ay=self.anchor(foot,k);stance=phase<p['duty'];s=0.;lift=0.
        if not stance:
            s=(phase-p['duty'])/(1-p['duty']);b,by=self.anchor(foot,k+1);blend=smooth(s)
            a=[x+(y-x)*blend for x,y in zip(a,b)];ay+=(by-ay)*blend;lift=math.sin(math.pi*s)**2
        root,yaw=self.at(t);local=rotate([a-b for a,b in zip(a,root)],-yaw)
        return {'stance':stance,'phase':s,'world_xy':a,'x':local[0],'y':local[1],'sole':.003+p['source_max_lift_m']*lift,'rotation_blend':lift,'yaw_relative':ay-yaw,'world_yaw':ay}

def restart_foot(t,plan,foot):
    p=plan['feet'][foot];T=plan['duration_s']
    anchor=finite_foot(8*T,plan,foot)['y']
    for row in finite_schedule(plan,foot):
        if t<row['off']:break
        if t<row['on']:
            s=(t-row['off'])/(row['on']-row['off']);lift=math.sin(math.pi*s)**2;world=anchor+(row['anchor']-anchor)*smooth(s)
            return {'stance':False,'phase':s,'world_xy':[p['source_stance_mean_m'][0],world],'x':p['source_stance_mean_m'][0],'y':world+distance(t,plan),'sole':.003+p['source_max_lift_m']*lift,'rotation_blend':lift,'yaw_relative':0.,'world_yaw':0.}
        anchor=row['anchor']
    return {'stance':True,'phase':0.,'world_xy':[p['source_stance_mean_m'][0],anchor],'x':p['source_stance_mean_m'][0],'y':anchor+distance(t,plan),'sole':.003,'rotation_blend':0.,'yaw_relative':0.,'world_yaw':0.}

def specs(plan):
    T=plan['duration_s'];stride=plan['candidate_stride_m']
    out={'RestartWalk':{'duration':3*T,'root_end':{'x':0,'z':2*stride,'yaw':0},'kind':'restart','entry':'StandStopped','exit':'WalkWorld'}}
    for name,sign in [('WalkTurnLeft',1),('WalkTurnRight',-1)]:
        path=TurnPath(plan,sign);xy,yaw=path.at(5*T)
        out[name]={'duration':5*T,'root_end':{'x':xy[0],'z':-xy[1],'yaw':yaw},'kind':'turn','sign':sign,'entry':'WalkWorld','exit':'WalkWorld'}
    return out
