import assert from 'node:assert/strict';
import {wreckWallPoseV72,shardEnvironmentStepV72} from '../../examples/threejs/mech-wreck-environment-v72.js';
const base={elapsed:2.25,duration:2.25,side:1,x:0,z:0,baseY:0,scale:1,groundAt:()=>0};
let wallChecks=0;
const safe=wreckWallPoseV72({...base,wallAt:()=>false});
const obstacle=wreckWallPoseV72({...base,wallAt:(x,z,y)=>{wallChecks++;return x<-1.45&&y<4;}});
assert.equal(obstacle.wallBlocked,true);
assert.ok(obstacle.roll<safe.roll && obstacle.wallQueries<=15 && wallChecks<=15);
assert.ok(obstacle.y>=0);
const unknown=wreckWallPoseV72({...base,groundAt:()=>NaN});
assert.equal(unknown.groundVerified,false);
const shard={obj:{position:{x:0,y:.1,z:0}},floor:0,vx:-4,vy:-.5,vz:0,
 life:2.4,parked:false,parkAge:0,settledTime:0,groundVerifiedEver:false};
const impact=shardEnvironmentStepV72(shard,.05,{groundAt:()=>0,wallAt:(x)=>x<-.05,
 allowGround:true,allowWall:true});
assert.equal(impact.hitWall,true);
assert.equal(shard.obj.position.x,0);
assert.ok(shard.vx>0);
const previous=shard.obj.position.x;
shardEnvironmentStepV72(shard,.05,{allowWall:false,allowGround:false});
assert.equal(shard.obj.position.x,previous);
function rest(g){const x={obj:{position:{x:0,y:.022,z:0}},floor:0,vx:0,vy:0,vz:0,
 life:2.4,parked:false,parkAge:0,settledTime:0,groundVerifiedEver:false};
 for(let i=0;i<90&&!x.parked;i++)shardEnvironmentStepV72(x,.05,{groundAt:g,wallAt:()=>false,allowWall:true,allowGround:true});
 return x;}
const verified=rest(()=>0),missing=rest(()=>NaN);
assert.equal(verified.parked,true);
assert.equal(missing.parked,false);
console.log('PASS v7.2 original OSM collision proxy, horizontal budget fallback, verified ground-only resting chips');
