import assert from 'node:assert/strict';
import {createPostRenderCaptureReferenceV78} from '../../examples/threejs/mech-real-capture-reference-v78.js';
let current='golden',seen=[];
const x=createPostRenderCaptureReferenceV78({getPreset:()=>current,setPreset:p=>{current=p;return true;},
 readImage:async preset=>{seen.push(preset);return {type:'image/png',size:3000,valid:true}},holdFrames:2});
assert.equal(x.start(),true);
assert.equal(x.start(),false);
for(let i=0;i<3;i++){
 x.afterRealRender();x.afterRealRender();
 for(let j=0;j<12;j++)await Promise.resolve();
}
assert.deepEqual(seen,['midday','golden','midnight']);
assert.equal(x.snapshot().phase,'complete');assert.equal(current,'golden');
const invalid=createPostRenderCaptureReferenceV78({getPreset:()=>current,setPreset:p=>{current=p;return true;},
 readImage:async()=>({type:'image/png',size:900,valid:false}),holdFrames:2});
invalid.start();invalid.afterRealRender();invalid.afterRealRender();
for(let j=0;j<12;j++)await Promise.resolve();
assert.equal(invalid.snapshot().phase,'error');
assert.equal(invalid.snapshot().photos.length,0);
assert.equal(current,'golden');
console.log('PASS v7.8: real-render-only 3 city presets, PNG validity, restore time and failure rejection');