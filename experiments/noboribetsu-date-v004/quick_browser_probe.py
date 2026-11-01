import asyncio,json,time,hashlib
from pathlib import Path
from playwright.async_api import async_playwright
D=Path('/mnt/data/noboribetsu_v004_work/runtime/dist')
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader','--enable-webgl'])
  pg=await b.new_page(viewport={'width':900,'height':580})
  logs=[];req=[]
  pg.on('console',lambda m: logs.append(m.type+':'+m.text[:120]))
  pg.on('pageerror',lambda e:logs.append('ERROR:'+str(e)[:350]))
  async def route(r):
   url=r.request.url;name=url.split('https://date.local/')[-1].split('?')[0];f=(D/name).resolve()
   if f.is_relative_to(D) and f.is_file():
    req.append((name,f.stat().st_size))
    await r.fulfill(status=200,body=f.read_bytes(),headers={'access-control-allow-origin':'*','content-type':{'.js':'text/javascript','.css':'text/css','.json':'application/json'}.get(f.suffix,'application/octet-stream')})
   else:await r.fulfill(status=404,body='missing',headers={'access-control-allow-origin':'*'})
  await pg.route('https://date.local/**',route)
  j=json.loads((D/'scene_view.json').read_text());allowed={str(m['bytes']):m['sha256'] for m in j['models']};allowed.update({str(m['bytes']):m['sha256'] for m in j['extension']['models'].values()})
  html=(D/'index.html').read_text().replace('<head>','<head><base href="https://date.local/"><script>Object.defineProperty(window,"crypto",{configurable:true,value:{subtle:{digest:async(alg,buf)=>{const h=window.__hashes[String(buf.byteLength)];if(!h)throw Error("Unexpected digest length "+buf.byteLength);return Uint8Array.from(h.match(/../g).map(n=>parseInt(n,16))).buffer}}}});window.__hashes='+json.dumps(allowed)+';</script>',1)
  print('SET CONTENT',flush=True)
  await pg.set_content(html,wait_until='domcontentloaded',timeout=15000)
  print('SET CONTENT OK',flush=True)
  for t in [2,5,10,15]:
   await pg.wait_for_timeout((t-(0 if t==2 else {5:2,10:5,15:10}[t]))*1000)
   print('at',t,'loaded',await pg.locator('#scene').get_attribute('data-loaded'),'loader',await pg.locator('#loadText').inner_text(),'error',await pg.locator('#loadError').inner_text(),'req',len(req),'last',req[-4:],'console',logs[-6:],flush=True)
  await b.close()
asyncio.run(main())