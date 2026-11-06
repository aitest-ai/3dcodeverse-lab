const fs=require('fs'),path=require('path'),assert=require('assert'),{chromium}=require('playwright');
const R=path.resolve(__dirname,'..'),E=path.join(R,'evidence-v13');fs.mkdirSync(E,{recursive:true});
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await b.newPage({viewport:{width:1400,height:1000}}),errors=[],rows=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.env.STUDIO_URL||'http://localhost:8803/web-v13/');await p.waitForFunction(()=>window.library?.getState().ready,null,{timeout:90000});
 for(const key of process.env.STUDIO_HORSE?[process.env.STUDIO_HORSE]:['horse-brown','horse-white']){
  await p.evaluate(k=>library.select(k),key);await p.evaluate(()=>{library.sequence('trip');library.seek(0,false)});
  const state=await p.evaluate(()=>library.getState());assert.equal(state.slots.length,2);
  const result=await p.evaluate(()=>{
   const D=library.getState().duration,N=Math.round(D*240),samples=[],events=[{},{}],active=[{},{}],summaries=[0,1].map(()=>({minimum_sole_y_m:Infinity,maximum_stance_patch_drift_m:0,maximum_stance_center_drift_m:0,minimum_support:4,planned_sole_height_max_error_m:0,endpoint_support:[],outside_reference_samples:0,minimum_trunk_margin_m:Infinity}));
   for(let n=0;n<=N;n++){
    const t=D*n/N;library.seek(t,false);const feet=library.contacts(),support=library.support();
    samples.push({time_s:t,feet,support:support.map(r=>({stance:r.stance,reference:r.trunk_reference,margin:r.signed_margin_m}))});
    for(let j=0;j<2;j++){
     const s=summaries[j],r=support[j];s.minimum_support=Math.min(s.minimum_support,r.stance.length);s.outside_reference_samples+=r.signed_margin_m<0;s.minimum_trunk_margin_m=Math.min(s.minimum_trunk_margin_m,r.signed_margin_m);if(n===0||n===N)s.endpoint_support.push(r.stance.length);
     for(const [k,f]of Object.entries(feet[j])){
      s.minimum_sole_y_m=Math.min(s.minimum_sole_y_m,f.minimum_y_m);
      if(!r.stance.includes(k)){active[j][k]=null;continue;}
      s.planned_sole_height_max_error_m=Math.max(s.planned_sole_height_max_error_m,Math.abs(f.minimum_y_m-.003));
      if(!active[j][k]){const id=k+':'+n;active[j][k]=id;events[j][id]={key:k,start_time:t,end_time:t,patch:f.patch,center:f.references.flat,n:0,edge:0,drift:0};}
      const e=events[j][active[j][k]];e.n++;e.end_time=t;e.drift=Math.max(e.drift,Math.hypot(...e.center.map((x,i)=>x-f.references.flat[i])));
      for(let i=0;i<f.patch.length;i++)e.edge=Math.max(e.edge,Math.hypot(...e.patch[i].map((x,k)=>x-f.patch[i][k])));
      s.maximum_stance_patch_drift_m=Math.max(s.maximum_stance_patch_drift_m,e.edge);s.maximum_stance_center_drift_m=Math.max(s.maximum_stance_center_drift_m,e.drift);
     }
    }
   }
   return {sample_hz:240,sample_count:N+1,duration_s:D,summary:summaries,events:events.map(e=>Object.values(e).map(({patch,center,...r})=>r)),samples};
  });
  fs.writeFileSync(path.join(E,key+'-transition-contacts.json'),JSON.stringify(result));
  rows.push({source_id:key,model_sha256:state.slots.map(s=>s.sha256),sample_hz:240,sample_count:result.sample_count,summary:result.summary,events:result.events});console.log(key,JSON.stringify(result.summary));
  const a=result.summary[0],c=result.summary[1];assert(c.minimum_support>=2);assert.deepStrictEqual(c.endpoint_support,[4,4]);assert(c.minimum_sole_y_m>=0);assert(c.planned_sole_height_max_error_m<.0003);assert(c.maximum_stance_patch_drift_m<.001);assert(a.maximum_stance_patch_drift_m>.05,'uncorrected comparison must reveal actual drift');
  // Compare exact clip endpoints in a common world frame, separately from temporal sampling.
  const seams=await p.evaluate(async()=>{
   const out=[],T=library.plans()[0].duration_s,stride=library.plans()[0].candidate_stride_m;
   async function raw(clip,t,offset){await library.chooseClip(clip);library.seek(t,false);return library.raw().map(s=>({...s,meshes:s.meshes.map(m=>({...m,vertices:m.vertices.map(v=>[v[0],v[1],v[2]+offset])}))}));}
   for(const [label,ac,at,ao,bc,bt,bo] of [['ready/start','StandReady',0,0,'StartWalk',0,0],['start/walk','StartWalk',3*T,0,'WalkWorld',0,2*stride],['walk/stop','WalkWorld',T,0,'StopWalk',0,stride],['stop/stand','StopWalk',3*T,0,'StandStopped',0,2*stride]]){
    const A=await raw(ac,at,ao),B=await raw(bc,bt,bo),maxima=[0,0];for(let j=0;j<2;j++)for(let m=0;m<A[j].meshes.length;m++)for(let i=0;i<A[j].meshes[m].vertices.length;i++)maxima[j]=Math.max(maxima[j],Math.hypot(...A[j].meshes[m].vertices[i].map((v,k)=>v-B[j].meshes[m].vertices[i][k])));out.push({join:label,max_surface_gap_m:maxima});
   }return out;
  });
  console.log(key,'SEAMS',JSON.stringify(seams));assert(seams.every(s=>s.max_surface_gap_m[1]<.00005));rows.at(-1).seams=seams;
  // True cold Blender vs browser skinning, all body vertices, both comparison mothers.
  const cold=[];
  for(let j=0;j<2;j++){
   const id=state.slots[j].id.split('@')[0],probes=JSON.parse(fs.readFileSync(path.join(R,'work/v13-cold',id+'.json')));let maximum=0;
   for(const probe of probes){await p.evaluate(n=>library.chooseClip(n),probe.clip);await p.evaluate(t=>library.seek(t,false),probe.time_s);const actual=await p.evaluate(({ids,j})=>library.region(ids)[j],{ids:Array.from({length:probe.body.length},(_,i)=>i),j});for(let i=0;i<actual.length;i++)maximum=Math.max(maximum,Math.hypot(...actual[i].map((x,k)=>x-probe.body[i][k])));}
   assert(maximum<.00003,'cold surface '+maximum);cold.push({id,maximum_m:maximum,probes:probes.length});
  }rows.at(-1).cold_body=cold;
  await p.evaluate(()=>{library.sequence('trip');library.seek(7.2,false)});const before=await p.evaluate(()=>library.contacts());await p.uncheck('#follow');const after=await p.evaluate(()=>library.contacts());for(let j=0;j<2;j++)for(const k of Object.keys(before[j]))assert(Math.hypot(...before[j][k].references.flat.map((x,i)=>x-after[j][k].references.flat[i]))<1e-6);await p.check('#follow');
  const all=await p.evaluate(()=>library.getState().slots[1].clips);assert.equal(all.length,18);for(const clip of all){await p.evaluate(n=>library.chooseClip(n),clip);await p.evaluate(()=>library.seek(library.getState().duration*.5));}
  await p.click('#supportJump');assert((await p.evaluate(()=>library.getState())).sequence);await p.click('#stopJump');assert((await p.evaluate(()=>library.getState())).time>8);await p.uncheck('#supportOverlay');await p.check('#supportOverlay');
 }
 fs.writeFileSync(path.join(E,'transition-diagnostics.json'),JSON.stringify({scope:'Actual Chromium skinning at 240 Hz over a complete finite start/two-walk/stop sequence. Planned support is not ground force or true COM.',entries:rows},null,2));
 await p.setViewportSize({width:390,height:844});await p.screenshot({path:path.join(E,'viewport-390.png'),fullPage:true});const mobile=await p.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));assert(mobile.scroll<=mobile.width+1);
 fs.writeFileSync(path.join(E,'browser-controls.json'),JSON.stringify({actual_browser:true,all_18_clips:true,finite_sequence:true,follow_world_invariant:true,start_stop_jump_and_overlay:true,errors,viewport_390:mobile,physical_mobile:'not-tested',human_art:'not-tested'},null,2));assert.equal(errors.length,0);await b.close();console.log('V13_TRANSITION_BROWSER_PASS');
})().catch(e=>{console.error(e);process.exit(1)});
