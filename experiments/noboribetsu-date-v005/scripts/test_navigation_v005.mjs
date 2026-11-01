import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const ROOT=process.env.DATE_V005_ROOT||path.resolve(import.meta.dirname,'../runtime');
const D=path.resolve(ROOT,'dist');
const read=f=>JSON.parse(fs.readFileSync(path.join(D,f),'utf8'));
const {CollisionWorld,collisionForStage}=await import(pathToFileURL(path.join(D,'navigation.js')));
const {WalkSession,routeSpawn}=await import(pathToFileURL(path.join(D,'walk-session.js')));
const {move}=await import(pathToFileURL(path.join(D,'controls.js')));
const base=read('collision.json'),prev=read('extension_collision.json'),next=read('v005_collision.json');
const m=read('scene_view.json'),info=read('v005_manifest.json');
assert(m.version==='V005-east-candidate-r1');
assert(Math.abs(info.route_start_m-130.01461217900092)<1.e-6);
assert(Math.abs(info.route_end_m-m.route.at(-1).s)<1.e-6);
assert(info.known_buildings.length===2);
const collision={...base,walkable:[...base.walkable,...prev.walkable,...next.walkable],obstacles:[...base.obstacles,...prev.obstacles,...next.obstacles]};
const worlds={A:new CollisionWorld(collisionForStage(collision,'A'),8),B:new CollisionWorld(collisionForStage(collision,'B'),8)};
const report={version:m.version,route_start_m:0,old_route_m:info.route_start_m,new_route_m:m.route.at(-1).s,add_m:info.added_length_m,route_points:m.route.length,
  source_collision:base.obstacles.length,v004_posts:prev.obstacles.length,v005_posts:next.obstacles.length,
  triangle_counts:{A:worlds.A.stats,B:worlds.B.stats},scanned:0,failures:[],max_y_jump:0};
for(const [stage,w] of Object.entries(worlds)){
 for(let i=0;i<m.route.length;i++){
  const p=m.route[i],prior=m.route[Math.max(0,i-1)];
  const c=w.check(p.x,p.z,p.y,{radius:.26,maxStep:.18,stepFrom:prior.y,maxGroundError:.50});report.scanned++;
  if(!c.ok)report.failures.push({stage,i,s:p.s,reason:c.reason,id:c.id});
 }
}
let q={...m.route[0]},blocked=0,far=0,backBlocked=0,maxSingleDelta=0;
for(let i=1;i<m.route.length;i++){
 const p=m.route[i],out=move(worlds.B,q,p.x-q.x,p.z-q.z);
 blocked+=out.blocked;
 if(Math.hypot(out.position.x-p.x,out.position.z-p.z)>.035)far++;
 maxSingleDelta=Math.max(maxSingleDelta,Math.abs(out.position.y-q.y));q={...out.position};
}
const enderr=Math.hypot(q.x-m.route.at(-1).x,q.z-m.route.at(-1).z);
for(let i=m.route.length-2;i>=0;i--){
 const p=m.route[i],out=move(worlds.B,q,p.x-q.x,p.z-q.z);
 backBlocked+=out.blocked;q={...out.position};
}
const homeerr=Math.hypot(q.x-m.route[0].x,q.z-m.route[0].z);
const A={visible:false},B={visible:false};const sess=new WalkSession({world:worlds.B,route:m.route,variants:{A,B}});
const pose=sess.cameraPose();sess.setStage('A');sess.world=worlds.A;
assert.deepEqual(sess.cameraPose(),pose);
sess.setStage('B');sess.world=worlds.B;
assert.deepEqual(sess.cameraPose(),pose);
const rear=routeSpawn(worlds.B,m.route,true);
assert(rear&&Number.isFinite(rear.heading));
for(const id of m.extension_v005.building_ids){
 const b=m.buildings.find(v=>v.id===id);assert(b);
 const xs=b.polygon.map(v=>v[0]),zs=b.polygon.map(v=>-v[1]);
 const p={x:(Math.min(...xs)+Math.max(...xs))/2,z:(Math.min(...zs)+Math.max(...zs))/2,y:b.base};
 const hit=worlds.B.check(p.x,p.z,p.y,{radius:.26,maxGroundError:6});
 report['building_'+id]=hit.reason;
}
report.walk={blocked,far,maxSingleDelta,enderr,backBlocked,homeerr};
report.camera_switch_zero_drift=true;
report.ok=report.failures.length===0&&blocked===0&&far===0&&backBlocked===0&&enderr<.05&&homeerr<.05&&maxSingleDelta<.18&&m.extension_v005.building_ids.every(id=>report['building_'+id]==='obstacle');
fs.writeFileSync(path.join(ROOT,'V005_navigation_qa.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
if(!report.ok)process.exitCode=1;