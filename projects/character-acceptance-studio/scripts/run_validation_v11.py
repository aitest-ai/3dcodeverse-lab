"""Fresh v10 prerequisite + v11 build, native cold checks, actual browser, standalone ZIP rebuild."""
import os,sys,subprocess,time,json,urllib.request,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R);(R/'work/v11').mkdir(parents=True,exist_ok=True);(R/'evidence-v11').mkdir(exist_ok=True);blender=os.environ.get('BLENDER_BIN','blender')
def run(args,env=None):print('RUN',args,flush=True);subprocess.run(args,check=True,env=env)
def py(name):run([sys.executable,'scripts/'+name])
def blend(name,env=None):run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/'+name],env)
env=os.environ.copy();env['STUDIO_V10_OUT']=str(R/'inputs-v11/v10');blend('build_horses_v10.py',env);py('calibrate_walk_v11.py');blend('build_horses_v11.py');py('prepare_registry_v11.py');blend('check_blender_v11.py');py('check_exports_v11.py');py('check_pins_v11.py')
for key in ['horse-brown','horse-white']:run([sys.executable,'../../scripts/blender5/validate_glb.py','library-v11/'+key+'-walk-world-review/0.1.0'])
server=subprocess.Popen([sys.executable,'START_STUDIO_V11.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(40):
  try:urllib.request.urlopen('http://localhost:8795/web-v11/',timeout=2).close();break
  except OSError:time.sleep(.25)
 run(['node','scripts/check_browser_v11.cjs']);py('verify_horses_v11.py');run(['node','scripts/capture_horses_v11.cjs']);py('summarize_horses_v11.py');py('package_horses_v11.py');py('check_delivery_v11.py')
finally:server.terminate();server.wait(timeout=10)
for name in ['delivery-smoke.json','acceptance-summary.json']:shutil.copyfile(R/'evidence-v11'/name,R/'deliveries-v11'/name)
print('FULL_V11_REVIEW_PIPELINE_PASS')
