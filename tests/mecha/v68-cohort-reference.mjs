import assert from 'node:assert/strict';
import {createBattleCohortV68,normalizeBattleReportV68} from '../../examples/threejs/mech-cohort-reference-v68.js';
function sample(level='standard',result='victory',seconds=110){
 return {schema:'taipei-mecha-v67-battle-aggregates',version:'6.7',difficulty:level,status:'complete',missionOutcome:result,gameSeconds:seconds,
 counts:{playerShots:10,playerDamage:12,relayDamage:14,dodgeAttempts:4,routeReplans:1},
 waves:[{wave:1,combatSeconds:25},{wave:2,combatSeconds:32}]};
}
const c=createBattleCohortV68();
assert.equal(c.add(sample()).added,true);
assert.equal(c.add(sample()).reason,'duplicate');
assert.equal(c.add(sample('standard','defeat',125)).added,true);
assert.equal(c.add(sample('training','victory',90)).added,true);
assert.equal(c.add(sample('challenge','time-expired',135)).added,true);
assert.equal(c.add({...sample('standard','abandoned',55),status:'recording'}).added,true);
const s=c.analyze();
assert.equal(s.loaded,5);assert.equal(s.eligible,4);
assert.equal(s.groups[1].eligible,2);assert.equal(s.groups[1].wins,1);assert.equal(s.groups[1].rate,50);
assert.equal(s.groups[1].medianVictorySeconds,110);
assert.ok(s.groups[1].wilson95[0]<50 && s.groups[1].wilson95[1]>50);
assert.equal(s.groups[1].perWave[2].reached,0);
assert.throws(()=>normalizeBattleReportV68({...sample(),version:'6.8'}));
assert.throws(()=>normalizeBattleReportV68({...sample(),counts:{playerShots:-1}}));
assert.throws(()=>normalizeBattleReportV68({...sample(),waves:[{wave:1,combatSeconds:40},{wave:1,combatSeconds:30}]}));
assert.ok(!JSON.stringify(s).includes('userId'));
c.clear();assert.equal(c.count,0);
console.log('PASS v6.8 three difficulties, duplicate exclusion, schema, invalid/incomplete exclusion, Wilson, wave denominators');
