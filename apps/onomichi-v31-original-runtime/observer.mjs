/**
 * V31 source-only observer. Attaches UI to a *cloned* V28 game index.
 * Never patches AvatarDriver, BicycleDriver, scene, world, routes or colliders.
 */
const scriptUrl=new URL(import.meta.url);
if(!document.getElementById('onomichi-v31-observer')){
 const host=document.createElement('section');
 host.id='onomichi-v31-observer';
 host.setAttribute('aria-label','瀨戶內 V31 原版遊玩驗收');
 const root=host.attachShadow({mode:'open'});
 const response=await fetch(new URL('./observer_ui.html',scriptUrl),{credentials:'same-origin'});
 if(!response.ok)throw Error('V31 overlay template unavailable');
 root.innerHTML=await response.text(); // bundled static local HTML; never dynamic user content
 document.body.append(host);
 const $=id=>root.getElementById(id);
 const state={recording:false,events:[],dropped:0,startPerf:null,startedAt:null,endedAt:null,
  audit:null,rafTimes:[],observerFps:null,errorCount:0};
 const allowedCodes=new Set(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft',
  'ArrowRight','Space','ShiftLeft','ShiftRight','Escape','KeyE','KeyF','KeyC','KeyV',
  'Digit1','Digit2','Digit3']);
 const manualIds=['walk','cycle','turn','camera','ferry','pose'];
 const isOwn=e=>typeof e.composedPath==='function'&&e.composedPath().includes(host);
 const typing=node=>!!node?.closest?.('input,textarea,select,[contenteditable=true]');
 const MAX_EVENTS=5000;
 function push(type,details={}){
  if(!state.recording)return;
  if(state.events.length>=MAX_EVENTS){state.dropped++;return}
  state.events.push({at_ms:Math.round(performance.now()-state.startPerf),type,...details});
  $('count').textContent=String(state.events.length);
 }
 function safeId(str){
  const s=String(str||'');
  return s.length<=60&&/^[A-Za-z0-9_-]*$/.test(s)?s:'';
 }
 function problem(kind){state.errorCount++;push('runtime_problem',{kind})}
 window.addEventListener('keydown',e=>{
  if(!isOwn(e)&&!typing(e.target)&&allowedCodes.has(e.code))
   push('key_down',{code:e.code,repeat:!!e.repeat});
 },{capture:true,passive:true});
 window.addEventListener('keyup',e=>{
  if(!isOwn(e)&&!typing(e.target)&&allowedCodes.has(e.code))
   push('key_up',{code:e.code});
 },{capture:true,passive:true});
 for(const kind of ['pointerdown','pointerup']){
  window.addEventListener(kind,e=>{
   if(!isOwn(e))push(kind,{pointer_type:['mouse','touch','pen'].includes(e.pointerType)?e.pointerType:'unknown'});
  },{capture:true,passive:true});
 }
 window.addEventListener('click',e=>{
  if(isOwn(e)||typing(e.target))return;
  const b=e.target?.closest?.('button,[role="button"]');
  if(b)push('game_button',{id:safeId(b.id)});
 },{capture:true,passive:true});
 window.addEventListener('error',e=>{
  // Only a category: do not capture file URLs, messages or any personal data.
  const tag=e.target?.tagName;
  problem(tag?'asset_'+String(tag).toLowerCase():'javascript_error');
 },true);
 window.addEventListener('unhandledrejection',()=>problem('promise_rejection'));
 document.addEventListener('webglcontextlost',()=>problem('webgl_context_lost'),true);
 document.addEventListener('visibilitychange',()=>push('visibility_change',{visible:!document.hidden}));
 function stop(){
  if(!state.recording)return;
  state.recording=false;state.endedAt=new Date().toISOString();
  $('start').disabled=false;$('stop').disabled=true;$('save').disabled=state.events.length===0;
  $('warning').textContent='已停止。事件不等於遊戲功能通過，請搭配實際畫面與人工觀察。';
 }
 function start(){
  if(state.recording)return;
  state.recording=true;state.events=[];state.dropped=0;state.errorCount=0;
  state.startPerf=performance.now();state.startedAt=new Date().toISOString();state.endedAt=null;
  $('count').textContent='0';
  $('start').disabled=true;$('stop').disabled=false;$('save').disabled=true;
  $('warning').textContent='正在記錄操作類型（不記輸入文字或滑鼠座標）。';
 }
 function reset(){
  stop();state.events=[];state.dropped=0;state.startPerf=null;state.startedAt=null;
  state.endedAt=null;state.errorCount=0;
  $('save').disabled=true;$('count').textContent='0';
  root.querySelectorAll('input[data-manual]').forEach(el=>el.checked=false);
 }
 function report(){
  const manuallyMarked=Object.fromEntries(manualIds.map(id=>
    [id,root.querySelector('input[data-manual="'+id+'"]')?.checked===true]));
  const real=state.audit?.status==='V28_ORIGINAL_ARCHIVE_AND_CORE_SHA_VERIFIED' &&
             state.audit?.core_hashes_verified===true;
  return {
   schema:'setouchi.v31.original_runtime_playtest.v1',
   version:'V31',
   status:real?'ORIGINAL_SOURCE_VERIFIED_INPUT_OBSERVATION_MANUAL_REVIEW':
                'SYNTHETIC_OR_UNVERIFIED_SOURCE_NOT_GAMEPLAY_APPROVED',
   provenance:{
    archive_sha256:state.audit?.original_v28_archive_sha256||null,
    source_status:state.audit?.status||'unknown',
    protected_source_hashes_verified:real,
    original_game_core_changed:state.audit?.original_game_core_changed===true
   },
   capture:{
    started_at_utc:state.startedAt,ended_at_utc:state.endedAt,
    canvas_count:document.querySelectorAll('canvas').length,
    viewport:{width:window.innerWidth,height:window.innerHeight,dpr:window.devicePixelRatio||1},
    browser_user_agent:navigator.userAgent,
    observer_raf_fps_not_game_fps:state.observerFps,
    recorded_event_count:state.events.length,dropped_after_cap:state.dropped,
    reported_runtime_problem_count:state.errorCount,
    codes_only:true,full_text_keys_collected:false,
    pointer_coordinates_collected:false,game_driver_internals_instrumented:false,
    events:state.events.slice()
   },
   human_checklist_self_reported_only:manuallyMarked,
   verified_by_automated_gameplay:false,
   original_V06_driver_internal_states_verified:false,
   real_rider_hand_pedal_contact_verified:false,
   road_width_or_bicycle_rights_verified:false,
   real_collision_verified:false,
   android_realplay_verified:false,
   original_site_modified:false,
   privacy:'Local-only JSON download; GPS and pointer coordinates never captured.'
  };
 }
 function save(){
  if(state.recording)stop();
  if(!state.events.length)return;
  const url=URL.createObjectURL(new Blob([JSON.stringify(report(),null,2)+'\n'],
   {type:'application/json'}));
  const link=document.createElement('a');
  link.href=url;link.download='Onomichi_V31_Original_Runtime_Playtest_Report.json';
  document.body.append(link);link.click();link.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
 }
 $('start').addEventListener('click',start);$('stop').addEventListener('click',stop);
 $('reset').addEventListener('click',reset);$('save').addEventListener('click',save);
 $('toggle').addEventListener('click',()=>{
  const expanded=!$('panel').classList.toggle('hidden');
  $('toggle').textContent=expanded?'縮小':'展開';
  $('toggle').setAttribute('aria-expanded',String(expanded));
 });
 function raf(now){
  state.rafTimes.push(now);
  while(state.rafTimes.length&&now-state.rafTimes[0]>1000)state.rafTimes.shift();
  if(state.rafTimes.length>1)
   state.observerFps=Math.round((state.rafTimes.length-1)*1000/
     Math.max(1,now-state.rafTimes[0]));
  requestAnimationFrame(raf);
 }
 requestAnimationFrame(raf);
 setInterval(()=>{
  $('fps').textContent=String(state.observerFps??'—');
  $('canvases').textContent=String(document.querySelectorAll('canvas').length);
  $('viewport').textContent=window.innerWidth+'×'+window.innerHeight;
 },1000);
 fetch(new URL('./audit.json',scriptUrl),{cache:'no-store',credentials:'same-origin'})
  .then(r=>{if(!r.ok)throw Error('missing audit');return r.json()})
  .then(audit=>{
   if(audit.schema!=='setouchi.v31.runtime.audit.v1')throw Error('invalid audit');
   state.audit=audit;
   $('source').textContent=audit.status==='V28_ORIGINAL_ARCHIVE_AND_CORE_SHA_VERIFIED'&&
    audit.core_hashes_verified===true
    ?'原 V28 ZIP 與 12 個核心檔 SHA 已核對；操作功能仍需實測'
    :'合成／未知來源：不可宣稱原版騎乘已驗收';
  })
  .catch(()=>{$('source').textContent='缺少有效 V31 來源驗證；不可宣稱原版驗收'});
 Object.defineProperty(window,'__onomichiV31Observer',{
  configurable:false,writable:false,
  value:Object.freeze({status:()=>({recording:state.recording,count:state.events.length}),report})
 });
}
