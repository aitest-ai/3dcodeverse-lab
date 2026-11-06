"""Extract actual ZIPs, verify every hash, rebuild independently and exercise the shipped browser."""
import hashlib,json,os,zipfile,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];W=R/'work/v13-clean-delivery';W.mkdir(exist_ok=False);D=R/'deliveries-v13';receipt=json.loads((D/'receipt-v13.json').read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for a in receipt['deliveries']:
 p=D/a['file'];assert h(p)==a['sha256']
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  for line in z.read('Character_Studio_0.13.0/'+a['index']).decode().splitlines():
   sha,name=line.split('  ',1);assert hashlib.sha256(z.read('Character_Studio_0.13.0/'+name)).hexdigest()==sha
  z.extractall(W)
 rows.append({**a,'crc_and_all_indexed_sha256':'pass'})
C=W/'Character_Studio_0.13.0';env=os.environ.copy();env['STUDIO_V13_OUT']=str(W/'rebuilt');blender=env.get('BLENDER_BIN','blender');subprocess.run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/build_horses_v13.py'],cwd=C,env=env,check=True,stdout=subprocess.DEVNULL);models=[]
lock=json.loads((C/'config-v13/horses.lock.json').read_text())
for a in lock['assets']+lock['comparison_assets']:
 p=W/'rebuilt'/a['asset_id']/a['version']/'model.glb';assert h(p)==a['model_sha256'];models.append({'asset_id':a['asset_id'],'sha256':h(p),'byte_identical_rebuild':True})
server=subprocess.Popen([sys.executable,'START_STUDIO_V13.py','--port','8805'],cwd=C,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 import urllib.request
 for _ in range(40):
  try:urllib.request.urlopen('http://localhost:8805/web-v13/',timeout=2).close();break
  except OSError:time.sleep(.25)
 env['STUDIO_URL']='http://localhost:8805/web-v13/';env['STUDIO_SMOKE_OUTPUT']=str(R/'evidence-v13/delivery-smoke.json');subprocess.run(['node','scripts/smoke_delivery_v13.cjs'],cwd=C,env=env,check=True)
finally:server.terminate();server.wait(timeout=10)
report={'archives':rows,'clean_models':models,'clean_actual_browser':'../evidence-v13/delivery-smoke.json','human_art':'not-tested','physical_mobile':'not-tested'};(D/'verification-v13.json').write_text(json.dumps(report,indent=2)+'\n');print('V13_CLEAN_REBUILD_AND_PACKAGE_PASS')
