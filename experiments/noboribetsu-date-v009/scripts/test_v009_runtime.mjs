import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import vm from 'node:vm';import assert from 'node:assert/strict';
const work=path.resolve(import.meta.dirname);const root=path.join(work,'runtime/dist');
const app=fs.readFileSync(path.join(root,'app.js'),'utf8');const manifest=JSON.parse(fs.readFileSync(path.join(root,'scene_view.json'),'utf8'));
const read=n=>JSON.parse(fs.readFileSync(path.join(root,n),'utf8'));
const extract=(a,b)=>{const i=app.indexOf(a),j=app.indexOf(b,i);assert(i>=0&&j>i,a+' anchor missing');return app.slice(i,j)};
assert.equal(manifest.version,'V009-utsuroi-candidate-r1');
assert.equal(manifest.extension_v009.source_v008_sha256,'ff6725b1ecb22b455203c69dd4dd194f68c2b356ce17364ad89e09941d4ca4ea');
assert(!app.includes('await loadV008StructureCandidate();'));
assert.equal(app.match(/await loadV009UtsuroiCandidate\(\);/g)?.length,1);
const v009Code=extract('async function loadV009UtsuroiCandidate(){','function place(atEnd=false){');
const req=[];
const ctx=vm.createContext({manifest,metrics:{},loadText:{textContent:''},v009Facades:null,refreshDiagnostics:()=>{},
 getJSON:async n=>read(n),loadStageModel:async m=>{
  const p=path.join(root,m.path),bytes=fs.readFileSync(p);
  assert.equal(bytes.byteLength,m.bytes);assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),m.sha256);
  req.push(m.stage);return {visible:true,name:m.stage};}});
await vm.runInContext(v009Code+'\nloadV009UtsuroiCandidate();',ctx);
assert.deepEqual(req,['V009_FACADES']);assert.equal(ctx.v009Facades.name,'V009_FACADES');assert.equal(ctx.v009Facades.visible,false);
// Malformed descriptor must be refused BEFORE loading a mesh.
let corruptReject=false;const wrong=vm.createContext({manifest,metrics:{},loadText:{textContent:''},refreshDiagnostics(){},v009Facades:null,
 getJSON:async n=>({...read(n),geometry:{...read(n).geometry,total_triangles:999}}),
 loadStageModel:async()=>{throw Error('Should reject before loading a model');}});
try{await vm.runInContext(v009Code+'\nloadV009UtsuroiCandidate();',wrong)}catch(e){corruptReject=String(e).includes('契約不一致')};assert(corruptReject);
// V005 and V007 and V008 are archived. V005 loader intentionally skips one file,
// and V009 boot calls neither V007 nor V008 loaders. No fake fetch estimates.
const v005Code=extract('async function loadV005Extension(){','async function loadV006Extension(){');
const oldCalls=[];
const oldCtx=vm.createContext({manifest,metrics:{},loadText:{textContent:''},collisionData:{walkable:[],obstacles:[]},B:{},
 refreshDiagnostics(){},v005Road:null,v005Facades:null,v005Signs:null,getJSON:async n=>read(n),
 CollisionWorld:class {},collisionForStage:()=>({}),suppressGreyBuildingPlaceholders:()=>{},
 loadStageModel:async m=>{oldCalls.push(m.stage);return {name:m.stage,visible:true};}});
await vm.runInContext(v005Code+'\nloadV005Extension();',oldCtx);
assert.deepEqual(oldCalls,['V005_ROAD','V005_SIGNS']);
assert(oldCtx.v005Facades==null);
// Stage A/B preserves pose in the same real function. Use safe stubs for renderer.
const stageCode=extract('function setStage(value){','function updateStatus(){');
const pose=()=>({eye:{x:0,y:1,z:0},target:{x:0,y:1,z:1},up:{x:0,y:1,z:0},fov:54});
const s={stage:'B',cameraPose:pose,setStage(v){this.stage=v}};
const button={classList:{toggle(){}},setAttribute(){}};
Object.assign(ctx,{session:s,inputEvents:{cancel(){}},collisionData:null,
 extensionFacades:{visible:false},extensionSigns:{visible:false},v005Signs:{visible:false},
 v005Facades:{visible:false},v007Facades:{visible:false},v008Facades:{visible:false},
 $:()=>button,updateCamera:()=>{},updateStatus:()=>{},performance:{now:()=>0},metrics:{stage_switches:[]}});
const orig=JSON.stringify(s.cameraPose());
vm.runInContext(stageCode+'\nsetStage("B");',ctx);assert.equal(ctx.v009Facades.visible,true);
assert.equal(ctx.v008Facades.visible,false);assert.equal(ctx.v007Facades.visible,false);
vm.runInContext('setStage("A");',ctx);assert.equal(ctx.v009Facades.visible,false);
assert.equal(JSON.stringify(s.cameraPose()),orig);
const archived=fs.statSync(path.join(root,'assets/v008_waraji_architecture.glb')).size+
 fs.statSync(path.join(root,'assets/v007_east_facades.glb')).size+
 fs.statSync(path.join(root,'assets/v005_east_facades.glb')).size;
const report={schema:'date-v009-runtime-no-GPU/1',status:'PASS_NODE_LOGIC_ONLY',
 verified_model_requests:req,verified_v005_requests:oldCalls,corrupt_manifest_rejected:true,
 new_model_sha256_verified:true,stage_switches:2,camera_pose_drift:0,
 archived_facades_not_downloaded_at_initial_boot_bytes:archived,
 precise_limit:'Static control and GLB hash validations only; WebGL2 and real GPU FPS not tested'};
fs.mkdirSync(path.join(work,'evidence'),{recursive:true});
fs.writeFileSync(path.join(work,'evidence/v009_runtime_contract.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));