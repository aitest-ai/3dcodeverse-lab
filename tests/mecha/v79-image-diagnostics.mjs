import assert from 'node:assert/strict';
import {inspectRGBAFrameV79,createSceneSignatureV79,compareSceneSignaturesV79,auditThreePresetsV79} from '../../examples/threejs/mech-image-diagnostics-v79.js';
const W=256,H=144;
function frame(fn,source='synthetic-test-not-real-city'){
 const data=new Uint8ClampedArray(W*H*4);
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){const [r,g,b,a=255]=fn(x,y),i=(y*W+x)*4;data[i]=r;data[i+1]=g;data[i+2]=b;data[i+3]=a;}
 return {width:W,height:H,data,source};
}
const morning=frame((x,y)=>[35+x%180,90+y%120,115+(x*y)%120]);
const evening=frame((x,y)=>[110+x%140,50+y%100,35+(x*y)%90]);
const night=frame((x,y)=>[15+x%80,20+y%100,50+(x*y)%120]);
const all=auditThreePresetsV79({midday:morning,golden:evening,midnight:night});
assert.deepEqual(all.presets,['midday','golden','midnight']);
assert.equal(all.schema,'taipei-mecha-v79-image-qa');
assert.equal(all.flags.length,0);
assert.equal(all.status,'automatic_checks_no_flags');
assert.ok(all.comparisons.midday_midnight.meanLumaDifference>0.015);
const black=frame(()=>[0,0,0]);
assert.ok(inspectRGBAFrameV79(black).flags.includes('near_black'));
assert.ok(auditThreePresetsV79({midday:black,golden:evening,midnight:night}).flags.includes('midday:near_black'));
assert.ok(inspectRGBAFrameV79(frame(()=>[10,20,30,0])).flags.includes('transparent_or_missing_pixels'));
assert.equal(compareSceneSignaturesV79(createSceneSignatureV79(morning),createSceneSignatureV79(morning)).meanLumaDifference,0);
assert.ok(auditThreePresetsV79({midday:morning,golden:morning,midnight:morning}).flags.includes('midday_golden:visually_similar_review'));
const otherDim={width:128,height:144,data:new Uint8ClampedArray(128*144*4),source:'synthetic'};
assert.ok(auditThreePresetsV79({midday:morning,golden:otherDim,midnight:night}).flags.includes('dimension_mismatch'));
assert.throws(()=>inspectRGBAFrameV79({width:100,height:100,data:new Uint8Array(5)}),/RGBA/);
assert.throws(()=>auditThreePresetsV79({midday:morning}),/Three/);
console.log('PASS v7.9 offline RGBA diagnostics: black, transparency, dimensions, similar scenes and real-origin nonclaim');
