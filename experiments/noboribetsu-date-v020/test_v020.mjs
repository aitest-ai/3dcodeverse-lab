import assert from 'node:assert/strict';
import fs from 'node:fs';
import {evaluatePorchGuide} from './dist/porch-guidance.js';
import {CollisionWorld,collisionForStage,nearestRoute,routeAt} from './dist/navigation.js';
const D='./dist/',read=n=>JSON.parse(fs.readFileSync(D+n,'utf8'));
const scene=read('scene_view.json'),patch=read('v019_porch_guide.json'),route=scene.route;
const at=s=>routeAt(route,s);
const state=(s,stage='B',enabled=true,position=at(s))=>evaluatePorchGuide(route,patch.samples,position,stage,enabled,patch.lateral_warning_offset_m);
assert.equal(route.length,472);
assert.equal(patch.samples.length,13);
assert.equal(state(40).nearby,false);
assert.deepEqual(state(40).visibleIndices,[]);
assert.equal(state(89.5).active,true);
assert.ok(state(89.5).visibleIndices.length>0 && state(89.5).visibleIndices.length<=13);
assert.deepEqual(state(89.5,'A').visibleIndices,[]);
assert.deepEqual(state(89.5,'B',false).visibleIndices,[]);
assert.equal(state(110).active,false);
assert.equal(state(123).nearby,false);
assert.equal(state(85).progress,0);
assert.equal(state(103).progress,1);
const p=at(90),a=at(89.5),b=at(90.5),t={x:b.x-a.x,z:b.z-a.z},len=Math.hypot(t.x,t.z),left={x:-t.z/len,z:t.x/len};
const offset=n=>({x:p.x+left.x*n,z:p.z+left.z*n});
assert.equal(state(90,'B',true,offset(-.6)).warning,true);
assert.equal(state(90,'B',true,offset(.6)).warning,false);
assert.equal(state(90,'B',true,{x:NaN,z:p.z}).active,false);
const c=read('collision.json');
for(const n of ['extension_collision.json','v005_collision.json','v006_collision.json']){const x=read(n);c.walkable.push(...x.walkable);c.obstacles.push(...x.obstacles)}
const world=new CollisionWorld(collisionForStage(c,'B'),8);
for(const pt of patch.samples){
 const g=world.ground(pt.x,pt.z,pt.y,.45);
 const q=g&&world.check(pt.x,pt.z,g.y,{radius:.26,maxStep:.18,stepFrom:g.y,maxGroundError:.45});
 assert.ok(q?.ok,'V019 original collision point invalid at s='+pt.s_m);
 assert.ok(Math.sqrt(nearestRoute(route,pt.x,pt.z).d2)<.015);
}
console.log('PASS: 13 guide points, V019 original collision, A/B gating, proximity, progress, left warning');
