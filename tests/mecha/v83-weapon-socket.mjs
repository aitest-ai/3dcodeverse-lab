import assert from 'node:assert/strict';
import {findUniqueBoneV83,readRigWeaponSocketV83,compareWeaponRayV83,createMuzzleSocketAuditV83} from '../../examples/threejs/mech-weapon-socket-v83.js';
const makeVector=(x,y,z)=>({x,y,z});
const bone={name:'weapon_socket.R',isBone:true,
 updateWorldMatrix(){},
 getWorldPosition(v){return {...v,x:10,y:3,z:4};},
 localToWorld(v){return {x:10+v.x,y:3+v.y,z:4+v.z};}};
const scene={traverse(fn){fn(bone);}};
assert.equal(findUniqueBoneV83(scene).bone,bone);
assert.equal(findUniqueBoneV83({traverse(f){f(bone);f(bone);}}).status,'duplicate_socket_bones');
assert.equal(findUniqueBoneV83({traverse(f){}}).status,'socket_bone_missing');
const pivot=readRigWeaponSocketV83({model:scene,makeVector});
assert.equal(pivot.status,'socket_pivot_only');
assert.equal(pivot.tip,null);
assert.equal(compareWeaponRayV83(pivot,{start:{x:10,y:3,z:4},dir:{x:0,y:0,z:-1}}).status,'pivot_reference_only');
assert.equal(compareWeaponRayV83(pivot,{start:{x:10,y:3,z:4},dir:{x:0,y:0,z:-1}}).originErrorMeters,null);
const calibrated=readRigWeaponSocketV83({model:scene,makeVector,localTip:{x:0,y:0,z:-.6},localForward:{x:0,y:0,z:-.8}});
assert.equal(calibrated.status,'calibrated_socket_tip');
assert.deepEqual(calibrated.tip,{x:10,y:3,z:3.4});
const aligned=compareWeaponRayV83(calibrated,{start:{x:10,y:3,z:3.4},dir:{x:0,y:0,z:-1}});
assert.deepEqual(aligned.flags,[]);
const offset=compareWeaponRayV83(calibrated,{start:{x:12,y:3,z:3.4},dir:{x:1,y:0,z:0}});
assert.deepEqual(offset.flags,['ray_visual_origin_offset','ray_visual_direction_offset']);
assert.equal(readRigWeaponSocketV83({model:scene,makeVector,localTip:{x:0,y:0,z:0},localForward:{x:0,y:0,z:0}}).status,'invalid_tip_calibration');
assert.equal(readRigWeaponSocketV83({model:scene,makeVector,poseReady:false}).status,'pose_not_ready');
const audit=createMuzzleSocketAuditV83({maxSamples:2});
assert.equal(audit.sample({frame:calibrated,authoritativeRay:{start:calibrated.tip,dir:{x:0,y:0,z:-1}}}),false);
audit.setEnabled(true);
assert.equal(audit.sample({frame:pivot,authoritativeRay:{start:calibrated.tip,dir:{x:0,y:0,z:-1}},weapon:'F'}),true);
assert.equal(audit.sample({frame:calibrated,authoritativeRay:{start:calibrated.tip,dir:{x:0,y:0,z:-1}},weapon:'charge'}),true);
assert.equal(audit.sample({frame:calibrated,authoritativeRay:{start:calibrated.tip,dir:{x:0,y:0,z:-1}}}),true);
assert.equal(audit.count,2);
assert.equal(audit.report().diagnostics.length,2);
for(const item of audit.report().diagnostics){assert.ok(!('worldPosition' in item));assert.ok(!('position' in item));}
assert.ok(!('pivot' in audit.report().diagnostics[0]));
audit.clear();assert.equal(audit.count,0);
console.log('PASS v8.3 actual rig socket pivot and calibrated tip, no automatic weapon-ray changes, bounded privacy-safe audit');
