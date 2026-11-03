"""Portable Godot Web export using a locally fetched official template; no engine shipped in Git."""
from pathlib import Path
import subprocess,os,argparse,shutil
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--godot',default=os.environ.get('GODOT_BIN',shutil.which('godot') or '/opt/godot/4.6.3/Godot_v4.6.3-stable_linux.x86_64'));a=p.parse_args()
env=dict(os.environ,XDG_DATA_HOME=str(R/'tools/data'),XDG_CONFIG_HOME=str(R/'tools/config'));preset=R/'godot/export_presets.cfg';original=preset.read_text();template=R/'tools/templates/4.6.3.stable/web_nothreads_release.zip'
(R/'web').mkdir(parents=True,exist_ok=True)
assert template.is_file(),'Run python scripts/fetch_web_templates.py first'
try:
 preset.write_text(original.replace('../tools/templates/4.6.3.stable/web_nothreads_release.zip',str(template)))
 for args in [['--editor','--import','--quit'],['--script','res://scripts/build_scene.gd'],['--export-release','Web']]:
  subprocess.run([a.godot,'--headless','--path',str(R/'godot'),*args],env=env,check=True)
 page=R/'web/index.html';page.write_text(page.read_text().replace('<head>','<head>\n<link rel="icon" href="index.png">'))
finally:preset.write_text(original)
