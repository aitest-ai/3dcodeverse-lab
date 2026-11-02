// V020: view-only proximity and lateral-position state for V019 centreline markers.
// No collision, route, ground or player-position mutation is permitted.
import {nearestRoute} from './navigation.js';
export const PORCH_GUIDE_WINDOW = Object.freeze({start:84.5,end:105,lookAhead:15,lookBack:3,previewStart:70,previewEnd:120});
export function evaluatePorchGuide(route,samples,position,stage,enabled,warningOffset=-0.45){
  if(!Array.isArray(route)||route.length<2||!Array.isArray(samples)||!position||
    ![position.x,position.z].every(Number.isFinite))
    return {active:false,visibleIndices:[],lateralOffsetM:null,progress:0,s:null,nearby:false,warning:false};
  const near=nearestRoute(route,position.x,position.z);
  if(!near||!Number.isFinite(near.s))return {active:false,visibleIndices:[],lateralOffsetM:null,progress:0,s:null,nearby:false,warning:false};
  const s=near.s,W=PORCH_GUIDE_WINDOW;
  const nearby=stage==='B'&&enabled===true&&s>=W.previewStart&&s<=W.previewEnd;
  const visibleIndices=nearby?samples.flatMap((p,i)=>
    Number.isFinite(p.s_m)&&p.s_m>=s-W.lookBack&&p.s_m<=s+W.lookAhead?[i]:[]):[];
  const active=stage==='B'&&enabled===true&&s>=W.start&&s<=W.end;
  let lateralOffsetM=null;
  if(active){
    // Signed left-side offset from the tangent; route is in local metres.
    const k=route.findIndex(p=>p.s>=s);
    const i=Math.max(1,k<0?route.length-1:k);
    const a=route[i-1],b=route[i],dx=b.x-a.x,dz=b.z-a.z,len=Math.hypot(dx,dz);
    lateralOffsetM=len>1e-8?(-(dz/len)*(position.x-near.x)+(dx/len)*(position.z-near.z)):null;
  }
  return {active,nearby,visibleIndices,lateralOffsetM,
    progress:Math.max(0,Math.min(1,(s-85)/18)),s,
    warning:active&&lateralOffsetM!==null&&lateralOffsetM<warningOffset};
}
