/**
 * Taipei Mech v5.5 - real, authority-constrained lateral sidestep.
 *
 * No teleportation, hit immunity or remote state mutation. The caller owns the
 * authoritative collision resolver AND must apply returned positions to its
 * controller. This is a pure simulation module (no Three.js dependency).
 *
 * World coordinates are x/z in meters. `right` is a normalized 2-D direction.
 */
const clamp = (x, low, high) => Math.min(high, Math.max(low, x));
const finite = n => typeof n === 'number' && Number.isFinite(n);
const xy = p => p && finite(p.x) && finite(p.z);
const ease = t => 0.5 - 0.5 * Math.cos(Math.PI * clamp(t, 0, 1));

export function createMechDodgeV55({
  distance = 3.2,
  duration = 0.36,
  cooldown = 0.85,
  staminaMax = 100,
  staminaCost = 35,
  staminaRegen = 18,
  radius = 0.72
} = {}) {
  for (const [key, value] of Object.entries({distance,duration,cooldown,staminaMax,staminaCost,staminaRegen,radius})) {
    if (!finite(value) || value < 0) throw new TypeError(key + ' must be finite and >= 0');
  }
  if (duration < 0.1 || duration > 2 || distance > 12 || radius < 0.1 || radius > 4 || staminaMax < staminaCost)
    throw new RangeError('Unsafe sidestep configuration');
  let phase = 'idle', elapsed = 0, lastSide = 1;
  let stamina = staminaMax, remainingCooldown = 0;
  let count = 0, contacts = 0, totalActual = 0;
  let disposed = false;
  const state = () => ({phase, progress:phase==='dodge'?clamp(elapsed/duration,0,1):0,
    stamina, remainingCooldown, side:lastSide, count, contacts, totalActual,
    moving:phase==='dodge', invulnerable:false});
  function begin(side = 1) {
    if (disposed || phase==='dodge' || remainingCooldown>1e-8 || stamina < staminaCost) return false;
    lastSide = Number(side)<0 ? -1 : 1;
    phase='dodge'; elapsed=0;
    stamina-=staminaCost;
    remainingCooldown=cooldown;
    count++;
    return true;
  }
  function update(dt, {position, right, resolveMovement} = {}) {
    const t=finite(dt)?clamp(dt,0,0.05):0;
    if (disposed) return {...state(), position:xy(position)?{x:position.x,z:position.z}:null,
      delta:{x:0,z:0}, blocked:false, error:'disposed'};
    const p=xy(position)?{x:position.x,z:position.z}:null;
    let requested={x:0,z:0}, delta={x:0,z:0}, blocked=false, error=null;
    remainingCooldown=Math.max(0,remainingCooldown-t);
    stamina=Math.min(staminaMax,stamina+staminaRegen*t);
    if (phase==='dodge') {
      const start=elapsed/duration;
      elapsed=Math.min(duration,elapsed+t);
      const travel=distance*(ease(elapsed/duration)-ease(start));
      if (travel>0 && p) {
        const len=right&&finite(right.x)&&finite(right.z)?Math.hypot(right.x,right.z):0;
        if (len>0.999 && len<1.001 && typeof resolveMovement==='function') {
          requested={x:lastSide*right.x*travel, z:lastSide*right.z*travel};
          const target={x:p.x+requested.x,z:p.z+requested.z};
          try {
            const q=resolveMovement({...p},target,{radius, mode:'sidestep'});
            // Fail closed: never trust a resolver that returns points beyond the requested segment.
            if (!xy(q)) {blocked=true;error='invalid collision result';}
            else {
              const tx=target.x-p.x, tz=target.z-p.z, mag2=tx*tx+tz*tz;
              const ux=q.x-p.x, uz=q.z-p.z;
              const dot=ux*tx+uz*tz, cross=Math.abs(ux*tz-uz*tx);
              if (!finite(dot)||!finite(cross)||dot < -1e-7 || dot > mag2+1e-5 || cross>Math.sqrt(mag2)*1e-4) {
                blocked=true;error='resolver attempted unsafe displacement';
              } else {
                delta={x:ux,z:uz};
                blocked=Math.hypot(ux-tx,uz-tz)>1e-5;
                if (blocked) contacts++;
                totalActual+=Math.hypot(ux,uz);
              }
            }
          } catch {blocked=true;error='resolver failed';}
        } else {blocked=true;error='collision resolver or normalized right vector missing';}
      } else if (travel>0) {blocked=true;error='position missing';}
      if (elapsed>=duration-1e-9) {phase='idle';elapsed=0;}
    }
    return {...state(), position:p?{x:p.x+delta.x,z:p.z+delta.z}:null,
      delta,requested,blocked,error};
  }
  function reset() {phase='idle';elapsed=0;stamina=staminaMax;remainingCooldown=0;lastSide=1;count=0;contacts=0;totalActual=0;}
  function dispose() {reset();disposed=true;}
  return {begin,update,snapshot:state,reset,dispose};
}

/**
 * Minimal swept circle-versus-AABB resolver for a flat test map.
 * Do not use this demo reference for multi-level OSM collision geometry.
 * Resolves swept horizontal movement to the nearest first contact.
 */
export function createFlatTestCollision({obstacles=[],bounds={minX:-40,maxX:40,minZ:-40,maxZ:40}}={}) {
  return function resolveMovement(from,to,{radius=0.72}={}) {
    if (!xy(from)||!xy(to)) return null;
    const dx=to.x-from.x,dz=to.z-from.z;
    let u=1;
    for(const b of obstacles){
      if (![b.minX,b.maxX,b.minZ,b.maxZ].every(finite)) continue;
      const minX=b.minX-radius,maxX=b.maxX+radius,minZ=b.minZ-radius,maxZ=b.maxZ+radius;
      // If already overlapping a collider, don't move further into it.
      if (from.x>minX && from.x<maxX && from.z>minZ && from.z<maxZ){
        if (to.x>minX && to.x<maxX && to.z>minZ && to.z<maxZ) u=0;
        continue;
      }
      let lo=0,hi=1;
      for(const [o,d,mn,mx] of [[from.x,dx,minX,maxX],[from.z,dz,minZ,maxZ]]){
        if(Math.abs(d)<1e-10){if(o<mn||o>mx){lo=2;break;}}
        else {const a=(mn-o)/d,c=(mx-o)/d;lo=Math.max(lo,Math.min(a,c));hi=Math.min(hi,Math.max(a,c));}
      }
      if(lo<=hi && hi>=0 && lo<=1)u=Math.min(u,Math.max(0,lo-1e-5));
    }
    for (const [o,d,min,max] of [[from.x,dx,bounds.minX+radius,bounds.maxX-radius],[from.z,dz,bounds.minZ+radius,bounds.maxZ-radius]]) {
      if(Math.abs(d)>1e-10){const limit=(d>0?max:min);u=Math.min(u,clamp((limit-o)/d,0,1));}
    }
    return {x:from.x+dx*u,z:from.z+dz*u};
  };
}
