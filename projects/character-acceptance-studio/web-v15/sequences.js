// Phase-aligned acceptance sequences. SE(2) attachment carries world travel/heading across native clips.
// This is not an arbitrary-time gameplay transition controller or a retargeter.
export const presets = {
  walk: {label:'待機 → 起步 → 走路 ×2 → 停步 → 待機', clips:['Idle','Start','Walk','Walk','Stop','Idle']},
  turn: {label:'待機 → 左轉 → 待機 → 右轉 → 待機', clips:['Idle','TurnLeft','Idle','TurnRight','Idle']},
};
export function rotate(yaw, x, z) {
  const c=Math.cos(yaw), s=Math.sin(yaw);
  return [c*x+s*z,-s*x+c*z];
}
export function compose(a,b) {
  const [x,z]=rotate(a.yaw,b.x,b.z);
  return {x:a.x+x,z:a.z+z,yaw:a.yaw+b.yaw};
}
export function inverse(a) {
  const [x,z]=rotate(-a.yaw,-a.x,-a.z);
  return {x,z,yaw:-a.yaw};
}
export function power(transform,count) {
  let result={x:0,z:0,yaw:0},base=transform,n=count;
  while(n>0){if(n%2)result=compose(result,base);base=compose(base,base);n=Math.floor(n/2);}
  return result;
}
export function buildSequence(id, clips) {
  const preset=presets[id];
  if(!preset)throw Error('Unknown acceptance sequence '+id);
  let end={x:0,z:0,yaw:0},time=0;
  const segments=preset.clips.map((name,index)=>{
    const clip=clips[name];
    if(!clip||!(clip.duration>0))throw Error('Missing sequence clip '+name);
    const attach=compose(end,inverse(clip.start));
    const segment={index,name,start:time,end:time+clip.duration,duration:clip.duration,attach};
    end=compose(attach,clip.end);time=segment.end;
    return segment;
  });
  return {id,label:preset.label,segments,duration:time,end};
}
export function sampleSequence(plan,time,cycles=0) {
  const t=Math.max(0,Math.min(plan.duration,time));
  const segment=plan.segments.find(s=>t<s.end-1e-9)||plan.segments.at(-1);
  return {...segment,local:Math.min(segment.duration,Math.max(0,t-segment.start)),
    attach:compose(power(plan.end,cycles),segment.attach)};
}
