import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import {CollisionWorld,collisionForStage,nearestRoute} from './runtime/dist/navigation.js';
const D=new URL('./runtime/dist/',import.meta.url),read=name=>JSON.parse(fs.readFileSync(new URL(name,D),'utf8'));
const scene=read('scene_view.json'),patch=read('v019_porch_guide.json');
const c=read('collision.json');
for(const name of ['extension_collision.json','v005_collision.json','v006_collision.json']){
  const x=read(name);c.walkable.push(...x.walkable);c.obstacles.push(...x.obstacles);
}
const world=new CollisionWorld(collisionForStage(c,'B'),8);
let samples=[];let errors=[];
for (const point of patch.samples){
 const nr=nearestRoute(scene.route,point.x,point.z);
 const ground=world.ground(point.x,point.z,point.y,.45);
 const q=ground && world.check(point.x,point.z,ground.y,{radius:.26,maxStep:.18,stepFrom:ground.y,maxGroundError:.45});
 const gap=Math.sqrt(nr.d2);
 const ok=!!q?.ok&&gap<.02;
 samples.push({s_m:point.s_m,centerline_gap_m:gap,walkable:ok,ground_y_m:ground?.y??null});
 if(!ok) errors.push({s_m:point.s_m,reason:q?.reason??'no ground',gap});
}
const summary={schema:'noboribetsu-date-v019-guidance-collision-verification/1',passed:errors.length===0,model_is_author_estimated:true,physical_accessibility_verified:false,collision_modified:false,route_modified:false,guide_marker_count:patch.samples.length,actual_game_collision_engine:true,walkable_markers:samples.filter(x=>x.walkable).length,errors,samples};
fs.mkdirSync(new URL('./qa/',import.meta.url),{recursive:true});fs.writeFileSync(new URL('./qa/V019_collision_guide_qa.json',import.meta.url),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify({passed:summary.passed,markers:summary.guide_marker_count,walkable:summary.walkable_markers,errors},null,2));
if(errors.length)process.exitCode=1;