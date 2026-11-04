"""Serve this self-contained studio. Open http://localhost:8765/web/ ."""
import argparse, functools, http.server, webbrowser
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);p.add_argument('--bind',default='127.0.0.1');p.add_argument('--open',action='store_true');a=p.parse_args()
root=Path(__file__).resolve().parent
class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control','no-cache')
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()
url=f'http://localhost:{a.port}/web/'
print('Character Acceptance Studio:',url,flush=True)
if a.open:webbrowser.open(url)
http.server.ThreadingHTTPServer((a.bind,a.port),functools.partial(Handler,directory=str(root))).serve_forever()
