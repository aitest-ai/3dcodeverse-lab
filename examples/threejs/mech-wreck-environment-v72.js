/**
 * v7.2: visual contact between original skinned mecha, actual OSM walls,
 * authentic sampled street/deck elevations and bounded metal fragments.
 * NEVER changes collision bodies, attack rays, mission HP or original city.
 * A few conservative silhouette points are NOT exact skinned-mesh physics.
 */
import {wreckTerrainPoseV71, shardTerrainStepV71} from './mech-wreck-ground-v71.js';
const clamp=(n,a,b)=>Math.min(b,Math.max(a,Number.isFinite(n)?n:a));
const finite=Number.isFinite;

/** Test three enlarged armor points against the original OSM colliders.
 * Bound: one tested roll costs at most 3 wall queries; the entire routine
 * costs at most 15 (target, previous pose and three refinements).
 */
export function wreckWallPoseV72({elapsed=0,duration=2.25,side=1,heavy=false,
 x=0,z=0,baseY=0,scale=1,groundAt=()=>NaN,wallAt=()=>false,
 reducedMotion=false,previousRoll=0}={}) {
 const base=wreckTerrainPoseV71({elapsed,duration,side,heavy,x,z,baseY,scale,groundAt,reducedMotion});
 const width=(heavy?1.30:1.04)*clamp(scale,.7,2);
 const height=(heavy?3.65:3.25)*clamp(scale,.7,2);
 const points=[[width*.85,height*.58],[-width*.85,height*.58],[0,height*.88]];
 let checks=0,contacts=0,blocked=false;
 const support=roll=>{
  const c=Math.cos(roll),s=Math.sin(roll);
  let lowest=Infinity;
  for(const [px,py] of [[-width,.07],[width,.07],[-width*.8,.48],[width*.8,.48],
    [-width*.7,height*.52],[width*.7,height*.52],[-width*.42,height*.86],[width*.42,height*.86]]){
   lowest=Math.min(lowest,py*c+px*s);
  }
  return Math.max(0,-lowest)+.018;
 };
 const collides=roll=>{
  const c=Math.cos(roll),s=Math.sin(roll),y0=base.floor+support(roll);
  for(const [px,py] of points){
   const xx=x+px*c-py*s, yy=y0+px*s+py*c;
   checks++;
   let hit=true; // invalid callback must not allow an unexamined wall crossing
   // Include the swept segment from the upright armor point. Thin facade
   // panels must not be skipped just because both endpoints are outside.
   try{hit=!!wallAt(xx,z,yy,.11,x+px,z,y0+py);}catch{hit=true;}
   if(hit){contacts++;return true;}
  }
  return false;
 };
 let allowed=base.roll;
 if(Math.abs(allowed)>1e-5 && collides(allowed)){
  blocked=true;
  // Narrow toward the last admitted safe angle. If even the previous pose
  // collides because of a dynamic facade, stop rolling rather than clipping.
  const sign=Math.sign(allowed),want=Math.abs(allowed);
  const last=clamp(Math.abs(previousRoll),0,want);
  let safe=0,unsafe=want;
  if(last>0 && !collides(sign*last))safe=last;
  for(let i=0;i<3;i++){
   const mid=(safe+unsafe)*.5;
   if(collides(sign*mid))unsafe=mid;else safe=mid;
  }
  allowed=sign*safe;
 }
 const lift=support(allowed),result={...base,roll:allowed,y:base.floor+lift,
  wallBlocked:blocked,wallQueries:checks,wallContacts:contacts};
 return result;
}

/** Safe horizontal shard step. When the shared wall-query budget is empty,
 * hold horizontal motion (still apply gravity) rather than blindly pass walls.
 * park duration is reserved for VERIFIED authentic street/deck elevation.
 */
export function shardEnvironmentStepV72(s,dt,{groundAt=()=>NaN,wallAt=()=>false,
 allowGround=false,allowWall=false,maxParkedAge=7}={}) {
 if(!s?.obj?.position||!finite(s.floor))return {moved:false,reason:'invalid-shard',wallQueries:0};
 const step=clamp(dt,0,.05);
 if(s.parked){
  s.parkAge=(s.parkAge||0)+step;
  s.life=Math.max(s.life,Math.max(0,maxParkedAge-s.parkAge));
  return {moved:false,parked:true,wallQueries:0,groundQueries:0};
 }
 const old={x:s.obj.position.x,y:s.obj.position.y,z:s.obj.position.z,
  vx:s.vx,vz:s.vz,floor:s.floor};
 if(!allowWall){s.vx=0;s.vz=0;}
 const grounded=shardTerrainStepV71(s,step,{groundAt,allowSample:allowGround});
 if(!allowWall){s.vx=old.vx*Math.max(0,1-.18*step);s.vz=old.vz*Math.max(0,1-.18*step);}
 let hit=false,queries=0;
 if(allowWall){
  // Actual original OSM pointInBuilding callback, independent of the
  // current shard visual material. Query the segment mid-point as well.
  const midX=(old.x+s.obj.position.x)*.5,midZ=(old.z+s.obj.position.z)*.5;
  const nearY=Math.min(s.obj.position.y,old.y);
  try{
   queries++;hit=!!wallAt(midX,midZ,nearY,.075,old.x,old.z,old.y);
   if(!hit){queries++;hit=!!wallAt(s.obj.position.x,s.obj.position.z,s.obj.position.y,.075,old.x,old.z,old.y);}
  }catch{hit=true;}
  if(hit){
   s.obj.position.x=old.x;s.obj.position.z=old.z;
   s.vx=-old.vx*.22;s.vz=-old.vz*.22;
   // The shard may still fall vertically, but it must not retain a
   // floor sampled beyond an impassable wall.
   s.floor=old.floor;
   s.obj.position.y=Math.max(old.floor+.022,s.obj.position.y);
  }
 }
 let verified=!!grounded.verified,groundQueries=verified?1:0;
 // A stationary shard needs ONE explicit ground confirmation too: v7.1's
 // terrain step samples only when x/z changed. Do not park on guessed floor.
 if(allowGround&&!verified &&
    Math.abs(s.obj.position.x-old.x)+Math.abs(s.obj.position.z-old.z)<.002 &&
    s.obj.position.y<=s.floor+.055){
   let g=NaN;groundQueries++;
   try{g=groundAt(s.obj.position.x,s.obj.position.z,s.floor);}catch{}
   if(finite(g)&&Math.abs(g-s.floor)<=.60){verified=true;s.floor=g;
     s.obj.position.y=Math.max(s.obj.position.y,g+.022);}
 }
 if(verified)s.groundVerifiedEver=true;
 // A true OSM ground sample is necessary to keep this visual chip longer.
 const speed=Math.hypot(s.vx,s.vz,s.vy);
 const onGround=s.obj.position.y<=s.floor+.027;
 s.settledTime=(onGround&&speed<.22&&s.groundVerifiedEver&&!hit)?(s.settledTime||0)+step:0;
 if(s.settledTime>.25 && !s.parked){
  s.parked=true;s.parkAge=0;s.vx=0;s.vz=0;s.vy=0;
  s.obj.position.y=s.floor+.022;
  s.life=Math.max(s.life,Math.min(7,maxParkedAge));
 }
 return {...grounded,hitWall:hit,wallQueries:queries,groundQueries,verified,
  parked:!!s.parked,contactVerified:!!s.groundVerifiedEver};
}
