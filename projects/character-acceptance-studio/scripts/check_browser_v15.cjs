const fs=require('fs'),path=require('path'),assert=require('assert'),{chromium}=require('playwright');
const R=path.resolve(__dirname,'..'),E=path.join(R,'evidence-v15');let browser;
(async()=>{
 browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await browser.newPage({viewport:{width:1400,height:1000}}),errors=[],entries=[];p.setDefaultTimeout(90000);p.on('pageerror',e=>errors.push(e.message));await p.goto(process.env.STUDIO_URL||'http://localhost:8808/web-v15/');await p.waitForFunction(()=>window.library?.getState().ready);
 for(const key of process.env.STUDIO_HORSE?[process.env.STUDIO_HORSE]:['horse-brown','horse-white']){
  await p.evaluate(k=>library.select(k),key);const ab=await p.evaluate(()=>library.getState());assert.equal(ab.slots.length,2);assert.deepStrictEqual(ab.slots.map(s=>s.clips.length),[18,21]);
  const results=[];
  for(const name of ['RestartWalk','WalkTurnLeft','WalkTurnRight','ControllerDemo']){
   await p.evaluate(async name=>{if(name==='ControllerDemo')await library.control.demo();else await library.chooseClip(name);library.seek(0,false);},name);
   const r=await p.evaluate(()=>{
    const D=library.getState().duration,N=Math.round(D*480),active={},events=[],stats={minimum_sole_m:Infinity,max_patch_drift_m:0,max_stance_height_error_m:0,minimum_support:4},states=[],boundaries=[];let previous=null;
    for(let n=0;n<=N;n++){
     const t=D*n/N;library.seek(t,false);const support=library.support()[0],feet=library.contacts()[0],q=library.control.state();
     if(q&&q.segmentStart!==previous){boundaries.push(q.segmentStart);previous=q.segmentStart;states.push({time:t,...q,root:library.motion()[0]});}
     stats.minimum_support=Math.min(stats.minimum_support,support.stance.length);
     for(const [k,f] of Object.entries(feet)){
      stats.minimum_sole_m=Math.min(stats.minimum_sole_m,f.minimum_y_m);
      if(!support.stance.includes(k)){delete active[k];continue;}
      stats.max_stance_height_error_m=Math.max(stats.max_stance_height_error_m,Math.abs(f.minimum_y_m-.003));
      if(!active[k]){active[k]={foot:k,start:t,end:t,patch:f.patch,drift:0};events.push(active[k]);}
      const a=active[k];a.end=t;
      for(let i=0;i<f.patch.length;i++)a.drift=Math.max(a.drift,Math.hypot(...a.patch[i].map((v,j)=>v-f.patch[i][j])));
      stats.max_patch_drift_m=Math.max(stats.max_patch_drift_m,a.drift);
     }
    }
    const seams=[];
    for(const t of boundaries.filter(x=>x>0&&x<D)){
     library.seek(t-1e-7,false);const a=library.raw()[0];library.seek(t,false);const b=library.raw()[0];let max=0;
     for(let m=0;m<a.meshes.length;m++)for(let i=0;i<a.meshes[m].vertices.length;i++)max=Math.max(max,Math.hypot(...a.meshes[m].vertices[i].map((v,j)=>v-b.meshes[m].vertices[i][j])));
     seams.push({time:t,maximum_surface_gap_m:max});
    }
    return {duration:D,sample_hz:480,samples:N+1,stats,events:events.map(({patch,...e})=>e),states,seams,end:library.control.state()};
   });results.push({name,...r});console.log(key,name,JSON.stringify(r.stats),'seam',Math.max(0,...r.seams.map(s=>s.maximum_surface_gap_m)));
   fs.writeFileSync(path.join(E,key+'-'+name+'.json'),JSON.stringify(r,null,2));
   assert(r.stats.minimum_sole_m>=0);assert(r.stats.minimum_support>=2);assert(r.stats.max_patch_drift_m<.001);assert(r.stats.max_stance_height_error_m<.0003);assert(r.seams.every(s=>s.maximum_surface_gap_m<.00005));
  }
  const cold=[];if(!process.env.STUDIO_SKIP_COLD){
   const id=key+'-locomotion-review',probes=JSON.parse(fs.readFileSync(path.join(R,'work/v15-cold',id+'.json')));let maximum=0;
   for(const probe of probes){await p.evaluate(n=>library.chooseClip(n),probe.clip);await p.evaluate(t=>library.seek(t,false),probe.time_s);const actual=await p.evaluate(ids=>library.region(ids)[0],Array.from({length:probe.body.length},(_,i)=>i));for(let i=0;i<actual.length;i++)maximum=Math.max(maximum,Math.hypot(...actual[i].map((x,k)=>x-probe.body[i][k])));}
   assert(maximum<.00003,'native/browser surface '+maximum);cold.push({id,maximum_m:maximum,probes:probes.length,vertices:probes[0].body.length});
  }
  // Hold/restart location, deterministic reverse seeking, and camera-independent measurements.
  await p.evaluate(()=>library.control.demo());const replay=await p.evaluate(()=>{library.seek(8.5,false);const held=library.motion()[0].position;library.seek(9,false);const restart=library.motion()[0].position;library.seek(20,false);const a=library.contacts();library.seek(1,false);library.seek(20,false);return {held,restart,a,b:library.contacts()};});assert.deepStrictEqual(replay.a,replay.b);assert(Math.hypot(...replay.held.map((v,i)=>v-replay.restart[i]))<1e-5);
  await p.uncheck('#follow');const unfollow=await p.evaluate(()=>library.contacts());for(const k of Object.keys(replay.a[0]))assert(Math.hypot(...unfollow[0][k].references.flat.map((v,i)=>v-replay.a[0][k].references.flat[i]))<1e-6);await p.check('#follow');
  // Stop during start; stop cancels queued left; go during stop waits for the stopped pose.
  await p.evaluate(()=>library.control.load([{time:0,command:'left'},{time:.1,command:'stop'},{time:4,command:'go'},{time:8,command:'stop'}],15));const control=await p.evaluate(()=>{const out=[];for(const t of [.2,3.6,6.99,7,10.5,14.1]){library.seek(t,false);out.push(library.control.state())}return out;});assert.equal(control[0].pending,null);assert.equal(control[1].clip,'StopWalk');assert.equal(control[2].clip,'StopWalk');assert.equal(control[3].clip,'RestartWalk');assert.equal(control[4].clip,'StopWalk');assert.equal(control[5].clip,'StandStopped');
  await p.evaluate(()=>library.control.load([{time:0,command:'left'},{time:4,command:'left'},{time:10,command:'stop'}],20));
  const turn=await p.evaluate(()=>{library.seek(3.5+10*28/24,false);return {state:library.control.state(),root:library.motion()[0]};});
  assert(Math.abs(turn.state.origin.yaw-Math.PI/6)<1e-9);assert(Math.abs(2*Math.atan2(turn.root.quaternion[1],turn.root.quaternion[3])-Math.PI/6)<1e-6);assert(turn.root.position[0]>2);assert(turn.state.clip==='StopWalk');
  await p.evaluate(()=>library.chooseClip('WalkTurnLeft'));const loop=await p.evaluate(()=>{library.seek(0,false,2);return library.motion()[0]});assert(Math.abs(loop.position[0]-turn.root.position[0])<1e-5);assert(Math.abs(loop.position[2]+1.866666666666667-turn.root.position[2])<1e-5);
  entries.push({key,sha256:ab.slots.map(s=>s.sha256),motions:results.map(({events,states,...r})=>r),cold,replay_exact:true,stop_restart_root_retained:true,stop_cancels_pending_turn:true,go_during_stop_waits:true,follow_invariant:true,successive_left_turns_30_degrees_actual_root:true,loop_se2_accumulation:true});
 }
 await p.setViewportSize({width:390,height:844});await p.screenshot({path:path.join(E,'viewport-390.png'),fullPage:true});const viewport=await p.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));assert(viewport.scroll<=viewport.width+1);assert.deepStrictEqual(errors,[]);
 fs.writeFileSync(path.join(E,'browser-diagnostics.json'),JSON.stringify({actual_browser:true,renderer:'Chromium SwiftShader; sampled skinning, not hardware performance',entries,viewport,errors,human_art:'not-tested',physical_mobile:'not-tested'},null,2));await browser.close();console.log('V15_BROWSER_PASS');
})().catch(async e=>{console.error(e);await browser?.close();process.exit(1)});
