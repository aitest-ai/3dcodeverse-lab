/** Taipei Mech v7.5: local, fail-closed visual positioning of smoke.
 * Uses original city height/collider callbacks; does not alter visibility,
 * collision shapes, ray damage, building materials or the map.
 */
export const clampSmokeV75=(v,a,b)=>Math.min(b,Math.max(a,Number.isFinite(v)?v:a));
export const SMOKE_CITY_SETTINGS_V75=Object.freeze({
  full:Object.freeze({wallBudget:16,groundBudget:12,smokeStride:1,minLightGap:.105}),
  balanced:Object.freeze({wallBudget:10,groundBudget:8,smokeStride:2,minLightGap:.21}),
  light:Object.freeze({wallBudget:6,groundBudget:5,smokeStride:3,minLightGap:Infinity})
});
export function createSmokeCityLimiterV75(){
 let mode='full',wallQueries=0,groundQueries=0,peakWalls=0,peakGround=0;
 let wallRejected=0,groundRejected=0,budgetHeld=0,verified=0;
 function setQuality(level){if(!Object.hasOwn(SMOKE_CITY_SETTINGS_V75,level))return false;mode=level;return true;}
 function newFrame(){wallQueries=0;groundQueries=0;}
 /** Move only if this FULL segment is safe; this makes even a thin wall
  * blocking when endpoints are outside. If budget is exhausted, hold pose.
  * Missing ground may not cause a teleport to a bridge at a different level.
  */
 function place(previous,desired,{groundAt=()=>NaN,wallAt=()=>true,groundReference=NaN,requireGround=false}={}){
  if(!previous||!desired||![previous.x,previous.y,previous.z,desired.x,desired.y,desired.z].every(Number.isFinite)){
   wallRejected++;return {position:previous,accepted:false,reason:'invalid-position'};
  }
  const settings=SMOKE_CITY_SETTINGS_V75[mode];
  if(wallQueries>=settings.wallBudget){budgetHeld++;return {position:previous,accepted:false,reason:'wall-budget'};}
  wallQueries++;peakWalls=Math.max(peakWalls,wallQueries);
  let obstructed=true;
  try {obstructed=!!wallAt(desired.x,desired.z,desired.y,.075,previous.x,previous.z,previous.y);}
  catch {obstructed=true;}
  if(obstructed){wallRejected++;return {position:previous,accepted:false,reason:'wall'};}
  let floorSample=null;
  if(requireGround){
   if(groundQueries>=settings.groundBudget){budgetHeld++;return {position:previous,accepted:false,reason:'ground-budget'};}
   groundQueries++;peakGround=Math.max(peakGround,groundQueries);
   let height=NaN;
   try{height=groundAt(desired.x,desired.z,Number.isFinite(groundReference)?groundReference:previous.y);}catch{}
   // Do not reclassify an upper bridge or subterranean floor as adjacent street.
   if(!Number.isFinite(height)||(Number.isFinite(groundReference)&&Math.abs(height-groundReference)>.75)){
    groundRejected++;return {position:previous,accepted:false,reason:'unknown-or-separate-deck'};
   }
   verified++;floorSample=height;
  }
  return {position:desired,accepted:true,reason:'clear',floorSample};
 }
 function stats(){return {mode,wallQueries,groundQueries,peakWalls,peakGround,wallRejected,groundRejected,budgetHeld,verified};}
 function reset(){newFrame();peakWalls=peakGround=wallRejected=groundRejected=budgetHeld=verified=0;}
 return {place,newFrame,setQuality,stats,reset};
}
