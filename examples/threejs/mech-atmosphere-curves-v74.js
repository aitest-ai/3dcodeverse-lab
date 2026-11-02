/** v7.4: deterministic cosmetic timing only. No physics, damage, or camera cuts. */
const clamp=(v,a,b)=>Math.min(b,Math.max(a,Number.isFinite(v)?v:a));
export const ATMOSPHERE_PRESETS_V74=Object.freeze({
  full:Object.freeze({maxSmoke:36,perBlast:12,maxLights:3,smokeLifetime:3.4,lightPower:3.3}),
  balanced:Object.freeze({maxSmoke:22,perBlast:7,maxLights:1,smokeLifetime:2.7,lightPower:2.2}),
  light:Object.freeze({maxSmoke:9,perBlast:3,maxLights:0,smokeLifetime:2.0,lightPower:0})
});
export function smokeCurveV74(age,lifetime,seed=0){
  const t=clamp(age/Math.max(.05,lifetime),0,1);
  const fadeIn=clamp(t*9,0,1),fadeOut=(1-t)**1.8;
  return {alpha:clamp(fadeIn*fadeOut*.46,0,.46),
    radius:(.46+(seed%5)*.095)*(1+2.6*t),
    rise:1.1*t+(seed%4)*.18*t,
    drift:Math.sin(seed*1.37+t*2.2)*.32*t,finished:t>=1};
}
export function lightCurveV74(age,lifetime){const t=clamp(age/Math.max(.05,lifetime),0,1);return {intensity:(1-t)**2.1,finished:t>=1};}
export function cameraImpulseV74(kind,level='full',distance=0,reducedMotion=false){
  if(reducedMotion)return 0;
  const base={muzzle:.012,blast:.14,enemy_down:.10,boss:.09,victory:.07}[kind]??0;
  const weight=level==='light'?.28:level==='balanced'?.66:1;
  return clamp(base*weight*clamp(1-distance/75,0,1),0,.16);
}
