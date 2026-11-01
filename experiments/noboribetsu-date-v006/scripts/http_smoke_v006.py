#!/usr/bin/env python3
"""Localhost HTTP resource smoke test; not an actual WebGL2 browser test."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
from urllib.request import urlopen
import hashlib,json,threading
root=Path(__file__).resolve().parent.parent
handler=partial(SimpleHTTPRequestHandler,directory=str(root/'dist'))
class Quiet(handler.func):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
t=threading.Thread(target=server.serve_forever,daemon=True);t.start();port=server.server_address[1]
tests=[]
try:
    for p in ('index.html','app.js','scene_view.json','v006_manifest.json','v006_collision.json','assets/v006_tail_road.glb','vendor/three.module.js'):
        with urlopen(f'http://127.0.0.1:{port}/{p}',timeout=15) as r:
            data=r.read();code=r.status
        expected=hashlib.sha256((root/'dist'/p).read_bytes()).hexdigest()
        tests.append({'path':p,'status':code,'bytes':len(data),'integrity':hashlib.sha256(data).hexdigest()==expected})
finally:server.shutdown();server.server_close()
status='PASS_HTTP_RESOURCES_ONLY' if all(t['status']==200 and t['integrity'] for t in tests) else 'FAIL'
result={'schema':'date-v006-local-http/1','status':status,'tests':tests,'browser_rendering':'NOT_TESTED'}
(root/'evidence/V006_http_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(status,len(tests),sum(q['bytes'] for q in tests))
if status=='FAIL':raise SystemExit(1)