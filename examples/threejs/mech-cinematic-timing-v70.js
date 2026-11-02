/** Portable v7.0 cinematic math: deterministic and bounded; no GPU/DOM/dependencies.
 * Existing HP, OSM geometry, damage, and model animation remain authoritative. */
export const cinematicClampV70=(x,a,b)=>Math.min(b,Math.max(a,Number.isFinite(x)?x:a));
export function wreckPoseV70(elapsed,duration,side=1,heavy=false){
 const p=cinematicClampV70(elapsed/Math.max(.05,duration),0,1);
 const eased=1-(1-p)**3;
 return {progress:p,roll:(side<0?-1:1)*(heavy?.41:.76)*eased,sink:.18*eased,
   done:p>=1};
}
export function cinematicRingV70(age,duration,kind='impact'){
 const p=cinematicClampV70(age/Math.max(.05,duration),0,1);
 return {radius:(kind==='victory'?1.4:.58)+p*(kind==='victory'?6.3:2.8),opacity:.75*(1-p)**2,done:p>=1};
}
export function shardCountV70(role,remaining,max){
 return Math.min(Math.max(0,Math.trunc(remaining)),Math.max(0,Math.trunc(max)),role==='heavy'?19:11);
}
