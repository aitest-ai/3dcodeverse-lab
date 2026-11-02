import fs from 'node:fs';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {CollisionWorld,collisionForStage,routeAt,nearestRoute,pointInPolygon,circleTouchesPolygon} from './base/dist/navigation.js';
import {WalkSession} from './base/dist/walk-session.js';
import {move,headingFromVector,basis} from './base/dist/controls.js';
const D=new URL('./base/dist/',import.meta.url);
const read=(name)=>JSON.parse(fs.readFileSync(new URL(name,D),'utf8'));
const scene=read('scene_view.json'), root=read('collision.json');
let combined=structuredClone(root);
for(const file of ['extension_collision.json','v005_collision.json','v006_collision.json']){
  const c=read(file);
  combined.walkable.push(...c.walkable);
  combined.obstacles.push(...c.obstacles);
}
const world=new CollisionWorld(collisionForStage(combined,'B'),8);
const radius=combined.player.radius_m;
const checks=[]; const fail=[]; const traces={forward:[],approach:[],slide:[]};
const assert=(cond,label,detail={})=>{checks.push({name:label,pass:!!cond,...detail});if(!cond)fail.push(label);};
const pos=(s)=>{const p=routeAt(scene.route,s); const g=world.ground(p.x,p.z,p.y,.45);return {...p,y:g?.y??p.y};};
const ok=(p)=>world.check(p.x,p.z,p.y,{radius,maxStep:.18,stepFrom:p.y,maxGroundError:.45});
function closestObstacle(p){let best=null;
 function segDist(x,z,a,b){const dx=b[0]-a[0],dz=b[1]-a[1],ll=dx*dx+dz*dz;const t=ll?Math.max(0,Math.min(1,((x-a[0])*dx+(z-a[1])*dz)/ll)):0;return Math.hypot(x-a[0]-dx*t,z-a[1]-dz*t)}
 for(const o of world.obstacles){if(p.y+1.7<(o.minY??-Infinity)||p.y>(o.maxY??Infinity))continue;let d=pointInPolygon(p.x,p.z,o.polygon)?0:Math.min(...o.polygon.map((a,i)=>segDist(p.x,p.z,a,o.polygon[(i+1)%o.polygon.length])));if(!best||d<best.d)best={id:o.id,d,obstacle:o};}return best;
}
// Recheck V017 centerline claims against the actual V017 navigation module.
let count=0,misaligned=0,closest={d:Infinity};
for(let s=82.877;s<=130.0146;s+=0.2){const p=pos(s);const check=ok(p);if(!check.ok)misaligned++;count++;const hit=closestObstacle(p);if(hit?.d<closest.d)closest={s,d:hit.d,id:hit.id};}
assert(count>=236&&misaligned===0,'V004 centerline: full navigation-world walkability',{count,misaligned});
assert(closest.d>radius+0.12 && closest.d<radius+0.45,'Narrowest post range consistent with V017',{margin:Number((closest.d-radius).toFixed(5)),s:closest.s,obstacle:closest.id});
const offsets=[-1.5,-1,-.5,0,.5,1,1.5];const offsetChecks=offsets.map(o=>({offset_m:o,passes:0,blocked:0,reasons:{}}));
for(let k=0;k<237;k++){let s=82.877+(130.0146-82.877)*k/236;const p=pos(s);for(let j=0;j<offsets.length;j++){const o=offsets[j],x=p.x-p.tz*o,z=p.z+p.tx*o;const q=world.check(x,z,p.y,{radius,maxStep:.18,stepFrom:p.y,maxGroundError:.45});if(q.ok)offsetChecks[j].passes++;else{offsetChecks[j].blocked++;offsetChecks[j].reasons[q.reason]=(offsetChecks[j].reasons[q.reason]||0)+1;}}}
assert(offsetChecks[3].blocked===0 && offsetChecks.slice(0,3).some(x=>x.blocked>0),'Lateral sampling distinguishes safe centerline from blocked porch side',{lateral:offsetChecks});
// Construct a route-following WalkSession and hold forward 0.10-second ticks from s~85 to s~102.
let variants={A:{visible:false},B:{visible:true}},walk=new WalkSession({world,route:scene.route,variants});walk.start();
const narrow=pos(85.0);walk.position={x:narrow.x,y:narrow.y,z:narrow.z};walk.heading=headingFromVector(narrow.tx,narrow.tz);walk.input.keyDown('KeyW');
let blockedSteps=0,maxDeviation=0,minMargin=Infinity,stepCount=240;
for(let k=0;k<stepCount;k++){const r=walk.advance(.1);blockedSteps+=r.blocked;const near=nearestRoute(scene.route,r.position.x,r.position.z);maxDeviation=Math.max(maxDeviation,Math.sqrt(near.d2));const hit=closestObstacle(r.position);minMargin=Math.min(minMargin,hit.d-radius);if(!ok(r.position).ok)fail.push('walk stepped into invalid space');traces.forward.push({x:r.position.x,z:r.position.z,step:k});}
walk.input.keyUp('KeyW'); const end=walk.position;
assert(end.x>narrow.x+9,'Keyboard forward movement advances past near posts',{progress_m:Number(Math.hypot(end.x-narrow.x,end.z-narrow.z).toFixed(3)),blockedSteps,maxDeviation:Number(maxDeviation.toFixed(3)),minMargin:Number(minMargin.toFixed(3))});
assert(minMargin>=-1e-6,'No obstacle penetration during forward motion',{minMargin:Number(minMargin.toFixed(5))});
// Rotating in place near the closest post must not displace the capsule.
walk.position={x:pos(closest.s).x,y:pos(closest.s).y,z:pos(closest.s).z};
const before={...walk.position};walk.turn(90);walk.lookBy(150,120);
assert(Math.hypot(walk.position.x-before.x,walk.position.z-before.z)<1e-8 && ok(walk.position).ok,'Turn/look while close to a porch column does not teleport',{heading:walk.heading});
// Move toward nearest porchpost until blocked. The actual collision solver should stop or slide, never penetrate.
const from=pos(closest.s);const hit=closestObstacle(from); const target={x:hit.obstacle.polygon.reduce((a,p)=>a+p[0],0)/hit.obstacle.polygon.length,z:hit.obstacle.polygon.reduce((a,p)=>a+p[1],0)/hit.obstacle.polygon.length};
const diff={x:target.x-from.x,z:target.z-from.z},len=Math.hypot(diff.x,diff.z);let cur={x:from.x,y:from.y,z:from.z};let nearBlocks=0,invalid=0,minAfter=Infinity;
for(let i=0;i<25;i++){let q=move(world,cur,diff.x/len*.08,diff.z/len*.08,{radius,maxStep:.18});cur=q.position;nearBlocks+=q.blocked;const ck=ok(cur);if(!ck.ok)invalid++;minAfter=Math.min(minAfter,closestObstacle(cur).d-radius);traces.approach.push({x:cur.x,z:cur.z,step:i});}
assert(nearBlocks>0 && invalid===0 && minAfter>=-1e-6,'Approaching porchpost is blocked rather than penetrated',{blocked_substeps:nearBlocks,invalid,minAfter:Number(minAfter.toFixed(5)),post_id:hit.id});
// Along the obstacle, a perpendicular attempt should remain valid (sliding may or may not progress).
const side={x:-diff.z/len,z:diff.x/len};let slideBlocks=0,slideDistance=0;
for(let i=0;i<18;i++){let next=move(world,cur,side.x*.055,side.z*.055,{radius,maxStep:.18});slideBlocks+=next.blocked;slideDistance+=Math.hypot(next.position.x-cur.x,next.position.z-cur.z);cur=next.position;if(!ok(cur).ok)invalid++;traces.slide.push({x:cur.x,z:cur.z,step:i});}
assert(invalid===0,'Sideways movement beside the pillar never enters an obstacle',{slide_m:Number(slideDistance.toFixed(3)),slideBlocked:slideBlocks});
// Standing still after releasing all controls must remain still.
walk.position={...cur};walk.input.clear();const idleStart={...walk.position};for(let i=0;i<30;i++)walk.advance(.1);
assert(Math.hypot(walk.position.x-idleStart.x,walk.position.z-idleStart.z)<1e-8,'Key release prevents drift',{drift_m:Math.hypot(walk.position.x-idleStart.x,walk.position.z-idleStart.z)});
// A/B switch should not change spatial state.
const stageStart={...walk.position},headStart=walk.heading;walk.setStage('A');walk.setStage('B');
assert(Math.hypot(walk.position.x-stageStart.x,walk.position.z-stageStart.z)<1e-8&&headStart===walk.heading,'A/B stage roundtrip preserves pose',{stage:walk.stage});
const payload={schema:'noboribetsu-date-v018-actual-collision-motion-qa/1',source_v017_runtime_sha256:crypto.createHash('sha256').update(fs.readFileSync(new URL('./Noboribetsu_Date_V017_R1_Runtime.zip',import.meta.url))).digest('hex'),source_files:['navigation.js','controls.js','walk-session.js','collision.json','extension_collision.json','v005_collision.json','v006_collision.json','scene_view.json'],environment:'Node 22: actual imported runtime collision/move/session code; no browser/GPU',scope:'V004 s=82.877..130.0146 plus narrow porch near s~89.87',player_radius_m:radius,nav_tris:world.triangles.length,obstacles:world.obstacles.length,traces,checks,failures:fail,pass:fail.length===0,limitations:['not real browser PointerEvents','not actual shop doorway threshold','not Android physical device','centerline & simulated movement only; not accessibility claim']};
fs.mkdirSync(new URL('./outputs/',import.meta.url),{recursive:true});fs.writeFileSync(new URL('./outputs/V018_motion_qa.json',import.meta.url),JSON.stringify(payload,null,2)+'\n');console.log(JSON.stringify({pass:payload.pass,checks:checks.map(c=>({name:c.name,pass:c.pass,...(c.margin!==undefined?{margin:c.margin}:{})})),fail,closest,blockedSteps,slideDistance},null,2));if(fail.length)process.exitCode=1;