import assert from 'node:assert/strict';
import {createEnemyActionDirectorV63} from '../../examples/threejs/mech-enemy-action-v63.js';
import {createEnemyVisualLoaderV63} from '../../examples/threejs/mech-enemy-glb-v63.js';
const aMap=new Map(['Idle','Run','Fire','Hit','Dodge','Punch'].map(name=>[name,{
  name,plays:0,reset(){return this},play(){this.plays++;return this},
  stop(){return this},crossFadeFrom(){return this},setLoop(a,n){assert.equal(a,'once');assert.equal(n,1);return this}
}]));
const director=createEnemyActionDirectorV63(aMap,{loopOnce:'once'});
for(let i=0;i<20;i++)director.update(.016,{moving:true,health:100});
assert.equal(director.snapshot().current,'Run');
assert.equal(aMap.get('Fire').plays,0,'telegraph may never trigger actual Fire clip');
director.update(.016,{shot:true,health:100});
assert.equal(director.snapshot().current,'Fire');
for(let i=0;i<46;i++)director.update(.016,{moving:false,health:100});
assert.equal(director.snapshot().current,'Idle');
assert.equal(director.snapshot().shots,1);
director.update(.016,{health:70});
assert.equal(director.snapshot().current,'Hit');
for(let i=0;i<46;i++)director.update(.016,{moving:true,health:70});
assert.equal(director.snapshot().current,'Run');
const names=['Mecha_Idle','Mecha_Run','Mecha_Fire','Mecha_Punch','Mecha_Dodge','Mecha_Hit'];
let loads=0,uncached=0;
const clips=names.map(name=>({name,tracks:[{name:'root.position',values:new Float32Array([0,.178,0,.14,.25,0])},{name:'spine.quaternion'}],
 clone(){return {name,tracks:this.tracks.map(t=>({...t,values:t.values?.slice()}))}}}));
const THREE={LoopOnce:'once',AnimationMixer:class {
  clipAction(clip){return {clip,reset(){return this},play(){return this},
    stop(){return this},crossFadeFrom(){return this},setLoop(){return this}}}
  update(dt){assert.ok(dt>=0&&dt<=.05);}
  stopAllAction(){}
  uncacheRoot(){uncached++}
}};
const loader=createEnemyVisualLoaderV63({THREE,loaderFactory:()=>({async loadAsync(uri){
  loads++;assert.match(uri,/enemy_(assault|ranger|heavy)_v62.glb/);
  return {scene:{traverse(){}},animations:clips};
}}),cloneFactory:()=>({scale:{setScalar(){}},rotation:{y:0}})});
await loader.preload();assert.equal(loads,3);
const enemy={role:'assault',hp:100,mesh:{parent:{},add(){},remove(){}},torso:{visible:true}};
loader.attach(enemy);
assert.equal(enemy.torso.visible,false);
loader.update(enemy,.016,{moving:true});
assert.equal(enemy._v63.director.snapshot().current,'Run');
loader.update(enemy,.016,{shot:true});
assert.equal(enemy._v63.director.snapshot().current,'Fire');
enemy.hp=90;loader.update(enemy,.016,{});
assert.equal(enemy._v63.director.snapshot().current,'Hit');
for(const action of enemy._v63.actions.values()){
  const t=action.clip.tracks.find(track=>track.name==='root.position');
  assert.ok(t,'vertical foot grounding must be preserved');
  assert.equal(t.values[0],t.values[3],'no horizontal root x movement');
  assert.equal(t.values[2],t.values[5],'no horizontal root z movement');
  assert.notEqual(t.values[1],t.values[4],'preserve vertical Run heel correction');
}
loader.detach(enemy);
assert.equal(enemy._v63,null);assert.equal(enemy.torso.visible,true);
assert.equal(loader.status().activeClones,0);
loader.dispose();assert.equal(uncached,1);
const noAsset=createEnemyVisualLoaderV63({THREE,loaderFactory:()=>({
  async loadAsync(){throw Error('missing GLB')}}),cloneFactory:()=>({})});
await noAsset.preload();
const old={role:'heavy',hp:180,mesh:{parent:{},add(){},remove(){}},torso:{visible:true}};
noAsset.attach(old);await Promise.resolve();
assert.equal(old.torso.visible,true,'fallback visible if no GLB');
noAsset.dispose();
console.log('PASS v6.3: real-shot Fire, HP hit, locomotion return, root masking, cleanup and asset fallback');
