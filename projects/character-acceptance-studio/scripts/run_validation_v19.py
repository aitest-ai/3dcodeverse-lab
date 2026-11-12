"""Fresh checkout: exact inputs, rejected experiment reconstruction, actual browser and archives."""
import os,sys,subprocess,time,urllib.request,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R);(R/'work/v19').mkdir(parents=True,exist_ok=True);(R/'evidence-v19').mkdir(exist_ok=True);blender=os.environ.get('BLENDER_BIN','blender')
def run(a):print('RUN',a,flush=True);subprocess.run(a,check=True)
def py(n):run([sys.executable,'scripts/'+n])
def blend(n):run([blender,'-b','-t','4','--python-exit-code','1','--python','scripts/'+n])
py('bootstrap_inputs_v19.py');blend('build_experiments_v19.py');blend('check_experiments_v19.py');py('prepare_registry_v19.py');py('validate_structure_v19.py');py('check_pins_v19.py')
server=subprocess.Popen([sys.executable,'START_STUDIO_V19.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(40):
  try:urllib.request.urlopen('http://localhost:8819/web-v19/',timeout=2).close();break
  except OSError:time.sleep(.25)
 run(['node','scripts/check_browser_v19.cjs']);run(['node','scripts/capture_motion_v19.cjs']);py('summarize_v19.py');py('package_v19.py');py('check_delivery_v19.py')
finally:server.terminate();server.wait(timeout=10)
shutil.copyfile(R/'evidence-v19/acceptance-summary.json',R/'deliveries-v19/acceptance-summary.json');print('V19_DIAGNOSTIC_PIPELINE_PASS__GEOMETRY_EXPERIMENTS_REJECTED')
