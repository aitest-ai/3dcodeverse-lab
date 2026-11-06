const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const R=path.resolve(__dirname,'..'),E=path.join(R,'evidence-v13'),resume=process.env.STUDIO_V13_CAPTURE_RESUME==='1';let activeBrowser;
(async()=>{
 for(const d of ['frames','thumbnails'])fs.mkdirSync(path.join(E,d),{recursive:true});
 const b=activeBrowser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await b.newPage({viewport:{width:1400,height:1000}}),sequences=[],videos=[],errors=[];p.on('pageerror',e=>errors.push(e.message));
 p.setDefaultNavigationTimeout(90000);p.setDefaultTimeout(90000);await p.goto(process.env.STUDIO_URL||'http://localhost:8803/web-v13/');await p.waitForFunction(()=>window.library?.getState().ready,null,{timeout:90000});
 async function frames(key,clip,view,times){const rows=[];for(const [i,t] of times.entries()){const name=`${key}-${clip}-${view}-${i}.png`,render=!resume||!fs.existsSync(path.join(E,'frames',name));await p.evaluate(({t,view,render})=>{library.seek(t,false);library.view(['start-join','walk-cycle','stop-join'].includes(view)?'side':view);if(render)library.draw()},{t,view,render});if(render)await p.locator('#stage').screenshot({path:path.join(E,'frames',name)});rows.push({file:'frames/'+name,time_s:t,snapshot:await p.evaluate(()=>library.snapshot())});}sequences.push({key,clip,view,duration_s:await p.evaluate(()=>library.getState().duration),frames:rows});}
 for(const key of ['horse-brown','horse-white']){
  await p.evaluate(k=>library.select(k),key);
  for(const clip of ['StartWalk','StopWalk']){await p.evaluate(n=>library.chooseClip(n),clip);const D=await p.evaluate(()=>library.getState().duration);for(const view of ['front','side','back','frontFeet','backFeet','support'])await frames(key,clip,view,Array.from({length:13},(_,i)=>D*i/12));}
  await p.evaluate(()=>library.sequence('trip'));const D=await p.evaluate(()=>library.getState().duration),T=D/8;
  await frames(key,'FullSequence','side',Array.from({length:25},(_,i)=>D*i/24));
  for(const [join,t] of [['start-join',3*T],['walk-cycle',4*T],['stop-join',5*T]])await frames(key,'FullSequence',join,[t-1/60,t,t+1/60].map(x=>x));
  // Join rows retain the current side camera; their metadata identifies the exact timeline point.
  await p.evaluate(()=>{library.seek(.6);library.view('full');library.draw()});if(!resume||!fs.existsSync(path.join(E,'thumbnails',key+'-walk-transition-review.jpg')))await p.locator('#stage').screenshot({path:path.join(E,'thumbnails',key+'-walk-transition-review.jpg')});
  await p.evaluate(()=>{library.seek(0);library.view('side');library.draw()});await p.click('#play');const done=p.waitForEvent('download',{timeout:45000});await p.click('#record');const d=await done;await d.saveAs(path.join(E,key+'-browser.webm'));
  const end=await p.evaluate(()=>library.getState());videos.push({key,file:key+'-browser.webm',requested_wall_seconds:12,requested_capture_hz:24,final_timeline_seconds:end.time,full_sequence_endpoint_reached:Math.abs(end.time-D)<1e-5,actual_duration:'see ffprobe; software rendering may drop frames'});console.log('CAPTURED',key);fs.writeFileSync(path.join(R,'work/v13/capture-progress.json'),JSON.stringify({sequences,videos,errors}));
 }
 // Selecting again rebuilds cards after both thumbnails exist; no redundant navigation required.
 for(const key of ['horse-brown','horse-white']){await p.evaluate(k=>library.select(k),key);await p.evaluate(()=>{library.seek(.8);library.view('side');library.draw();window.scrollTo(0,0)});await p.screenshot({path:path.join(E,key+'-studio.png'),fullPage:true});}
 fs.writeFileSync(path.join(E,'frame-catalog.json'),JSON.stringify({version:'0.13.0',source:'Actual Chromium; A newly constructed uncorrected transition experiment / B same body blend and root ramp with world-anchor IK; source v12 did not contain transitions.',sequences},null,2));
 const count=sequences.reduce((n,s)=>n+s.frames.length,0);if(count!==380)throw Error('Unexpected frame count '+count);
 fs.writeFileSync(path.join(E,'capture-run.json'),JSON.stringify({errors,frames:count,videos,reused_earlier_frames_with_same_locked_models:resume,human_art:'not-tested',physical_mobile:'not-tested'},null,2));await b.close();if(errors.length)throw Error(errors.join('\n'));
})().catch(async e=>{console.error(e);try{await activeBrowser?.close()}catch{}process.exit(1)});
