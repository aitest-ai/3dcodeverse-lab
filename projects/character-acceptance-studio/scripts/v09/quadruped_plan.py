"""Curved walk contacts: native four-paw phase offsets, fixed world stance anchors, no biped transfer."""
import math

def smooth(x):return x*x*x*(10-15*x+6*x*x)
def rotate(v,yaw):
 c,s=math.cos(yaw),math.sin(yaw);return [c*v[0]-s*v[1],s*v[0]+c*v[1],v[2]]
class CurvedWalk:
 def __init__(self,paws,plan,period,cycles=4):self.paws,self.plan,self.period,self.cycles=paws,plan,period,cycles;self.duration=period*cycles;self.radius=plan['stride']*cycles/(math.pi/2)
 def path(self,t,sign):
  angle=sign*math.pi/2*t/self.duration;r=self.radius;return [sign*r*(1-math.cos(angle)),-sign*r*math.sin(angle),0],angle
 def sample(self,t,key,sign):
  phase=t/self.period-self.plan['phase'][key];cycle=math.floor(phase);u=phase-cycle;duty=self.plan['duty'];start=(cycle+self.plan['phase'][key])*self.period
  def anchor(time):
   root,yaw=self.path(time+duty*self.period/2,sign);v=rotate(self.paws[key]['center'],yaw);return [root[0]+v[0],root[1]+v[1],v[2]],yaw
  a,ya=anchor(start);b,yb=anchor(start+self.period)
  if u<duty:return {'P':a,'yaw':ya,'clearance':0,'contact':True,'contact_id':cycle}
  v=(u-duty)/(1-duty);w=smooth(v);return {'P':[x+(y-x)*w for x,y in zip(a,b)],'yaw':ya+(yb-ya)*w,'clearance':self.plan['lift']*math.sin(math.pi*v)**2,'contact':False,'contact_id':cycle}
