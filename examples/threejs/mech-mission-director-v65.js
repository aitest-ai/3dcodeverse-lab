/**
 * Taipei 101 defence v6.5 mission director: deterministic, no DOM / Three.js.
 * This directs waves, emphasis and boss pressure; it NEVER declares a world
 * position traversable, edits hit points, or spawns an enemy by itself.
 * A candidate becomes real only after the existing original OSM tests approve.
 * 1 world unit = 1m, +X=east and +Z=south in original Slop Taipei data.
 */
const clamp=(x,a,b)=>Math.max(a,Math.min(b,Number.isFinite(x)?x:a));
const DIRECTIONS=Object.freeze({
  north:{bearing:Math.PI,label:'北側'},
  east:{bearing:Math.PI/2,label:'東側'},
  south:{bearing:0,label:'南側'},
  west:{bearing:-Math.PI/2,label:'西側'}
});
const PLANS=Object.freeze({
  1:Object.freeze(['east','west']),
  2:Object.freeze(['north','south','east']),
  3:Object.freeze(['west','east','north','south'])
});
const terminal=new Set(['victory','defeat','deployment_failed']);
export function compassSectorV65(position,origin){
  if(!position||!origin||![position.x,position.z,origin.x,origin.z].every(Number.isFinite))return '未知';
  const dx=position.x-origin.x,dz=position.z-origin.z;
  if(Math.hypot(dx,dz)<.4)return '附近';
  return Math.abs(dx)>Math.abs(dz)?(dx>0?'東側':'西側'):(dz>0?'南側':'北側');
}
export function createMissionDirectorV65({noticeSeconds=3,criticalRatio=.30,heavyPhaseRatio=.50}={}){
  if(!Number.isFinite(noticeSeconds)||noticeSeconds<.1||noticeSeconds>10 ||
    !Number.isFinite(criticalRatio)||criticalRatio<=0||criticalRatio>=1 ||
    !Number.isFinite(heavyPhaseRatio)||heavyPhaseRatio<=0||heavyPhaseRatio>=1)
    throw new RangeError('Invalid mission director limits');
  let running=false,overdrive=false,critical=false,currentWave=0,finished=null;
  let notice=null,noticeLeft=0,serial=0;
  let events=[],spawned=[],totalEvents=0;
  const eventLimit=32;
  function announce(kind,label,{priority=1,seconds=noticeSeconds,wave=null,stage=null}={}){
    // Lasting important results should not be erased by ordinary hit notifications.
    if(notice&&noticeLeft>0 && priority<notice.priority)return null;
    const event={sequence:++serial,kind,label:String(label).slice(0,95),wave,stage,priority};
    notice=event;noticeLeft=seconds;
    events.push({kind,wave,stage});if(events.length>eventLimit)events.shift();totalEvents++;
    return event;
  }
  function reset(){running=false;overdrive=false;critical=false;currentWave=0;finished=null;
    notice=null;noticeLeft=0;serial=0;events=[];spawned=[];totalEvents=0;}
  function start(){reset();running=true;announce('opening','臺北 101 訊號防線｜敵機入侵，守護中繼站！',{priority:2,seconds:2.7});return snapshot();}
  function wavePlan(wave,roles){
    if(!Number.isInteger(wave)||wave<1||wave>3||!Array.isArray(roles))return [];
    const dirs=PLANS[wave];
    return roles.map((role,i)=>{
      const direction=dirs[i%dirs.length],entry=DIRECTIONS[direction];
      return Object.freeze({role,direction,sector:entry.label,
        // Entirely candidate parameters; original city verifies every destination.
        angle:entry.bearing,range:wave===1?32+i*9:wave===2?37+i*7:42+i*8});
    });
  }
  function confirmedSpawn(id,position,anchor,role){
    if(!running||!Number.isSafeInteger(id)||id<1||!['assault','ranger','heavy'].includes(role))return null;
    const side=compassSectorV65(position,anchor);
    if(side==='未知'||side==='附近')return null;
    // Do not record world coordinates in event history or client JSON.
    const item={id,role,side};spawned.push(item);
    if(spawned.length>12)spawned.shift();return {...item};
  }
  function observe({mission,heavy=null,playerHP=null}={}){
    if(!running || !mission || mission.phase==='idle')return snapshot();
    const phase=mission.phase;
    if(Number.isFinite(mission.wave)&&mission.wave>currentWave && (phase==='combat'||phase==='deploy')){
      currentWave=mission.wave;
      const n=currentWave;
      announce('wave_entry',n===1?'第一波｜東西兩翼出現敵機':n===2?'第二波｜多向包圍，注意遠距狙擊':'第三波｜重裝型機甲進入防線',
        {wave:n,priority:n===3?3:(n===1?1:2),seconds:n===3?3.2:2.5});
    }
    if(phase==='combat'&&!critical&&Number.isFinite(mission.relayHP) && Number.isFinite(mission.relayMaxHP) &&
       mission.relayMaxHP>0 && mission.relayHP/mission.relayMaxHP<=criticalRatio){
      critical=true;
      announce('relay_critical','警告！中繼站耐久告急，優先攔截攻擊者',{priority:4,seconds:4.3,wave:currentWave});
    }
    if(phase==='combat' && currentWave===3 && !overdrive && heavy &&
       Number.isFinite(heavy.hp) && Number.isFinite(heavy.maxHp) && heavy.maxHp>0 &&
       heavy.hp>0 && heavy.hp/heavy.maxHp<=heavyPhaseRatio){
      overdrive=true;
      announce('boss_phase2','重裝型進入第二階段｜開炮更快、火力增強！',{priority:3,seconds:3.8,wave:3,stage:2});
    }
    if(terminal.has(phase)&&!finished){
      finished=phase;
      const win=phase==='victory';
      announce(win?'victory':'defeat',win?'防衛成功｜臺北 101 中繼站安全':'防衛失敗｜按 M 再挑戰，按 R 返回自由戰鬥',
        {priority:5,seconds:180,wave:currentWave});
    }
    return snapshot();
  }
  function update(dt){
    if(noticeLeft>0){noticeLeft=Math.max(0,noticeLeft-clamp(dt,0,.05));if(noticeLeft===0)notice=null;}
    return snapshot();
  }
  function bossTuning(role){
    const active=running&&currentWave===3&&overdrive&&role==='heavy'&&!finished;
    return Object.freeze({phase:active?2:1,overdrive:active,
      // A longer visual tell remains (>0.8s); damage cap avoids surprise one-hit.
      cooldownScale:active?.74:1,windupScale:active?.82:1,
      speedScale:active?1.18:1,damageScale:active?1.25:1});
  }
  function snapshot(){return {active:running,currentWave,overdrive,critical,finished,
    notice:notice?{...notice}:null,noticeRemaining:noticeLeft,totalEvents,
    lanes:spawned.map(x=>({...x})),events:events.map(x=>({...x}))};}
  return {start,reset,observe,update,bossTuning,wavePlan,confirmedSpawn,snapshot};
}
