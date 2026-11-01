/**
 * Taipei 101 Defence v6.0 - deterministic mission state machine.
 * No Three.js dependency, no timers, no DOM, no collision bypass.
 * All IDs are supplied by the authoritative battle engine only after a wave
 * has successfully spawned on real Taipei ground.
 */
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
const valid=n=>typeof n==='number'&&Number.isFinite(n);
const VALID_ROLES=new Set(['assault','ranger','heavy']);
export const DEFENSE_WAVES_V60=Object.freeze([
  Object.freeze({label:'前哨突破',roles:Object.freeze(['assault','assault'])}),
  Object.freeze({label:'狙擊包圍',roles:Object.freeze(['assault','ranger','assault'])}),
  Object.freeze({label:'重裝決戰',roles:Object.freeze(['assault','ranger','heavy','assault'])})
]);

export function createTaipeiDefenseMissionV60({duration=300,relayMaxHP=100,betweenWaves=4,waves=DEFENSE_WAVES_V60}={}){
  if(!valid(duration)||duration<30||duration>1800)throw new RangeError('duration must be 30-1800 seconds');
  if(!valid(relayMaxHP)||relayMaxHP<1||relayMaxHP>10000)throw new RangeError('invalid relay health');
  if(!valid(betweenWaves)||betweenWaves<0||betweenWaves>60)throw new RangeError('invalid intermission');
  if(!Array.isArray(waves)||waves.length<1||waves.length>12||waves.some(w=>!Array.isArray(w.roles)||w.roles.length<1||w.roles.length>12||w.roles.some(r=>!VALID_ROLES.has(r))))throw new TypeError('invalid waves');
  let phase='idle',reason=null,remaining=duration,relayHP=relayMaxHP,waveIndex=-1,interval=0;
  let anchor=null,kills=0,enemyIds=new Set(),visited=new Set();
  let eventCount=0;
  function snapshot(){return Object.freeze({phase,reason,remainingSeconds:Math.max(0,remaining),
    relayHP,relayMaxHP,wave:Math.max(0,waveIndex+1),totalWaves:waves.length,
    waveLabel:waveIndex>=0?(waves[waveIndex]?.label||('第'+(waveIndex+1)+'波')):'',
    activeEnemies:enemyIds.size,intermissionRemaining:phase==='intermission'?interval:0,
    kills,objective:anchor?{...anchor}:null,events:eventCount,
    score:phase==='victory'?kills*100+Math.floor(remaining)+Math.floor(relayHP*5):null,
    active:['deploy','combat','intermission'].includes(phase),
    finished:['victory','defeat','deployment_failed'].includes(phase)});}
  function reset(){phase='idle';reason=null;remaining=duration;relayHP=relayMaxHP;waveIndex=-1;interval=0;anchor=null;kills=0;enemyIds.clear();visited.clear();eventCount=0;return snapshot();}
  function start(position){
    if(!position||![position.x,position.y,position.z].every(valid))return {ok:false,reason:'unsafe-objective'};
    reset();anchor={x:position.x,y:position.y,z:position.z};waveIndex=0;phase='deploy';eventCount++;
    return {ok:true,state:snapshot()};
  }
  function requestedWave(){return phase==='deploy'?Object.freeze({wave:waveIndex+1,label:waves[waveIndex]?.label||'',roles:[...waves[waveIndex].roles]}):null;}
  function deploy(ids){
    if(phase!=='deploy')return false;
    const wanted=waves[waveIndex].roles.length;
    if(!Array.isArray(ids)||ids.length!==wanted||new Set(ids).size!==ids.length||ids.some(x=>!Number.isSafeInteger(x)||x<1||visited.has(x))){
      phase='deployment_failed';reason='unsafe-spawn';enemyIds.clear();eventCount++;return false;
    }
    enemyIds=new Set(ids);ids.forEach(id=>visited.add(id));phase='combat';eventCount++;return true;
  }
  function destroyEnemy(id){
    if(phase!=='combat'||!enemyIds.has(id))return false;
    enemyIds.delete(id);kills++;eventCount++;
    if(enemyIds.size===0){
      if(waveIndex===waves.length-1){phase='victory';reason='all-waves-cleared';eventCount++;}
      else{phase='intermission';interval=betweenWaves;eventCount++;}
    }
    return true;
  }
  function damageRelay(amount){
    if(phase!=='combat'||!valid(amount)||amount<=0)return false;
    relayHP=clamp(relayHP-amount,0,relayMaxHP);
    eventCount++;
    if(relayHP===0){phase='defeat';reason='relay-destroyed';eventCount++;}
    return true;
  }
  function tick(dt,{playerHP=100,active=true,withinArea=true}={}){
    if(!['combat','intermission','deploy'].includes(phase))return snapshot();
    if(valid(playerHP)&&playerHP<=0){phase='defeat';reason='player-destroyed';eventCount++;return snapshot();}
    if(withinArea===false){phase='defeat';reason='left-defense-area';eventCount++;return snapshot();}
    if(!active)return snapshot();
    // Long tab stalls are not simulated as large combat steps.
    const step=valid(dt)?clamp(dt,0,.05):0;
    remaining=Math.max(0,remaining-step);
    if(remaining<=0){phase='defeat';reason='time-expired';eventCount++;return snapshot();}
    if(phase==='intermission'){
      interval=Math.max(0,interval-step);
      if(interval<=0){waveIndex++;phase='deploy';eventCount++;}
    }
    return snapshot();
  }
  return {start,reset,snapshot,requestedWave,deploy,destroyEnemy,damageRelay,tick};
}
