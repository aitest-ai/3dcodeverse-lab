import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {pathToFileURL} from 'node:url';
const root=process.env.DATE_V006_ROOT||path.resolve(import.meta.dirname,'..');const d=path.join(root,'dist');
const read=p=>JSON.parse(fs.readFileSync(path.join(d,p),'utf8'));
const {CollisionWorld,collisionForStage}=await import(pathToFileURL(path.join(d,'navigation.js')));
const {WalkSession,routeSpawn}=await import(pathToFileURL(path.join(d,'walk-session.js')));
const {move}=await import(pathToFileURL(path.join(d,'controls.js')));
const base=read('collision.json'),v004=read('extension_collision.json'),v005=read('v005_collision.json'),v006=read('v006_collision.json');
const view=read('scene_view.json'),info=read('v006_manifest.json');
assert.equal(view.version,'V009-utsuroi-candidate-r1');
assert.equal(v006.walkable.length,1);assert.equal(v006.obstacles.length,0);assert.equal(info.new_buildings,0);
assert(Math.abs(view.route.at(-1).s-231.56641497226084)<.000001);
assert(Math.abs(info.previous_route_end_m-197.72393408812707)<.000001);
const collision={...base,walkable:[...base.walkable,...v004.walkable,...v005.walkable,...v006.walkable],obstacles:[...base.obstacles,...v004.obstacles,...v005.obstacles]};
const wa=new CollisionWorld(collisionForStage(collision,'A'),8),wb=new CollisionWorld(collisionForStage(collision,'B'),8);
const r={schema:'date-v009-route-preservation/1',status:'FAIL',route_length_m:view.route.at(-1).s,route_points:view.route.length,checks:0,failures:[],new_walkable_triangles:v006.walkable[0].triangles.length};
for(const [name,w] of [['A',wa],['B',wb]]){
 for(let i=0;i<view.route.length;i++){
  const p=view.route[i],prior=view.route[Math.max(i-1,0)];
  const x=w.check(p.x,p.z,p.y,{radius:.26,maxStep:.18,stepFrom:prior.y,maxGroundError:.5});r.checks++;
  if(!x.ok)r.failures.push({stage:name,i,s:p.s,reason:x.reason,obstacle:x.id});
 }
}
let pos={...view.route[0]};const travel={blocked:0,off_route:0,return_blocked:0,max_step_delta:0};
for(const p of view.route.slice(1)){
 const beforeY=pos.y;const m=move(wb,pos,p.x-pos.x,p.z-pos.z);travel.blocked+=m.blocked;travel.max_step_delta=Math.max(travel.max_step_delta,Math.abs(m.position.y-beforeY));
 travel.off_route+=Number(Math.hypot(m.position.x-p.x,m.position.z-p.z)>.035);pos={...m.position};
}
travel.end_distance_m=Math.hypot(pos.x-view.route.at(-1).x,pos.z-view.route.at(-1).z);
for(let i=view.route.length-2;i>=0;i--){const p=view.route[i],m=move(wb,pos,p.x-pos.x,p.z-pos.z);travel.return_blocked+=m.blocked;pos={...m.position};}
travel.home_distance_m=Math.hypot(pos.x-view.route[0].x,pos.z-view.route[0].z);
const A={visible:false},B={visible:false};const s=new WalkSession({world:wb,route:view.route,variants:{A,B}});const before=s.cameraPose();s.setStage('A');s.world=wa;assert.deepEqual(s.cameraPose(),before);s.setStage('B');s.world=wb;assert.deepEqual(s.cameraPose(),before);
const tail=routeSpawn(wb,view.route,true);assert(Number.isFinite(tail.heading));
r.travel=travel;r.camera_stage_switch_drift=0;r.stage_world_triangle_counts={A:wa.stats,B:wb.stats};
r.status=r.failures.length===0&&travel.blocked===0&&travel.return_blocked===0&&travel.off_route===0&&travel.end_distance_m<.05&&travel.home_distance_m<.05&&travel.max_step_delta<.18?'PASS_STATIC_NAVIGATION_ONLY':'FAIL';
fs.writeFileSync(path.join(root,'evidence/V009_navigation_qa.json'),JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify(r,null,2));if(r.status==='FAIL')process.exit(1);