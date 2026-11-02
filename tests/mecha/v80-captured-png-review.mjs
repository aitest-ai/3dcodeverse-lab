import assert from 'node:assert/strict';
import {decodeCapturedPngV80,reviewCapturedSnapshotsV80,describeCapturedReviewV80} from '../../examples/threejs/mech-capture-review-v80.js';
const width=256,height=144;
const make=(idx)=>{const data=new Uint8ClampedArray(width*height*4);
 for(let i=0;i<width*height;i++){const x=i%width,y=Math.floor(i/width),p=i*4;
  data[p]=(x+idx*51)%256;data[p+1]=(y*2+idx*13)%256;data[p+2]=(x+y+idx*67)%256;data[p+3]=255;}
 return {width,height,data,source:'synthetic-test-only'};};
const files=['midday','golden','midnight'].map(preset=>({preset,blob:new Blob([new Uint8Array(3000)],{type:'image/png'})}));
let count=0;
const result=await reviewCapturedSnapshotsV80(files,{decode:async()=>make(count++)});
assert.equal(result.schema,'taipei-mecha-v80-ingame-image-review');
assert.deepEqual(result.presets,['midday','golden','midnight']);
assert.equal(Object.keys(result.metrics).length,3);
assert.ok(describeCapturedReviewV80(result).includes('WebGPU'));
assert.ok(!JSON.stringify(result).includes('sameCamera'));
await assert.rejects(()=>reviewCapturedSnapshotsV80(files.slice(0,2)),/Complete/);
await assert.rejects(()=>reviewCapturedSnapshotsV80([files[0],files[0],files[2]]),/duplicate/);
await assert.rejects(()=>reviewCapturedSnapshotsV80(files.map((x,i)=>i===1?{...x,blob:null}:x)),/Invalid/);
let closed=false;
const decoded=await decodeCapturedPngV80(files[0].blob,{
 createBitmap:async()=>({width,height,close(){closed=true}}),
 createCanvas:()=>({getContext:()=>({drawImage(){},getImageData:()=>({data:new Uint8ClampedArray(320*180*4)})})})
});
assert.equal(decoded.width,320);assert.ok(closed);
await assert.rejects(()=>decodeCapturedPngV80(new Blob([new Uint8Array(10)],{type:'image/png'})),/Only local/);
console.log('PASS v8.0: 3 real PNG-input interfaces, privacy, invalid captures, browser decode, no fake image generation');
