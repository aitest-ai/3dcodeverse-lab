/* V30 source locks and pure validation helpers. No assets, uploads or network. */
export const V30_ASSETS=Object.freeze({
 actor:'4dab76c398f4c30c3aa62ef88e389b28974018c01fd271c08bf029d840d263d1',
 bike:'7cb53e92247cf081354c1551b91ae812aab56be7c07748ed00764f0d2c844ece'
});
export const V30_MARKERS=Object.freeze([
 {id:'rider_hand_left',part:'actor',name:'左手掌',color:'#58d7be'},
 {id:'bike_grip_left',part:'bike',name:'左車把',color:'#58d7be'},
 {id:'rider_hand_right',part:'actor',name:'右手掌',color:'#83baff'},
 {id:'bike_grip_right',part:'bike',name:'右車把',color:'#83baff'},
 {id:'rider_foot_left',part:'actor',name:'左腳掌',color:'#ffc487'},
 {id:'bike_pedal_left',part:'bike',name:'左踏板',color:'#ffc487'},
 {id:'rider_foot_right',part:'actor',name:'右腳掌',color:'#e7a2f4'},
 {id:'bike_pedal_right',part:'bike',name:'右踏板',color:'#e7a2f4'}
]);
export const V30_PAIRS=Object.freeze([
 ['rider_hand_left','bike_grip_left','左手－車把'],
 ['rider_hand_right','bike_grip_right','右手－車把'],
 ['rider_foot_left','bike_pedal_left','左腳－踏板'],
 ['rider_foot_right','bike_pedal_right','右腳－踏板']
]);
export function ensureOriginalSha(hashes){
 if(!hashes||hashes.actor!==V30_ASSETS.actor||hashes.bike!==V30_ASSETS.bike)
  throw new Error('不是 V28 來源鎖定的原人物與自行車 GLB，禁止當成原版載入');
 return true;
}
export async function digestSha256(buffer){
 if(!(buffer instanceof ArrayBuffer))throw new Error('請提供 ArrayBuffer 原始位元組');
 if(typeof crypto==='undefined'||!crypto.subtle)throw new Error('此瀏覽器不支援 SHA256 Web Crypto');
 const bytes=new Uint8Array(await crypto.subtle.digest('SHA-256',buffer));
 return Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');
}
export function validateGlbHeader(buf){
 if(!(buf instanceof ArrayBuffer)||buf.byteLength<20||buf.byteLength>150*1024*1024)
  throw new Error('GLB 大小不合理（允許 20B 至 150MB）');
 const d=new DataView(buf);
 if(d.getUint32(0,true)!==0x46546c67||d.getUint32(4,true)!==2||d.getUint32(8,true)!==buf.byteLength)
  throw new Error('非有效 glTF 2.0 GLB 格式');
 if(d.getUint32(16,true)!==0x4e4f534a||d.getUint32(12,true)<2)
  throw new Error('缺少 GLB JSON 區段');
 return true;
}
export function finiteOffset(offset){
 return Array.isArray(offset)&&offset.length===3&&offset.every(n=>typeof n==='number'&&Number.isFinite(n)&&Math.abs(n)<=3);
}
export function validateMarkerConfig(data){
 if(!data||data.schema!=='setouchi.v30.marker.config.v1')throw new Error('標記設定版本不符');
 ensureOriginalSha(data.asset_sha256);
 if(!data.markers||typeof data.markers!=='object')throw new Error('標記資料缺失');
 for(const m of V30_MARKERS){
  const v=data.markers[m.id];
  if(!v||!Array.isArray(v.path)||!v.path.every(i=>Number.isInteger(i)&&i>=0&&i<50000)||!finiteOffset(v.offset))
   throw new Error('標記 '+m.name+' 的節點路徑或本地偏移無效');
 }
 return true;
}
export function nearestStats(values){
 if(!Array.isArray(values)||!values.length||values.some(v=>!Number.isFinite(v)||v<0))return null;
 const v=[...values].sort((a,b)=>a-b),p=q=>{
  const pos=(v.length-1)*q,lo=Math.floor(pos),hi=Math.ceil(pos);
  return v[lo]+(v[hi]-v[lo])*(pos-lo);
 };
 return {count:v.length,median:p(.5),p95:p(.95),max:v[v.length-1]};
}
export const V30_LIMITATIONS=Object.freeze({
 sourceShaRequired:true, originalGameEngineIntegrated:false,
 originalGameplayTested:false, legalRoadRightsVerified:false,
 realRoadCollisionApproved:false, privateAssetsUploaded:false,
 sourceBranchModified:false, originalSiteDeployed:false
});
