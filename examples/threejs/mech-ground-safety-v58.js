/** Taipei Mech v5.8: conservative ground-height checks; no teleport, damage or physics overrides. */
const finite = n => typeof n==='number' && Number.isFinite(n);
export function canStartGroundedDodge({y,groundY,verticalVelocity=0,tolerance=.14,maxVerticalVelocity=.22}={}) {
 if(![y,groundY,verticalVelocity].every(finite))return {allowed:false,reason:'ground-unavailable'};
 if(Math.abs(verticalVelocity)>maxVerticalVelocity||Math.abs(y-groundY)>tolerance)return {allowed:false,reason:'airborne'};
 return {allowed:true,reason:'grounded'};
}
export function reconcileGroundedDodgeHeight({y,oldGround,newGround,verticalVelocity=0,tolerance=.14,maxStep=.38}={}) {
 if(![y,oldGround,newGround,verticalVelocity].every(finite))return {y,changed:false,reason:'ground-unavailable'};
 if(Math.abs(verticalVelocity)>.22||Math.abs(y-oldGround)>tolerance)return {y,changed:false,reason:'airborne'};
 if(Math.abs(newGround-oldGround)>maxStep)return {y,changed:false,reason:'step-too-high'};
 return {y:newGround,changed:Math.abs(newGround-y)>1e-5,reason:'grounded'};
}
