/**
 * Taipei Mech v7.3 - RAM-only performance telemetry for actual addon update.
 * IMPORTANT: update call cadence and CPU update duration are NOT GPU frame time.
 * Renderer.info counters describe previous renders; WebGPU timestamp/GPU FPS not measured.
 * No GPS, identifiers, timestamps, camera coords, network or persistent storage.
 */
const finite=Number.isFinite;
const clamp=(x,lo,hi)=>Math.min(hi,Math.max(lo,finite(x)?x:lo));
const percentile=(xs,q)=>{
  if(!xs.length)return null;
  const a=xs.slice().sort((x,y)=>x-y),idx=Math.ceil(q*a.length)-1;
  return Number(a[Math.max(0,Math.min(a.length-1,idx))].toFixed(2));
};
const zero=()=>({calls:null,triangles:null,geometries:null,textures:null});
export function createMechPerformanceV73({maxSamples=240}={}){
  if(!Number.isInteger(maxSamples)||maxSamples<30||maxSamples>900)throw new RangeError('maxSamples 30..900 required');
  const samples=[],history=[];let previous=NaN,frames=0,paused=0,invalid=0;
  let render=zero(),cinematic=null,profile='full',peakWrecks=0,peakShards=0,peakWallQueries=0;
  let latest={};
  function observe({nowMs,addonCpuMs,gameDtMs,renderer=null,effects=null,quality=null}={}){
    if(!finite(nowMs)||!finite(addonCpuMs)||addonCpuMs<0||addonCpuMs>2000){invalid++;return false;}
    const gap=finite(previous)?nowMs-previous:null;previous=nowMs;
    if(gap!==null && (gap<0||gap>250)){paused++;return false;}
    const item={cpuMs:clamp(addonCpuMs,0,2000),gapMs:gap===null?null:gap,gameDtMs:clamp(gameDtMs,0,1000)};
    samples.push(item);if(samples.length>maxSamples)samples.shift();frames++;
    if(renderer && typeof renderer==='object'){
      render={calls:finite(renderer.calls)?renderer.calls:null,
        triangles:finite(renderer.triangles)?renderer.triangles:null,
        geometries:finite(renderer.geometries)?renderer.geometries:null,
        textures:finite(renderer.textures)?renderer.textures:null};
    }
    if(effects && typeof effects==='object'){
      // Count only these explicitly whitelisted aggregated values.
      cinematic={activeWrecks:clamp(effects.activeWrecks,0,12),
        shards:clamp(effects.shards,0,250),parked:clamp(effects.parked,0,250),
        rings:clamp(effects.rings,0,12),peakWallQueries:clamp(effects.peakWallQueries,0,1000),
        wallContacts:clamp(effects.wallContacts,0,100000),
        unknownGroundFrames:clamp(effects.unknownGroundFrames,0,100000)};
      peakWrecks=Math.max(peakWrecks,cinematic.activeWrecks);
      peakShards=Math.max(peakShards,cinematic.shards);
      peakWallQueries=Math.max(peakWallQueries,cinematic.peakWallQueries);
    }
    if(['full','balanced','light'].includes(quality))profile=quality;
    return true;
  }
  function snapshot(){
    const cpu=samples.map(s=>s.cpuMs),gaps=samples.map(s=>s.gapMs).filter(finite);
    const p95=percentile(gaps,.95),cpu95=percentile(cpu,.95);
    const status=!gaps.length?'warming':p95>33.3?'cadence-slow':cpu95>12?'addon-heavy':'observed';
    const out={schema:'taipei-mecha-v73-performance',version:'7.3',quality:profile,
      frames,validSamples:samples.length,excludedTabOrLongStalls:paused,invalidSamples:invalid,
      updateCallGapMs:{p50:percentile(gaps,.5),p95},
      mechAddonCpuMs:{p50:percentile(cpu,.5),p95:cpu95},
      rendererLastReported:{...render},
      effects:cinematic?{...cinematic}:null,
      peaks:{activeWrecks:peakWrecks,shards:peakShards,wallQueries:peakWallQueries},
      status,limitations:[
        'This reports time BETWEEN addon update calls, not true rendered GPU FPS.',
        'Addon CPU time excludes the rest of the original Taipei frame and GPU render queue.',
        'renderer.info describes the renderer last available counters; no GPU timestamp queries.',
        'No real Windows WebGPU acceptance is implied by this report.'
      ]};
    return out;
  }
  function reset(){samples.length=0;history.length=0;previous=NaN;frames=paused=invalid=0;
    render=zero();cinematic=null;profile='full';peakWrecks=peakShards=peakWallQueries=0;}
  return {observe,snapshot,reset};
}
