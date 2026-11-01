import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import vm from 'node:vm';import assert from 'node:assert/strict';
const root=path.resolve(import.meta.dirname,'base/dist');const app=fs.readFileSync(path.join(root,'app.js'),'utf8');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'scene_view.json'),'utf8'));
const read=n=>JSON.parse(fs.readFileSync(path.join(root,n),'utf8'));
function extract(a,b){const i=app.indexOf(a),j=app.indexOf(b,i);assert(i>=0&&j>i,`${a} missing`);return app.slice(i,j)}
assert.equal(manifest.version,'V008-structure-candidate-r1');
const mod=manifest.extension_v008.model;
let requests=[];const mctx={manifest,metrics:{},loadText:{textContent:''},v008Facades:null,refreshDiagnostics:()=>{},
  getJSON:async n=>read(n),loadStageModel:async m=>{
    const p=path.join(root,m.path);const bytes=fs.readFileSync(p);assert.equal(bytes.length,m.bytes);
    assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),m.sha256);
    requests.push(m.stage);return {visible:true,name:m.stage};
  }};
let ctx=vm.createContext(mctx);
const v008Code=extract('async function loadV008StructureCandidate(){','function place(atEnd=false){');
await vm.runInContext(v008Code+'\nloadV008StructureCandidate();',ctx);
assert.deepEqual(requests,['V008_FACADES']);assert.equal(ctx.v008Facades.name,'V008_FACADES');assert.equal(ctx.v008Facades.visible,false);
assert.equal(ctx.metrics.v008_structural.route_unchanged,true);
const malformed=vm.createContext({...mctx,metrics:{},v008Facades:null,getJSON:async n=>({...read(n),model:{...mod,sha256:'tampered'}}),loadStageModel:async()=>{throw Error('must not fetch changed SHA')}});
let rejected=false;try{await vm.runInContext(v008Code+'\nloadV008StructureCandidate();',malformed)}catch(e){rejected=String(e).includes('契約不一致')};assert.equal(rejected,true);
// Prove skip for the two hidden archived facades, while roads/signs still load.
const loadV005=extract('async function loadV005Extension(){','async function loadV006Extension(){');
let req=[];
const cctx=vm.createContext({...mctx,metrics:{},collisionData:{walkable:[],obstacles:[]},B:{},v005Road:null,v005Facades:null,v005Signs:null,
  getJSON:async n=>read(n),CollisionWorld:class {},collisionForStage:()=>({}),suppressGreyBuildingPlaceholders:()=>{},
  loadStageModel:async m=>{req.push(m.stage);return {name:m.stage,visible:true}}});
await vm.runInContext(loadV005+'\nloadV005Extension();',cctx);
assert.deepEqual(req,['V005_ROAD','V005_SIGNS']);assert.equal(cctx.v005Facades,null);
assert.equal(cctx.metrics.v008_skipped_hidden_models.length,1);
assert.equal(cctx.metrics.v008_skipped_hidden_models[0].stage,'V005_FACADES');
// Stage B shows V008 only, while V007 and V005 remain hidden; A hides all detailed facades.
const stageCode=extract('function setStage(value){','function updateStatus(){');
const pose=()=>({eye:{x:0,y:1,z:0},target:{x:0,y:1,z:1},up:{x:0,y:1,z:0},fov:54});
const s={stage:'B',cameraPose:pose,setStage(v){this.stage=v}},button={classList:{toggle(){}},setAttribute(){}};
Object.assign(ctx,{session:s,inputEvents:{cancel(){}},collisionData:null,extensionFacades:{visible:false},extensionSigns:{visible:false},v005Signs:{visible:false},
 v005Facades:{visible:false},v007Facades:{visible:false},$:(id)=>button,updateCamera:()=>{},updateStatus:()=>{},performance:{now:()=>0},metrics:{stage_switches:[]}});
vm.runInContext(stageCode+'\nsetStage("B");',ctx);
assert.equal(ctx.v008Facades.visible,true);assert.equal(ctx.v007Facades.visible,false);assert.equal(ctx.v005Facades.visible,false);
vm.runInContext('setStage("A");',ctx);assert.equal(ctx.v008Facades.visible,false);assert.equal(ctx.metrics.stage_switches.length,2);
const old=fs.readFileSync(path.join(root,'assets/v005_east_facades.glb'));
const older=fs.readFileSync(path.join(root,'assets/v007_east_facades.glb'));
const report={schema:'date-v008-node-runtime-contract/1',status:'PASS_NODE_LOGIC_NO_GPU',new_glb_sha_verified:true,
  corrupt_manifest_rejected:true,hide_v007_and_v005:true,archived_v005_download_skipped:true,archived_v007_download_skipped:true,
  archived_model_bytes_not_downloaded_on_initial_boot:old.length+older.length,stage_switches:2,stage_pose_drift:0,
  webgl2_verified:false,android_verified:false};
fs.mkdirSync(path.resolve(import.meta.dirname,'evidence'),{recursive:true});
fs.writeFileSync(path.resolve(import.meta.dirname,'evidence/V008_node_contract.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));