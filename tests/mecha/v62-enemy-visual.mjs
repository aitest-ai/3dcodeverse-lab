import assert from 'node:assert/strict';
import {createEnemyVisualLoaderV62,ENEMY_ASSETS_V62} from '../../examples/threejs/mech-enemy-glb-v62.js';
assert.deepEqual(Object.keys(ENEMY_ASSETS_V62),['assault','ranger','heavy']);
let loads=0,uncached=0;
const clipNames=['Mecha_Idle','Mecha_Run','Mecha_Fire','Mecha_Punch','Mecha_Dodge','Mecha_Hit'];
const clips=clipNames.map(name=>({name,tracks:[{name:'root.position'},{name:'leg.rotation'}],clone(){return {...this,tracks:[...this.tracks]};}}));
const loader={async loadAsync(url){loads++;assert.match(url,/enemy_(assault|ranger|heavy)_v62.glb/);
 return {scene:{name:'rig',traverse(fn){fn({})}},animations:clips};}};
const actions=new Map();
const THREE={AnimationMixer:class{constructor(root){this.root=root;}clipAction(clip){
 const a={name:clip.name,tracks:clip.tracks,reset(){return this},play(){return this},crossFadeFrom(){return this}};
 actions.set(a.name,a);return a;}update(dt){assert.ok(dt>=0&&dt<=.05);}
 stopAllAction(){}uncacheRoot(){uncached++;}}};
const visuals=createEnemyVisualLoaderV62({THREE,loaderFactory:()=>loader,
 cloneFactory:()=>({rotation:{y:0},scale:{setScalar(){}},name:'asset'})});
await visuals.preload();assert.equal(loads,3);
const createEnemy=role=>{const children=new Set();return {role,dead:false,
 mesh:{parent:{},add(v){children.add(v)},remove(v){children.delete(v)}},torso:{visible:true}};};
const a=createEnemy('assault'),b=createEnemy('assault');
visuals.attach(a);visuals.attach(b);assert.equal(loads,3);
assert.ok(a._v62&&b._v62&&a._v62.visual!==b._v62.visual);
assert.equal(a.torso.visible,false);visuals.update(a,.016,{moving:true});
assert.equal(a._v62.current,'Run');
for(const item of actions.values())assert.ok(item.tracks.every(t=>t.name!=='root.position'));
visuals.detach(a);assert.equal(a.torso.visible,true);
assert.equal(visuals.status().activeClones,1);
visuals.dispose();assert.equal(visuals.status().activeClones,0);assert.equal(uncached,2);
const broken=createEnemyVisualLoaderV62({THREE,
 loaderFactory:()=>({loadAsync:async()=>{throw new Error('missing asset')}}),cloneFactory:()=>({})});
await broken.preload();const bad=createEnemy('ranger');broken.attach(bad);await Promise.resolve();
assert.equal(bad.torso.visible,true);assert.equal(bad._v62,undefined);broken.dispose();
console.log('PASS v6.2: async cache, 15-bone clone bridge, 6 animation clips, root masking, safe fallback, reset & disposal');
