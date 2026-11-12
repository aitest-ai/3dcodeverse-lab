"""Verify actual archive members, offline rebuild in an empty folder and browser/MP4 playback."""
import os,sys,json,zipfile,hashlib,subprocess,time,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliveries-v19';W=R/'work/v19-clean';W.mkdir(parents=True,exist_ok=False);receipt=json.loads((D/'receipt-v19.json').read_text());rows=[]
for row in receipt['deliveries']:
 p=D/row['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None;prefix='Character_Studio_0.19.0/';index=z.read(prefix+row['index']).decode().splitlines();assert len(index)==row['indexed_files'];names=set()
  for line in index:
   sha,name=line.split('  ',1);assert not Path(name).is_absolute() and '..' not in Path(name).parts;assert hashlib.sha256(z.read(prefix+name)).hexdigest()==sha;names.add(prefix+name)
  assert set(z.namelist())==names|{prefix+row['index']};z.extractall(W)
 rows.append(row)
clean=W/'Character_Studio_0.19.0';env=os.environ.copy();env['STUDIO_V19_OUT']=str(clean/'work/rebuild');blender=os.environ.get('BLENDER_BIN','blender');subprocess.run([sys.executable,'scripts/bootstrap_inputs_v19.py'],cwd=clean,check=True);subprocess.run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/build_experiments_v19.py'],cwd=clean,env=env,check=True);rebuild=[]
for key in ['vivi','vita']:
 a=clean/'experiments-v19'/(key+'-rejected.glb');p=clean/'work/rebuild'/a.name;sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==hashlib.sha256(a.read_bytes()).hexdigest();rebuild.append({'key':key,'sha256':sha,'byte_exact_glb_rebuild':True,'status':'rejected'})
server=subprocess.Popen([sys.executable,'START_STUDIO_V19.py','--port','8820'],cwd=clean,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(40):
  try:urllib.request.urlopen('http://localhost:8820/web-v19/',timeout=2).close();break
  except OSError:time.sleep(.25)
 env=os.environ.copy();env['STUDIO_URL']='http://localhost:8820/web-v19/';env['SMOKE_OUT']=str(R/'evidence-v19/clean-browser.json');subprocess.run(['node','scripts/smoke_delivery_v19.cjs'],cwd=clean,env=env,check=True)
finally:server.terminate();server.wait(timeout=10)
result={'archives':rows,'rebuild':rebuild,'clean_browser':json.loads((R/'evidence-v19/clean-browser.json').read_text()),'art_approved':False};(R/'evidence-v19/delivery-smoke.json').write_text(json.dumps(result,indent=2)+'\n');(D/'delivery-smoke.json').write_text(json.dumps(result,indent=2)+'\n');print('V19_CLEAN_DELIVERY_PASS')
