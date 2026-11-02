/** v7.6 authored smoke texture and temporal color: original deterministic
 * stylized volumetric proxy, NOT a physically simulated volume. Pure JS,
 * no network, no GPU side effects. 2 shared 64px textures = 32 KiB RGBA.
 */
const clamp=(x,a,b)=>Math.max(a,Math.min(b,Number.isFinite(x)?x:a));
const fract=x=>x-Math.floor(x);
const hash=(x,y,variant)=>fract(Math.sin(x*127.1+y*311.7+variant*74.7)*43758.5453);
const smooth=(x,y,variant)=>{
  const ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy;
  const ux=fx*fx*(3-2*fx),uy=fy*fy*(3-2*fy);
  const a=hash(ix,iy,variant),b=hash(ix+1,iy,variant);
  const c=hash(ix,iy+1,variant),d=hash(ix+1,iy+1,variant);
  return (a+(b-a)*ux)*(1-uy)+(c+(d-c)*ux)*uy;
};
export const SMOKE_STYLE_V76=Object.freeze({
  resolution:64,variants:2,minAlpha:0,maxOpacity:.31,
  layers:'two shared nonrepeating appearance variants; one Sprite per smoke particle'
});
export function makeSmokePixelsV76(size=64,variant=0){
  if(!Number.isInteger(size)||size<16||size>128)throw RangeError('size 16..128');
  if(!Number.isInteger(variant)||variant<0||variant>3)throw RangeError('invalid variant');
  const pixels=new Uint8Array(size*size*4);
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
    const nx=(x+.5)/size*2-1,ny=(y+.5)/size*2-1;
    const u=nx*1.02+Math.sin(ny*4.4+variant*.8)*.065;
    const radius=Math.hypot(u,ny*.97);
    const n1=smooth((nx+1)*3.3,(ny+1)*3.5,variant);
    const n2=smooth((nx+1)*8.8,(ny+1)*7.2,variant+9);
    const n3=smooth((nx+1)*15.5,(ny+1)*17.5,variant+13);
    const edge=clamp((1.01-radius)/(.26+.12*(n1-.5)),0,1);
    const breakup=clamp(.45+.7*n1+.38*(n2-.5)+.13*(n3-.5),0,1);
    // Frayed translucency at the rim and a dark irregular center reduce the
    // old uniform grey/white-disc problem, without pushing opacity above cap.
    const alpha=Math.pow(edge,1.35)*breakup*.66;
    const shade=clamp(.64+.32*n1+.13*(n2-.5),.48,1);
    const i=(y*size+x)*4;
    pixels[i]=Math.round(115*shade);pixels[i+1]=Math.round(127*shade);
    pixels[i+2]=Math.round(134*shade);pixels[i+3]=Math.round(clamp(alpha,0,.66)*255);
  }
  return pixels;
}
export function smokeMaterialFrameV76(age,lifetime,seed=0,kind='blast'){
  const t=clamp(age/Math.max(.05,lifetime),0,1);
  const rise=clamp(t*8,0,1),decay=Math.pow(1-t,1.78);
  // Fire-colored thin core at birth -> dusty blue grey -> cooled dark smoke.
  const hot=(kind==='facade'?.10:kind==='enemy_down'?.65:1)*Math.pow(1-t,8);
  const cool=(kind==='facade'?1.0:.90);
  const r=(.37+hot*.18)*cool,g=(.415+hot*.065)*cool,b=(.45-hot*.13)*cool;
  const variant=Math.abs(Math.trunc(seed))%SMOKE_STYLE_V76.variants;
  return {variant,opacity:clamp(rise*decay*(.25+(seed%5)*.010),0,SMOKE_STYLE_V76.maxOpacity),
    tint:[clamp(r,0,1),clamp(g,0,1),clamp(b,0,1)],
    radius:(.46+(seed%5)*.095)*(1+2.6*t),
    rise:1.1*t+(seed%4)*.18*t,drift:Math.sin(seed*1.37+t*2.2)*.32*t,
    finished:t>=1};
}
export function blastLightFrameV76(age,lifetime,{peak=1,kind='blast'}={}){
  const t=clamp(age/Math.max(.05,lifetime),0,1);
  // Actual short-lived light flash: immediate ignition, nonzero but quick
  // decay, no extra shadows; RGB components are *linear* three.js colors.
  const envelope=Math.pow(1-t,2.5)*(kind==='muzzle'?.6:1);
  const heat=Math.pow(1-t,4);
  const from=kind==='muzzle'?[.60,.88,1]:kind==='boss'?[1,.60,.27]:[1,.43,.16];
  const to=kind==='muzzle'?[.35,.64,.85]:[.58,.31,.20];
  const rgb=from.map((v,i)=>clamp(to[i]+(v-to[i])*heat,0,1));
  return {intensity:clamp(peak,0,30)*envelope,rgb,finished:t>=1};
}
