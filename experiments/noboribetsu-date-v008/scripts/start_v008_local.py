#!/usr/bin/env python3
"""Serve V008 Runtime only. Local by default; no cloud deployment or upload."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import argparse
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8768);p.add_argument('--host',default='127.0.0.1',help='Use 0.0.0.0 only on a trusted private LAN')
a=p.parse_args();root=Path(__file__).resolve().parent/'dist'
if not (root/'v008_architecture_manifest.json').is_file():raise SystemExit('V008 assets missing: unzip entire runtime archive first')
h=partial(SimpleHTTPRequestHandler,directory=str(root))
with ThreadingHTTPServer((a.host,a.port),h) as server:
 print('V008 candidate local preview:',f'http://{a.host}:{a.port}/','Ctrl+C to stop',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:pass