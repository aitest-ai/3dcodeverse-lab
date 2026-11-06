// Ground-plane geometry only. No mass, inertia or force estimate is implied.
export const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
export function hull2(points){
 const p=Array.from(new Map(points.map(v=>[v.join(','),v])).values()).sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
 if(p.length<3)return p;const lower=[],upper=[];
 for(const v of p){while(lower.length>1&&cross(lower.at(-2),lower.at(-1),v)<=0)lower.pop();lower.push(v)}
 for(const v of p.toReversed()){while(upper.length>1&&cross(upper.at(-2),upper.at(-1),v)<=0)upper.pop();upper.push(v)}
 return lower.slice(0,-1).concat(upper.slice(0,-1));
}
function segmentDistance(p,a,b){const dx=b[0]-a[0],dz=b[1]-a[1],d=dx*dx+dz*dz,u=d?Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dz)/d)):0;return Math.hypot(p[0]-a[0]-u*dx,p[1]-a[1]-u*dz)}
export function signedMargin(p,hull){if(!hull.length)return null;if(hull.length===1)return -Math.hypot(p[0]-hull[0][0],p[1]-hull[0][1]);let distance=Infinity,inside=hull.length>=3;for(let i=0;i<hull.length;i++){const a=hull[i],b=hull[(i+1)%hull.length];distance=Math.min(distance,segmentDistance(p,a,b));if(cross(a,b,p)<-1e-10)inside=false}return inside?distance:-distance}
export function supportState(plan,time){const phase=time/plan.duration_s;return Object.fromEntries(Object.entries(plan.feet).map(([key,p])=>{const a=phase-p.phase,cycle=Math.floor(a+1e-10),u=a-cycle;return [key,{stance:u>=-1e-10&&u<p.duty-1e-10,cycle,phase:u}]}))}
export function schedule(plan){
 const boundaries=[0,1,...Object.values(plan.feet).flatMap(p=>[p.phase,(p.phase+p.duty)%1])].sort((a,b)=>a-b);const intervals=[];
 for(let i=0;i<boundaries.length-1;i++){const start=boundaries[i],end=boundaries[i+1];if(end-start<1e-10)continue;const stance=Object.entries(supportState(plan,(start+end)/2*plan.duration_s)).filter(([,p])=>p.stance).map(([k])=>k);intervals.push({start,end,stance,count:stance.length})}
 return intervals;
}
