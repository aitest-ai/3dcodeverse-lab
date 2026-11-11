"""Fresh checkout: pinned inputs, material edit, cold native, real browser, clean bundles."""
import os,sys,subprocess,time,urllib.request,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R);(R/'work/v18').mkdir(parents=True,exist_ok=True);(R/'evidence-v18').mkdir(exist_ok=True);blender=os.environ.get('BLENDER_BIN','blender')
def run(a):print('RUN',a,flush=True);subprocess.run(a,check=True)
def py(n):run([sys.executable,'scripts/'+n])
def blend(n):run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/'+n])
py('bootstrap_inputs_v18.py');blend('build_surface_v18.py');py('prepare_registry_v18.py')
validator=R/'../../scripts/blender5/validate_glb.py'
if not validator.exists():validator=R/'scripts/v18/validate_glb.py'
for key,ver in [('vivi','0.6.0'),('vita','0.5.0')]:run([sys.executable,str(validator),'library-v18/vroid-'+key+'-motion-review/'+ver])
blend('check_surface_v18.py')
server=subprocess.Popen([sys.executable,'START_STUDIO_V18.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(40):
  try:urllib.request.urlopen('http://localhost:8816/web-v18/',timeout=2).close();break
  except OSError:time.sleep(.25)
 run(['node','scripts/check_browser_v18.cjs']);run(['node','scripts/capture_surface_v18.cjs']);run(['node','scripts/capture_motion_v18.cjs']);py('summarize_surface_v18.py');py('package_surface_v18.py');py('check_delivery_v18.py')
finally:server.terminate();server.wait(timeout=10)
shutil.copyfile(R/'evidence-v18/acceptance-summary.json',R/'deliveries-v18/acceptance-summary.json');print('FULL_V18_REVIEW_PIPELINE_PASS')
