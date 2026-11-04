/**
 * V29 local-only live Three.js Object3D marker sampler.
 * Add only to a copy of the original V28 review viewer AFTER mixer.update.
 * Never modifies meshes, routes, colliders, World JSON, game entrypoint or site.
 * No network calls. Bone tip / palm, grip and sole offsets require human verification.
 */
export const REQUIRED_MARKERS=Object.freeze([
 'rider_hand_left','rider_hand_right','rider_foot_left','rider_foot_right',
 'bike_grip_left','bike_grip_right','bike_pedal_left','bike_pedal_right'
]);
export const SOURCE_SHA=Object.freeze({
 actor_glb:'4dab76c398f4c30c3aa62ef88e389b28974018c01fd271c08bf029d840d263d1',
 bike_glb:'7cb53e92247cf081354c1551b91ae812aab56be7c07748ed00764f0d2c844ece'
});
const phases=new Set(['straight','turn','start_stop']);
export function createContactProbe({renderer,markers,actorAnimation='Cycle',browserName='',
 nowUtc=new Date().toISOString(),maxSamples=30000}={}){
 if(!renderer||typeof renderer.getContext!=='function')throw new Error('需真實 Three.js WebGLRenderer');
 const context=renderer.getContext();
 if(typeof WebGL2RenderingContext==='undefined'||!(context instanceof WebGL2RenderingContext))
  throw new Error('缺少真正 WebGL2；DOM 測試不能代表 3D 騎行');
 if(actorAnimation!=='Cycle')throw new Error('必須使用原版 Cycle 動畫');
 if(!markers||REQUIRED_MARKERS.some(k=>!markers[k]?.node||
    typeof markers[k].node.getWorldPosition!=='function'))
  throw new Error('必須明確綁定原版人物與單車的 8 個 marker Object3D');
 if(typeof browserName!=='string'||browserName.trim().length<3)
  throw new Error('必須記錄真實瀏覽器名稱/版本');
 const frames=[];let last=-Infinity;
 function captureFrame(t_s,phase){
  if(!Number.isFinite(t_s)||t_s<0||t_s<=last)throw new Error('t_s 必須嚴格遞增');
  if(!phases.has(phase))throw new Error('必須由實際操作標記 straight/turn/start_stop');
  if(frames.length>=maxSamples)throw new Error('安全樣本上限');
  const measured={};
  for(const name of REQUIRED_MARKERS){
   const {node,localOffset=[0,0,0],vecFactory}=markers[name];
   if(!Array.isArray(localOffset)||localOffset.length!==3||
     localOffset.some(v=>!Number.isFinite(v)))throw new Error(name+' marker offset 無效');
   if(typeof vecFactory!=='function')throw new Error(name+' 缺少原 THREE.Vector3 vecFactory');
   node.updateWorldMatrix(true,false);
   const p=vecFactory(...localOffset);node.localToWorld(p);
   const coords=[p.x,p.y,p.z];
   if(!coords.every(Number.isFinite))throw new Error(name+' 世界座標無效');
   measured[name]=coords;
  }
  frames.push({t_s,phase,markers:measured});last=t_s;return frames.length;
 }
 function exportData(){
  return {schema:'setouchi.pose_contact.capture.v1',source:'runtime_capture',
   coordinate_system:'THREE_WORLD_METERS',player_animation:actorAnimation,
   asset_sha256:{...SOURCE_SHA},
   environment:{webgl2:true,capture_method:'live_scene_world_matrices',
     browser:browserName,capture_utc:nowUtc},
   frames:frames.map(f=>({...f,markers:Object.fromEntries(
     Object.entries(f.markers).map(([k,v])=>[k,[...v]]))})),
   safety_notice:'Evidence only. Locally verify original GLB SHA and visually inspect grips/feet; never activate the road.'};
 }
 function download(filename='Onomichi_V29_Local_Pose_Contact_Capture.json'){
  if(typeof document==='undefined'||typeof URL==='undefined'||typeof Blob==='undefined')
   throw new Error('只能由本機瀏覽器手動另存，不可網路上傳');
  const url=URL.createObjectURL(new Blob([JSON.stringify(exportData(),null,2)+'\n'],
    {type:'application/json'}));
  try{const a=document.createElement('a');a.href=url;a.download=filename;a.click()}
  finally{URL.revokeObjectURL(url)}
 }
 return Object.freeze({captureFrame,exportData,download,get frameCount(){return frames.length}});
}
