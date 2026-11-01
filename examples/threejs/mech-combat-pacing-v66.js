/**
 * Taipei 101 v6.6: fair, deterministic telegraph admission.
 * This only decides WHEN an enemy may begin a NEW warning, never changes its
 * locked shot, existing warning, original city ray, HP or movement.
 * Free-roam combat remains untouched. No wall-clock, coordinates or timers.
 */
const clamp=(n,a,b)=>Math.min(b,Math.max(a,Number.isFinite(n)?n:a));
const WAVE_SETTINGS=Object.freeze({
  1:Object.freeze({grace:.65,limit:1,gap:.28}),
  2:Object.freeze({grace:1.05,limit:2,gap:.48}),
  3:Object.freeze({grace:1.45,limit:2,gap:.62})
});
export function createCombatPacingV66({bossPhaseGrace=.85}={}){
  if(!Number.isFinite(bossPhaseGrace)||bossPhaseGrace<0||bossPhaseGrace>3)throw new RangeError('invalid boss grace');
  let clock=0,wave=0,phase='idle',graceUntil=0,heavyGraceUntil=0,lastWarning=-Infinity;
  let overdrive=false,admitted=0,delayed=0,peakWarnings=0;
  function reset(){clock=0;wave=0;phase='idle';graceUntil=0;heavyGraceUntil=0;
    lastWarning=-Infinity;overdrive=false;admitted=0;delayed=0;peakWarnings=0;}
  function update(dt,{missionPhase='idle',waveNumber=0,heavyOverdrive=false}={}){
    const step=clamp(dt,0,.05);clock+=step;
    const nextPhase=String(missionPhase);
    const nextWave=Number.isInteger(waveNumber)?waveNumber:0;
    if(nextPhase!==phase || nextWave!==wave){
      phase=nextPhase;wave=nextWave;
      if(phase==='combat'&&WAVE_SETTINGS[wave])graceUntil=clock+WAVE_SETTINGS[wave].grace;
      else graceUntil=0;
      if(phase!=='combat'){heavyGraceUntil=0;overdrive=false;}
    }
    if(phase==='combat'&&wave===3&&heavyOverdrive&&!overdrive){
      overdrive=true;heavyGraceUntil=clock+bossPhaseGrace;
    }
    return snapshot();
  }
  function permit({role='assault',currentMode='approach',activeWarnings=0}={}){
    // A warning already underway must be allowed to finish; never cancel or
    // retroactively change the warning because a slot is full.
    if(currentMode==='telegraph')return true;
    if(phase!=='combat'||!WAVE_SETTINGS[wave])return true;
    const settings=WAVE_SETTINGS[wave];
    peakWarnings=Math.max(peakWarnings,Math.max(0,Math.trunc(activeWarnings)||0));
    const denied=clock<graceUntil || Math.max(0,activeWarnings)>=settings.limit ||
      clock-lastWarning<settings.gap || (role==='heavy'&&clock<heavyGraceUntil);
    if(denied)delayed++;
    return !denied;
  }
  function started(){
    // Only the real AI transition into 'telegraph' calls this method. No
    // reservation on cooldown/invalid LOS that would unfairly block other AI.
    lastWarning=clock;admitted++;
  }
  function snapshot(){return {phase,wave,admitted,delayed,peakWarnings,
    preparationRemaining:Math.max(0,graceUntil-clock),
    heavyGraceRemaining:Math.max(0,heavyGraceUntil-clock),
    warningGapRemaining:Math.max(0,lastWarning+(WAVE_SETTINGS[wave]?.gap||0)-clock),
    concurrentLimit:WAVE_SETTINGS[wave]?.limit??null};}
  return {update,permit,started,snapshot,reset};
}
