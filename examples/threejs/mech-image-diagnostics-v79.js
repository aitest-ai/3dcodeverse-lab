/**
 * Taipei Mech v7.9 - independent, offline, browser/Node-compatible screenshot QA.
 * Pixel heuristics only. No WebGPU provenance, GPS, upload or frame-rate claim.
 */
export const SCENE_PRESETS_V79 = Object.freeze(['midday','golden','midnight']);
const asPercent=n=>Math.round(n*1000)/10, fixed=n=>Math.round(n*100)/100;
export function inspectRGBAFrameV79({width,height,data,source='unverified'}={}){
 if(!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1||width>16384||height>16384)throw new RangeError('Frame dimensions must be 1..16384');
 if(!data||typeof data.length!=='number'||data.length!==width*height*4)throw new TypeError('Full RGBA byte array required');
 const step=Math.max(1,Math.floor(Math.sqrt(width*height/9216)));
 let total=0,opaque=0,black=0,white=0,clipped=0,luma=0,lumaSquare=0,colorful=0;
 const bins=new Set();
 for(let y=0;y<height;y+=step)for(let x=0;x<width;x+=step){
  const i=(y*width+x)*4,r=data[i],g=data[i+1],b=data[i+2],a=data[i+3];
  if(![r,g,b,a].every(v=>Number.isInteger(v)&&v>=0&&v<=255))throw new TypeError('RGBA components must be bytes');
  total++;if(a<250)continue;
  opaque++;const v=(.2126*r+.7152*g+.0722*b)/255;luma+=v;lumaSquare+=v*v;
  if(v<.055)black++;if(v>.955)white++;if(v<.022||v>.978)clipped++;
  if(Math.max(r,g,b)-Math.min(r,g,b)>28)colorful++;
  bins.add(`${r>>5},${g>>5},${b>>5}`);
 }
 const o=Math.max(1,opaque),mean=luma/o,variance=Math.max(0,lumaSquare/o-mean*mean);
 const result={width,height,source,samples:total,opaquePercent:asPercent(opaque/total),meanLuma:fixed(mean),lumaStd:fixed(Math.sqrt(variance)),
 blackPercent:asPercent(black/o),whitePercent:asPercent(white/o),clippedPercent:asPercent(clipped/o),colorBins:bins.size,colorfulPercent:asPercent(colorful/o),flags:[]};
 if(result.opaquePercent<98)result.flags.push('transparent_or_missing_pixels');
 if(result.blackPercent>=98)result.flags.push('near_black');
 if(result.whitePercent>=98)result.flags.push('near_white');
 if(result.colorBins<6||result.lumaStd<.025)result.flags.push('low_detail');
 if(result.clippedPercent>=94)result.flags.push('severe_clipping');
 return result;
}
export function createSceneSignatureV79({width,height,data}={},gridWidth=16,gridHeight=9){
 if(!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1||!data||data.length!==width*height*4)throw new TypeError('Frame RGBA dimensions mismatch');
 const values=[];
 for(let gy=0;gy<gridHeight;gy++)for(let gx=0;gx<gridWidth;gx++){
  const x=Math.min(width-1,Math.floor((gx+.5)*width/gridWidth)),y=Math.min(height-1,Math.floor((gy+.5)*height/gridHeight));
  const i=(y*width+x)*4;
  values.push(data[i+3]<250?-1:(.2126*data[i]+.7152*data[i+1]+.0722*data[i+2])/255);
 }
 return values;
}
export function compareSceneSignaturesV79(a,b){
 if(!Array.isArray(a)||!Array.isArray(b)||a.length!==b.length||a.length<9)throw new TypeError('Matching signatures required');
 let count=0,delta=0;
 for(let i=0;i<a.length;i++){if(!Number.isFinite(a[i])||!Number.isFinite(b[i])||a[i]<0||b[i]<0)continue;count++;delta+=Math.abs(a[i]-b[i]);}
 return {comparedTiles:count,meanLumaDifference:count?fixed(delta/count):null};
}
/** Red flags invite HUMAN review; green result never authenticates the screenshot. */
export function auditThreePresetsV79(frames){
 if(!frames||SCENE_PRESETS_V79.some(p=>!frames[p]))throw new TypeError('Three ordered preset frames required');
 const dims=new Set(SCENE_PRESETS_V79.map(p=>`${frames[p].width}x${frames[p].height}`));
 const metrics=Object.fromEntries(SCENE_PRESETS_V79.map(p=>[p,inspectRGBAFrameV79(frames[p])]));
 const flags=[];if(dims.size!==1)flags.push('dimension_mismatch');
 for(const p of SCENE_PRESETS_V79)for(const flag of metrics[p].flags)flags.push(`${p}:${flag}`);
 const comparisons={};
 if(dims.size===1)for(const [a,b] of [['midday','golden'],['golden','midnight'],['midday','midnight']]){
  const diff=compareSceneSignaturesV79(createSceneSignatureV79(frames[a]),createSceneSignatureV79(frames[b]));
  comparisons[`${a}_${b}`]=diff;
  if(diff.comparedTiles>=100&&diff.meanLumaDifference!==null&&diff.meanLumaDifference<.015)flags.push(`${a}_${b}:visually_similar_review`);
 }
 return {schema:'taipei-mecha-v79-image-qa',version:'7.9',analysis:'offline-decoded-rgba-only',presets:[...SCENE_PRESETS_V79],
 metrics,comparisons,flags,status:flags.length?'manual_review_needed':'automatic_checks_no_flags',
 limitations:'Cannot prove WebGPU origin, common camera, performance, correct city geometry, or human-visible animation quality; human review always required.'};
}
