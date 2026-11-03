from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
import argparse,webbrowser
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8130);p.add_argument('--no-browser',action='store_true');a=p.parse_args()
root=Path(__file__).resolve().parent/'web';url=f'http://127.0.0.1:{a.port}/'
server=ThreadingHTTPServer(('127.0.0.1',a.port),partial(SimpleHTTPRequestHandler,directory=str(root)))
print('Harbor Quality v02',url,flush=True)
if not a.no_browser:webbrowser.open(url)
try:server.serve_forever()
except KeyboardInterrupt:server.server_close()
