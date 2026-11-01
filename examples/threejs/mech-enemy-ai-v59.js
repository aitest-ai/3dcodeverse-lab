/**
 * Taipei Mech v5.9: pure tactical AI with deterministic, bounded movement.
 * The host supplies authentic OSM collision / terrain / line-of-sight and
 * remains authoritative for damage. No AI teleportation or invulnerability.
 * Coordinates x,z are world meters. Update dt is seconds.
 */
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const finite = Number.isFinite;
export const ENEMY_ROLES_V59 = Object.freeze({
  assault: Object.freeze({label:'突擊型', hp:100, scale:1, radius:1.45,
    speed:3.25, preferredMin:9, preferredMax:17, range:40,
    windup:.43, cooldown:1.45, recovery:.20, damage:7, hitRadius:1.65}),
  ranger: Object.freeze({label:'遠距型', hp:80, scale:.94, radius:1.34,
    speed:2.4, preferredMin:27, preferredMax:39, range:66,
    windup:.75, cooldown:2.0, recovery:.35, damage:9, hitRadius:1.50}),
  heavy: Object.freeze({label:'重裝型', hp:180, scale:1.23, radius:1.85,
    speed:1.52, preferredMin:14, preferredMax:24, range:52,
    windup:1.10, cooldown:2.8, recovery:.54, damage:16, hitRadius:2.00})
});
const validPoint = p => p && finite(p.x) && finite(p.z);
const distance = (a,b) => Math.hypot(a.x-b.x,a.z-b.z);

export function createEnemyBrainV59({role='assault',id=1}={}) {
  const profile = ENEMY_ROLES_V59[role];
  if (!profile) throw new RangeError('Unknown enemy role');
  if (!Number.isInteger(id) || id<1) throw new TypeError('id must be positive integer');
  let mode='approach', clock=0, timer=0, cooldown=.38+id*.19;
  let lockedTarget=null, shots=0, warningCount=0, blockedSteps=0;
  let preferredSide=id%2 ? 1 : -1;
  let lastFire=null,lastStage='normal',lockedWindup=profile.windup;
  const isOverdrive=()=>role==='heavy'&&lastStage==='overdrive';
  function snapshot() {
    return {id,role,label:profile.label,mode,windup:mode==='telegraph' ? timer : 0,
      windupTotal:mode==='telegraph'?lockedWindup:profile.windup*(isOverdrive()?.82:1),cooldown,shots,warningCount,blockedSteps,
      lockedTarget:lockedTarget ? {...lockedTarget} : null,fireRange:profile.range};
  }
  function reset() {
    mode='approach';clock=0;timer=0;cooldown=.38+id*.19;
    lockedTarget=null;shots=0;warningCount=0;blockedSteps=0;
    preferredSide=id%2 ? 1 : -1;lastFire=null;lastStage='normal';lockedWindup=profile.windup;
  }
  function update({dt, position, target, visible=false, navigationTarget=null, preferNavigation=false, allowWindup=true, stage='normal', canOccupy=()=>true, sampleGround=()=>null}={}) {
    lastStage=stage==='overdrive'?'overdrive':'normal';
    const faster=isOverdrive();
    if(!validPoint(position)||!validPoint(target))return {...snapshot(),position:null,fire:false,blocked:false,error:'invalid-position'};
    // Treat long browser stalls as a pause, never simulate a whole second at once.
    const step=finite(dt) ? clamp(dt,0,.05) : 0;
    clock+=step;cooldown=Math.max(0,cooldown-step);
    const pos={x:position.x,z:position.z,y:finite(position.y)?position.y:0};
    const p={x:target.x,z:target.z};
    const d=distance(pos,p);
    let fired=false,aim=null,blocked=false,moving=false;
    if(mode==='telegraph') {
      timer=Math.max(0,timer-step);
      if(timer<=1e-8){
        // Locked target is immutable until release: real lateral player movement can dodge.
        fired=true;aim=lockedTarget ? {...lockedTarget} : null;
        shots++;mode='recover';timer=profile.recovery;cooldown=profile.cooldown*(faster?.74:1);
        lastFire=aim;
      }
    } else if(mode==='recover') {
      timer-=step;
      if(timer<=0){mode='approach';timer=0;}
    } else if(d<=profile.range && d>=2 && !!visible && cooldown<=1e-8 && allowWindup) {
      mode='telegraph';lockedWindup=profile.windup*(faster?.82:1);timer=lockedWindup;
      lockedTarget={x:p.x,z:p.z,y:finite(target.y)?target.y:pos.y};
      warningCount++;
    } else if(step>0 && d>1e-5 && d<125) {
      const toward={x:(p.x-pos.x)/d,z:(p.z-pos.z)/d};
      const lateral={x:-toward.z*preferredSide,z:toward.x*preferredSide};
      let moveDir;
      const navigating=(!visible||preferNavigation) && validPoint(navigationTarget) &&
        distance(pos,navigationTarget)>0.65;
      if(navigating){
        // Navigation only redirects the legs; the original target, LOS,
        // cooldown and locked telegraph remain authoritative.
        const span=distance(pos,navigationTarget);
        moveDir={x:(navigationTarget.x-pos.x)/span,z:(navigationTarget.z-pos.z)/span};
        mode='navigate';
      } else if(d>profile.preferredMax) {moveDir=toward;mode=visible?'approach':'search';}
      else if(d<profile.preferredMin) {moveDir={x:-toward.x,z:-toward.z};mode='retreat';}
      else {moveDir=lateral;mode=visible?'flank':'search';}
      const stride=profile.speed*(faster?1.18:1)*step;
      // Authenticated collision checker must reject buildings, water and unsafe terrain.
      function attempt(direction) {
        const next={x:pos.x+direction.x*stride,z:pos.z+direction.z*stride};
        if(!validPoint(next) || typeof canOccupy!=='function' || !canOccupy(next.x,next.z,pos,profile.radius))return null;
        let y=pos.y;
        if(typeof sampleGround==='function') {
          const ground=sampleGround(next.x,next.z,pos.y);
          if(!finite(ground) || Math.abs(ground-pos.y)>.50)return null;
          y=ground;
        }
        return {...next,y};
      }
      let next=attempt(moveDir);
      if(!next) {
        blocked=true;blockedSteps++;
        // No blind crossing of geometry: alternative lanes are checked too.
        next=attempt(lateral);
        if(!next)next=attempt({x:-lateral.x,z:-lateral.z});
        if(!next)preferredSide*=-1;
      }
      if(next){pos.x=next.x;pos.z=next.z;pos.y=next.y;moving=true;}
    }
    return {...snapshot(),position:pos,fire:fired,fireTarget:aim,
      faceTarget:mode==='telegraph' && lockedTarget ? {...lockedTarget} : {...p},
      blocked,moving,speed:moving?profile.speed*(faster?1.18:1):0};
  }
  return {role,profile,update,reset,snapshot,get lastFire(){return lastFire;}};
}
