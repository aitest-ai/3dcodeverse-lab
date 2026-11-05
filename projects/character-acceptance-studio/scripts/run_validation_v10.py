"""Full fresh-checkout build, actual Blender/browser validation, downloadable review packages."""
import os,sys,subprocess,time,json,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R);(R/'work/v10').mkdir(parents=True,exist_ok=True);(R/'evidence-v10').mkdir(exist_ok=True);blender=os.environ.get('BLENDER_BIN','blender')
def run(args):print('RUN',args,flush=True);subprocess.run(args,check=True)
def py(name):run([sys.executable,'scripts/'+name])
def blend(name):run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/'+name])
blend('build_horses_v10.py');py('prepare_registry_v10.py');blend('check_blender_v10.py');py('check_exports_v10.py');py('check_pins_v10.py');(R/'evidence-v10/horse-diagnostics.json').write_text('{"entries":[]}\n')
for key in ['horse-brown','horse-white']:run([sys.executable,'../../scripts/blender5/validate_glb.py','library-v10/'+key+'-grounded-review/0.1.0'])
server=subprocess.Popen([sys.executable,'START_STUDIO_V10.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(40):
  try:urllib.request.urlopen('http://localhost:8791/web-v10/',timeout=2).close();break
  except OSError:time.sleep(.25)
 run(['node','scripts/check_browser_v10.cjs']);py('verify_horses_v10.py');run(['node','scripts/capture_horses_v10.cjs']);py('summarize_horses_v10.py');py('package_horses_v10.py');py('check_delivery_v10.py')
finally:server.terminate();server.wait(timeout=10)
# Keep post-package proof alongside the immutable ZIPs rather than creating a self-referential archive.
import shutil
for name in ['delivery-smoke.json','acceptance-summary.json']:shutil.copyfile(R/'evidence-v10'/name,R/'deliveries-v10'/name)
print('FULL_V10_REVIEW_PIPELINE_PASS')
