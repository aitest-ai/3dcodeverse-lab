/**
 * Reusable v5.1 Three.js planted-foot solver reference.
 * This is a visual postprocess, NOT a foot-contact physics engine.
 * Install after AnimationMixer.update() and before visual hydraulics update.
 * Production Windows addon additionally implements teleport reset, toggle,
 * bounded turning lean, status UI and model fallbacks.
 */
export function createPlantedFootCCD({THREE, model, rig, groundHeightAt}) {
  if (!THREE?.Vector3 || !THREE?.Quaternion || !model || !rig) throw Error('Three.js model and rig required');
  const V = THREE.Vector3, Q = THREE.Quaternion;
  const hips = ['L','R'].map(side => ({
    side, thigh:model.getObjectByName('thigh.'+side),
    shin:model.getObjectByName('shin.'+side),
    foot:model.getObjectByName('foot.'+side),
    held:false, target:new V(), ankleHeight:null
  }));
  if (hips.some(x=>!x.thigh || !x.shin || !x.foot)) {
    return {available:false,update(){},reset(){},dispose(){}};
  }
  const p0=new V(),p1=new V(),from=new V(),toward=new V(),delta=new Q(),parentQ=new Q(),rot=new Q(),footQ=new Q(),footParentQ=new Q();
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  let previous=null,enabled=true;
  function reset(){previous=null;for(const l of hips){l.held=false;l.ankleHeight=null;}}
  function ground(x,z) {
    const value=typeof groundHeightAt==='function'?groundHeightAt(x,z):NaN;
    if(Number.isFinite(value))return value;
    return rig.getWorldPosition(new V()).y;
  }
  function turn(joint,foot,goal) {
    joint.getWorldPosition(p0);
    foot.getWorldPosition(p1);
    from.subVectors(p1,p0); toward.subVectors(goal,p0);
    const lf=from.length(),lt=toward.length();
    if(lf<1e-5 || lt<1e-5)return;
    from.multiplyScalar(1/lf);toward.multiplyScalar(1/lt);
    const angle=Math.acos(clamp(from.dot(toward),-1,1));
    if(angle<1e-4)return;
    delta.setFromUnitVectors(from,toward);
    if(angle>.16)delta.copy(new Q().slerp(delta,.16/angle));
    joint.parent.getWorldQuaternion(parentQ);
    rot.copy(parentQ).invert().multiply(delta).multiply(parentQ);
    joint.quaternion.premultiply(rot).normalize();
  }
  function update({speed=0,runPhase=0}={}) {
    if(!enabled)return;
    const rootNow=rig.getWorldPosition(new V());
    if(previous && rootNow.distanceTo(previous)>1.45)reset();
    previous=rootNow;
    model.updateMatrixWorld(true);
    for(const l of hips) {
      const phase=((runPhase+(l.side==='R'?.5:0))%1+1)%1;
      const stance=Math.abs(speed)<.35 || phase<.54;
      l.foot.getWorldPosition(p1);
      const present=p1.clone();
      const surface=ground(present.x,present.z);
      if(l.ankleHeight===null)l.ankleHeight=clamp(present.y-surface,.10,.42);
      if(!stance){l.held=false;continue;}
      if(!l.held || present.distanceTo(l.target)>1.05){
        l.target.copy(present);l.target.y=surface+l.ankleHeight;l.held=true;
      }
      l.foot.getWorldQuaternion(footQ);
      for(let i=0;i<3;i++){turn(l.shin,l.foot,l.target);turn(l.thigh,l.foot,l.target);}
      // Preserve animated world foot orientation despite hip/knee correction.
      l.foot.parent.getWorldQuaternion(footParentQ);
      l.foot.quaternion.copy(footParentQ.invert()).multiply(footQ).normalize();
    }
  }
  return {available:true,update,reset,setEnabled(x){enabled=!!x;reset();},dispose(){enabled=false;reset();}};
}
