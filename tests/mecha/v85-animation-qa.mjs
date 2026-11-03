import assert from 'node:assert/strict';
import {validateV85Report,createV85ReviewExport,V85_CLIPS} from '../../examples/threejs/mech-animation-qa-v85.js';
const raw={schema:'taipei-mecha-v85-fullframe-muzzle-qa',version:'8.5',
 source_blend_sha256:'a'.repeat(64),candidate_glb_sha256:'b'.repeat(64),
 total_samples:288,passed:true,samples:V85_CLIPS.flatMap(clip=>Array.from({length:48},(_,i)=>({clip,frame:i+1,gap_m:.009,angle_deg:1.3,pass:true})))};
assert.equal(validateV85Report(raw).accepted,true);
assert.equal(validateV85Report(raw).summary.passed,true);
const out=createV85ReviewExport(raw,{humanReviewCompleted:true,notes:'synthetic test'});
assert.equal(out.animationQA,'passed_geometry_only');
assert.ok(!('points' in out.clips.Fire));
const missing=structuredClone(raw);missing.samples.pop();assert.equal(validateV85Report(missing).accepted,false);
const duplicate=structuredClone(raw);duplicate.samples[0]={...duplicate.samples[1]};assert.equal(validateV85Report(duplicate).accepted,false);
const bad=structuredClone(raw);bad.samples[0].gap_m=.03;bad.passed=false;
assert.equal(validateV85Report(bad).summary.passed,false);
const falseClaim=structuredClone(raw);falseClaim.passed=false;assert.equal(validateV85Report(falseClaim).accepted,false);
console.log('PASS v8.5: 288-frame 6-clip contract; invalid, incomplete and misleading reports rejected');
