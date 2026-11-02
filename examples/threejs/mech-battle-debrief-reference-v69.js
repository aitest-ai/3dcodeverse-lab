/**
 * v6.9 shared portable example: aggregate REAL enemy role hit events into a
 * single-match end-of-battle summary. Source game owns damage, LOS and mission.
 * This reference is intentionally smaller than the full Windows overlay.
 * No network, storage, raw coordinates, device IDs or player identifiers.
 */
export const ROLE_LABELS_V69=Object.freeze({assault:'突擊型',ranger:'遠距型',heavy:'重裝型'});
const fresh=()=>({playerDamage:0,relayDamage:0,hitsOnPlayer:0,hitsOnRelay:0});
const nonnegative=n=>typeof n==='number'&&Number.isFinite(n)&&n>=0;
export function createMechDebriefReferenceV69(){
 let active=false,closed=false,records={};let result=null;
 function begin(){active=true;closed=false;result=null;records=Object.fromEntries(
 Object.keys(ROLE_LABELS_V69).map(k=>[k,fresh()]));}
 function record({role,type,damage}={}){
  if(!active||closed||!Object.hasOwn(ROLE_LABELS_V69,role)||!nonnegative(damage))return false;
  const item=records[role],n=Math.min(10000,Math.round(damage));
  if(type==='player_hit'){item.playerDamage+=n;item.hitsOnPlayer++;return true;}
  if(type==='relay_hit'){item.relayDamage+=n;item.hitsOnRelay++;return true;}
  return false;
 }
 function finish(stats){
  if(!active||closed||stats?.schema!=='taipei-mecha-v67-battle-aggregates'||stats?.status!=='complete')return null;
  closed=true;
  const roles=Object.entries(records).map(([role,row])=>({role,label:ROLE_LABELS_V69[role],...row,
    totalDamage:row.playerDamage+row.relayDamage}));
  const top=roles.slice().sort((a,b)=>b.totalDamage-a.totalDamage)[0];
  const waves=(Array.isArray(stats.waves)?stats.waves:[]).filter(w=>Number.isInteger(w.wave)&&nonnegative(w.relayDamage))
    .map(w=>({wave:w.wave,relayDamage:w.relayDamage,combatSeconds:nonnegative(w.combatSeconds)?w.combatSeconds:0}));
  const worst=waves.slice().sort((a,b)=>b.relayDamage-a.relayDamage)[0];
  result={schema:'taipei-mecha-v69-portable-debrief',outcome:stats.missionOutcome||'unknown',
    difficulty:stats.difficulty||'standard',
    mostDamagingRole:top&&top.totalDamage>0?top.role:null,
    mostDamagingWave:worst&&worst.relayDamage>0?worst.wave:null,
    roles,waves,
    dodgeAttempts:nonnegative(stats.counts?.dodgeAttempts)?stats.counts.dodgeAttempts:0,
    dodgeDuringWarnings:nonnegative(stats.counts?.dodgeDuringWarnings)?stats.counts.dodgeDuringWarnings:0,
    limitations:['One-match actual HP damage attribution, not a causal ranking.',
      'Sidestepping while warned is not evidence of a successful dodge.']};
  return snapshot();
 }
 function snapshot(){return result?JSON.parse(JSON.stringify(result)):null;}
 function reset(){active=false;closed=false;result=null;records={};}
 return {begin,record,finish,snapshot,reset};
}
