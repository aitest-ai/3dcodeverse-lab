/** v7.1: bounded, terrain-aware VISUAL landing for original skinned enemy GLBs.
 * The actual OSM city getGroundHeight stays the only authoritative source of
 * road/deck elevation. No invented streets, terrain meshes or gameplay physics.
 */
export const clampV71=(n,a,b)=>Math.max(a,Math.min(b,Number.isFinite(n)?n:a));
export function wreckTerrainPoseV71({elapsed=0,duration=2.25,side=1,heavy=false,
 x=0,z=0,baseY=0,scale=1,groundAt=()=>NaN,reducedMotion=false}={}){
 const p=clampV71(elapsed/Math.max(.05,duration),0,1);
 const eased=1-(1-p)**3;
 const angle=(reducedMotion?0:(side<0?-1:1)*(heavy?.41:.76)*eased);
 const width=(heavy?1.30:1.04)*clampV71(scale,.7,2),height=(heavy?3.65:3.25)*clampV71(scale,.7,2);
 // Approximate lower silhouette contact points; conservatively consider BOTH
 // feet (unlike the old fixed -18 cm sink) and broad mid-body armor edges.
 const samples=[[-width,.07],[width,.07],[-width*.8,.48],[width*.8,.48],
   [-width*.7,height*.52],[width*.7,height*.52],[-width*.42,height*.86],[width*.42,height*.86]];
 const c=Math.cos(angle),s=Math.sin(angle);
 let lowest=Infinity;
 for(const [px,py] of samples)lowest=Math.min(lowest,py*c+px*s);
 const supportLift=Math.max(0,-lowest)+.018;
 // Evaluate exact street/deck near the feet and the projected falling side.
 // Discard distant height discontinuities that might be an upper-level bridge.
 const groundCandidates=[];
 for(const [dx,dz] of [[0,0],[-Math.sin(angle)*height*.55,0],[-Math.sin(angle)*width,0],[0,width*.45]]){
   let g=NaN;
   try{g=groundAt(x+dx,z+dz,baseY);}catch{}
   if(Number.isFinite(g)&&Math.abs(g-baseY)<=.70)groundCandidates.push(g);
 }
 const floor=groundCandidates.length?Math.max(...groundCandidates):baseY;
 // No valid ground samples: preserve last known height, mark as uncertain.
 return {progress:p,roll:angle,y:floor+supportLift,
  floor,clearance:supportLift+lowest,groundVerified:groundCandidates.length>0,
  terrainSamples:groundCandidates.length,done:p>=1};
}
export function shardTerrainStepV71(s,dt,{groundAt=()=>NaN,allowSample=true}={}){
 const t=clampV71(dt,0,.05),obj=s?.obj;
 if(!obj||!Number.isFinite(s.floor))return {moved:false,reason:'invalid-shard'};
 const targetX=obj.position.x+s.vx*t,targetZ=obj.position.z+s.vz*t;
 let candidateFloor=s.floor,verified=false;
 if(allowSample && Math.abs(targetX-obj.position.x)+Math.abs(targetZ-obj.position.z)>0.002){
  let v=NaN;
  try{v=groundAt(targetX,targetZ,s.floor);}catch{}
  // Never snap up to an unrelated deck or far-away building level.
  if(Number.isFinite(v)&&Math.abs(v-s.floor)<=.60){candidateFloor=v;verified=true;}
 }
 obj.position.x=targetX;obj.position.z=targetZ;
 s.vy-=9.81*t;
 obj.position.y=Math.max(candidateFloor+.022,obj.position.y+s.vy*t);
 s.floor=candidateFloor;
 if(obj.position.y<=candidateFloor+.024){
   if(Math.abs(s.vy)<.45){s.vy=0;s.vx*=.60;s.vz*=.60;}
   else {s.vy=Math.min(2.4,Math.abs(s.vy)*.19);s.vx*=.58;s.vz*=.58;}
 }
 s.vx*=Math.max(0,1-.18*t);s.vz*=Math.max(0,1-.18*t);
 return {moved:true,verified,ground:candidateFloor,resting:s.vy===0};
}
