/**
 * Taipei Mecha v8.0 portable review of EXISTING genuine-v7.8 capture Blobs.
 * This module never creates a frame or verifies WebGPU provenance.
 * Full Windows installer/overlay lives in the separate v8.0 downloadable diff ZIP.
 */
import {auditThreePresetsV79,SCENE_PRESETS_V79} from './mech-image-diagnostics-v79.js';

export async function decodeCapturedPngV80(blob,{createBitmap=globalThis.createImageBitmap?.bind(globalThis),
 createCanvas=()=>globalThis.document?.createElement('canvas'),maxBytes=30000000,sampleWidth=320,sampleHeight=180}={}){
 if(!blob||blob.type!=='image/png'||!Number.isInteger(blob.size)||blob.size<2000||blob.size>maxBytes)
   throw Error('Only local PNG blobs between 2KB and 30MB can be reviewed');
 if(typeof createBitmap!=='function'||typeof createCanvas!=='function')
   throw Error('Browser PNG decoding unavailable; no synthetic image fallback');
 const bitmap=await createBitmap(blob);
 try{
  const {width,height}=bitmap||{};
  if(!Number.isInteger(width)||!Number.isInteger(height)||width<256||height<144||width>16384||height>16384)
    throw Error('Decoded PNG dimensions unsupported');
  const canvas=createCanvas();
  if(!canvas||typeof canvas.getContext!=='function')throw Error('No real-pixel inspection canvas');
  canvas.width=sampleWidth;canvas.height=sampleHeight;
  const ctx=canvas.getContext('2d',{willReadFrequently:true});
  if(!ctx?.drawImage||!ctx?.getImageData)throw Error('Cannot inspect decoded screenshot pixels');
  ctx.drawImage(bitmap,0,0,sampleWidth,sampleHeight);
  const data=ctx.getImageData(0,0,sampleWidth,sampleHeight).data;
  if(!data||data.length!==sampleWidth*sampleHeight*4)throw Error('Missing decoded pixel data');
  return {width:sampleWidth,height:sampleHeight,data,source:'v78-capture-blob-unverified-gpu-origin'};
 }finally{bitmap?.close?.()}
}

export async function reviewCapturedSnapshotsV80(files,{decode=decodeCapturedPngV80}={}){
 if(!Array.isArray(files)||files.length!==3)throw Error('Complete v7.8 three-PNG capture required');
 if(typeof decode!=='function')throw TypeError('Decoded real-PNG provider required');
 const src=new Map();
 for(const item of files){
  if(!SCENE_PRESETS_V79.includes(item?.preset)||src.has(item.preset))throw Error('Unknown or duplicate preset');
  if(!item.blob||item.blob.type!=='image/png'||!Number.isInteger(item.blob.size)||item.blob.size<2000||item.blob.size>30000000)
    throw Error('Invalid real PNG blob');
  src.set(item.preset,item.blob);
 }
 const frames={};
 for(const p of SCENE_PRESETS_V79){
  if(!src.has(p))throw Error('Required preset missing: '+p);
  frames[p]=await decode(src.get(p));
 }
 const result=auditThreePresetsV79(frames);
 return {...result,schema:'taipei-mecha-v80-ingame-image-review',version:'8.0',
  input:'v7.8 local user-triggered PNG capture; decoded pixels only',
  privacy:'No raw image, filename, GPS, camera transform, device identity or network upload',
  limitations:'Pixel inspection cannot prove WebGPU origin, camera parity, FPS, animation integrity or five-minute gameplay; manual real-device acceptance required.'};
}
export function describeCapturedReviewV80(result){
 if(!result||result.schema!=='taipei-mecha-v80-ingame-image-review')return '尚未有 v8.0 圖片驗收結果';
 const lines=[result.flags?.length?'⚠ 畫面有疑點，需人工複查':'✓ 自動像素檢查未發現疑點（不是實機通過）'];
 for(const p of SCENE_PRESETS_V79){
  const m=result.metrics?.[p];
  if(m)lines.push(`${p}：平均亮度 ${m.meanLuma}、暗部 ${m.blackPercent}%、高亮 ${m.whitePercent}%、色階 ${m.colorBins}`);
 }
 if(result.flags?.length)lines.push('請複查：'+result.flags.join('、'));
 lines.push('不驗證真實 WebGPU 來源、實際 GPU FPS、街廓碰撞或動畫穿模');
 return lines.join('\n');
}
