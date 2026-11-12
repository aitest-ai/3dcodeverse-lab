"""Run repository GLB validator in isolated hard-linked per-experiment outputs."""
import os,sys,json,subprocess,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];W=R/'work/v19-structure';W.mkdir(parents=True,exist_ok=True);validator=R/'../../scripts/blender5/validate_glb.py'
if not validator.exists():validator=R/'scripts/v18/validate_glb.py'
report=json.loads((R/'evidence-v19/surface-diagnostics.json').read_text())
for key in ['vivi','vita']:
 d=W/key;d.mkdir(exist_ok=True);manifest=json.loads((R/'experiments-v19'/(key+'-manifest.json')).read_text());(d/'asset_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');row=next(r for r in report['entries'] if r['key']==key);(d/'report.json').write_text(json.dumps(row,indent=2)+'\n')
 for name in [manifest['model_file'],manifest['source_file']]:
  p=d/name
  if not p.exists():os.link(R/'experiments-v19'/name,p)
 subprocess.run([sys.executable,str(validator),str(d)],check=True);shutil.copyfile(d/'validation.json',R/'experiments-v19'/(key+'-validation.json'))
