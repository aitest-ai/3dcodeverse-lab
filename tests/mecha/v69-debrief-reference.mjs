import assert from 'node:assert/strict';
import {createMechDebriefReferenceV69} from '../../examples/threejs/mech-battle-debrief-reference-v69.js';
const m=createMechDebriefReferenceV69();
m.begin();
m.record({role:'assault',type:'player_hit',damage:6,point:{x:123456}});
m.record({role:'ranger',type:'relay_hit',damage:9,z:123456});
m.record({role:'heavy',type:'player_hit',damage:20});
m.record({role:'heavy',type:'relay_hit',damage:22});
const base={schema:'taipei-mecha-v67-battle-aggregates',status:'complete',
  missionOutcome:'defeat',difficulty:'standard',counts:{dodgeAttempts:5,dodgeDuringWarnings:3},
  waves:[{wave:1,combatSeconds:20,relayDamage:0},{wave:2,combatSeconds:35,relayDamage:9},
  {wave:3,combatSeconds:42,relayDamage:22}]};
const out=m.finish(base);
assert.equal(out.mostDamagingRole,'heavy');
assert.equal(out.mostDamagingWave,3);
assert.equal(out.dodgeAttempts,5);
assert.equal(out.dodgeDuringWarnings,3);
assert.ok(!JSON.stringify(out).includes('123456'));
assert.equal(m.record({role:'heavy',type:'player_hit',damage:999}),false);
assert.equal(m.finish(base),null);
m.reset();assert.equal(m.snapshot(),null);
console.log('PASS v6.9: role attribution on true HP loss, wave relay exposure, no location fields, terminal immutability and reset');
