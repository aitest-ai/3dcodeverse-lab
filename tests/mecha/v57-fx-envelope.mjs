import assert from 'node:assert/strict';
import {beamIntensity,ringPulse,explosionEnvelope} from '../../examples/threejs/mech-fx-v57.js';
assert.equal(beamIntensity(1,0),0);
assert.equal(beamIntensity(-1,1),0);
assert.ok(beamIntensity(.8,1)>beamIntensity(.2,1),'core fades smoothly');
let last=0;
for(let i=0;i<=100;i++){
 const state=ringPulse(.08,1-i/100,1);
 assert.ok(state.position>=last-1e-10,'energy ring moves forward');
 assert.ok(state.alpha>=0 && state.alpha<=1);
 last=state.position;
 const intensity=beamIntensity(1-i/100,1,{charged:true});
 assert.ok(Number.isFinite(intensity) && intensity>=0 && intensity<=1);
 const explosion=explosionEnvelope(1-i/100,1);
 assert.ok(explosion.opacity>=0 && explosion.opacity<=1);
}
console.log('PASS v5.7 FX envelope: forward travelling rings, charged pulses, bounded/fading core and blast envelope');
