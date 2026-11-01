/**
 * Taipei Mech v6.1: distinct, accessibility-aware mission presentation.
 * Pure local DOM: no telemetry uploads, external images, timers or audio.
 * Owns only an overlay; never changes health, actual controls, or mission logic.
 */
export function createMissionPresentationV61({documentRef=document}={}) {
  if (!documentRef?.body?.appendChild || !documentRef.createElement)
    throw new TypeError('DOM required');
  const root=documentRef.createElement('section');
  root.id='taipei-mech-mission-v61';
  root.setAttribute('aria-label','臺北 101 防衛任務資訊');
  root.hidden=true;
  root.innerHTML=`<style>
#taipei-mech-mission-v61{position:fixed;z-index:1002;left:50%;top:12px;transform:translateX(-50%);width:min(420px,calc(100vw - 38px));pointer-events:none;color:#f4fcff;font:600 12px/1.45 system-ui,'Noto Sans TC',sans-serif;filter:drop-shadow(0 4px 14px #0008)}
#taipei-mech-mission-v61[hidden]{display:none!important}
#taipei-mech-mission-v61 .v61-frame{padding:8px 12px 9px;border:1px solid rgba(137,221,226,.65);background:linear-gradient(105deg,rgba(12,36,48,.94),rgba(14,42,55,.88));border-radius:11px;backdrop-filter:blur(8px)}
#taipei-mech-mission-v61 .v61-header{display:flex;justify-content:space-between;gap:9px;align-items:center;font-size:12px}
#taipei-mech-mission-v61 .v61-clock{font:750 17px/1.1 ui-monospace,SFMono-Regular,Consolas,monospace;font-variant-numeric:tabular-nums;color:#bdf7ff}
#taipei-mech-mission-v61 .v61-sub{font-size:10px;line-height:1.5;color:#c2e0e6;margin-top:4px}
#taipei-mech-mission-v61 .v61-track{background:rgba(255,255,255,.17);height:5px;overflow:hidden;border-radius:5px;margin-top:5px}
#taipei-mech-mission-v61 .v61-track span{display:block;width:100%;height:100%;background:linear-gradient(90deg,#f0a54b,#f8e8a2);transition:width .20s}
#taipei-mech-mission-v61 .v61-callout{margin-top:6px;background:linear-gradient(90deg,rgba(170,56,41,.94),rgba(83,28,39,.94));border:1px solid #ffc395;border-radius:9px;padding:8px 11px;letter-spacing:.025em;animation:v61-enter .22s ease-out}
#taipei-mech-mission-v61 .v61-callout[hidden]{display:none}
#taipei-mech-mission-v61[data-result="victory"] .v61-callout{background:linear-gradient(100deg,rgba(16,122,104,.95),rgba(12,75,90,.96));border-color:#b7fff0}
#taipei-mech-mission-v61[data-critical="true"] .v61-frame{border-color:#ffae75}
@keyframes v61-enter{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}
@media(max-width:690px){#taipei-mech-mission-v61{top:auto;bottom:max(106px,env(safe-area-inset-bottom) + 98px);width:min(310px,calc(100vw - 18px));left:50%}#taipei-mech-mission-v61 .v61-frame{padding:6px 9px}#taipei-mech-mission-v61 .v61-sub{font-size:10px}}
@media(prefers-reduced-motion:reduce){#taipei-mech-mission-v61 .v61-callout{animation:none}#taipei-mech-mission-v61 .v61-track span{transition:none}}
</style>
<div class="v61-frame"><div class="v61-header"><span data-v61-wave>臺北 101 防衛戰</span><span class="v61-clock" data-v61-clock>05:00</span></div><div class="v61-sub" data-v61-sub>守護中繼站</div><div class="v61-track"><span data-v61-relay></span></div></div>
<div class="v61-callout" data-v61-callout role="status" aria-live="polite" hidden></div>`;
  documentRef.body.appendChild(root);
  const q=k=>root.querySelector(`[data-v61-${k}]`);
  const wave=q('wave'),clock=q('clock'),sub=q('sub'),bar=q('relay'),callout=q('callout');
  let previousPhase='idle',previousWave=0,previousHP=null,bannerRemaining=0,lastPriority=0;
  function flash(message,seconds=3,priority=1){
    if(priority<lastPriority&&bannerRemaining>0)return;
    callout.textContent=message;callout.hidden=false;
    bannerRemaining=seconds;lastPriority=priority;
  }
  function update(s,{enemyWarnings=0}={}){
    if(!s||typeof s.phase!=='string')return;
    root.hidden=s.phase==='idle';
    if(root.hidden){callout.hidden=true;previousPhase='idle';previousWave=0;previousHP=null;bannerRemaining=0;lastPriority=0;return;}
    const remaining=Math.max(0,Number.isFinite(s.remainingSeconds)?s.remainingSeconds:0);
    const t=Math.ceil(remaining);
    clock.textContent=String(Math.floor(t/60)).padStart(2,'0')+':'+String(t%60).padStart(2,'0');
    wave.textContent=`臺北 101 防衛｜第 ${s.wave??0}/${s.totalWaves??3} 波`;
    const hp=Math.max(0,Number.isFinite(s.relayHP)?s.relayHP:0),max=Math.max(1,Number.isFinite(s.relayMaxHP)?s.relayMaxHP:100);
    bar.style.width=Math.max(0,Math.min(100,100*hp/max))+'%';
    const warn=Number.isFinite(enemyWarnings)?Math.max(0,enemyWarnings):0;
    sub.textContent=`中繼站 ${Math.ceil(hp)}/${max}｜敵機 ${s.activeEnemies??0}｜預警 ${warn}｜M 重試 · R 自由戰鬥`;
    root.dataset.critical=String(hp/max<.3);
    root.dataset.result=s.phase==='victory'?'victory':s.phase==='defeat'||s.phase==='deployment_failed'?'defeat':'battle';
    if(s.phase!==previousPhase){
      if(s.phase==='combat'&&s.wave!==previousWave)flash(`第 ${s.wave} 波｜${s.waveLabel||'敵機接近'}！`,3.5,1);
      else if(s.phase==='intermission')flash('本波清除｜下一波即將抵達',2.9,1);
      else if(s.phase==='victory')flash(`防衛成功！得分 ${s.score??0}｜按 M 再挑戰`,120,3);
      else if(s.phase==='defeat')flash('防衛失敗｜按 M 重新挑戰',120,3);
      else if(s.phase==='deployment_failed')flash('附近沒有安全生成位置｜請更換路面重試',120,3);
    }
    if(previousHP!==null&&hp<previousHP&&s.phase==='combat'){
      flash(hp/max<.3?'警告！中繼站耐久低於 30%':'中繼站遭受攻擊！',2.25,hp/max<.3?2:1);
    }
    previousPhase=s.phase;previousWave=s.wave;previousHP=hp;
  }
  function tick(dt){
    const step=Number.isFinite(dt)?Math.max(0,Math.min(.1,dt)):0;
    if(bannerRemaining>0){bannerRemaining=Math.max(0,bannerRemaining-step);if(bannerRemaining===0){callout.hidden=true;lastPriority=0;}}
  }
  function dispose(){root.remove();}
  return {update,tick,flash,dispose,root};
}
