"""Extract actual ZIPs, verify every hash, rebuild independently and exercise the shipped browser."""
import hashlib,json,os,zipfile,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];W=R/'work/v11-clean-delivery';W.mkdir(exist_ok=False);D=R/'deliveries-v11';receipt=json.loads((D/'receipt-v11.json').read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for a in receipt['deliveries']:
 p=D/a['file'];assert h(p)==a['sha256']
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  for line in z.read('Character_Studio_0.11.0/'+a['index']).decode().splitlines():
   sha,name=line.split('  ',1);assert hashlib.sha256(z.read('Character_Studio_0.11.0/'+name)).hexdigest()==sha
  z.extractall(W)
 rows.append({**a,'crc_and_all_indexed_sha256':'pass'})
C=W/'Character_Studio_0.11.0';env=os.environ.copy();env['STUDIO_V11_OUT']=str(W/'rebuilt');blender=env.get('BLENDER_BIN','blender');subprocess.run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/build_horses_v11.py'],cwd=C,env=env,check=True,stdout=subprocess.DEVNULL);models=[]
for a in json.loads((C/'config-v11/horses.lock.json').read_text())['assets']:
 p=W/'rebuilt'/a['asset_id']/a['version']/'model.glb';assert h(p)==a['model_sha256'];models.append({'asset_id':a['asset_id'],'sha256':h(p),'byte_identical_rebuild':True})
server=subprocess.Popen([sys.executable,'START_STUDIO_V11.py','--port','8797'],cwd=C,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 import urllib.request
 for _ in range(40):
  try:urllib.request.urlopen('http://localhost:8797/web-v11/',timeout=2).close();break
  except OSError:time.sleep(.25)
 env['STUDIO_URL']='http://localhost:8797/web-v11/';env['STUDIO_SMOKE_OUTPUT']=str(R/'evidence-v11/delivery-smoke.json');subprocess.run(['node','scripts/smoke_delivery_v11.cjs'],cwd=C,env=env,check=True)
finally:server.terminate();server.wait(timeout=10)
report={'archives':rows,'clean_models':models,'clean_actual_browser':'../evidence-v11/delivery-smoke.json','human_art':'not-tested','physical_mobile':'not-tested'};(D/'verification-v11.json').write_text(json.dumps(report,indent=2)+'\n');print('V11_CLEAN_REBUILD_AND_PACKAGE_PASS')
