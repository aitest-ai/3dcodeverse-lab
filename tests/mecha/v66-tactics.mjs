import assert from 'node:assert/strict';
import {createCombatPacingV66} from '../../examples/threejs/mech-combat-pacing-v66.js';
import {createEnemyRecoveryV66} from '../../examples/threejs/mech-unstuck-v66.js';
import {createEnemyBrainV59} from '../../examples/threejs/mech-enemy-ai-v59.js';
import {createTaipeiDefenseMissionV60} from '../../examples/threejs/mech-mission-v60.js';
const pacing=createCombatPacingV66();
assert.equal(pacing.permit({activeWarnings:10}),true,'unchanged free combat');
pacing.update(.016,{missionPhase:'combat',waveNumber:1});
assert.equal(pacing.permit({activeWarnings:0}),false);
for(let i=0;i<14;i++)pacing.update(.05,{missionPhase:'combat',waveNumber:1});
assert.equal(pacing.permit({activeWarnings:0}),true);
pacing.started();assert.equal(pacing.permit({activeWarnings:1}),false);
assert.equal(pacing.permit({currentMode:'telegraph',activeWarnings:9}),true);
pacing.update(.05,{missionPhase:'combat',waveNumber:2});
for(let i=0;i<24;i++)pacing.update(.05,{missionPhase:'combat',waveNumber:2});
assert.equal(pacing.permit({activeWarnings:0}),true);pacing.started();
assert.equal(pacing.permit({activeWarnings:1}),false);
for(let i=0;i<11;i++)pacing.update(.05,{missionPhase:'combat',waveNumber:2});
assert.equal(pacing.permit({activeWarnings:1}),true);
assert.equal(pacing.permit({activeWarnings:2}),false);
pacing.update(.05,{missionPhase:'combat',waveNumber:3});
for(let i=0;i<31;i++)pacing.update(.05,{missionPhase:'combat',waveNumber:3});
pacing.update(.016,{missionPhase:'combat',waveNumber:3,heavyOverdrive:true});
assert.equal(pacing.permit({role:'heavy',activeWarnings:0}),false);
assert.equal(pacing.permit({role:'assault',activeWarnings:0}),true);
const recovery=createEnemyRecoveryV66();
let replans=0,exhausted=false;
for(let i=0;i<500;i++){
 const state=recovery.update(.016,{before:{x:0,z:0},after:{x:0,z:0},
   blocked:true,moving:false,mode:'search',goalDistance:40});
 if(state.requestReplan)replans++;
 if(state.exhausted){exhausted=true;break;}
}
assert.equal(replans,3);assert.ok(exhausted);
assert.equal(recovery.snapshot().forceNavigation,false);
const a=createEnemyBrainV59({role:'assault',id:3}).update({dt:.016,
 position:{x:0,y:0,z:0},target:{x:30,z:0,y:0},visible:true,
 navigationTarget:{x:0,z:-7},preferNavigation:true,allowWindup:false,
 canOccupy:()=>true,sampleGround:()=>0});
assert.equal(a.mode,'navigate');assert.ok(a.position.z<0);
const m=createTaipeiDefenseMissionV60({intermissions:[3.4,4.4]});
assert.equal(m.start({x:0,y:0,z:0}).ok,true);m.deploy([1,2]);m.destroyEnemy(1);m.destroyEnemy(2);
assert.equal(m.snapshot().intermissionRemaining,3.4);
console.log('PASS v6.6 actual portable cores: bounded attempts, OSM steer, fair wave admission and preparation');
