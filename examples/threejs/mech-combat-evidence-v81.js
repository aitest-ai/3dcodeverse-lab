/**
 * Taipei Mecha v8.1 opt-in post-RenderPipeline evidence recorder.
 * A screenshot proves only a rendered image after a keyboard input, NOT weapon
 * firing, hit/miss, enemy HP, physical dodge, FPS, or genuine device compliance.
 * No uploads, storage, location, account ID, or automatic downloads.
 * Original v7.8 captureWebGPUCanvasV78 validates returned PNG pixels.
 */
export const ACTIONS_V81=Object.freeze(['beam_input','charge_input','blast_input','dodge_right_input','dodge_left_input']);

export function createCombatEvidenceV81({captureFrame,holdFrames=3,maxShots=5,cooldownMs=800,onUpdate=()=>{}}={}){
  if(typeof captureFrame!=='function')throw TypeError('Actual post-render PNG capture callback required');
  if(!Number.isInteger(holdFrames)||holdFrames<2||holdFrames>30||!Number.isInteger(maxShots)||maxShots<1||maxShots>12||!Number.isFinite(cooldownMs)||cooldownMs<0)throw RangeError('Unsafe recorder limits');
  let enabled=false,busy=false,pending=null,shots=[],errors=[],generation=0,enabledAt=null,lastTrigger=-Infinity;
  const notify=()=>{try{onUpdate(snapshot())}catch{}};
  function snapshot(){return {enabled,busy,waiting:!!pending,count:shots.length,maxShots,lastError:errors.at(-1)??null};}
  function toggle(next=!enabled){
    if(Boolean(next)===enabled)return snapshot();
    enabled=Boolean(next);generation++;
    if(!enabled){pending=null;busy=false;}
    else{enabledAt=null;lastTrigger=-Infinity;}
    notify();return snapshot();
  }
  function observeInput(action,clockMs,{gameActive=true,cameraLocked=false}={}){
    if(!enabled||!gameActive||cameraLocked||!ACTIONS_V81.includes(action)||!Number.isFinite(clockMs))return false;
    if(shots.length>=maxShots||busy||pending||clockMs-lastTrigger<cooldownMs)return false;
    if(enabledAt===null)enabledAt=clockMs;
    lastTrigger=clockMs;
    pending={action,elapsedMs:Math.max(0,Math.round(clockMs-enabledAt)),frames:0,token:generation};
    notify();return true;
  }
  function afterRender({gameActive=true,cameraLocked=false}={}){
    // A concurrent v7.8 camera-lock or mode change invalidates pending GPU readback.
    // Never accept a mixed-camera screenshot after another capture starts.
    if(cameraLocked||!gameActive){
      if(pending||busy){generation++;pending=null;busy=false;notify();}
      return;
    }
    if(!enabled||!pending||busy)return;
    const current=pending;
    if(++current.frames<holdFrames)return;
    pending=null;busy=true;
    // Run screenshot readback only after real city's renderPipeline.render().
    Promise.resolve().then(()=>captureFrame()).then(result=>{
      if(current.token!==generation)return;
      if(!result?.valid||result.blob?.type!=='image/png'||result.blob.size<2000)throw Error('Real PNG validation failed');
      const checks=result.checks??null;
      const item={index:shots.length+1,action:current.action,elapsedMs:current.elapsedMs,
        framesAfterInput:current.frames,blob:result.blob,
        imageChecks:checks};
      shots.push(item);
      if(shots.length>=maxShots)enabled=false; // hard safety cap; review remains accessible
    }).catch(e=>{
      if(current.token!==generation)return;
      errors.push(String(e?.message||e).slice(0,180));
    }).finally(()=>{
      if(current.token===generation){busy=false;notify();}
    });
  }
  function getFiles(){return shots.map(s=>({name:`Taipei_Mech_v81_input_${String(s.index).padStart(2,'0')}_${s.action}.png`,blob:s.blob}));}
  function report(){return {schema:'taipei-mecha-v81-input-frame-evidence',version:'8.1',
    captureKind:'post_real_render_after_keyboard_input',source:'v7.8 original RenderPipeline plus verified browser PNG',
    shots:shots.map(({blob,...safe})=>({...safe,bytes:blob.size})),errors:errors.slice(),
    limitations:[
      'These are key input observations. Weapon activation, damage, collisions and dodge success are NOT proven.',
      'Screenshots may lag input by multiple actual frames, depending on GPU queue.',
      'Only a genuine Windows WebGPU live playtest can verify visual appearance, animations and FPS.',
      'No raw PNG, camera position, GPS, absolute timestamp, device identity or location included in this JSON.'
    ]};}
  function clear(){generation++;enabled=false;pending=null;busy=false;shots=[];errors=[];enabledAt=null;lastTrigger=-Infinity;notify();}
  function dispose(){clear();}
  return {toggle,observeInput,afterRender,snapshot,getFiles,report,clear,dispose};
}

/** Input classification only. Deliberately does not claim an action succeeded. */
export function classifyCombatKeyV81(event){
  if(!event||event.repeat||event.ctrlKey||event.metaKey||event.altKey||event.target?.isContentEditable||['INPUT','TEXTAREA','SELECT'].includes(event.target?.tagName))return null;
  const key=String(event.key||'').toLowerCase();
  if(key==='f')return event.shiftKey?'charge_input':'beam_input';
  if(key==='g'&&!event.shiftKey)return 'blast_input';
  if(key==='v')return event.shiftKey?'dodge_left_input':'dodge_right_input';
  return null;
}
