"""Fresh checkout: build from pinned human mothers, browser review, self-contained bundles."""
import os,sys,subprocess,time,urllib.request,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R);(R/'work/v17').mkdir(parents=True,exist_ok=True);(R/'evidence-v17').mkdir(exist_ok=True);blender=os.environ.get('BLENDER_BIN','blender')
def run(a):print('RUN',a,flush=True);subprocess.run(a,check=True)
def py(n):run([sys.executable,'scripts/'+n])
def blend(n):run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/'+n])
py('bootstrap_inputs_v17.py');blend('build_arms_v17.py');py('prepare_registry_v17.py');py('verify_arms_v17.py');blend('check_blender_v17.py');blend('check_export_guard_v17.py')
for key,ver in [('vivi','0.5.0'),('vita','0.4.0')]:run([sys.executable,'../../scripts/blender5/validate_glb.py','library-v17/vroid-'+key+'-motion-review/'+ver])
server=subprocess.Popen([sys.executable,'START_STUDIO_V17.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(40):
  try:urllib.request.urlopen('http://localhost:8812/web-v17/',timeout=2).close();break
  except OSError:time.sleep(.25)
 run(['node','scripts/check_browser_v17.cjs']);blend('check_crossings_v17.py');run(['node','scripts/check_corrective_v17.cjs']);run(['node','scripts/capture_arms_v17.cjs']);py('summarize_arms_v17.py');py('package_arms_v17.py');py('check_delivery_v17.py')
finally:server.terminate();server.wait(timeout=10)
shutil.copyfile(R/'evidence-v17/acceptance-summary.json',R/'deliveries-v17/acceptance-summary.json');print('FULL_V17_REVIEW_PIPELINE_PASS')
