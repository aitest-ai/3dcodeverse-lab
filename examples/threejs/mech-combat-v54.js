/**
 * Taipei Mech v5.4: damped visual-only combat impulses.
 * Layer on spine + right-arm AFTER mixer.update and BEFORE IK/hydraulics.
 * Does not change controller positions, weapon rays, collision or invulnerability.
 */
export function createMechCombatMotion() {
 const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
 const keys=['pitch','roll','arm','head'];
 const pose={pitch:0,roll:0,arm:0,head:0};
 const velocity={pitch:0,roll:0,arm:0,head:0};
 const events={light:0,charged:0,heavy:0,hit:0,dodge:0};
 const profiles={
  light:{pitch:-.34,roll:.005,arm:-.85,head:.02},
  charged:{pitch:-.95,roll:.04,arm:-1.85,head:.08},
  heavy:{pitch:-1.16,roll:.09,arm:-1.65,head:.11},
  hit:{pitch:.95,roll:-.60,arm:.27,head:-.22}
 };
 let dodgeTime=0,side=1,clock=0,lastDodge=-99,lastKind='idle',disposed=false;
 function impulse(kind,{damage=0}={}){
  if(disposed || !Object.prototype.hasOwnProperty.call(profiles,kind))return false;
  const scale=kind==='hit'?clamp(.65+(Number(damage)||0)/50,.65,1.45):1;
  for(const c of keys)velocity[c]=clamp(velocity[c]+profiles[kind][c]*scale,-3.5,3.5);
  events[kind]++;lastKind=kind;return true;
 }
 function dodge(direction=1){
  if(disposed||dodgeTime>0||clock-lastDodge<.72)return false;
  side=Number(direction)<0?-1:1;dodgeTime=.46;lastDodge=clock;events.dodge++;lastKind='dodge';return true;
 }
 function snapshot(){return {...pose,dodgeLean:0,dodgePitch:0,activeDodge:dodgeTime>0,kind:lastKind,events:{...events}};}
 function update(dt){
  if(disposed)return snapshot();
  const step=clamp(Number.isFinite(dt)?dt:0,0,.05);clock+=step;
  const n=Math.max(1,Math.ceil(step/.0125)),h=step/n;
  for(let i=0;i<n;i++)for(const c of keys){
   const omega=c==='arm'?18:c==='head'?14:11;
   velocity[c]+=(-2*omega*velocity[c]-omega*omega*pose[c])*h;
   pose[c]=clamp(pose[c]+velocity[c]*h,-.23,.23);
  }
  const t=dodgeTime,progress=1-t/.46;
  dodgeTime=Math.max(0,t-step);
  const sway=t>0?Math.sin(Math.PI*clamp(progress,0,1)):0;
  return {...snapshot(),dodgeLean:side*.19*sway,dodgePitch:-.055*sway,activeDodge:t>0};
 }
 function reset(){for(const c of keys){pose[c]=0;velocity[c]=0;}dodgeTime=0;clock=0;lastDodge=-99;lastKind='idle';}
 function dispose(){disposed=true;reset();}
 return {impulse,dodge,snapshot,update,reset,dispose};
}
