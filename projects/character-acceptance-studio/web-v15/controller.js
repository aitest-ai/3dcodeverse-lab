// Intent replay at complete native clip boundaries. World placement composes in SE(2).
import {compose} from './sequences.js';
export const commands=['go','stop','left','right'];
const zero=()=>({x:0,z:0,yaw:0});
export function sampleController(events,time,entry){
 const T=entry.walk_plan.duration_s;
 const lengths={StartWalk:3*T,RestartWalk:3*T,StopWalk:3*T,WalkWorld:T,WalkTurnLeft:5*T,WalkTurnRight:5*T};
 let clip='StandReady',start=0,origin=zero(),moving=false,pending=null;
 const hold=()=>clip==='StandReady'||clip==='StandStopped';
 function begin(name,t){clip=name;start=t;}
 function advance(t){
  let guard=0;
  while(!hold()&&start+lengths[clip]<=t+1e-10){
   if(++guard>200000)throw Error('Controller replay limit');
   const end=start+lengths[clip];origin=compose(origin,entry.root_clips[clip].end);
   if(clip==='StopWalk'){begin('StandStopped',end);if(moving)begin('RestartWalk',end);}
   else if(!moving)begin('StopWalk',end);
   else if(pending){begin(pending==='left'?'WalkTurnLeft':'WalkTurnRight',end);pending=null;}
   else begin('WalkWorld',end);
  }
 }
 for(const e of events){
  if(e.time>time+1e-10)break;
  advance(e.time);
  if(e.command==='stop'){moving=false;pending=null;}
  else {moving=true;if(e.command==='left'||e.command==='right')pending=e.command;}
  if(hold()&&moving)begin(clip==='StandReady'?'StartWalk':'RestartWalk',e.time);
 }
 advance(time);
 const isHold=hold(),clipTime=isHold?0:Math.max(0,Math.min(lengths[clip],time-start));
 const state=isHold?(clip==='StandReady'?'ready':'stopped'):clip==='StopWalk'?'stopping':clip.includes('Turn')?'turning':clip==='WalkWorld'?'walking':'starting';
 return {clip,clipTime,origin,state,moving,pending,segmentStart:start,segmentEnd:isHold?null:start+lengths[clip],waitSeconds:isHold?0:Math.max(0,start+lengths[clip]-time)};
}
export function request(events,time,command){
 if(!commands.includes(command)||!Number.isFinite(time)||time<0)throw Error('Invalid controller command');
 // Keep command order at the same instant: stop then go must still cancel a queued turn.
 return [...events.filter(e=>e.time<=time),{time,command}];
}
export const demoEvents=[{time:0,command:'go'},{time:4,command:'stop'},{time:9,command:'left'},{time:15,command:'right'},{time:22,command:'stop'},{time:27,command:'go'},{time:31,command:'stop'}];
export const demoDuration=36;
