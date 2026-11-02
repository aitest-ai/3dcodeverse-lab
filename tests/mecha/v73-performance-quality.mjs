import assert from 'node:assert/strict';
import {createMechPerformanceV73} from '../../examples/threejs/mech-performance-v73.js';
import {qualityProfileV73,nextQualityV73} from '../../examples/threejs/mech-quality-v73.js';
const q=createMechPerformanceV73();
for(let i=0;i<120;i++){
 q.observe({nowMs:1000+16.67*i,addonCpuMs:3+(i%8),gameDtMs:16.67,
 renderer:i%20===0?{calls:512,triangles:1200000,geometries:300,textures:70}:null,
 effects:{shards:i%75,activeWrecks:i%5,parked:5,rings:1,peakWallQueries:44,wallContacts:4},quality:'full'});
}
const s=q.snapshot();
assert.equal(s.frames,120);
assert.ok(s.updateCallGapMs.p95>16&&s.updateCallGapMs.p95<17);
assert.equal(s.rendererLastReported.calls,512);
assert.equal(s.peaks.wallQueries,44);
assert.equal(s.quality,'full');
assert.equal(qualityProfileV73('full').shardFactor,1);
assert.ok(qualityProfileV73('balanced').shardFactor<1);
assert.ok(qualityProfileV73('light').shardFactor<qualityProfileV73('balanced').shardFactor);
assert.equal(nextQualityV73('light'),'full');
q.observe({nowMs:999999,addonCpuMs:1});
assert.equal(q.snapshot().excludedTabOrLongStalls,1);
const serialized=JSON.stringify(s);
assert.ok(!serialized.includes('longitude')&&!serialized.includes('deviceId'));
assert.ok(s.limitations.some(x=>x.includes('GPU')));
q.reset();assert.equal(q.snapshot().frames,0);
console.log('PASS v7.3 performance: real addon-only CPU and call cadence, no GPU FPS fabrication, bounded visual-only controls and privacy');
