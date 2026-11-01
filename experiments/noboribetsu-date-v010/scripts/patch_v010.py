"""Apply V010 input-time accounting without changing any geometry/model asset."""
from pathlib import Path
import sys
if len(sys.argv)!=2: raise SystemExit('Usage: python patch_v010.py /path/to/EXTRACTED_V009_RUNTIME (new copy, never original)')
R=Path(sys.argv[1]).resolve()/'dist'
if not R.is_dir():raise FileNotFoundError(R)
app=R/'app.js';inputjs=R/'input-events.js';index=R/'index.html';qa=R/'qa.json'
s=app.read_text()
def swap(old,new,label):
 global s
 assert s.count(old)==1,(label,s.count(old))
 s=s.replace(old,new)
# Preserve original behavior at high FPS; fix misses at sub-1fps software rendering.
swap('let metricFrames=[];','''let metricFrames=[];
// V010: account for elapsed motion time before input changes, even when
// SwiftShader stalls requestAnimationFrame. Keep collision steps <= 0.1 s.
let lastMotionMs=performance.now();
function advanceMotionTo(now){
  if(!Number.isFinite(now))return;
  const elapsed=Math.max(0,Math.min(2.0,(now-lastMotionMs)/1000));
  lastMotionMs=now;
  if(!session?.canControl||document.hidden)return;
  let remaining=elapsed;
  for(let i=0;i<20&&remaining>1e-6;i++){
    const dt=Math.min(0.1,remaining);
    session.advance(dt);
    remaining-=dt;
  }
  // Keep visible position status current even when rendering is blocked.
  updateCamera();updateStatus();
}
''','motion function')
swap('''  if(session){if(!document.hidden)session.advance(dt);updateCamera();}''','''  if(session){advanceMotionTo(t);updateCamera();}''','replace frame advance')
swap('''  getSession:()=>session,onHome:()=>place(false),onChange:()=>{updateCamera();updateStatus();}''','''  getSession:()=>session,onHome:()=>place(false),onBeforeInputChange:()=>advanceMotionTo(performance.now()),onChange:()=>{updateCamera();updateStatus();}''','flush handler')
swap('''  if(!session||!renderReady)return;inputEvents.cancel();session.start();''','''  if(!session||!renderReady)return;inputEvents.cancel();session.start();lastMotionMs=performance.now();''','start clock reset')
swap("version:'V009-utsuroi-candidate-r1',boot_ms:","version:'V010-controls-candidate-r1',asset_version:'V009-utsuroi-candidate-r1',boot_ms:",'metrics version')
swap("dataset,{position:[position.x,position.y,position.z].map(v=>v.toFixed(3)).join(','),heading:heading.toFixed(6),pitch:pitch.toFixed(6),stage,fov:String(session.fov),version:'V009-utsuroi-candidate-r1'}", "dataset,{position:[position.x,position.y,position.z].map(v=>v.toFixed(3)).join(','),heading:heading.toFixed(6),pitch:pitch.toFixed(6),stage,fov:String(session.fov),version:'V010-controls-candidate-r1'}", 'dataset version')
swap("$('modeLabel').textContent='第一人稱 · '+stage+' 場景 · V009 變裝攝影館側牆精修'", "$('modeLabel').textContent='第一人稱 · '+stage+' 場景 · V010 低幀率移動修正'",'mode label')
swap("a.download='Noboribetsu_Date_V009_browser_diagnostics.json'", "a.download='Noboribetsu_Date_V010_browser_diagnostics.json'",'download label')
swap("'完整 B 場景與 V009 側牆已驗證；舊外觀仍保存但不重複下載，A 按需下載'", "'完整 B 場景與 V009 外觀已載入；V010 低幀率移動修正已啟用，A 按需下載'",'load label')
app.write_text(s)
si=inputjs.read_text()
old='getSession,onHome=()=>{},onChange=()=>{}'
assert si.count(old)==1
si=si.replace(old,'getSession,onHome=()=>{},onBeforeInputChange=()=>{},onChange=()=>{}')
# Must account for input state BEFORE changing key set.
si=si.replace("      e.preventDefault();const fresh=s.input.keyDown(e.code);", "      onBeforeInputChange();e.preventDefault();const fresh=s.input.keyDown(e.code);")
old="  bind(windowTarget,'keyup',e=>session()?.input.keyUp(e.code));"
new="  bind(windowTarget,'keyup',e=>{if(WALK_KEYS.includes(e.code))onBeforeInputChange();session()?.input.keyUp(e.code);});"
assert old in si;si=si.replace(old,new)
old='''    const s=session();if(s){
      const a=s.input.stickPointer,b=s.input.lookPointer?.id;s.cancel();'''
new='''    const s=session();if(s){
      onBeforeInputChange();
      const a=s.input.stickPointer,b=s.input.lookPointer?.id;s.cancel();'''
assert old in si;si=si.replace(old,new)
old='''    const s=session();if(!s)return;
    const stickOwner=s.input.stickPointer===id,lookOwner=s.input.lookPointer?.id===id;
    s.input.release(id);'''
new='''    const s=session();if(!s)return;
    const stickOwner=s.input.stickPointer===id,lookOwner=s.input.lookPointer?.id===id;
    if(stickOwner)onBeforeInputChange();
    s.input.release(id);'''
assert old in si;si=si.replace(old,new)
old='''    session()?.input.moveStick(e.pointerId,e.clientX-r.left-r.width/2,e.clientY-r.top-r.height/2,47);paintStick();'''
new='''    onBeforeInputChange();session()?.input.moveStick(e.pointerId,e.clientX-r.left-r.width/2,e.clientY-r.top-r.height/2,47);paintStick();'''
assert old in si;si=si.replace(old,new)
inputjs.write_text(si)
i=index.read_text()
for a,b in [('V009 變裝攝影館側牆精修候選','V010 低幀率移動修正候選（沿用 V009 外觀）'),('V009 變裝攝影館側牆精修候選 R1','V010 操控修正候選 R1'),('V009 候選｜231.6 m','V010 候選｜231.6 m')]:
 i=i.replace(a,b)
index.write_text(i)
import json
v=json.loads(qa.read_text());v.update({'runtime_patch':'V010-motion-candidate-r1','render_model_assets':'unchanged V009','change_scope':'only motion time accumulation and input flush for low FPS; no model/collision/route edits','webgl2_swiftshader_test':'requires isolated Xvfb plus browser acceptance; does NOT establish Android or private host acceptance'})
qa.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print('Patched',R)