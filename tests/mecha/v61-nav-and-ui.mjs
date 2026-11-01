import assert from 'node:assert/strict';
import {createEnemyNavigationV61} from '../../examples/threejs/mech-enemy-navigation-v61.js';
import {createEnemyBrainV59} from '../../examples/threejs/mech-enemy-ai-v59.js';
import {createMissionPresentationV61} from '../../examples/threejs/mech-mission-presentation-v61.js';

const obstacle={minX:4,maxX:9,minZ:-5,maxZ:5};
function blocked(a,b,r=.6){
 const d=Math.hypot(a.x-b.x,a.z-b.z),n=Math.max(1,Math.ceil(d/.35));
 for(let i=0;i<=n;i++){const t=i/n,x=a.x+(b.x-a.x)*t,z=a.z+(b.z-a.z)*t;
  if(x>=obstacle.minX-r&&x<=obstacle.maxX+r&&z>=obstacle.minZ-r&&z<=obstacle.maxZ+r)return true;}
 return false;
}
const nav=createEnemyNavigationV61({budget:6});
assert.ok(nav.begin({from:{x:0,y:0,z:0},to:{x:20,z:0},minRange:5,maxRange:10}));
for(let i=0;i<100 && nav.snapshot().status==='planning';i++){
 const before=nav.snapshot().expanded;
 nav.step({canStep:(a,b)=>blocked(a,b)?null:0,hasSight:(a,b)=>!blocked(a,b,0)});
 assert.ok(nav.snapshot().expanded-before<=6);
}
assert.equal(nav.snapshot().status,'ready');
let p={x:0,z:0,y:0},count=0;for(let i=0;i<30;i++){const wp=nav.waypoint(p);if(!wp)break;
 assert.equal(blocked(p,wp),false);p=wp;count++;}
assert.ok(count>=3);assert.equal(nav.snapshot().status,'done');
assert.ok(nav.invalidated({target:{x:30,z:0}}));
const denied=createEnemyNavigationV61({budget:4,maxNodes:40,maxRadius:20});
denied.begin({from:{x:0,y:0,z:0},to:{x:18,z:0},minRange:2,maxRange:8});
for(let i=0;i<80&&denied.snapshot().status==='planning';i++)denied.step({canStep:()=>null,hasSight:()=>false});
assert.equal(denied.snapshot().status,'failed');
const ai=createEnemyBrainV59({role:'assault',id:2}).update({dt:.016,position:{x:0,y:0,z:0},
 target:{x:20,z:0},visible:false,navigationTarget:{x:0,z:-8},canOccupy:()=>true,sampleGround:()=>0});
assert.equal(ai.mode,'navigate');assert.ok(ai.position.z<0);assert.equal(ai.fire,false);

function element(){const children=new Map();return {hidden:false,style:{},dataset:{},textContent:'',innerHTML:'',
 setAttribute(){},remove(){this.removed=true},querySelector(s){if(!children.has(s))children.set(s,element());return children.get(s)}};}
const doc={body:{appendChild(){}},createElement:element};
const ui=createMissionPresentationV61({documentRef:doc});
const s={phase:'combat',wave:1,totalWaves:3,waveLabel:'前哨突破',remainingSeconds:288.2,
 relayHP:100,relayMaxHP:100,activeEnemies:2};
ui.update(s,{enemyWarnings:1});
assert.equal(ui.root.hidden,false);
assert.equal(ui.root.querySelector('[data-v61-clock]').textContent,'04:49');
ui.update({...s,relayHP:20});assert.equal(ui.root.dataset.critical,'true');
ui.update({...s,phase:'victory',score:1800});
assert.equal(ui.root.dataset.result,'victory');
ui.dispose();assert.ok(ui.root.removed);
console.log('PASS v6.1: incremental OSM-safe route, no corner cuts, limited work, LOS target, navigation steer, safe failure and mission HUD lifecycle');
