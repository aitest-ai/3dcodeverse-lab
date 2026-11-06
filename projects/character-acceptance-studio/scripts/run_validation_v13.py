"""Fresh repository only: historical inputs, native transitions, browser proof and clean bundle."""
import os,shutil,subprocess,sys,time,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R);(R/'work/v13').mkdir(parents=True,exist_ok=True);(R/'evidence-v13').mkdir(exist_ok=True);blender=os.environ.get('BLENDER_BIN','blender')
def run(args,env=None):print('RUN',args,flush=True);subprocess.run(args,check=True,env=env)
def py(n):run([sys.executable,'scripts/'+n])
def node(n):run(['node','scripts/'+n])
def blend(n,env=None):run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/'+n],env)
env=os.environ.copy();env['STUDIO_V10_OUT']=str(R/'inputs-v11/v10');blend('build_horses_v10.py',env)
for version in ['v11','v12','v13']:blend('build_horses_'+version+'.py');py('prepare_registry_'+version+'.py')
py('check_plan_v13.py');blend('check_blender_v13.py');py('check_exports_v13.py');py('check_pins_v13.py')
for key in ['horse-brown','horse-white']:
    for suffix in ['transition-baseline','walk-transition-review']:run([sys.executable,'../../scripts/blender5/validate_glb.py','library-v13/'+key+'-'+suffix+'/0.1.0'])
server=subprocess.Popen([sys.executable,'START_STUDIO_V13.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(40):
        try:urllib.request.urlopen('http://localhost:8803/web-v13/',timeout=2).close();break
        except OSError:time.sleep(.25)
    node('check_browser_v13.cjs');node('check_joins_v13.cjs');py('verify_horses_v13.py');node('capture_horses_v13.cjs');py('summarize_horses_v13.py');py('package_horses_v13.py');py('check_delivery_v13.py')
finally:server.terminate();server.wait(timeout=10)
for name in ['delivery-smoke.json','acceptance-summary.json']:shutil.copyfile(R/'evidence-v13'/name,R/'deliveries-v13'/name)
print('FULL_V13_REVIEW_PIPELINE_PASS')
