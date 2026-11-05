#!/usr/bin/env python3
"""Offline localhost viewer; no CDN/model accounts/GPU service required."""
import argparse,http.server,functools,webbrowser
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8791);p.add_argument('--open',action='store_true');a=p.parse_args();root=Path(__file__).resolve().parent;url=f'http://localhost:{a.port}/web-v10/';print(url,flush=True)
server=http.server.ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root)))
if a.open:webbrowser.open(url)
try:server.serve_forever()
except KeyboardInterrupt:server.server_close()
