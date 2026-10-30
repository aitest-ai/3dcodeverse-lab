/**
 * Reusable pure v5.3 foot-contact planning / slope validation layer.
 * The full Windows game uses world-space CCD in mech-foot-ik.js and
 * MechGroundSampler to supply verified hits and Three.js quaternions.
 * This module is the dependency-free reference/acceptance kernel.
 */
export const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
export function terrainContact(hit, controllerY=0) {
  if (!hit || !Number.isFinite(hit.height) || !hit.normal ||
      !Number.isFinite(controllerY) || Math.abs(hit.height-controllerY)>.55) return null;
  const {x,y,z}=hit.normal;
  if (![x,y,z].every(Number.isFinite)) return null;
  const len=Math.hypot(x,y,z);
  if(len<1e-6)return null;
  const normal={x:x/len,y:y/len,z:z/len};
  if(normal.y<.72)return null;
  return {height:hit.height,normal,tiltRadians:clamp(Math.acos(clamp(normal.y,-1,1)),0,.24)};
}
export function createFootfallGate({minInterval=.18,maxError=.28}={}) {
  const legs={L:{stance:false,initialized:false,at:-1e3},
              R:{stance:false,initialized:false,at:-1e3}};
  let elapsed=0,emitted=0;
  function reset(){elapsed=0;for(const l of Object.values(legs)){l.stance=false;l.initialized=false;l.at=-1e3;}}
  function update({dt,side,stance,speed,error,position,normal}) {
    const leg=legs[side];if(!leg)return null;
    elapsed+=Math.max(0,Math.min(.1,Number(dt)||0));
    const valid=Number.isFinite(speed)&&Math.abs(speed)>.35 &&
      Number.isFinite(error)&&error<=maxError &&
      Array.isArray(position)&&position.length===3&&position.every(Number.isFinite);
    const justPlanted=!!stance&&!leg.stance;
    const shouldEmit=justPlanted&&leg.initialized&&valid&&elapsed-leg.at>minInterval;
    leg.stance=!!stance;leg.initialized=true;
    if(!shouldEmit)return null;
    leg.at=elapsed;emitted++;
    return {side,position:[...position],normal:normal||{x:0,y:1,z:0},
      strength:clamp(Math.abs(speed)/7,.14,.85)};
  }
  return {update,reset,get count(){return emitted;}};
}
export function createLaunchSettle() {
  let wasMoving=false,launch=0,settle=0;
  const reset=()=>{wasMoving=false;launch=0;settle=0;};
  function update(dt,speed){
    const step=clamp(Number(dt)||0,0,.08);
    const moving=Number.isFinite(speed)&&Math.abs(speed)>.48;
    if(moving&&!wasMoving)launch=1;
    if(!moving&&wasMoving)settle=1;
    wasMoving=moving;
    launch*=Math.exp(-step*6);settle*=Math.exp(-step*5);
    return {launch,settle};
  }
  return {update,reset};
}
