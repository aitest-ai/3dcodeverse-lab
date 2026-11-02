#!/usr/bin/env python3
"""Read-only verification + extraction of the frozen V017 runtime for V018 QA.

Place V017 Runtime ZIP in this same directory, or pass its path as argv[1].
The script will refuse nonempty `base/` and never modify the original ZIP.
"""
from pathlib import Path
import hashlib,sys,zipfile
ROOT=Path(__file__).resolve().parent
SRC=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'Noboribetsu_Date_V017_R1_Runtime.zip'
DEST=ROOT/'base'
EXPECTED='eb6ceb13d51b813b8111070cd13eadf36b13fb9ff246964519e6118892458866'
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(2**20),b''):h.update(chunk)
 return h.hexdigest()
if not SRC.is_file() or digest(SRC)!=EXPECTED:raise SystemExit('V017 Runtime SHA-256 mismatch / missing: do not continue')
if DEST.exists() and list(DEST.iterdir()):raise SystemExit('base/ is not empty; refusing to overwrite')
with zipfile.ZipFile(SRC) as z:
 if z.testzip():raise SystemExit('V017 ZIP CRC failed')
 names=z.namelist()
 if len(names)!=115 or any(n.startswith('/') or '..' in Path(n).parts for n in names):raise SystemExit('V017 archive structure invalid')
 DEST.mkdir(exist_ok=True)
 z.extractall(DEST)
print('PASS: original V017 Runtime verified and extracted without modifications (115 files).')