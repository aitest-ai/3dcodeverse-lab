import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
const $=id=>document.getElementById(id), stage=$('stage');
const labels={Idle:'待機',Walk:'走路',Run:'跑步',Start:'起步',Stop:'停步',TurnLeft:'左轉身',TurnRight:'右轉身',PoseTest:'原有短姿態測試',Turn:'來源軀幹擺動（非轉身）'};
let registry,entry,variants=[],playing=true,t=0,duration=1,loadEpoch=0,abort,frameCount=0,last=performance.now(),metricLast=last,recording=false;
const reviews=[],loader=new GLTFLoader(),camera=new THREE.PerspectiveCamera(35,1,.01,100);
async function assetFetch(url,options){
  const embedded=window.STUDIO_EMBED?.files[url];
  if(embedded){const bytes=Uint8Array.from(atob(embedded.base64),c=>c.charCodeAt(0));return new Response(bytes,{headers:{'Content-Type':embedded.mime,'Content-Length':String(bytes.length)}})}
  if(window.STUDIO_EMBED) return new Response('Embedded resource missing',{status:404});
  return fetch(url,options);
}
function resourceURL(url){const item=window.STUDIO_EMBED?.files[url];return item?'data:'+item.mime+';base64,'+item.base64:url}
let renderer,controls;
const scene=new THREE.Scene();scene.background=new THREE.Color('#dce2d8');
scene.add(new THREE.HemisphereLight(0xffffff,0x5b6a52,2.6));
for(const [x,y,z,p] of [[3,5,4,3],[-3,3,-3,1.8]]){const l=new THREE.DirectionalLight(0xfff4df,p);l.position.set(x,y,z);scene.add(l)}
const floor=new THREE.Mesh(new THREE.PlaneGeometry(200,200),new THREE.MeshStandardMaterial({color:0xd4dbce,roughness:.95}));floor.rotation.x=-Math.PI/2;floor.position.y=-.002;scene.add(floor);
const grid=new THREE.GridHelper(40,80,0x66795f,0xaab5a3);grid.position.y=-.001;scene.add(grid);
const origin=new THREE.AxesHelper(.25);origin.position.set(-.65,.002,0);scene.add(origin);
try{renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;stage.prepend(renderer.domElement);controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.minDistance=.2;controls.maxDistance=8;controls.target.set(0,.9,0)}catch(e){fail('無法啟動 WebGL：'+e.message)}
function fail(message){$('error').textContent=message+'\n可按「重新載入固定版本」重試。';$('error').hidden=false;$('load').hidden=true;}
function busy(text,value){$('load').hidden=false;$('loadText').textContent=text;$('progress').value=value;}
function dispose(root){root.traverse(o=>{o.geometry?.dispose();for(const m of (Array.isArray(o.material)?o.material:[o.material]))if(m){for(const v of Object.values(m))if(v?.isTexture)v.dispose();m.dispose()}})}
async function loadPinned(asset,signal,onprogress){
  if(!/^[a-f0-9]{64}$/.test(asset.sha256))throw Error('資產缺少有效 SHA-256，拒絕載入');
  const response=await assetFetch(asset.url,{signal,cache:'no-cache'});if(!response.ok)throw Error(`HTTP ${response.status}: ${asset.url}`);
  const chunks=[];let loaded=0;const total=asset.bytes,reader=response.body.getReader();
  while(true){const {value,done}=await reader.read();if(done)break;chunks.push(value);loaded+=value.length;onprogress(loaded,total)}
  if(loaded!==total)throw Error(`檔案長度不符：預期 ${total}，收到 ${loaded}`);
  const bytes=new Uint8Array(loaded);let offset=0;for(const c of chunks){bytes.set(c,offset);offset+=c.length}
  if(!crypto.subtle)throw Error('SHA-256 需要安全來源。請使用 localhost 或 HTTPS 開啟工作室');
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
  if(hash!==asset.sha256)throw Error(`SHA-256 不符，已攔截\n預期 ${asset.sha256}\n實際 ${hash}`);
  const result=await loader.parseAsync(bytes.buffer,new URL('.',new URL(asset.url,location.href)).href);
  return result;
}
async function reload(){
  if(!renderer)return;const epoch=++loadEpoch;abort?.abort();abort=new AbortController();playing=false;$('error').hidden=true;busy('載入鎖定資產…',0);
  for(const v of variants){scene.remove(v.root,v.helper);v.mixer.stopAllAction();v.mixer.uncacheRoot(v.root);v.helper.dispose();dispose(v.root)}variants=[];
  entry=registry.characters.find(c=>c.id===$('character').value);const compare=$('compare').checked;
  const which=compare?['source','candidate']:[$('revision').value];
  $('revision').disabled=compare;$('leftLabel').textContent=compare?'A · '+(entry.source.label||'原始來源'):which[0]==='source'?(entry.source.label||'原始來源'):'修正候選';$('rightLabel').hidden=!compare;
  const pending=[];
  try{
    for(let i=0;i<which.length;i++){
      const variant=which[i],asset=entry[variant];
      if(!asset)throw Error('此角色尚無該修正版；請切換原始來源');
      const gltf=await loadPinned(asset,abort.signal,(done,total)=>{if(epoch===loadEpoch)busy(`${entry.name} · ${variant==='source'?'來源':'候選'} ${(done/1048576).toFixed(2)} / ${(total/1048576).toFixed(2)} MiB`,(i+done/total)/which.length)});
      if(epoch!==loadEpoch){dispose(gltf.scene);for(const v of pending){v.helper.dispose();dispose(v.root)}return}
      const root=gltf.scene;root.updateMatrixWorld(true);const mixer=new THREE.AnimationMixer(root),helper=new THREE.SkeletonHelper(root);helper.visible=$('skeleton').checked;
      pending.push({root,mixer,helper,clips:gltf.animations,variant,asset,action:null});
    }
    if(epoch!==loadEpoch){for(const v of pending)dispose(v.root);return}
    variants=pending;for(const v of variants)scene.add(v.root,v.helper);
    const names=variants[variants.length-1].clips.map(c=>c.name);const previous=$('clip').value;$('clip').replaceChildren();
    for(const name of names){const o=new Option(`${labels[name]||name} · ${name}`,name);$('clip').add(o)}
    for(const name of ['Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight'])if(!names.includes(name)){const o=new Option(`${labels[name]} · 此版未提供`,name);o.disabled=true;$('clip').add(o)}
    $('clip').value=names.includes(previous)?previous:names.includes('Idle')?'Idle':names[0];
    if(!names.length)throw Error('此資產沒有動畫；不以 A 姿態冒充待機');
    $('identity').textContent=`${entry.id} / ${entry.version} · ${entry.profileSummary}`;
    $('profileLink').href=resourceURL(entry.profile);$('metadata').textContent=JSON.stringify({id:entry.id,version:entry.version,source:entry.provenance,license:entry.license,profile:entry.profile,assets:which.map(k=>({variant:k,...entry[k]})),warnings:entry.warnings},null,2);
    setClip();setView('full');$('load').hidden=true;playing=true;$('play').textContent='暫停';
    window.dispatchEvent(new CustomEvent('studio-ready'));
  }catch(e){for(const v of pending){if(!variants.includes(v))dispose(v.root)}if(epoch===loadEpoch&&e.name!=='AbortError')fail(e.message)}
}
function setClip(){
  t=0;const name=$('clip').value;let missing=false;
  for(const v of variants){v.mixer.stopAllAction();const clip=v.clips.find(c=>c.name===name);v.action=null;if(!clip){v.root.visible=false;missing=true;continue}v.root.visible=true;v.action=v.mixer.clipAction(clip);v.action.setLoop(THREE.LoopOnce,1);v.action.clampWhenFinished=true;v.action.play()}
  duration=variants.at(-1)?.action?.getClip().duration||1;$('timeline').max=duration;
  $('loop').checked=['Idle','Walk','Run','PoseTest'].includes(name);
  const meta=entry.motions?.[name];$('clipNote').textContent=(meta?.note||'來源原有片段；動態美術未核准。')+(missing?' A 來源無同名片段，僅顯示 B；不可視為修改前對照。':'');
  $('motionNote').textContent=`原地模式 · ${meta?.speed_mps?`配速參考 ${meta.speed_mps.toFixed(2)} m/s`:'沒有配速量測'} · 非即時 Foot IK。`;
  evaluate();
}
function evaluate(){for(const v of variants)if(v.action){v.action.reset();v.action.play();v.mixer.setTime(t);v.root.updateMatrixWorld(true)}$('timeline').value=t;$('time').textContent=`${t.toFixed(3)} / ${duration.toFixed(3)} s`;grid.position.z=$('groundMotion').checked?-((entry?.motions?.[$('clip').value]?.speed_mps||0)*t)%0.5:0;}
function setView(name){
  if(!controls)return;const h=entry?.height_m||1.7;
  const views={front:[[0,h*.53,3.8],[0,h*.5,0]],side:[[4.8,h*.53,0],[0,h*.5,0]],back:[[0,h*.53,-3.8],[0,h*.5,0]],full:[[2.45,h*.75,3.5],[0,h*.48,0]],elbow:[[1.2,h*.67,1.5],[.25,h*.66,0]],chest:[[0,h*.76,1.5],[0,h*.76,0]],hem:[[0,h*.53,1.5],[0,h*.53,0]],feet:[[.55,.25,1.35],[0,.1,0]]};
  const [pos,target]=views[name]||views.full;camera.position.fromArray(pos);controls.target.fromArray(target);controls.update();for(const b of document.querySelectorAll('[data-view]'))b.classList.toggle('active',b.dataset.view===name);
}
function draw(){
  if(!renderer)return;const w=stage.clientWidth,h=stage.clientHeight;const split=variants.length===2,panels=split?2:1;
  if(renderer.domElement.clientWidth!==w||renderer.domElement.clientHeight!==h||renderer.domElement.width!==Math.floor(w*renderer.getPixelRatio()))renderer.setSize(w,h,false);
  renderer.setScissorTest(true);camera.aspect=(w/panels)/h;camera.updateProjectionMatrix();
  for(let i=0;i<panels;i++){variants.forEach((v,j)=>{v.root.visible=!!v.action&&j===i;v.helper.visible=v.root.visible&&$('skeleton').checked});const x=Math.floor(i*w/panels),width=i===panels-1?w-x:Math.floor(w/panels);renderer.setViewport(x,0,width,h);renderer.setScissor(x,0,width,h);renderer.render(scene,camera)}
  renderer.setScissorTest(false);
}
function snapshot(){draw();return {schema_version:1,studio_version:registry.version,character_id:entry.id,version:entry.version,assets:variants.map(v=>({variant:v.variant,sha256:v.asset.sha256})),clip:$('clip').value,time_s:t,rate:Number($('rate').value),loop:$('loop').checked,grid_motion:$('groundMotion').checked,camera:{position:camera.position.toArray(),target:controls.target.toArray()},recorded_at:new Date().toISOString(),environment:{userAgent:navigator.userAgent,webgl:renderer.getContext().getParameter(renderer.getContext().VERSION)},art_approved:false,game_ready:false}}
function download(blob,name){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),2000)}
$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'暫停':'播放'};
for(const [id,sign] of [['prev',-1],['next',1]])$(id).onclick=()=>{playing=false;$('play').textContent='播放';t=Math.max(0,Math.min(duration,t+sign/(entry?.fps||30)));evaluate()};
$('timeline').oninput=()=>{playing=false;$('play').textContent='播放';t=Number($('timeline').value);evaluate()};
$('rate').oninput=()=>{$('rateValue').textContent=Number($('rate').value).toFixed(2)+'×'};
for(const id of ['character','revision','compare'])$(id).onchange=reload;$('retry').onclick=reload;$('clip').onchange=setClip;
for(const b of document.querySelectorAll('[data-view]'))b.onclick=()=>setView(b.dataset.view);
$('png').onclick=()=>{if(variants.length){draw();renderer.domElement.toBlob(b=>download(b,`${entry.id}-${$('clip').value}-${t.toFixed(3)}.png`))}};
$('record').onclick=()=>{
  if(recording||!variants.length)return;
  if(!window.MediaRecorder||!renderer.domElement.captureStream){$('recordStatus').textContent='此瀏覽器未提供錄影；可儲存逐格 PNG。';return}
  const mime=['video/webm;codecs=vp9','video/webm;codecs=vp8','video/webm'].find(s=>MediaRecorder.isTypeSupported(s));if(!mime){$('recordStatus').textContent='此瀏覽器不支援 WebM；請儲存逐格 PNG。';return}
  recording=true;$('record').disabled=true;const stream=renderer.domElement.captureStream(24),chunks=[],rec=new MediaRecorder(stream,{mimeType:mime});rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};rec.onstop=()=>{download(new Blob(chunks,{type:mime}),`${entry.id}-${$('clip').value}.webm`);stream.getTracks().forEach(t=>t.stop());recording=false;$('record').disabled=false;$('recordStatus').textContent='已儲存。軟體繪圖可能掉格，請搭配逐格檢查。'};rec.start();$('recordStatus').textContent='錄製中… 6 秒';setTimeout(()=>rec.stop(),6000)
};
$('addReview').onclick=()=>{if(!variants.length)return;const r={...snapshot(),region:$('region').value,verdict:$('verdict').value,notes:$('notes').value.trim()};reviews.push(r);$('reviewCount').textContent=`${reviews.length} 筆`;
  const li=document.createElement('li');li.textContent=`${r.character_id} / ${r.clip} @ ${r.time_s.toFixed(3)}s · ${r.region} · ${r.verdict}：${r.notes}`;$('reviewItems').append(li);$('notes').value=''};
$('exportReview').onclick=()=>download(new Blob([JSON.stringify({schema_version:1,observations:reviews,art_approved:false,game_ready:false},null,2)],{type:'application/json'}),'character-review.json');
window.studio={getState:()=>({ready:variants.length>0&&$('error').hidden&&$('load').hidden,loading:!$('load').hidden,error:$('error').hidden?null:$('error').textContent,character:entry?.id,clip:$('clip').value,time:t,duration,playing,variants:variants.map(v=>{const joints={};v.root.traverse(o=>{if(o.isBone&&/foot_|hand_|pelvis|spine_03/.test(o.name))joints[o.name]=o.getWorldPosition(new THREE.Vector3()).toArray()});return {variant:v.variant,clips:v.clips.map(c=>c.name),sha256:v.asset.sha256,joints}}),webgl:renderer?.getContext().getParameter(renderer.getContext().VERSION)}),seek(seconds){playing=false;t=Math.max(0,Math.min(duration,seconds));evaluate();draw()},view:setView,snapshot,draw};
function animate(now){requestAnimationFrame(animate);const dt=Math.min(.1,(now-last)/1000);last=now;if(playing&&variants.length&&$('error').hidden){t+=dt*Number($('rate').value);if(t>duration){if($('loop').checked)t%=duration;else{t=duration;playing=false;$('play').textContent='播放'}}evaluate()}draw();frameCount++;if(now-metricLast>1500){$('metrics').textContent=`${(frameCount*1000/(now-metricLast)).toFixed(1)} fps · ${renderer?.getContext().getParameter(renderer.getContext().VERSION)||'無 WebGL'} · 0.5 m 網格`;frameCount=0;metricLast=now}}
try{const response=await assetFetch('../assets/registry.json',{cache:'no-cache'});if(!response.ok)throw Error('無法讀取角色目錄');registry=await response.json();for(const c of registry.characters)$('character').add(new Option(`${c.name} · ${c.version}`,c.id));await reload();requestAnimationFrame(animate)}catch(e){fail(e.message)}
