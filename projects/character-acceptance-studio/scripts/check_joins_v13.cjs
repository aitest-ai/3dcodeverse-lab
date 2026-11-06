const fs=require('fs'),path=require('path'),assert=require('assert'),{chromium}=require('playwright');
const R=path.resolve(__dirname,'..');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage(),reports=[];
 await p.goto(process.env.STUDIO_URL||'http://localhost:8803/web-v13/');await p.waitForFunction(()=>window.library?.getState().ready,null,{timeout:90000});
 for(const key of ['horse-brown','horse-white']){
  await p.evaluate(k=>library.select(k),key);
  const result=await p.evaluate(async()=>{
   const {distance,speed}=await import('./transitions.js'),plan=library.plans()[0],T=plan.duration_s,h=1/240;library.sequence('trip');
   const velocity=[];
   for(const [name,t] of [['start/walk',3*T],['walk cycle reference',4*T],['walk/stop',5*T]]){
    const raw=[];for(const s of [t-h,t,t+h]){library.seek(s,false);raw.push(library.raw());}
    const maxima=[0,0];for(let j=0;j<2;j++)for(let m=0;m<raw[0][j].meshes.length;m++)for(let i=0;i<raw[0][j].meshes[m].vertices.length;i++){
     const a=raw[0][j].meshes[m].vertices[i],b=raw[1][j].meshes[m].vertices[i],c=raw[2][j].meshes[m].vertices[i];maxima[j]=Math.max(maxima[j],Math.hypot(...a.map((v,k)=>(2*b[k]-v-c[k])/h)));
    }velocity.push({join:name,one_sided_velocity_difference_m_s:maxima});
   }
   let rootError=0;const rootSamples=[];
   for(let i=0;i<=40;i++){const t=8*T*i/40;library.seek(t,false);const actual=library.motion();for(const r of actual)rootError=Math.max(rootError,Math.abs(r.position[2]-distance(t,plan)));rootSamples.push({time:t,expected_m:distance(t,plan),actual:actual.map(r=>r.position[2])});}
   const endpointSpeeds=[];
   for(const [a,c]of [[0,h],[8*T-h,8*T]]){library.seek(a,false);const x=library.motion();library.seek(c,false);const y=library.motion();endpointSpeeds.push(x.map((r,j)=>Math.abs(y[j].position[2]-r.position[2])/h));}
   return {root_max_error_m:rootError,root_samples:rootSamples,velocity,endpoint_speed_m_s:endpointSpeeds,analytic_endpoint_speed:[speed(0,plan),speed(8*T,plan)]};
  });
  console.log(key,JSON.stringify({...result,root_samples:undefined}));assert(result.root_max_error_m<.00002);assert(result.endpoint_speed_m_s.flat().every(v=>v<.001));
  const reference=result.velocity[1].one_sided_velocity_difference_m_s[1];for(const i of [0,2])assert(result.velocity[i].one_sided_velocity_difference_m_s[1]<=reference*1.2+.01,'transition velocity must be comparable to preserved walk-cycle join');
  reports.push({source_id:key,...result});
 }
 fs.writeFileSync(path.join(R,'evidence-v13/joins-and-root.json'),JSON.stringify({method:'Actual browser surface velocity finite differences at 1/240 s; compare transition joins to the preserved WalkWorld cycle join. This is kinematic continuity, not dynamic balance.',entries:reports},null,2));await b.close();console.log('V13_JOINS_AND_ROOT_PASS');
})().catch(e=>{console.error(e);process.exit(1)});
