/**
 * Taipei Mecha v8.3 — read-only rig socket / authoritative beam origin audit.
 *
 * The original Blender v5.0 rig includes weapon_socket.R, but the bone pivot
 * IS NOT the physical muzzle tip. Never substitute its coordinates into the
 * game's damage ray or missile spawn without a genuinely authored tip anchor.
 * No imports, GPU allocations, network, telemetry, or persistent state.
 */
export const MUZZLE_AUDIT_SCHEMA_V83 = 'taipei-mecha-v83-rig-socket-audit';
const finite = v => typeof v === 'number' && Number.isFinite(v);
const vec = v => v && finite(v.x) && finite(v.y) && finite(v.z);
const xyz = v => ({ x: v.x, y: v.y, z: v.z });
const dist = (a,b) => Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z);
const dot = (a,b) => a.x*b.x+a.y*b.y+a.z*b.z;
const unit = v => {const n=Math.hypot(v.x,v.y,v.z); return n>1e-8?{x:v.x/n,y:v.y/n,z:v.z/n}:null};

/** Search the *actual loaded* glTF Object3D hierarchy. Reject duplicates. */
export function findUniqueBoneV83(model,name='weapon_socket.R') {
 if(!model||typeof model.traverse!=='function')return {status:'no_loaded_glb',bone:null};
 let bones=[];
 model.traverse(node=>{if(node?.name===name && node.isBone===true)bones.push(node);});
 if(bones.length===0)return {status:'socket_bone_missing',bone:null};
 if(bones.length>1)return {status:'duplicate_socket_bones',bone:null};
 return {status:'ok',bone:bones[0]};
}

/**
 * Read after the original animation mixer + recoil pose and world matrix updates.
 * `makeVector` constructs a THREE.Vector3. Optional localTip & localForward
 * MUST come from a verified author-created calibration, not inferred from a PNG.
 */
export function readRigWeaponSocketV83({model,makeVector,socketName='weapon_socket.R',
  localTip=null,localForward=null,poseReady=true}={}) {
 if(!poseReady)return {status:'pose_not_ready',authoritativeRayUnchanged:true};
 const found=findUniqueBoneV83(model,socketName);
 if(found.status!=='ok')return {status:found.status,authoritativeRayUnchanged:true};
 const bone=found.bone;
 if(typeof makeVector!=='function'||typeof bone.getWorldPosition!=='function')
   return {status:'three_vector_provider_missing',authoritativeRayUnchanged:true};
 try {
   bone.updateWorldMatrix?.(true,false);
   const p=bone.getWorldPosition(makeVector(0,0,0));
   if(!vec(p))return {status:'nonfinite_socket',authoritativeRayUnchanged:true};
   const pivot=xyz(p);
   // A bone pivot is a bone pivot, NEVER a confirmed barrel tip.
   if(localTip===null && localForward===null)
     return {status:'socket_pivot_only',pivot,tip:null,forward:null,authoritativeRayUnchanged:true};
   if(!vec(localTip)||!vec(localForward)||typeof bone.localToWorld!=='function')
     return {status:'invalid_tip_calibration',pivot,tip:null,forward:null,authoritativeRayUnchanged:true};
   const localSep=dist(localTip,localForward);
   if(localSep<.02||localSep>2.0||dist(localTip,{x:0,y:0,z:0})>3.0)
     return {status:'invalid_tip_calibration',pivot,tip:null,forward:null,authoritativeRayUnchanged:true};
   const end=bone.localToWorld(makeVector(localTip.x,localTip.y,localTip.z));
   const front=bone.localToWorld(makeVector(localForward.x,localForward.y,localForward.z));
   if(!vec(end)||!vec(front))return {status:'nonfinite_tip',pivot,tip:null,forward:null,authoritativeRayUnchanged:true};
   const forward=unit({x:front.x-end.x,y:front.y-end.y,z:front.z-end.z});
   if(!forward)return {status:'degenerate_direction',pivot,tip:null,forward:null,authoritativeRayUnchanged:true};
   return {status:'calibrated_socket_tip',pivot,tip:xyz(end),forward,authoritativeRayUnchanged:true};
 }catch(error){return {status:'socket_world_transform_error',authoritativeRayUnchanged:true};}
}

/**
 * Compares optional real authoritative `combat.fire(start,dir,...)` call.
 * NEVER changes a projectile origin, hitscan, ray collider, enemy HP or recoil.
 */
export function compareWeaponRayV83(socketFrame,{start,dir}={},
   {positionWarningMeters=.25,angleWarningDegrees=12}={}) {
 if(!vec(start)||!vec(dir)||!socketFrame || !['socket_pivot_only','calibrated_socket_tip'].includes(socketFrame.status))
  return {status:'unavailable',flags:['missing_authoritative_ray_or_socket']};
 const axis=unit(dir);
 if(!axis)return {status:'unavailable',flags:['zero_ray_direction']};
 const tip=socketFrame.tip;
 if(!tip){return {status:'pivot_reference_only',socketPivotToRayMeters:Math.round(dist(socketFrame.pivot,start)*1000)/1000,
  originErrorMeters:null,angleErrorDegrees:null,flags:['no_authored_muzzle_tip']};}
 const gap=dist(tip,start);
 const alignment=socketFrame.forward?Math.acos(Math.max(-1,Math.min(1,dot(socketFrame.forward,axis))))*180/Math.PI:null;
 const flags=[];
 if(gap>positionWarningMeters)flags.push('ray_visual_origin_offset');
 if(alignment!==null&&alignment>angleWarningDegrees)flags.push('ray_visual_direction_offset');
 return {status:'calibrated_comparison',originErrorMeters:Math.round(gap*1000)/1000,
  angleErrorDegrees:alignment===null?null:Math.round(alignment*10)/10,flags};
}

export function createMuzzleSocketAuditV83({maxSamples=24}={}) {
 if(!Number.isInteger(maxSamples)||maxSamples<1||maxSamples>64)throw RangeError('maxSamples 1..64');
 let records=[],enabled=false,rejected=0;
 function setEnabled(value){enabled=!!value;return enabled;}
 function sample({frame,authoritativeRay=null,weapon='unknown'}={}){
   if(!enabled)return false;
   if(!frame||!['socket_pivot_only','calibrated_socket_tip'].includes(frame.status)){rejected++;return false;}
   // bounded diagnostic only; not a replay of absolute world coordinates.
   const comparison=compareWeaponRayV83(frame,authoritativeRay??{});
   if(records.length>=maxSamples)records.shift();
   records.push({weapon:String(weapon).slice(0,22),socketStatus:frame.status,
    rayStatus:comparison.status,pivotToRayMeters:comparison.socketPivotToRayMeters??null,originErrorMeters:comparison.originErrorMeters??null,
    angleErrorDegrees:comparison.angleErrorDegrees??null,
    flags:comparison.flags.slice()});return true;
 }
 function report(){return {schema:MUZZLE_AUDIT_SCHEMA_V83,version:'8.3',enabled,diagnostics:records.map(x=>({...x,flags:x.flags.slice()})),
   rejected,limitations:'Socket pivot does not equal an authored muzzle tip; evidence is diagnostic only. Damage ray and gameplay remain unchanged. No world/GPS coordinates or raw images exported.'};}
 function clear(){records=[];rejected=0;enabled=false;}
 return {setEnabled,sample,report,clear,get count(){return records.length;}};
}
