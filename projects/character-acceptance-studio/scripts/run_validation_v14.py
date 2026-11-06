"""Fresh repository only: historical inputs, native transitions, browser proof and clean bundle."""
import os,shutil,subprocess,sys,time,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R);(R/'work/v14').mkdir(parents=True,exist_ok=True);(R/'evidence-v14').mkdir(exist_ok=True);blender=os.environ.get('BLENDER_BIN','blender')
def run(args,env=None):print('RUN',args,flush=True);subprocess.run(args,check=True,env=env)
def py(n):run([sys.executable,'scripts/'+n])
def node(n):run(['node','scripts/'+n])
def blend(n,env=None):run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/'+n],env)
env=os.environ.copy();env['STUDIO_V10_OUT']=str(R/'inputs-v11/v10');blend('build_horses_v10.py',env)
for version in ['v11','v12','v13','v14']:blend('build_horses_'+version+'.py');py('prepare_registry_'+version+'.py')
py('check_plan_v14.py');blend('check_smoothing_v14.py');blend('check_blender_v14.py');py('check_exports_v14.py');py('check_pins_v14.py')
for key in ['horse-brown','horse-white']:
    for suffix in ['walk-smooth-review']:run([sys.executable,'../../scripts/blender5/validate_glb.py','library-v14/'+key+'-'+suffix+'/0.1.0'])
server=subprocess.Popen([sys.executable,'START_STUDIO_V14.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(40):
        try:urllib.request.urlopen('http://localhost:8806/web-v14/',timeout=2).close();break
        except OSError:time.sleep(.25)
    node('check_browser_v14.cjs');node('check_joins_v14.cjs');node('check_shape_v14.cjs');py('verify_horses_v14.py');node('capture_horses_v14.cjs');py('summarize_horses_v14.py');py('package_horses_v14.py');py('check_delivery_v14.py')
finally:server.terminate();server.wait(timeout=10)
for name in ['delivery-smoke.json','acceptance-summary.json']:shutil.copyfile(R/'evidence-v14'/name,R/'deliveries-v14'/name)
print('FULL_V14_REVIEW_PIPELINE_PASS')
