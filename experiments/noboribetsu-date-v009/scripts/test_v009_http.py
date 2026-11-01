#!/usr/bin/env python3
"""Local Python HTTP resource check, not browser navigation or WebGL2 game test."""
from pathlib import Path
import json,hashlib,threading,functools,urllib.request
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
base=Path(__file__).parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
serve=functools.partial(Quiet,directory=str(base/'runtime/dist'))
http=ThreadingHTTPServer(('127.0.0.1',0),serve)
t=threading.Thread(target=http.serve_forever,daemon=True);t.start()
view=json.loads((base/'runtime/dist/scene_view.json').read_text())
resources=['index.html','style.css','app.js','qa.json','scene_view.json','v009_facade_manifest.json',
  'assets/v009_utsuroi_facade.glb','vendor/three.module.js','vendor/addons/loaders/GLTFLoader.js',
  'review_v009.html','evidence/utsuroi_side_V008.png','evidence/utsuroi_side_V009.png']
results=[]
try:
 for rel in resources:
  with urllib.request.urlopen(f'http://127.0.0.1:{http.server_port}/{rel}',timeout=6) as r:
   data=r.read();assert r.status==200
  local=(base/'runtime/dist'/rel).read_bytes()
  assert data==local
  results.append({'resource':rel,'http':200,'bytes':len(data)})
 assert view['version']=='V009-utsuroi-candidate-r1'
 assert 'review_v009.html' in (base/'runtime/dist/index.html').read_text()
finally:http.shutdown();http.server_close()
report={'schema':'date-v009-local-http/1','status':'PASS_LOCAL_RESOURCE_HTTP_ONLY',
 'resources_checked':len(results),'results':results,
 'webgl2_gpu_playback_verified':False,'private_cdns_verified':False,'android_verified':False}
(base/'evidence/http_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'resources_checked':len(results),'bytes':sum(x['bytes'] for x in results)},ensure_ascii=False))