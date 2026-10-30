import assert from 'node:assert/strict';
import {createMechDodgeV55,createFlatTestCollision} from '../../examples/threejs/mech-dodge-v55.js';
const close=(a,b,eps=.02)=>assert.ok(Math.abs(a-b)<eps,a+' not near '+b);
const floor=createFlatTestCollision();
function simulate(fps,world=floor,start={x:0,z:0},side=1){
 const dodge=createMechDodgeV55();let position={...start};
 assert.equal(dodge.begin(side),true);
 for(let i=0;i<Math.ceil(fps*.4);i++){
  const step=dodge.update(1/fps,{position,right:{x:1,z:0},resolveMovement:world});
  position=step.position;
 }
 return {position,st:dodge.snapshot()};
}
close(simulate(30).position.x,3.2);close(simulate(60).position.x,3.2);close(simulate(120).position.x,3.2);
close(simulate(60,floor,{x:0,z:0},-1).position.x,-3.2);
const obstacle=createFlatTestCollision({obstacles:[{minX:1.5,maxX:3,minZ:-2,maxZ:2}]});
const hit=simulate(60,obstacle);assert.ok(hit.position.x<.8 && hit.position.x>.5,'swept collision must stop before building');
const edge=createFlatTestCollision({bounds:{minX:-4,maxX:2,maxZ:-4,maxZ:4}});
close(simulate(60,edge).position.x,1.28);
const dodge=createMechDodgeV55({staminaRegen:0,cooldown:0});assert.ok(dodge.begin());
assert.equal(dodge.begin(),false,'no mid-dodge spam');
let pos={x:0,z:0};for(let i=0;i<30;i++)pos=dodge.update(.016,{position:pos,right:{x:1,z:0},resolveMovement:floor}).position;
assert.ok(dodge.begin());for(let i=0;i<30;i++)pos=dodge.update(.016,{position:pos,right:{x:1,z:0},resolveMovement:floor}).position;
assert.equal(dodge.begin(),false,'stamina cap works');
const malicious=createMechDodgeV55();assert.ok(malicious.begin());
const block=malicious.update(.016,{position:{x:0,z:0},right:{x:1,z:0},resolveMovement:()=>({x:999,z:999})});
assert.equal(block.position.x,0);assert.ok(block.blocked);assert.match(block.error,/unsafe/);
const noCollision=createMechDodgeV55();noCollision.begin();
const no=noCollision.update(.016,{position:{x:0,z:0},right:{x:1,z:0}});
assert.equal(no.position.x,0);assert.ok(no.blocked,'missing collision authority must not move');
assert.equal(noCollision.snapshot().invulnerable,false,'dodge does not silently give invulnerability');
const limited=createMechDodgeV55();limited.begin();const limitedStep=limited.update(100,{position:{x:0,z:0},right:{x:1,z:0},resolveMovement:floor});
assert.ok(limitedStep.position.x<1,'large frame stall must not teleport');
const cd=createMechDodgeV55();cd.begin();for(let i=0;i<24;i++)cd.update(.016,{position:{x:0,z:0},right:{x:1,z:0},resolveMovement:floor});
assert.equal(cd.begin(),false,'cooldown enforced');for(let i=0;i<30;i++)cd.update(.016,{position:{x:0,z:0},right:{x:1,z:0},resolveMovement:floor});
assert.equal(cd.begin(),true,'cooldown expires');
cd.dispose();assert.equal(cd.begin(),false);
console.log('PASS v5.5: real displacement (30/60/120 FPS), swept obstruction, bounds, stamina, cooldown, safe resolver, no i-frames, stall safety');
