#!/usr/bin/env python3
"""Serve V011 over localhost for real WebCrypto and normal browser navigation.
Run `python start_v011_local.py` in the Runtime folder, then open printed URL.
"""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import argparse,functools
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);a=p.parse_args()
root=Path(__file__).resolve().parent/'dist'
if not (root/'index.html').is_file():raise FileNotFoundError(root)
handler=functools.partial(SimpleHTTPRequestHandler,directory=str(root))
server=ThreadingHTTPServer(('127.0.0.1',a.port),handler)
print(f'Open http://127.0.0.1:{a.port}/index.html (localhost secure context supports WebCrypto). Ctrl+C to stop.',flush=True)
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:server.server_close()