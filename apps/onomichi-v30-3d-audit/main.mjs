/*
 * Setouchi V30 standalone original-GLB pose workbench.
 * This does NOT patch original game main.mjs, world.json, navigation or collision.
 * Source GLBs are loaded from local file inputs only, SHA-256 checked, never uploaded.
 */
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {V30_ASSETS,V30_MARKERS,V30_PAIRS,digestSha256,validateGlbHeader,
  ensureOriginalSha,validateMarkerConfig,nearestStats} from './rules.mjs';
import {createContactProbe} from '../../scripts/research/onomichi_v29_runtime_probe.mjs';

const $=id=>document.getElementById(id);
const ui={actorFile:$('actorFile'),bikeFile:$('bikeFile'),load:$('load'),sourceState:$('sourceState'),
 sourceInfo:$('sourceInfo'),err:$('err'),webglState:$('webglState'),overlay:$('overlay'),
 frames:$('frames'),record:$('record'),export:$('export'),confirmed:$('confirmed'),
 markers:$('markers'),metrics:$('metrics'),checks:$('checks'),rate:$('rate'),phase:$('phase'),
 play:$('play'),saveConfig:$('saveConfig'),configFile:$('configFile')};
let renderer=null,scene=null,camera=null,controls=null,clock=null,mixer=null,cycleAction=null;
let stage=null,actorGroup=null,bikeGroup=null,loaded=null;
let availableNodes={actor:[],bike:[]},markerUI={},markerSpheres={},markerLines={};
let currentProbe=null,recording=false,recordStart=0,lastSample=-Infinity,playing=true;
const clockPhase={straight:'直行標記',turn:'轉彎標記',start_stop:'起停標記'};
const markerColors=Object.fromEntries(V30_MARKERS.map(m=>[m.id,m.color]));
const glbLoader=new GLTFLoader();

function note(message,error=false){
 ui.err.textContent=error?message:'';
 if(!error)ui.sourceInfo.textContent=message;
}
function checkRows(){
 const hasModels=!!loaded;
 const entries=[
  ['WebGL2 畫面',renderer?'已建立':'未啟動'],
  ['原版人物 GLB SHA256',hasModels?'一致':'未確認'],
  ['原版自行車 GLB SHA256',hasModels?'一致':'未確認'],
  ['原版 Cycle 動畫',cycleAction?'存在':'未確認'],
  ['8 個接觸點',markersReady()?'已指定（仍須人工檢查）':'尚未完成'],
  ['遊戲整合／道路碰撞','尚未驗收'],
  ['Android 實際騎行','尚未驗收']
 ];
 ui.checks.replaceChildren();
 for(const [name,value] of entries){
  const tr=document.createElement('tr');
  for(const t of [name,value]){const td=document.createElement('td');td.textContent=t;tr.append(td)}
  ui.checks.append(tr);
 }
}
function worldPoint(ref){
 const obj=ref.node,objPoint=new THREE.Vector3(...ref.localOffset);
 obj.updateWorldMatrix(true,false);
 return obj.localToWorld(objPoint);
}
function markersReady(){
 if(!loaded||Object.keys(markerUI).length!==V30_MARKERS.length)return false;
 return V30_MARKERS.every(m=>!!selectedMarker(m.id));
}
function selectedMarker(id){
 const row=markerUI[id];
 if(!row||!row.select.value)return null;
 const choice=availableNodes[row.part].find(n=>n.key===row.select.value);
 if(!choice)return null;
 const localOffset=row.offset.map(input=>Number(input.value));
 if(localOffset.some(n=>!Number.isFinite(n)||Math.abs(n)>3))return null;
 return {node:choice.node,localOffset,vecFactory:(x,y,z)=>new THREE.Vector3(x,y,z),path:choice.path};
}
function stopRecord(){
 if(!recording)return;
 recording=false;
 ui.record.textContent='重新開始記錄';
 ui.export.disabled=!(currentProbe&&currentProbe.frameCount);
 updateRecordButton();
}
function calibrationChanged(){
 stopRecord();
 ui.confirmed.checked=false;
 updateRecordButton();
 checkRows();
}
function updateRecordButton(){
 ui.record.disabled=!markersReady()||!ui.confirmed.checked||!renderer;
 ui.saveConfig.disabled=!markersReady();
}
function listNodes(root){
 const result=[];
 function walk(node,path){
  result.push({key:path.join('/'),path:[...path],node,
   label:(node.name||'(未命名)')+' · '+node.type+' · ['+(path.join('/')||'root')+']'});
  node.children.forEach((child,i)=>walk(child,[...path,i]));
 }
 walk(root,[]);
 return result;
}
function buildMarkerUI(){
 markerUI={};ui.markers.replaceChildren();
 for(const marker of V30_MARKERS){
  const div=document.createElement('div');div.className='markerRow';
  const head=document.createElement('div');head.className='markerName';
  const dot=document.createElement('i');dot.className='dot';dot.style.setProperty('--dot',marker.color);
  head.append(dot,document.createTextNode(marker.name));
  const select=document.createElement('select');select.setAttribute('aria-label',marker.name+' 對應的原版節點');
  select.append(new Option('請選擇真實節點（不自動猜）',''));
  for(const n of availableNodes[marker.part])select.append(new Option(n.label,n.key));
  select.addEventListener('change',calibrationChanged);
  const offsets=document.createElement('div');offsets.className='offsets';
  const inputs=[];
  ['X','Y','Z'].forEach(axis=>{
   const label=document.createElement('label');label.textContent=axis+' (m)';
   const input=document.createElement('input');input.type='number';input.value='0';input.step='.01';
   input.min='-3';input.max='3';input.addEventListener('change',calibrationChanged);
   label.append(input);offsets.append(label);inputs.push(input);
  });
  div.append(head,select,offsets);ui.markers.append(div);
  markerUI[marker.id]={select,offset:inputs,part:marker.part};
 }
 updateRecordButton();
}
function updateViz(){
 if(!scene)return;
 const markerPositions={};
 for(const marker of V30_MARKERS){
  const ref=selectedMarker(marker.id);
  const sphere=markerSpheres[marker.id];
  sphere.visible=!!ref;
  if(!ref)continue;
  const p=worldPoint(ref);sphere.position.copy(p);markerPositions[marker.id]=p;
 }
 for(const [a,b] of V30_PAIRS){
  const line=markerLines[a];
  line.visible=!!(markerPositions[a]&&markerPositions[b]);
  if(line.visible){
   line.geometry.setFromPoints([markerPositions[a],markerPositions[b]]);
  }
 }
 const stats=V30_PAIRS.map(([a,b,label])=>{
  if(!markerPositions[a]||!markerPositions[b])return null;
  return {label,mm:markerPositions[a].distanceTo(markerPositions[b])*1000,color:markerColors[a]};
 });
 ui.metrics.replaceChildren();
 for(const s of stats){
  const div=document.createElement('div');div.className='metric';
  if(!s){div.textContent='尚未選定節點';ui.metrics.append(div);continue}
  const small=document.createElement('span');small.textContent=s.label;
  const strong=document.createElement('strong');strong.textContent=s.mm.toFixed(1);
  strong.style.color=s.color;
  const units=document.createElement('span');units.textContent='即時距離 (mm)';
  div.append(small,strong,units);ui.metrics.append(div);
 }
}
function createScene(){
 try{
  const canvas=$('canvas');
  renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false,powerPreference:'high-performance'});
  if(!(renderer.getContext() instanceof WebGL2RenderingContext))
   throw new Error('此環境未提供 WebGL2，無法執行真實 3D 檢查');
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure=1.12;
  scene=new THREE.Scene();scene.background=new THREE.Color('#102530');
  camera=new THREE.PerspectiveCamera(45,1,.02,300);
  camera.position.set(3,2.2,4.3);
  controls=new OrbitControls(camera,canvas);
  controls.target.set(0,.8,0);controls.enableDamping=true;
  controls.minDistance=.15;controls.maxDistance=40;controls.maxPolarAngle=Math.PI*.93;
  scene.add(new THREE.HemisphereLight(0xcce4fc,0x35464e,2.25));
  const key=new THREE.DirectionalLight(0xfff3e2,2.8);
  key.position.set(3,7,5);scene.add(key);
  const fill=new THREE.DirectionalLight(0x9ccdea,1.15);
  fill.position.set(-4,3,-3);scene.add(fill);
  const grid=new THREE.GridHelper(25,50,0x649493,0x345059);
  grid.material.transparent=true;grid.material.opacity=.43;
  scene.add(grid);
  const axes=new THREE.AxesHelper(.8);scene.add(axes);
  stage=new THREE.Group();scene.add(stage);
  actorGroup=new THREE.Group();bikeGroup=new THREE.Group();
  stage.add(actorGroup,bikeGroup);
  for(const marker of V30_MARKERS){
   const mesh=new THREE.Mesh(new THREE.SphereGeometry(.029,12,8),
     new THREE.MeshBasicMaterial({color:marker.color,depthTest:false}));
   mesh.visible=false;mesh.renderOrder=10;markerSpheres[marker.id]=mesh;scene.add(mesh);
  }
  for(const [a,b] of V30_PAIRS){
   const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]),
      new THREE.LineBasicMaterial({color:markerColors[a],linewidth:2,depthTest:false}));
   line.renderOrder=9;line.visible=false;markerLines[a]=line;scene.add(line);
  }
  clock=new THREE.Clock();
  const observer=new ResizeObserver(resize);observer.observe($('viewport'));resize();
  renderer.setAnimationLoop(tick);
  ui.webglState.textContent='WebGL2 已啟動｜僅格線';
  checkRows();
 }catch(e){
  ui.webglState.textContent='WebGL2 無法啟動';
  ui.overlay.textContent='無法建立真實 WebGL2 畫面；不會以 2D 假圖冒充。';
  note(String(e.message||e),true);
  renderer=null;checkRows();
 }
}
function resize(){
 if(!renderer)return;
 const host=$('viewport'),w=host.clientWidth||800,h=host.clientHeight||480;
 renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();
}
function cameraPreset(x,y,z){
 if(!camera||!controls)return;
 let target=new THREE.Vector3(0,.85,0),r=4.0;
 if(loaded){
  const bounds=new THREE.Box3().setFromObject(stage);
  if(!bounds.isEmpty()){target=bounds.getCenter(new THREE.Vector3());r=Math.max(2.1,bounds.getSize(new THREE.Vector3()).length()*1.35)}
 }
 controls.target.copy(target);
 camera.position.set(target.x+x*r,target.y+y*r,target.z+z*r);
 camera.lookAt(target);controls.update();
}
function tick(){
 if(!renderer)return;
 const dt=Math.min(clock.getDelta(),.05);
 if(cycleAction&&mixer&&playing)mixer.update(dt*Number(ui.rate.value));
 if(loaded){
  stage.updateWorldMatrix(true,true);
  updateViz();
  if(recording&&currentProbe){
   const time=performance.now();
   if(time-lastSample>=80){
    try{
     currentProbe.captureFrame(Math.max(.0001,(time-recordStart)/1000),ui.phase.value);
     lastSample=time;ui.frames.textContent=currentProbe.frameCount+' 幀';
   }catch(e){stopRecord();note('採樣已停止：'+e.message,true)}
   }
  }
 }
 controls?.update();
 renderer.render(scene,camera);
}
function fitCamera(){cameraPreset(.7,.55,1)}
function clearModels(){
 stopRecord();
 for(const group of [actorGroup,bikeGroup]){
  while(group?.children.length)group.remove(group.children[0]);
 }
 mixer=null;cycleAction=null;loaded=null;
 availableNodes={actor:[],bike:[]};
 buildMarkerUI();ui.confirmed.checked=false;
 ui.play.disabled=true;ui.play.textContent='暫停 Cycle';playing=true;
 ui.overlay.textContent='未載入原版 GLB，目前僅有測試地板與座標格線。';
 checkRows();
}
function parseGLB(arrayBuffer){
 return new Promise((resolve,reject)=>glbLoader.parse(arrayBuffer,'',resolve,reject));
}
async function loadOriginals(){
 const af=ui.actorFile.files?.[0],bf=ui.bikeFile.files?.[0];
 if(!renderer)throw new Error('WebGL2 沒有啟動；不可載入成假 3D');
 if(!af||!bf)throw new Error('必須同時選取原人物與原自行車兩份 .glb');
 ui.load.disabled=true;ui.sourceState.textContent='核對檔案中…';
 try{
  // Do not leave old validated models visible if a new uploaded GLB fails.
  clearModels();
  const [ab,bb]=await Promise.all([af.arrayBuffer(),bf.arrayBuffer()]);
  validateGlbHeader(ab);validateGlbHeader(bb);
  const [as,bs]=await Promise.all([digestSha256(ab),digestSha256(bb)]);
  ensureOriginalSha({actor:as,bike:bs});
  ui.sourceState.textContent='來源正確，解碼中…';
  const [actor,bike]=await Promise.all([parseGLB(ab),parseGLB(bb)]);
  const cycle=actor.animations.find(c=>c.name==='Cycle');
  if(!cycle)throw new Error('人物 GLB 未找到真正 Cycle 動畫，禁止以靜態姿勢冒充');
  clearModels();
  actorGroup.add(actor.scene);bikeGroup.add(bike.scene);
  availableNodes.actor=listNodes(actor.scene);
  availableNodes.bike=listNodes(bike.scene);
  mixer=new THREE.AnimationMixer(actor.scene);
  cycleAction=mixer.clipAction(cycle);cycleAction.play();
  loaded={actor,bike,hashes:{actor:as,bike:bs}};
  buildMarkerUI();applyPose();fitCamera();
  ui.overlay.textContent='已載入 SHA256 相符的真模型；仍需人工確認手腳與車輪動作。';
  ui.sourceState.textContent='原版來源 SHA256 通過';
  note('原人物：'+availableNodes.actor.length+' 個可選節點；Cycle 片段 '+cycle.duration.toFixed(2)+' 秒。\n'+
       '原自行車：'+availableNodes.bike.length+' 個可選節點。\n'+
       '來源原始 SHA256 均一致；只在本機記憶體解碼，未修改原始檔。');
  ui.play.disabled=false;ui.saveConfig.disabled=true;
  checkRows();updateRecordButton();
 }finally{ui.load.disabled=false}
}
function applyPose(){
 if(!actorGroup)return;
 for(const id of ['px','py','pz','yaw']){
  if(!Number.isFinite(Number($(id).value)))throw new Error(id+' 必須為有效數值');
 }
 actorGroup.position.set(Number($('px').value),Number($('py').value),Number($('pz').value));
 actorGroup.rotation.set(0,THREE.MathUtils.degToRad(Number($('yaw').value)),0);
 calibrationChanged();
}
function bindings(){
 const b={};
 for(const m of V30_MARKERS){
  const marker=selectedMarker(m.id);
  if(!marker)throw new Error('尚未選取／校準：'+m.name);
  b[m.id]=marker;
 }
 return b;
}
function makeProbe(){
 return createContactProbe({renderer,markers:bindings(),browserName:navigator.userAgent,
  actorAnimation:'Cycle'});
}
function downloadJson(filename,data){
 const blob=new Blob([JSON.stringify(data,null,2)+'\n'],{type:'application/json'});
 const url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function markerConfig(){
 const b=bindings(),markers={};
 for(const m of V30_MARKERS){
  markers[m.id]={path:b[m.id].path,offset:b[m.id].localOffset,
    nodeName:b[m.id].node.name||''};
 }
 return {schema:'setouchi.v30.marker.config.v1',asset_sha256:{...V30_ASSETS},
  viewer:'isolated_v30_threejs_3d_pose_workbench',recordedAt:new Date().toISOString(),
  previewActorTransform:{
   position:[actorGroup.position.x,actorGroup.position.y,actorGroup.position.z],
   yawDeg:THREE.MathUtils.radToDeg(actorGroup.rotation.y)},
  markers,
  status:'MANUAL_CONTACT_CALIBRATION_NOT_GAMEPLAY_APPROVED'};
}
async function importConfig(file){
 if(!loaded)throw new Error('請先載入原始人車 GLB');
 const d=JSON.parse(await file.text());
 validateMarkerConfig(d);
 stopRecord();ui.confirmed.checked=false;
 for(const m of V30_MARKERS){
  const v=d.markers[m.id],row=markerUI[m.id];
  const match=availableNodes[row.part].find(c=>JSON.stringify(c.path)===JSON.stringify(v.path));
  if(!match||match.node.name!==(v.nodeName||''))throw new Error('節點樹不符：'+m.name);
  row.select.value=match.key;
  v.offset.forEach((n,i)=>row.offset[i].value=String(n));
 }
 if(d.previewActorTransform){
  const p=d.previewActorTransform.position;
  if(Array.isArray(p)&&p.length===3&&p.every(v=>Number.isFinite(v)&&Math.abs(v)<=3)){
   ['px','py','pz'].forEach((id,i)=>$(id).value=String(p[i]));
  }
  const yaw=d.previewActorTransform.yawDeg;
  if(Number.isFinite(yaw)&&Math.abs(yaw)<=180)$('yaw').value=String(yaw);
  applyPose();
 }
 checkRows();updateRecordButton();
 note('已匯入先前 marker 設定。請重新用眼睛核對 8 個球的位置，然後再勾選確認。');
}
function toggleRecord(){
 if(recording){stopRecord();note('已停止並保留本次座標擷取，可匯出 V29 相容 JSON');return}
 if(!loaded||!markersReady()||!ui.confirmed.checked)throw new Error('需原模型與人工核對的 8 個接觸點');
 currentProbe=makeProbe();
 recordStart=performance.now();lastSample=-Infinity;recording=true;ui.export.disabled=true;
 ui.record.textContent='停止記錄';ui.frames.textContent='0 幀';
 note('正在擷取真正 3D 工作臺的世界座標。此頁不是原 V06 主遊戲，仍需原遊戲實測。');
}
function exportCapture(){
 if(recording)stopRecord();
 if(!currentProbe||!currentProbe.frameCount)throw new Error('尚無擷取樣本');
 const d=currentProbe.exportData();
 d.environment.viewer_mode='isolated_v30_original_glb_pose_workbench';
 d.environment.original_v06_runtime_driving=false;
 d.environment.real_road_contact=false;
 d.environment.manual_marker_calibration_confirmed=true;
 d.environment.actor_preview_transform={
  position:[actorGroup.position.x,actorGroup.position.y,actorGroup.position.z],
  yawDeg:THREE.MathUtils.radToDeg(actorGroup.rotation.y)
 };
 d.note='True original GLBs SHA verified in V30 viewer; independent Cycle clip, no AvatarDriver/BicycleDriver gameplay verification.';
 const distances=Object.fromEntries(V30_PAIRS.map(([a,b,name])=>{
  const samples=d.frames.map(frame=>{
   const p=frame.markers[a],q=frame.markers[b];
   return Math.hypot(...p.map((v,i)=>v-q[i]))*1000;
  });
  return [name,nearestStats(samples)];
 }));
 d.preview_summary_mm=distances;
 downloadJson('Onomichi_V30_True_GLBS_Isolated_Pose_Capture.json',d);
 note('已匯出真 GLB 的獨立 3D 擷取證據。下一步請用 V29 Python 指定原 actor/bike GLB 再驗證 SHA，並進行真人視覺驗收。');
}
function wire(){
 ui.load.addEventListener('click',()=>loadOriginals().catch(e=>{note(String(e.message||e),true);ui.sourceState.textContent='核對未通過';checkRows()}));
 for(const input of [ui.actorFile,ui.bikeFile])input.addEventListener('change',()=>{
  if(loaded)clearModels();
  ui.sourceState.textContent='新來源待核對';
  note('新 GLB 尚未通過來源 SHA256，舊模型畫面已清除。');
 });
 for(const id of ['px','py','pz','yaw'])$(id).addEventListener('change',()=>{try{applyPose()}catch(e){note(e.message,true)}});
 $('resetPose').addEventListener('click',()=>{
  ['px','py','pz','yaw'].forEach(id=>$(id).value='0');
  applyPose();note('人物預覽位置已回正；原始檔未更動。');
 });
 for(const [id,x,y,z] of [['front',0,.3,1],['side',1,.3,0],['rear',0,.3,-1],['threeQuarter',.65,.5,.8]])
  $(id).addEventListener('click',()=>cameraPreset(x,y,z));
 $('fit').addEventListener('click',fitCamera);
 ui.play.addEventListener('click',()=>{
  playing=!playing;ui.play.textContent=playing?'暫停 Cycle':'繼續 Cycle';
 });
 ui.confirmed.addEventListener('change',updateRecordButton);
 ui.record.addEventListener('click',()=>{try{toggleRecord()}catch(e){note(e.message,true)}});
 ui.export.addEventListener('click',()=>{try{exportCapture()}catch(e){note(e.message,true)}});
 ui.saveConfig.addEventListener('click',()=>{try{
  downloadJson('Onomichi_V30_Contact_Marker_Config.json',markerConfig());
 }catch(e){note(e.message,true)}});
 ui.configFile.addEventListener('change',async ev=>{
  if(!ev.target.files?.[0])return;
  try{await importConfig(ev.target.files[0])}catch(e){note('校準設定拒絕：'+e.message,true)}
 });
}
wire();buildMarkerUI();createScene();
