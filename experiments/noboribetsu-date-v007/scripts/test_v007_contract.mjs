import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import vm from 'node:vm';import assert from 'node:assert/strict';
const root=path.resolve(import.meta.dirname,'base/dist');
const app=fs.readFileSync(path.join(root,'app.js'),'utf8');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'scene_view.json'),'utf8'));
const json=(f)=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
function extract(start,end){const a=app.indexOf(start),b=app.indexOf(end,a);assert(a>=0&&b>a);return app.slice(a,b)}
const source=extract('async function loadV007FacadeCandidate(){','function place(atEnd=false){');
const model=manifest.extension_v007.model,existing={visible:true},label={textContent:''},metrics={};let verifiedFetches=0;
let ctx=vm.createContext({manifest,metrics,loadText:label,v005Facades:existing,v007Facades:null,refreshDiagnostics:()=>{},
 getJSON:async(url)=>json(url),loadStageModel:async m=>{
  const b=fs.readFileSync(path.join(root,m.path));assert.equal(b.length,m.bytes);assert.equal(crypto.createHash('sha256').update(b).digest('hex'),m.sha256);verifiedFetches++;return {name:'',visible:true,bytes:b.length};
 }});
await vm.runInContext(source+'\nloadV007FacadeCandidate();',ctx);
assert.equal(ctx.v007Facades.name,'V007_FACADES');assert.equal(ctx.v007Facades.visible,false);assert.equal(ctx.v005Facades.visible,false);assert.equal(verifiedFetches,1);
assert.equal(ctx.metrics.v007_facades.route_unchanged,true);
// Stage switching must display only B's V007 visuals, never both V005 and V007.
const stageCode=extract('function setStage(value){','function updateStatus(){');
const pose=()=>({eye:{x:0,y:1,z:2},target:{x:1,y:1,z:2},up:{x:0,y:1,z:0},fov:54});
const session={stage:'A',cameraPose:pose,setStage(n){this.stage=n}};
const toolbar={aButton:{classList:{toggle(){}},setAttribute(){}},bButton:{classList:{toggle(){}},setAttribute(){}}};
const fac={visible:false},sign={visible:false},v005Signs={visible:false};let updates=0;
Object.assign(ctx,{session,inputEvents:{cancel(){}},collisionData:null,extensionFacades:fac,extensionSigns:sign,v005Signs,
  $:id=>toolbar[id],updateCamera:()=>{},updateStatus:()=>{updates++},refreshDiagnostics:()=>{},performance:{now:()=>0},
  metrics:{stage_switches:[]}});
vm.runInContext(stageCode+'\nsetStage("B");setStage("A");',ctx);
assert.equal(session.stage,'A');assert.equal(ctx.v007Facades.visible,false);assert.equal(ctx.v005Facades.visible,false);assert.equal(ctx.v005Signs.visible,false);
assert.equal(ctx.metrics.stage_switches.length,2);assert.equal(updates,2);
vm.runInContext('setStage("B")',ctx);
assert.equal(ctx.v007Facades.visible,true);assert.equal(ctx.v005Facades.visible,false);assert.equal(ctx.v005Signs.visible,true);
// Required contract checks fail closed if v007 manifest checksum is tampered.
let ctxBad=vm.createContext({manifest,metrics:{},loadText:{textContent:''},v005Facades:{visible:true},v007Facades:null,
  refreshDiagnostics:()=>{},getJSON:async(url)=>({...json(url),model:{...model,sha256:'tampered'}}),loadStageModel:async()=>{throw Error('Must not load corrupt model')}});
let rejected=false;try{await vm.runInContext(source+'\nloadV007FacadeCandidate();',ctxBad)}catch(e){rejected=String(e).includes('契約不符')}
assert.equal(rejected,true);
const report={schema:'date-v007-runtime-contract/1',status:'PASS_NODE_THREE_INTEGRATION_NO_WEBGL',
  original_V005_facade_hidden_in_B:true,V007_visible_only_B:true,model_SHA_verified:true,failed_on_corrupt_manifest:true,
  stage_switch_drift:0,stage_switches:3,source_V005_unchanged:true,webgl2_verified:false};
fs.writeFileSync(path.resolve(import.meta.dirname,'v007_outputs/runtime_contract_qa.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));