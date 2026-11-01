/** Privacy-limited, bounded frame-update QA recorder; NO GPU FPS, GPS or user IDs. */
const finite = n => typeof n==='number'&&Number.isFinite(n);
const round=(n,k=2)=>finite(n)?Number(n.toFixed(k)):null;
const percentile=(a,p)=>a.length?a[Math.min(a.length-1,Math.floor((a.length-1)*p))]:null;
export function createMechQARecorder({maxSamples=3600,maxEvents=100}={}){
 if(!Number.isInteger(maxSamples)||maxSamples<30||maxSamples>10000)throw new RangeError('bad maxSamples');
 if(!Number.isInteger(maxEvents)||maxEvents<1||maxEvents>500)throw new RangeError('bad maxEvents');
 let samples=[],cursor=0,events=[],calls=0,lastWall=null,paused=0,blockedEdges=0,lastBlocked=false,activeFrames=0,missingGlb=0,worstFoot=0;
 let city=null,terrain=null,rendererInfo=null;
 const startedAt=new Date().toISOString();
 const ordered=()=>samples.length===maxSamples?samples.slice(cursor).concat(samples.slice(0,cursor)):samples.slice();
 function mark(kind,meta={}){
  if(typeof kind!=='string'||!/^[a-z0-9_-]{1,48}$/i.test(kind))return false;
  const evt={kind,frame:calls};
  if(kind==='dodge_start')evt.side=Number(meta.side)<0?-1:1;
  events.push(evt);if(events.length>maxEvents)events.shift();return true;
 }
 function observe({wallTimeMs,gameDtMs,mechCpuMs,active=false,blocked=false,footIK=null,city:cm=null,terrain:tr=null,renderer:ren=null,modelActive=false}={}){
  if(![wallTimeMs,gameDtMs,mechCpuMs].every(finite))return false;
  const gap=lastWall===null?null:wallTimeMs-lastWall;lastWall=wallTimeMs;calls++;
  if(active)activeFrames++;if(active&&!modelActive)missingGlb++;
  if(blocked&&!lastBlocked){blockedEdges++;mark('dodge_blocked');}lastBlocked=!!blocked;
  if(footIK?.legs)for(const leg of footIK.legs)if(finite(leg.positionError))worstFoot=Math.max(worstFoot,leg.positionError);
  if(cm)city={blockedChecks:cm.blockedChecks??null,checkedSteps:cm.checkedSteps??null,unsafeWorld:cm.unsafeWorld??null};
  if(tr)terrain={available:!!tr.available,enabled:!!tr.enabled,hits:tr.hits??null,samples:tr.samples??null,rejected:tr.rejected??null,coverage:tr.coverage??null};
  if(ren)rendererInfo={calls:finite(ren.calls)?ren.calls:null,triangles:finite(ren.triangles)?ren.triangles:null,
   geometries:finite(ren.geometries)?ren.geometries:null,textures:finite(ren.textures)?ren.textures:null};
  if(gap!==null&&(!finite(gap)||gap<=0||gap>250))paused++;
  const obs={gapMs:gap!==null&&gap>0&&gap<=250?round(gap,3):null,
   gameDtMs:round(gameDtMs,3),mechCpuMs:round(Math.max(0,mechCpuMs),3),active:!!active};
  if(samples.length<maxSamples)samples.push(obs);else samples[cursor]=obs;
  cursor=(cursor+1)%maxSamples;return true;
 }
 function snapshot(){
  const gaps=samples.map(s=>s.gapMs).filter(finite).sort((a,b)=>a-b);
  const cpu=samples.map(s=>s.mechCpuMs).filter(finite).sort((a,b)=>a-b);
  const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:null;
  const median=percentile(gaps,.5);
  return {schema:'taipei-mecha-qa-v58',windowSamples:samples.length,totalUpdateCalls:calls,updateCadenceHz:median?round(1000/median,1):null,
   updateGapMs:{median:round(median),p95:round(percentile(gaps,.95)),max:round(percentile(gaps,1)),mean:round(mean(gaps))},
   mechAddonCpuMs:{median:round(percentile(cpu,.5)),p95:round(percentile(cpu,.95)),max:round(percentile(cpu,1))},
   excludedPausedIntervals:paused,blockedDodgeEvents:blockedEdges,worstFootPositionError:round(worstFoot,4),activeFrames,
   glbUnavailableFrames:missingGlb,city,terrain,rendererInfo,
   limitations:'Update-call cadence, not confirmed GPU FPS; renderer.info may describe previous frame; no Windows visual acceptance implied.'};
 }
 function exportReport(){return {version:'v5.8',startedAt,exportedAt:new Date().toISOString(),
  privacy:'No world coordinates, browser identifiers, GPS, images or personal content.',
  diagnostics:snapshot(),events:events.slice(),recentSamples:ordered()};}
 function reset(){samples=[];cursor=0;events=[];calls=0;lastWall=null;paused=0;blockedEdges=0;lastBlocked=false;activeFrames=0;missingGlb=0;worstFoot=0;city=null;terrain=null;rendererInfo=null;}
 return {observe,mark,snapshot,exportReport,reset};
}
