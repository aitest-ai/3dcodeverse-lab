import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const ROOT=process.env.NOBORIBETSU_V004_WORKDIR||import.meta.dirname;
const dist=path.resolve(ROOT,'runtime/dist');
const read=n=>JSON.parse(fs.readFileSync(path.join(dist,n),'utf-8'));
const {CollisionWorld,collisionForStage,nearestRoute}=await import(pathToFileURL(path.join(dist,'navigation.js')));
const {WalkSession,routeSpawn}=await import(pathToFileURL(path.join(dist,'walk-session.js')));
const {move}=await import(pathToFileURL(path.join(dist,'controls.js')));
const orig=read('collision.json'),ext=read('extension_collision.json'),m=read('scene_view.json'),info=read('extension_manifest.json');
const combined={...orig,walkable:[...orig.walkable,...ext.walkable],obstacles:[...orig.obstacles,...ext.obstacles]};
const worlds={A:new CollisionWorld(collisionForStage(combined,'A'),8),B:new CollisionWorld(collisionForStage(combined,'B'),8)};
let failures=[],summary={version:m.version,route_old:info.route_previous_length_m,route_new:m.route.at(-1).s,route_points:m.route.length,old_obstacles:orig.obstacles.length,new_posts:ext.obstacles.length,collision_stats:{A:worlds.A.stats,B:worlds.B.stats},scanned_points:0,blocked_points:[]};
assert(m.route.at(-1).s>129&&m.route.at(-1).s<131);
for(const [stage,world] of Object.entries(worlds)){
  for(let i=0;i<m.route.length;i++){
    const p=m.route[i],last=m.route[i-1];
    const check=world.check(p.x,p.z,p.y,{radius:.26,maxStep:.18,stepFrom:last?.y??p.y,maxGroundError:.45});
    summary.scanned_points++;
    if(!check.ok){failures.push({stage,i,reason:check.reason,p:[p.x,p.z,p.y]});}
  }
}
summary.blocked_points=failures;
for(const p of [m.route[0],m.route.at(-1)]){
  const w=worlds.B;const result=w.check(p.x,p.z,p.y,{radius:.26,maxStep:.18,stepFrom:p.y,maxGroundError:.45});
  assert(result.ok,`endpoints must be valid: ${JSON.stringify(result)}`);
}
// Simulate full route in tiny increments using the real move collision logic; hand-crafted direct teleport is insufficient.
const world=worlds.B;
let q={...m.route[0]},blocked=0,far=0,maxSingleDelta=0;
for(let i=1;i<m.route.length;i++){
 const target=m.route[i]; const dx=target.x-q.x,dz=target.z-q.z; const out=move(world,q,dx,dz);blocked+=out.blocked;
 const distance=Math.hypot(out.position.x-target.x,out.position.z-target.z);
 if(distance>.035)far++;
 maxSingleDelta=Math.max(maxSingleDelta,Math.abs(out.position.y-q.y));
 q={...out.position};
}
summary.walk={blocked,far,maxSingleDelta,end_position:q,end_error_m:Math.hypot(q.x-m.route.at(-1).x,q.z-m.route.at(-1).z)};
// Session stage switch must be zero pose drift, and return from the new endpoint works.
const A={visible:false},B={visible:false};const session=new WalkSession({world:worlds.B,route:m.route,variants:{A,B}});
const before=session.cameraPose();session.setStage('A');session.world=worlds.A;const after=session.cameraPose();
assert.deepEqual(before,after);assert.equal(A.visible,true);assert.equal(B.visible,false);
const last=routeSpawn(worlds.B,m.route,true);assert(Number.isFinite(last.heading));
summary.switch_zero_drift=true;summary.return_heading=last.heading;
// Check that 3 OSM masses remain solid at building center as independent collision from facade geometry.
for(const id of m.extension.building_ids){
 const b=m.buildings.find(b=>b.id===id);assert(b);
 const xs=b.polygon.map(p=>p[0]), zs=b.polygon.map(p=>-p[1]);
 const x=(Math.min(...xs)+Math.max(...xs))/2,z=(Math.min(...zs)+Math.max(...zs))/2;
 const hit=world.check(x,z,m.route.at(-1).y,{radius:.26,maxGroundError:5});
 summary[`obstacle_${id}`]=hit.reason;
}
summary.ok=failures.length===0&&blocked===0&&far===0&&summary.walk.end_error_m<.05;
fs.writeFileSync(path.join(ROOT,'navigation_v004_result.json'),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify(summary,null,2));
if(!summary.ok)process.exitCode=2;