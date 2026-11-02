import assert from 'node:assert/strict';
import {makeSmokePixelsV76,smokeMaterialFrameV76,blastLightFrameV76,SMOKE_STYLE_V76} from '../../examples/threejs/mech-atmosphere-material-v76.js';
const first=makeSmokePixelsV76(64,0),second=makeSmokePixelsV76(64,1);
assert.equal(first.byteLength,16384);assert.equal(second.byteLength,16384);
assert.notDeepEqual(first,second,'two textures must not be identical');
assert.equal(first[3],0);
const center=first[(32*64+32)*4+3];assert.ok(center>0);
for(let i=0;i<350;i++){
 const v=smokeMaterialFrameV76(i/100,3.4,i%16);
 assert.ok(v.opacity>=0 && v.opacity<=SMOKE_STYLE_V76.maxOpacity);
 assert.ok(v.tint.every(n=>n>=0&&n<=1));
}
assert.equal(smokeMaterialFrameV76(3.4,3.4,3).opacity,0);
assert.ok(smokeMaterialFrameV76(2.8,3.4,2).radius>smokeMaterialFrameV76(.2,3.4,2).radius);
const early=blastLightFrameV76(.01,.34,{peak:3.3});
const late=blastLightFrameV76(.32,.34,{peak:3.3});
assert.ok(early.intensity>late.intensity);
assert.equal(blastLightFrameV76(.34,.34,{peak:3.3}).intensity,0);
assert.ok(early.rgb[0]>early.rgb[2]);
console.log('PASS v7.6 real source: two 64px textures, nonuniform alpha, capped sprite opacity, warm-to-cool transient lighting');
