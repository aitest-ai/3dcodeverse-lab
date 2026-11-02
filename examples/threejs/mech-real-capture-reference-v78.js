/**
 * Taipei Mech v7.8 portable WebGPU post-render capture scheduler.
 * This is a SMALLER independent reference for cross-AI reuse. The COMPLETE
 * Windows screenshot + camera freeze module is in the separate full ZIP.
 * Never claims a fake/Canvas2D image is a real game screenshot.
 */
export const PRESETS_V78=Object.freeze(['midday','golden','midnight']);
export function createPostRenderCaptureReferenceV78({getPreset,setPreset,readImage,holdFrames=4}={}){
  if([getPreset,setPreset,readImage].some(x=>typeof x!=='function'))
    throw new TypeError('Actual city preset and after-render PNG providers required');
  let phase='idle',previous=null,frames=0,index=0,photos=[],busy=false,run=0,error=null;
  function start(){
    if(phase==='warmup'||phase==='capturing')return false;
    const p=getPreset();
    if(!PRESETS_V78.includes(p)){phase='error';error='Original city preset unknown';return false;}
    previous=p;frames=0;index=0;photos=[];busy=false;error=null;phase='warmup';run++;
    setPreset(PRESETS_V78[0]);return true;
  }
  function restore(){if(previous){setPreset(previous);previous=null;}busy=false;}
  function afterRealRender(){
    if(phase!=='warmup'||busy)return;
    if(++frames<holdFrames)return;
    phase='capturing';busy=true;const currentRun=run,preset=PRESETS_V78[index];
    Promise.resolve().then(()=>readImage(preset)).then(image=>{
      if(currentRun!==run)return;
      if(!image||image.type!=='image/png'||image.size<2000||image.valid!==true)
        throw Error('Rejected blank or unverified WebGPU PNG');
      photos.push({preset,bytes:image.size});
      index++;frames=0;busy=false;
      if(index===PRESETS_V78.length){phase='complete';restore();}
      else{phase='warmup';setPreset(PRESETS_V78[index]);}
    }).catch(e=>{if(currentRun!==run)return;error=String(e.message||e);phase='error';restore();});
  }
  function cancel(){run++;if(['warmup','capturing'].includes(phase)){phase='cancelled';restore();}}
  function snapshot(){return {phase,photos:photos.slice(),error,originalPreset:previous};}
  return {start,afterRealRender,cancel,snapshot};
}
