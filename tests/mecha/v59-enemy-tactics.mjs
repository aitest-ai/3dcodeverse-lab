import assert from 'node:assert/strict';
import {createEnemyBrainV59,ENEMY_ROLES_V59} from '../../examples/threejs/mech-enemy-ai-v59.js';
assert.deepEqual(Object.keys(ENEMY_ROLES_V59),['assault','ranger','heavy']);
for(const role of Object.keys(ENEMY_ROLES_V59)){
 const ai=createEnemyBrainV59({role,id:1});
 assert.ok(ai.profile.hp>0&&ai.profile.range>0&&ai.profile.windup>0);
 const ahead=ai.update({dt:.016,position:{x:0,z:0,y:0},target:{x:80,z:0,y:0},
   visible:false,canOccupy:()=>true,sampleGround:()=>0});
 assert.ok(ahead.position.x>0);
 ai.reset(); assert.equal(ai.snapshot().shots,0);
}
const retreat=createEnemyBrainV59({role:'ranger'}).update({dt:.016,
 position:{x:0,z:0,y:0},target:{x:8,z:0,y:0},visible:false,
 canOccupy:()=>true,sampleGround:()=>0});
assert.ok(retreat.position.x<0,'ranger retreats from melee');
const wall=createEnemyBrainV59({role:'assault'});
const blocked=wall.update({dt:10,position:{x:0,z:0,y:0},target:{x:80,z:0,y:0},
 visible:false,canOccupy:()=>false,sampleGround:()=>0});
assert.equal(blocked.position.x,0);
assert.ok(blocked.blocked);
const noGround=createEnemyBrainV59({role:'heavy'}).update({dt:.016,
 position:{x:0,z:0,y:0},target:{x:80,z:0,y:0},visible:false,
 canOccupy:()=>true,sampleGround:()=>5});
assert.equal(noGround.position.x,0);
for(const role of Object.keys(ENEMY_ROLES_V59)){
 const ai=createEnemyBrainV59({role,id:2});
 let pos={x:0,z:0,y:0},locked=false,fire=null;
 for(let i=0;i<650;i++){
  const target=i<70?{x:25,z:0,y:0}:{x:45,z:12,y:0};
  const s=ai.update({dt:.016,position:pos,target,visible:true,
    canOccupy:()=>true,sampleGround:()=>0});
  pos=s.position;
  if(s.mode==='telegraph')locked=true;
  if(s.fire){fire=s;break;}
 }
 assert.ok(locked&&fire,role+' must warn before firing');
 assert.equal(fire.fireTarget.x,25);
 assert.equal(fire.fireTarget.z,0);
 assert.equal(ai.snapshot().shots,1);
}
function trial(hz){
 const ai=createEnemyBrainV59({role:'assault'});let pos={x:0,z:0,y:0},shots=0;
 for(let i=0;i<9*hz;i++){
  const s=ai.update({dt:1/hz,position:pos,target:{x:13,z:0,y:0},
    visible:true,canOccupy:()=>true,sampleGround:()=>0});
  pos=s.position;if(s.fire)shots++;
 }
 return shots;
}
const shots=[30,60,120].map(trial);
assert.ok(shots[0]>=2&&shots[0]<=6);
assert.ok(Math.abs(shots[0]-shots[1])<=1);
assert.ok(Math.abs(shots[1]-shots[2])<=1);
assert.throws(()=>createEnemyBrainV59({role:'fake'}));
console.log('PASS v5.9 AI: distinct 3 roles, LOS input, obstacle & terrain gates, locked warning shot, cooldown & 30/60/120Hz parity');
