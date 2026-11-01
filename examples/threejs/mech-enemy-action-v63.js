/**
 * v6.3 enemy action director. One-shot Fire/Hit only on authoritative events;
 * pre-fire warnings must not fire the animation. Animation root translation is
 * masked by visual GLB loader; OSM controller always owns actual movement.
 */
export function createEnemyActionDirectorV63(actions,{loopOnce=null}={}) {
  if (!actions || typeof actions.get!=='function') throw new TypeError('Action map required');
  let current='Idle', hold=0, lastHP=null, shots=0, flinches=0, transitions=0;
  const clamp=(n,lo,hi)=>Math.max(lo,Math.min(hi,Number.isFinite(n)?n:lo));
  const oneshot={Fire:{hold:.64,speed:3.05},Hit:{hold:.64,speed:3.05}};
  const action=(name)=>actions.get(name)||null;
  function switchTo(name) {
    const next=action(name);
    if(!next||name===current)return false;
    const previous=action(current);
    next.enabled=true;
    next.reset?.();
    next.timeScale=oneshot[name]?.speed ?? (name==='Run'?1.18:1);
    next.clampWhenFinished=!!oneshot[name];
    if(oneshot[name]&&loopOnce!==null)next.setLoop?.(loopOnce,1);
    next.play?.();
    if(previous&&previous!==next){
      if(typeof next.crossFadeFrom==='function')next.crossFadeFrom(previous,name==='Hit'?.07:.12,false);
      else previous.stop?.();
    }
    current=name;transitions++;return true;
  }
  function prime(){
    const idle=action('Idle');
    if(idle){idle.enabled=true;idle.clampWhenFinished=false;idle.timeScale=1;idle.reset?.();idle.play?.();}
    current='Idle';hold=0;
  }
  function update(dt,{moving=false,shot=false,health=null}={}) {
    const step=clamp(dt,0,.05);
    const hp=Number.isFinite(health)?health:null;
    const newHit=hp!==null&&lastHP!==null&&hp<lastHP;
    if(hp!==null)lastHP=hp;
    if(newHit){flinches++;hold=oneshot.Hit.hold;switchTo('Hit');}
    else if(shot){shots++;hold=oneshot.Fire.hold;switchTo('Fire');}
    else if(hold>0){
      hold=Math.max(0,hold-step);
      if(hold===0)switchTo(moving?'Run':'Idle');
    } else switchTo(moving?'Run':'Idle');
    return {current,hold,shots,flinches,transitions,hit:newHit};
  }
  function reset(){
    for(const a of actions.values())a.stop?.();
    lastHP=null;shots=0;flinches=0;transitions=0;prime();
  }
  function snapshot(){return {current,hold,shots,flinches,transitions};}
  prime();
  return {update,reset,snapshot};
}
