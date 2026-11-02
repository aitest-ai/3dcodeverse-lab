/** Taipei Mech v7.7 — scene-aware cosmetic light, not a new city light rig.
 * Real Slop Taipei uses golden / midday / midnight buttons. Camera world-space
 * distance only adjusts translucent smoke overdraw, never weapon visibility,
 * cover tests, OSM geometry, physics or damage. No clock/location guesses.
 */
const clamp=(x,lo,hi)=>Math.max(lo,Math.min(hi,Number.isFinite(x)?x:lo));
const smooth=t=>{const v=clamp(t,0,1);return v*v*(3-2*v);};
export const SCENE_PRESETS_V77=Object.freeze({
  golden:Object.freeze({label:'黃金時刻',smokeTint:[.93,.87,.81],lightScale:.75,warmth:1.05}),
  midday:Object.freeze({label:'晴朗正午',smokeTint:[.95,.98,1],lightScale:.47,warmth:.88}),
  midnight:Object.freeze({label:'臺北夜晚',smokeTint:[.75,.82,.98],lightScale:1.0,warmth:1.0})
});
export function cityLightingPresetV77(value){return Object.hasOwn(SCENE_PRESETS_V77,value)?value:'golden';}
export function smokeViewFrameV77({preset='golden',cameraDistance=20,baseAlpha=0,baseTint=[.45,.45,.45],t=0}={}){
 const p=SCENE_PRESETS_V77[cityLightingPresetV77(preset)];
 const near=smooth((clamp(cameraDistance,0,10000)-1.65)/2.85);
 const far=1-smooth((clamp(cameraDistance,0,10000)-48)/46);
 const factor=clamp(near*far,0,1);
 const age=clamp(t,0,1);
 // Avoid bright opaque white discs; keep material alpha bounded even in daylight.
 const color=baseTint.map((x,i)=>clamp(x*p.smokeTint[i]*(1-.12*age),0,1));
 return {opacity:clamp(baseAlpha*factor,0,.31),tint:color,nearFade:near,farFade:far};
}
export function sceneExplosionLightV77({preset='golden',baseIntensity=1,baseRGB=[1,.45,.16],t=0}={}){
 const p=SCENE_PRESETS_V77[cityLightingPresetV77(preset)];
 // Existing short-lived THREE.PointLight is the actual local PBR illumination.
 // On bright midday its contrast is lower; at night it must remain bounded by
 // the original light cap and cannot spawn additional shadow sources.
 const color=baseRGB.map((v,i)=>clamp(v*(i===0?p.warmth:i===2?1/p.warmth:1),0,1));
 return {intensity:clamp(baseIntensity,0,50)*p.lightScale,color};
}
export function cameraDistanceV77(camera,point){
 if(!camera||!point||![camera.x,camera.y,camera.z,point.x,point.y,point.z].every(Number.isFinite))return 20;
 return Math.hypot(camera.x-point.x,camera.y-point.y,camera.z-point.z);
}
