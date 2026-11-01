#!/usr/bin/env python3
"""V010 localhost test: real browser WebCrypto + no external publishing."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import sys
root=Path(__file__).resolve().parent/'dist'
assert (root/'index.html').is_file()
port=int(sys.argv[1]) if len(sys.argv)>1 else 8770
server=ThreadingHTTPServer(('127.0.0.1',port),partial(SimpleHTTPRequestHandler,directory=str(root)))
print(f'V010 localhost (not public): http://127.0.0.1:{port}/')
try: server.serve_forever()
except KeyboardInterrupt:pass