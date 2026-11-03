"""Run the prebuilt game locally; no npm install or third-party Python packages needed."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
import argparse,webbrowser
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8123);p.add_argument('--no-browser',action='store_true');a=p.parse_args()
root=Path(__file__).resolve().parent/'dist'
if not (root/'index.html').exists():raise SystemExit('Missing dist. Run npm ci && npm run build first.')
url=f'http://127.0.0.1:{a.port}/'
server=ThreadingHTTPServer(('127.0.0.1',a.port),partial(SimpleHTTPRequestHandler,directory=str(root)))
print('Harbor Walk:',url,'\nCharacter atelier:',url+'viewer.html','\nPress Ctrl+C to stop.',flush=True)
if not a.no_browser:webbrowser.open(url)
try:server.serve_forever()
except KeyboardInterrupt:server.server_close()
