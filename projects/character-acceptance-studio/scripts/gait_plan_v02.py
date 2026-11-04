"""Explicit root/contact/step plans, in metres and seconds. No source bind or mesh copied.
Ground anchors stay in world space. Animation quality still requires actual mesh/browser review.
"""
import math
def smooth(x):
    x=max(0,min(1,x));return x*x*x*(10+x*(-15+6*x))
def lerp(a,b,w):return [x+(y-x)*w for x,y in zip(a,b)]
def rot(p,yaw):
    c,s=math.cos(yaw),math.sin(yaw);return [c*p[0]-s*p[1],s*p[0]+c*p[1],p[2] if len(p)>2 else 0]
class Planner:
    def __init__(self,leg,width,walk_period,run_period):
        self.leg=leg;self.width=width;self.periods={'Walk':walk_period,'Run':run_period};self.strides={'Walk':leg*1.10,'Run':leg*2.4}
        self.duration={'Idle':2.5,'Walk':walk_period,'Run':run_period,'Start':walk_period+.4,'Stop':walk_period+.4,'TurnLeft':1.6,'TurnRight':1.6}
    def idle(self,side):return [(1 if side=='l' else -1)*self.width,0,0]
    def steady(self,name,phase,side):
        period=self.periods[name];stride=self.strides[name];a=(-.025 if side=='l' else .475) if name=='Walk' else (.01 if side=='l' else .51);duty=.65 if name=='Walk' else .30
        k=math.floor(phase-a);start=a+k;end=start+duty;mid=start+duty/2
        P=[self.idle(side)[0],-stride*mid,0]
        if phase<=end:
            heel=.12*period if name=='Walk' else .04*period;toe=.14*period if name=='Walk' else .08*period
            elapsed=(phase-start)*period;remaining=(end-phase)*period
            pitch=(-.10*(1-smooth(elapsed/heel))) if elapsed<heel and name=='Walk' else (.22 if name=='Walk' else .18)*smooth(1-remaining/toe) if remaining<toe else 0
            mode='heel' if pitch<-.000001 else 'toe' if pitch>.000001 else 'flat'
            return dict(P=P,pitch=pitch,yaw=0,contact=True,pivot=mode,contact_id=f'{side}:{k}',clearance=0)
        u=(phase-end)/(1-duty);Q=[P[0],P[1]-stride,0]
        pitch=self.swing_pitch(u,.22 if name=='Walk' else .18,-.10 if name=='Walk' else 0)
        return dict(P=lerp(P,Q,smooth(u)),pitch=pitch,yaw=0,contact=False,pivot='swing',contact_id=None,clearance=(.075 if name=='Walk' else self.leg*.17)*math.sin(math.pi*u)**2,pivot_blend=smooth(u))
    @staticmethod
    def swing_pitch(u,first,last):
        return first+(-.18-first)*smooth(u/.45) if u<.45 else -.18+(last+.18)*smooth((u-.45)/.55)
    def track(self,t,D,side,initial,steps,initial_pitch=0,final_pitch=0,initial_yaw=0):
        previous=initial;previous_yaw=initial_yaw;land=0
        for index,step in enumerate(steps):
            lift,end,target,yaw=step
            if t<lift:
                return self.stance(t,land,lift,D,previous,previous_yaw,side+':'+str(index),initial_pitch if land==0 else -.1,None)
            if t<=end:
                u=(t-lift)/(end-lift);last_pitch=final_pitch if index==len(steps)-1 and end>=D-.001 else -.1
                return dict(P=lerp(previous,target,smooth(u)),yaw=previous_yaw+(yaw-previous_yaw)*smooth(u),pitch=self.swing_pitch(u,.22,last_pitch),pivot='swing',pivot_blend=smooth(u),contact=False,contact_id=None,clearance=.065*math.sin(math.pi*u)**2)
            previous,previous_yaw,land=target,yaw,end
        return self.stance(t,land,D,D,previous,previous_yaw,side+':final',initial_pitch if land==0 else -.1,final_pitch)
    @staticmethod
    def stance(t,land,lift,D,P,yaw,identifier,first,last):
        duration=max(.001,lift-land);heeltime=min(.12,duration*.25);toetime=min(.13,duration*.25)
        if last is not None and duration<.2:pitch=first+(last-first)*smooth((t-land)/duration)
        elif t<land+heeltime:pitch=first*(1-smooth((t-land)/heeltime))
        elif t>lift-toetime:pitch=(.22 if last is None else last)*smooth((t-(lift-toetime))/toetime)
        else:pitch=0
        return dict(P=P,yaw=yaw,pitch=pitch,contact=True,pivot='heel' if pitch<-.000001 else 'toe' if pitch>.000001 else 'flat',contact_id=identifier,clearance=0)
    def sample(self,name,t):
        D=self.duration[name];u=max(0,min(1,t/D));stride=self.strides['Walk'];T=self.periods['Walk'];v=stride/T
        yaw=0;root=[0,0,0];body='Idle';phase=t/2.5;blend=0
        if name in ['Walk','Run']:
            body=name;phase=t/self.periods[name];root=[0,-self.strides[name]*phase,0];feet={s:self.steady(name,phase,s) for s in ['l','r']}
        elif name=='Idle':feet={s:dict(P=self.idle(s),yaw=0,pitch=0,contact=True,pivot='flat',contact_id=s+':idle',clearance=0) for s in ['l','r']}
        elif name in ['Start','Stop']:
            a=.8
            def accel_distance(x):
                if x>=a:return v*(x-a/2)
                q=max(0,x/a);return v*a*(q**3-.5*q**4)
            distance=accel_distance(t) if name=='Start' else stride-accel_distance(D-t)
            root=[0,-distance,0];body='Walk'
            # Hermite gait phase with a steady-walk derivative at the linked endpoint.
            if name=='Start':phase=.5+(3*u*u-2*u*u*u)*1.5+(u*u*u-u*u)*D/T;blend=smooth(u/.25)
            else:phase=(3*u*u-2*u*u*u)*1.5+(u*u*u-2*u*u+u)*D/T;blend=1-smooth((u-.75)/.25)
            L=self.idle('l');R=self.idle('r')
            if name=='Start':
                steps={'l':[(.12*D,.36*D,[L[0],-.3*stride,0],0),(.70*D,.98*D,[L[0],-1.3*stride,0],0)],'r':[(.40*D,.64*D,[R[0],-.8*stride,0],0)]}
                feet={s:self.track(t,D,s,self.idle(s),steps[s],0,self.steady('Walk',0,s)['pitch']) for s in ['l','r']}
            else:
                steps={'l':[(.42*D,.68*D,[L[0],-stride,0],0)],'r':[(.10*D,.38*D,[R[0],-.65*stride,0],0),(.72*D,.95*D,[R[0],-stride,0],0)]}
                feet={s:self.track(t,D,s,self.steady('Walk',0,s)['P'],steps[s],self.steady('Walk',0,s)['pitch'],0) for s in ['l','r']}
        else:
            sign=1 if name=='TurnLeft' else -1;angle=sign*math.pi/2;outside='r' if sign>0 else 'l';inside='l' if outside=='r' else 'r'
            yaw=angle*.5*smooth((u-.15)/.33)+angle*.5*smooth((u-.52)/.33);root=[sign*.06*smooth(u),-.05*smooth(u),0]
            center=[sign*.06,-.05,0];feet={}
            for s in ['l','r']:
                target=[a+b for a,b in zip(center,rot(self.idle(s),angle))];lift,end=(.15,.48) if s==outside else (.52,.85)
                feet[s]=self.track(t,D,s,self.idle(s),[(lift*D,end*D,target,angle)],0,0)
            phase=t/2.5*(1-smooth((u-.85)/.15))
        return {'root':root,'yaw':yaw,'body':body,'phase':phase,'walk_blend':blend,'feet':feet,'duration':D}
