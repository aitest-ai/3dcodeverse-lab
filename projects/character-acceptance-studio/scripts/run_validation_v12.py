"""Fresh v10/v11 prerequisite build, v12 native + browser proof, complete standalone review ZIP."""
import os,sys,subprocess,time,urllib.request,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R);(R/'work/v12').mkdir(parents=True,exist_ok=True);(R/'evidence-v12').mkdir(exist_ok=True);blender=os.environ.get('BLENDER_BIN','blender')
def run(args,env=None):print('RUN',args,flush=True);subprocess.run(args,check=True,env=env)
def py(n):run([sys.executable,'scripts/'+n])
def blend(n,env=None):run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/'+n],env)
env=os.environ.copy();env['STUDIO_V10_OUT']=str(R/'inputs-v11/v10');blend('build_horses_v10.py',env);blend('build_horses_v11.py');py('prepare_registry_v11.py');blend('build_horses_v12.py');py('prepare_registry_v12.py');run(['node','scripts/check_support_v12.cjs']);blend('check_blender_v12.py');py('check_exports_v12.py');py('check_pins_v12.py')
for key in ['horse-brown','horse-white']:run([sys.executable,'../../scripts/blender5/validate_glb.py','library-v12/'+key+'-walk-support-review/0.1.0'])
server=subprocess.Popen([sys.executable,'START_STUDIO_V12.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(40):
  try:urllib.request.urlopen('http://localhost:8799/web-v12/',timeout=2).close();break
  except OSError:time.sleep(.25)
 run(['node','scripts/check_browser_v12.cjs']);py('verify_horses_v12.py');run(['node','scripts/capture_horses_v12.cjs']);py('summarize_horses_v12.py');py('package_horses_v12.py');py('check_delivery_v12.py')
finally:server.terminate();server.wait(timeout=10)
for name in ['delivery-smoke.json','acceptance-summary.json']:shutil.copyfile(R/'evidence-v12'/name,R/'deliveries-v12'/name)
print('FULL_V12_REVIEW_PIPELINE_PASS')
