import assert from 'node:assert/strict';
import {createMechMotion} from '../../examples/threejs/mech-motion-v52.js';
import {createMechGroundSampler} from '../../examples/threejs/mech-ground-sampler-v52.js';

const m=createMechMotion();
let p={x:0,z:0};
m.update({dt:1/60,position:p,heading:0});
for(let i=0;i<24;i++){p={x:0,z:p.z+.05};m.update({dt:1/60,position:p,heading:0});}
assert.ok(m.snapshot().speed>2);
let h=0;
for(let i=0;i<18;i++){h+=.025;p={x:p.x+.01,z:p.z+.05};m.update({dt:1/60,position:p,heading:h});}
assert.ok(m.snapshot().roll<-.01);
let peak=0;
for(let i=0;i<20;i++){const x=m.update({dt:1/60,position:p,heading:h});peak=Math.max(peak,x.braking);}
assert.ok(peak>.08);
p={x:100,z:100};assert.equal(m.update({dt:1/60,position:p,heading:2}).roll,0);

class V {constructor(x=0,y=0,z=0){this.set(x,y,z)}
set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
copy(v){return this.set(v.x,v.y,v.z)} normalize(){return this} applyMatrix3(){return this}}
class Mat {getNormalMatrix(){return this}}
class Ray{static result=[];set(o,d){}intersectObjects(meshes){assert.equal(meshes.length,1);return Ray.result}}
const road={isMesh:true,name:'City_Road',userData:{},matrixWorld:{}},
      building={isMesh:true,name:'Road_Building_Wall',userData:{},matrixWorld:{}};
const terrain=createMechGroundSampler({
 THREE:{Vector3:V,Matrix3:Mat,Raycaster:Ray},
 scene:{traverse(cb){cb(road);cb(building);}},getReferenceHeight:()=>0});
assert.equal(terrain.snapshot().meshCount,1);
Ray.result=[{point:{y:.2},face:{normal:new V(0,1,0)},object:road}];
assert.equal(terrain.sample(1,2),.2);
Ray.result=[{point:{y:10},face:{normal:new V(0,1,0)},object:road}];
assert.ok(Number.isNaN(terrain.sample(1,2)));
Ray.result=[{point:{y:.2},face:{normal:new V(0,.12,0)},object:road}];
assert.ok(Number.isNaN(terrain.sample(1,2)));
terrain.setEnabled(false);assert.ok(Number.isNaN(terrain.sample(1,2)));
terrain.dispose();
console.log('PASS v5.2 runtime: acceleration, lean, braking, teleport and safe terrain height fallback');
