"""Verify each ZIP member, reconstruct in an empty folder and load that folder in Chromium."""
import os,sys,json,zipfile,hashlib,subprocess,time,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliveries-v16';W=R/'work/v16-clean';W.mkdir(parents=True,exist_ok=False);receipt=json.loads((D/'receipt-v16.json').read_text());rows=[]
for row in receipt['deliveries']:
 p=D/row['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None;prefix='Character_Studio_0.16.0/';index=z.read(prefix+row['index']).decode().splitlines();assert len(index)==row['indexed_files'];names=set()
  for line in index:
   sha,name=line.split('  ',1);assert not Path(name).is_absolute() and '..' not in Path(name).parts;assert hashlib.sha256(z.read(prefix+name)).hexdigest()==sha;names.add(prefix+name)
  assert set(z.namelist())==names|{prefix+row['index']};z.extractall(W)
 rows.append(row)
clean=W/'Character_Studio_0.16.0';env=os.environ.copy();env['STUDIO_V16_OUT']=str(clean/'work/rebuild');blender=os.environ.get('BLENDER_BIN','blender');subprocess.run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/build_hands_v16.py'],cwd=clean,env=env,check=True)
rebuild=[]
for e in json.loads((clean/'library-v16/catalog.json').read_text())['entries']:
 if e['variant']!='corrected':continue
 p=clean/'work/rebuild'/e['asset_id']/e['version']/'model.glb';sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==e['model']['sha256'];rebuild.append({'id':e['id'],'sha256':sha,'byte_exact_glb_rebuild':True})
server=subprocess.Popen([sys.executable,'START_STUDIO_V16.py','--port','8811'],cwd=clean,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(40):
  try:urllib.request.urlopen('http://localhost:8811/web-v16/',timeout=2).close();break
  except OSError:time.sleep(.25)
 env=os.environ.copy();env['STUDIO_URL']='http://localhost:8811/web-v16/';env['SMOKE_OUT']=str(R/'evidence-v16/clean-browser.json');subprocess.run(['node','scripts/smoke_delivery_v16.cjs'],cwd=clean,env=env,check=True)
finally:server.terminate();server.wait(timeout=10)
result={'archives':rows,'rebuild':rebuild,'clean_browser':json.loads((R/'evidence-v16/clean-browser.json').read_text()),'art_approved':False};(R/'evidence-v16/delivery-smoke.json').write_text(json.dumps(result,indent=2)+'\n');(D/'delivery-smoke.json').write_text(json.dumps(result,indent=2)+'\n');print('V16_CLEAN_DELIVERY_PASS')
