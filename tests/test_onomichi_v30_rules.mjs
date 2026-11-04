import test from 'node:test';
import assert from 'node:assert/strict';
import {V30_ASSETS,V30_MARKERS,V30_LIMITATIONS,ensureOriginalSha,digestSha256,
 validateGlbHeader,finiteOffset,validateMarkerConfig,nearestStats} from '../apps/onomichi-v30-3d-audit/rules.mjs';
test('accepts only source SHA locks',()=>{
 assert.equal(ensureOriginalSha({...V30_ASSETS}),true);
 assert.throws(()=>ensureOriginalSha({actor:'a',bike:V30_ASSETS.bike}),/原版載入/);
});
test('WebCrypto SHA is deterministic',async()=>{
 const buffer=new TextEncoder().encode('abc').buffer;
 assert.equal(await digestSha256(buffer),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
});
test('GLB container header rejects ZIP and bogus lengths',()=>{
 const good=new ArrayBuffer(24),v=new DataView(good);
 v.setUint32(0,0x46546c67,true);v.setUint32(4,2,true);v.setUint32(8,24,true);
 v.setUint32(12,4,true);v.setUint32(16,0x4e4f534a,true);
 assert.equal(validateGlbHeader(good),true);
 v.setUint32(8,20,true);
 assert.throws(()=>validateGlbHeader(good),/GLB/);
});
test('requires all 8 exact calibrated markers',()=>{
 const data={schema:'setouchi.v30.marker.config.v1',asset_sha256:{...V30_ASSETS},
 markers:Object.fromEntries(V30_MARKERS.map(m=>[m.id,{path:[1,3],offset:[.1,.2,.3]}]))};
 assert.equal(validateMarkerConfig(data),true);
 delete data.markers.bike_grip_right;
 assert.throws(()=>validateMarkerConfig(data),/標記/);
});
test('rejects negative, infinite and out-of-range offsets',()=>{
 assert.equal(finiteOffset([0,0,0]),true);
 assert.equal(finiteOffset([0,0,Infinity]),false);
 assert.equal(finiteOffset([0,0,4]),false);
 assert.equal(finiteOffset([0,0,-.02]),true);
});
test('computes sample quantiles, no automatic pose or road approvals',()=>{
 assert.equal(nearestStats([1,2,3,4,5]).median,3);
 assert.equal(nearestStats([1,2,3,4,5]).p95,4.8);
 assert.equal(nearestStats([]),null);
 assert.equal(V30_LIMITATIONS.originalGameplayTested,false);
 assert.equal(V30_LIMITATIONS.legalRoadRightsVerified,false);
});
