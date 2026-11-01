/** Taipei 101 Mecha v6.7 - game-clock, aggregate-only battle statistics.
 * No storage, network, fingerprinting, world positions or raw movement trace.
 * The caller must EXPLICITLY trigger export; collecting happens only in RAM.
 * The counters describe a single mission and are never treated as GPU FPS.
 */
const clamp=(n,a,b)=>Math.min(b,Math.max(a,Number.isFinite(n)?n:a));
const eventTypes=new Set(['player_shot','enemy_shot','enemy_warning','enemy_hit','enemy_down',
  'player_hit','relay_hit','dodge_started','dodge_blocked','dodge_moved',
  'route_replan','route_exhausted','boss_phase2','wave_start']);
const defaultCounts=()=>({playerShots:0,lightShots:0,chargedShots:0,rocketShots:0,
  enemyShots:0,enemyShotsHit:0,enemyWarnings:0,enemyHits:0,enemyDown:0,
  playerDamage:0,relayDamage:0,dodgeAttempts:0,dodgeDuringWarnings:0,
  dodgeBlocked:0,dodgeMovedMeters:0,routeReplans:0,routeExhausted:0,bossPhase2:0});
export function createBattleMetricsV67({maxSeconds=3600}={}){
  if(!Number.isFinite(maxSeconds)||maxSeconds<60||maxSeconds>7200)throw new RangeError('bad limit');
  let mode='idle',difficulty='standard',lastWave=0,seconds=0,reason=null,counts=defaultCounts(),
    waves=new Map(),damageTraceExcluded=true,dtClamps=0;
  const waveItem=n=>{
    if(!Number.isInteger(n)||n<1||n>12)return null;
    if(!waves.has(n))waves.set(n,{wave:n,combatSeconds:0,enemyDown:0,
      playerShots:0,enemyShots:0,playerDamage:0,relayDamage:0,dodgeAttempts:0,
      blockedDodges:0,routeReplans:0,routeExhausted:0});
    return waves.get(n);
  };
  function begin({level='standard'}={}){
    if(!['training','standard','challenge'].includes(level))throw new RangeError('invalid level');
    mode='recording';difficulty=level;lastWave=0;seconds=0;reason=null;
    counts=defaultCounts();waves.clear();dtClamps=0;return true;
  }
  function cancel(){mode='idle';reason=null;seconds=0;lastWave=0;counts=defaultCounts();waves.clear();}
  function finish(outcome){
    if(mode!=='recording')return false;
    mode='complete';reason=['victory','defeat','deployment_failed','abandoned','time-expired'].includes(outcome)?outcome:'unknown';
    return true;
  }
  function record(type,data={}){
    if(mode!=='recording'||!eventTypes.has(type))return false;
    if(type==='wave_start'){
      const n=Number(data.wave);if(Number.isInteger(n)&&n>=1&&n<=12){lastWave=n;waveItem(n);}
      return true;
    }
    const w=waveItem(lastWave);
    const damage=Math.round(clamp(data.damage,0,10000));
    switch(type){
      case 'player_shot':{
        counts.playerShots++;if(w)w.playerShots++;
        const weapon=data.weapon;
        if(weapon==='light')counts.lightShots++;
        else if(weapon==='charged')counts.chargedShots++;
        else if(weapon==='rocket')counts.rocketShots++;
        break;
      }
      case 'enemy_shot': counts.enemyShots++;if(w)w.enemyShots++;
        if(data.hit===true)counts.enemyShotsHit++;break;
      case 'enemy_warning': counts.enemyWarnings++;break;
      case 'enemy_hit': counts.enemyHits++;break;
      case 'enemy_down': counts.enemyDown++;if(w)w.enemyDown++;break;
      case 'player_hit':counts.playerDamage+=damage;if(w)w.playerDamage+=damage;break;
      case 'relay_hit':counts.relayDamage+=damage;if(w)w.relayDamage+=damage;break;
      case 'dodge_started':counts.dodgeAttempts++;if(w)w.dodgeAttempts++;
        if(data.underWarning===true)counts.dodgeDuringWarnings++;break;
      case 'dodge_blocked':counts.dodgeBlocked++;if(w)w.blockedDodges++;break;
      case 'dodge_moved':counts.dodgeMovedMeters+=clamp(data.distance,0,1);break;
      case 'route_replan':counts.routeReplans++;if(w)w.routeReplans++;break;
      case 'route_exhausted':counts.routeExhausted++;if(w)w.routeExhausted++;break;
      case 'boss_phase2':counts.bossPhase2++;break;
    }
    return true;
  }
  function observe(dt,{mission=null,playing=true}={}){
    if(mode!=='recording'||!mission)return;
    if(mission.finished){finish(mission.phase==='victory'?'victory':mission.reason||'defeat');return;}
    if(!playing || !mission.active)return;
    const safeDt=clamp(dt,0,.05);
    if(Number.isFinite(dt)&&dt>.05)dtClamps++;
    if(seconds>=maxSeconds){finish('time-expired');return;}
    seconds+=Math.min(safeDt,maxSeconds-seconds);
    const number=Number(mission.wave);
    if(Number.isInteger(number)&&number>lastWave&&number<=12){lastWave=number;waveItem(number);}
    if(mission.phase==='combat'){const w=waveItem(lastWave);if(w)w.combatSeconds+=safeDt;}
  }
  function report(){
    const fixed={...counts,dodgeMovedMeters:Number(counts.dodgeMovedMeters.toFixed(2))};
    const arr=[...waves.values()].sort((a,b)=>a.wave-b.wave).map(w=>({...w,combatSeconds:Number(w.combatSeconds.toFixed(2))}));
    return {schema:'taipei-mecha-v67-battle-aggregates',version:'6.7',status:mode,
      difficulty,missionOutcome:reason,gameSeconds:Number(seconds.toFixed(2)),
      counts:fixed,waves:arr,excludedPausedFrames:dtClamps,
      definitions:{enemyShotsHit:'真正造成傷害的敵機射線次數（非預警數）',
      enemyHits:'敵機受傷事件數；爆破可能單次命中多個敵機，不能當成射擊命中率',
      dodgeAttempts:'實際成功啟動側閃的次數',
      dodgeDuringWarnings:'啟動側閃時至少一架敵機仍在預警；不等於成功閃避攻擊',
      dodgeBlocked:'側閃過程撞上障礙物的連續事件次數',
      routeReplans:'原本 OSM 控制器要求重新尋路的次數'},
      limitations:['只計算遊戲內實際模擬時間，不是現實時間或 GPU FPS',
        '不記錄地理座標、動作軌跡、個資、帳號、裝置資訊或隨機種子',
        '遊戲未完成 Windows WebGPU 的真實五分鐘驗收；本報告是單次遊玩資料，不足以證明難度平衡']};
  }
  function snapshot(){const r=report();return {status:r.status,outcome:r.missionOutcome,gameSeconds:r.gameSeconds,
    difficulty:r.difficulty,counts:r.counts,waves:r.waves};}
  return {begin,cancel,finish,record,observe,report,snapshot};
}
