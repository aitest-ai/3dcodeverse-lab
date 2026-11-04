"""Isolated v0.4 browser studio; v0.1 launch and assets remain unchanged."""
import argparse,functools,http.server,webbrowser
from scripts.restore_library_v04 import restore
restore()
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8771);p.add_argument('--bind',default='127.0.0.1');p.add_argument('--open',action='store_true');a=p.parse_args();root=Path(__file__).resolve().parent
class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):self.send_header('Cache-Control','no-cache');super().end_headers()
url=f'http://localhost:{a.port}/web-v04/';print('Studio v0.4:',url,flush=True)
if a.open:webbrowser.open(url)
http.server.ThreadingHTTPServer((a.bind,a.port),functools.partial(Handler,directory=str(root))).serve_forever()
