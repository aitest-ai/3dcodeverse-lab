/**
 * v6.8 portable reference for comparing locally exported v6.7 battle reports.
 * Standalone full offline HTML (including stricter upload/CSV UI) is in the
 * independently delivered Windows ZIP, not this asset-toolchain repository.
 * Never writes to storage, performs networking, or transmits user data.
 */
export const LEVELS_V68=Object.freeze(['training','standard','challenge']);
const schema='taipei-mecha-v67-battle-aggregates';
const completed=new Set(['victory','defeat','time-expired']);
const valid=n=>typeof n==='number'&&Number.isFinite(n)&&n>=0;
const median=a=>{if(!a.length)return null;const b=a.slice().sort((x,y)=>x-y);return b.length%2?b[(b.length-1)/2]:(b[b.length/2-1]+b[b.length/2])/2;};
const avg=a=>a.length?a.reduce((p,c)=>p+c,0)/a.length:null;
const round=n=>n===null?null:Number(n.toFixed(2));
const wilson=(success,total)=>{
 if(!total)return null;
 const z=1.95996398454,p=success/total,b=z*z,den=1+b/total;
 const mid=(p+b/(2*total))/den;
 const delta=z*Math.sqrt(p*(1-p)/total+b/(4*total*total))/den;
 return [Number((100*Math.max(0,mid-delta)).toFixed(1)),Number((100*Math.min(1,mid+delta)).toFixed(1))];
};
const countKeys=['playerShots','playerDamage','relayDamage','dodgeAttempts','routeReplans','enemyDown','enemyShots'];
export function normalizeBattleReportV68(r){
 if(!r||r.schema!==schema||r.version!=='6.7')throw Error('unsupported schema or game version');
 if(!LEVELS_V68.includes(r.difficulty))throw Error('invalid difficulty');
 if(!['complete','recording'].includes(r.status)||!valid(r.gameSeconds)||r.gameSeconds>3600)throw Error('invalid run metadata');
 if(!r.counts||typeof r.counts!=='object'||!Array.isArray(r.waves)||r.waves.length>12)throw Error('invalid counts or waves');
 for(const k of ['playerShots','playerDamage','relayDamage','dodgeAttempts'])if(!valid(r.counts[k]))throw Error('missing mandatory '+k);
 const c={};
 for(const k of countKeys){if(r.counts[k]!==undefined&&!valid(r.counts[k]))throw Error('invalid '+k);c[k]=r.counts[k]??0;}
 const seen=new Set(),waves=[];
 for(const w of r.waves){
  if(!w||!Number.isInteger(w.wave)||w.wave<1||w.wave>12||seen.has(w.wave)||!valid(w.combatSeconds))throw Error('invalid wave');
  seen.add(w.wave);
  waves.push({wave:w.wave,combatSeconds:w.combatSeconds,relayDamage:valid(w.relayDamage)?w.relayDamage:0,
   playerDamage:valid(w.playerDamage)?w.playerDamage:0});
 }
 if(waves.reduce((s,w)=>s+w.combatSeconds,0)>r.gameSeconds+1)throw Error('invalid time sum');
 const comparable=r.status==='complete'&&completed.has(r.missionOutcome);
 return {difficulty:r.difficulty,status:r.status,outcome:r.missionOutcome,seconds:r.gameSeconds,
  counts:c,waves,comparable,victory:comparable&&r.missionOutcome==='victory'};
}
export function analyzeBattleCohortV68(raw){
 if(!Array.isArray(raw))throw TypeError('array expected');
 const rs=raw.map(normalizeBattleReportV68);
 const groups=LEVELS_V68.map(level=>{
  const all=rs.filter(r=>r.difficulty===level),eligible=all.filter(r=>r.comparable),wins=eligible.filter(r=>r.victory);
  const perWave=[1,2,3].map(wave=>{
   const reached=eligible.map(r=>r.waves.find(w=>w.wave===wave)).filter(Boolean);
   return {wave,reached:reached.length,medianSeconds:round(median(reached.map(w=>w.combatSeconds)))};
  });
  return {difficulty:level,loaded:all.length,eligible:eligible.length,excluded:all.length-eligible.length,
   wins:wins.length,losses:eligible.length-wins.length,
   rate:eligible.length?round(100*wins.length/eligible.length):null,
   wilson95:wilson(wins.length,eligible.length),
   medianVictorySeconds:round(median(wins.map(r=>r.seconds))),
   medianRelayDamage:round(median(eligible.map(r=>r.counts.relayDamage))),
   medianPlayerDamage:round(median(eligible.map(r=>r.counts.playerDamage))),
   averageReplans:round(avg(eligible.map(r=>r.counts.routeReplans))),perWave};
 });
 return {schema:'taipei-mecha-v68-descriptive-compare',loaded:rs.length,
  eligible:groups.reduce((s,x)=>s+x.eligible,0),groups,
  limitations:['Only completed victory, defeat and time-expired runs enter win denominator.',
   'Unreached waves are missing, not zero seconds.', 'No real players, GPS or coordinates are inferred.',
   'Descriptive comparison and Wilson interval are not causal claims of optimal difficulty.']};
}
export function createBattleCohortV68({maxReports=200}={}){
 if(!Number.isInteger(maxReports)||maxReports<1||maxReports>500)throw RangeError('invalid limit');
 let reports=[],seen=new Set();
 function add(raw,{allowIdentical=false}={}){
  const normalized=normalizeBattleReportV68(raw);
  if(reports.length>=maxReports)return {added:false,reason:'capacity'};
  const fingerprint=JSON.stringify(normalized);
  if(!allowIdentical&&seen.has(fingerprint))return {added:false,reason:'duplicate'};
  reports.push(raw);seen.add(fingerprint);return {added:true};
 }
 function clear(){reports=[];seen.clear();}
 return {add,clear,analyze(){return analyzeBattleCohortV68(reports)},get count(){return reports.length;}};
}
