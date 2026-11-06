"""Fresh checkout: build from pinned human mothers, browser review, self-contained bundles."""
import os,sys,subprocess,time,urllib.request,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R);(R/'work/v16').mkdir(parents=True,exist_ok=True);(R/'evidence-v16').mkdir(exist_ok=True);blender=os.environ.get('BLENDER_BIN','blender')
def run(a):print('RUN',a,flush=True);subprocess.run(a,check=True)
def py(n):run([sys.executable,'scripts/'+n])
def blend(n):run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/'+n])
blend('build_hands_v16.py');py('prepare_registry_v16.py');py('verify_hands_v16.py');blend('check_blender_v16.py');blend('check_export_guard_v16.py')
for key,ver in [('vivi','0.4.0'),('vita','0.3.0')]:run([sys.executable,'../../scripts/blender5/validate_glb.py','library-v16/vroid-'+key+'-motion-review/'+ver])
server=subprocess.Popen([sys.executable,'START_STUDIO_V16.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(40):
  try:urllib.request.urlopen('http://localhost:8810/web-v16/',timeout=2).close();break
  except OSError:time.sleep(.25)
 run(['node','scripts/check_browser_v16.cjs']);blend('check_crossings_v16.py');run(['node','scripts/capture_hands_v16.cjs']);py('summarize_hands_v16.py');py('package_hands_v16.py');py('check_delivery_v16.py')
finally:server.terminate();server.wait(timeout=10)
shutil.copyfile(R/'evidence-v16/acceptance-summary.json',R/'deliveries-v16/acceptance-summary.json');print('FULL_V16_REVIEW_PIPELINE_PASS')
