/** Taipei Mecha v8.4 real exported Empty node position, visual-only candidate.
 * Never adjusts combat.fire, OSM collider ray, damage, projectile or enemy AI.
 */
export const ANCHOR_NAME_V84='MuzzleTip_R';
const valid=v=>v&&[v.x,v.y,v.z].every(n=>Number.isFinite(n));
const unit=v=>{const d=Math.hypot(v.x,v.y,v.z);return d>1e-8?{x:v.x/d,y:v.y/d,z:v.z/d}:null};
export function sampleAuthoredMuzzleV84({model,makeVector,poseUpdated=false}={}){
 if(!poseUpdated)return {status:'pose_not_evaluated'};
 if(!model||typeof model.traverse!=='function'||typeof makeVector!=='function')return {status:'no_live_glb'};
 const matches=[];model.traverse(n=>{if(n?.name===ANCHOR_NAME_V84)matches.push(n)});
 if(matches.length!==1)return {status:matches.length?'duplicate_anchor':'anchor_missing'};
 const node=matches[0];
 if(typeof node.getWorldPosition!=='function'||typeof node.localToWorld!=='function')return {status:'invalid_node'};
 try{
  node.updateWorldMatrix?.(true,false);
  const p=node.getWorldPosition(makeVector(0,0,0));
  const front=node.localToWorld(makeVector(0,-1,0));
  if(!valid(p)||!valid(front))return {status:'nonfinite_transform'};
  const direction=unit({x:front.x-p.x,y:front.y-p.y,z:front.z-p.z});
  if(!direction)return {status:'degenerate_forward'};
  return {status:'authored_node_ready',tip:{x:p.x,y:p.y,z:p.z},forward:direction,
   provenance:'distinct GLB MuzzleTip_R node from measured cannon geometry'};
 }catch{return {status:'node_transform_error'}}
}
export function evaluateVisualOnlyAlignmentV84(authored,ray,{maxDistance=.3,maxDegrees=18}={}){
 if(authored?.status!=='authored_node_ready'||!valid(ray?.start)||!valid(ray?.dir))
   return {status:'unavailable',safeForVisualPreview:false};
 const direction=unit(ray.dir);if(!direction)return {status:'invalid_ray',safeForVisualPreview:false};
 const gap=Math.hypot(authored.tip.x-ray.start.x,authored.tip.y-ray.start.y,authored.tip.z-ray.start.z);
 const dot=authored.forward.x*direction.x+authored.forward.y*direction.y+authored.forward.z*direction.z;
 const angle=Math.acos(Math.max(-1,Math.min(1,dot)))*180/Math.PI;
 return {status:'evaluated',tipToRayMeters:Math.round(gap*1000)/1000,
  angleDegrees:Math.round(angle*10)/10,safeForVisualPreview:gap<=maxDistance&&angle<=maxDegrees,
  gameplayRayUnchanged:true};
}
