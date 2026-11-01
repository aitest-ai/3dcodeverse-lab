/**
 * v6.6: bounded enemy stagnation detection. Recovery asks the existing A*
 * navigator to REPLAN, using the original Taipei OSM collision on all steps.
 * This module never moves a model, teleports it, changes HP or ignores walls.
 */
const clamp=(n,a,b)=>Math.min(b,Math.max(a,Number.isFinite(n)?n:a));
const isPoint=p=>p&&Number.isFinite(p.x)&&Number.isFinite(p.z);
const distance=(a,b)=>Math.hypot(a.x-b.x,a.z-b.z);
export function createEnemyRecoveryV66({window=.92,minProgress=.34,blockedDelay=.45,
 recoveryDuration=2.6,replanCooldown=1.5,maxAttempts=3,restAfterExhaustion=4.0}={}){
 for(const x of [window,minProgress,blockedDelay,recoveryDuration,replanCooldown,restAfterExhaustion])
   if(!Number.isFinite(x)||x<=0||x>30)throw new RangeError('invalid recovery configuration');
 if(!Number.isInteger(maxAttempts)||maxAttempts<1||maxAttempts>8)throw new RangeError('invalid retry limit');
 let elapsed=0,anchor=null,anchorGoal=null,blockedFor=0,recoverFor=0,cooldown=0,rest=0;
 let attempts=0,totalReplans=0,exhausted=0,reason='idle';
 function reset(){elapsed=0;anchor=null;anchorGoal=null;blockedFor=0;recoverFor=0;cooldown=0;
  rest=0;attempts=0;totalReplans=0;exhausted=0;reason='idle';}
 function update(dt,{before,after,mode='approach',blocked=false,moving=false,
  goalDistance=Infinity,engaged=true}={}){
   const step=clamp(dt,0,.05);
   cooldown=Math.max(0,cooldown-step);recoverFor=Math.max(0,recoverFor-step);
   rest=Math.max(0,rest-step);
   if(!isPoint(before)||!isPoint(after))return {requestReplan:false,reason:'missing-position',...snapshot()};
   if(!engaged||['telegraph','recover'].includes(mode)||!Number.isFinite(goalDistance)||goalDistance<4){
     elapsed=0;blockedFor=0;anchor={x:after.x,z:after.z};anchorGoal=goalDistance;reason='engaged';
     return {requestReplan:false,...snapshot()};
   }
   if(!anchor){anchor={x:before.x,z:before.z};anchorGoal=goalDistance;}
   const moved=distance(before,after);
   if(blocked&&!moving && moved<.02)blockedFor+=step;
   else blockedFor=Math.max(0,blockedFor-step*1.5);
   elapsed+=step;
   const progress=distance(anchor,after);
   const realAdvance=Number.isFinite(anchorGoal) && anchorGoal-goalDistance>.22;
   if(progress>Math.max(minProgress*2,.70) && (mode==='navigate'||realAdvance)){ 
     // Confirmed meaningful distance travelled; previous route obstacles may
     // have cleared, so the next obstacle gets its own capped retry budget.
     anchor={x:after.x,z:after.z};anchorGoal=goalDistance;elapsed=0;blockedFor=0;attempts=0;rest=0;
     reason='moving';
     return {requestReplan:false,...snapshot()};
   }
   const stagnant=elapsed>=window && progress<minProgress;
   const blockedEnough=blockedFor>=blockedDelay;
   if((stagnant||blockedEnough)&&cooldown===0&&rest===0){
     if(attempts>=maxAttempts){
       exhausted++;rest=restAfterExhaustion;recoverFor=0;cooldown=replanCooldown;
       elapsed=0;blockedFor=0;anchor={x:after.x,z:after.z};anchorGoal=goalDistance;reason='route-exhausted';
       return {requestReplan:false,...snapshot()};
     }
     attempts++;totalReplans++;cooldown=replanCooldown;recoverFor=recoveryDuration;
     elapsed=0;blockedFor=0;anchor={x:after.x,z:after.z};anchorGoal=goalDistance;reason='replan';
     return {requestReplan:true,...snapshot()};
   }
   if(elapsed>=window){elapsed=0;anchor={x:after.x,z:after.z};anchorGoal=goalDistance;}
   reason=rest>0?'cooldown':recoverFor>0?'recovering':'observing';
   return {requestReplan:false,...snapshot()};
 }
 function snapshot(){return {forceNavigation:recoverFor>0&&rest===0,
   recoveryRemaining:recoverFor,restRemaining:rest,
   cooldownRemaining:cooldown,attempts,totalReplans,exhausted,reason};}
 return {update,snapshot,reset};
}
