/**
 * Taipei Mech v5.7 visual intensity only. Pure deterministic envelopes;
 * may not affect line-of-sight, hitpoints, projectile flight or collision.
 * The caller owns meshes and disposal. Keep bounded even at 30/120 FPS.
 */
export const clampFX = (n,a=0,b=1) => Math.max(a,Math.min(b,Number.isFinite(n)?n:a));
export function beamIntensity(remaining,total,{charged=false,hostile=false}={}) {
  if (!Number.isFinite(total) || total<=0) return 0;
  const t=clampFX(1-remaining/total);
  const attack=clampFX(t/.055);
  const decay=Math.pow(1-t,charged?.6:hostile?1.1:1.45);
  return clampFX((.20+.80*attack)*decay);
}
export function ringPulse(distanceFraction,remaining,total,{charged=false}={}) {
  if (!Number.isFinite(total)||total<=0)return {position:0,alpha:0,scale:1};
  const p=clampFX(1-remaining/total);
  const x=clampFX(distanceFraction+.74*p);
  const alpha=clampFX((.9-p)*(.42+(charged?.45:.12)));
  return {position:x,alpha,scale:1+.42*Math.sin(Math.PI*p)};
}
export function explosionEnvelope(remaining,total) {
  if(!Number.isFinite(total)||total<=0)return {opacity:0,scale:1};
  const t=clampFX(1-remaining/total);
  return {opacity:clampFX(1-t*t),scale:1+2.2*t};
}
