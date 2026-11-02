#!/usr/bin/env python3
"""Strict and read-only source/derived file verification for V016."""
from pathlib import Path
import hashlib,json,zipfile,subprocess
R=Path(__file__).resolve().parent;D=R/'base/dist';O=R/'outputs';O.mkdir(exist_ok=True)
basezip=R/'Noboribetsu_Date_V015_R1_Runtime.zip'
if not basezip.exists():basezip=Path('/mnt/data/Noboribetsu_Date_V015_R1_Runtime.zip')
assert basezip.is_file()
with zipfile.ZipFile(basezip) as z:
 names=[x for x in z.namelist() if not x.endswith('/')]
 original={n:hashlib.sha256(z.read(n)).hexdigest() for n in names}
current={str(x.relative_to(R/'base')):hashlib.sha256(x.read_bytes()).hexdigest() for x in (R/'base').rglob('*') if x.is_file()}
allowed={'dist/app.js','dist/index.html','dist/scene_view.json','dist/qa.json'}
changed={n for n in original if original[n]!=current.get(n)}
assert changed==allowed,(changed,allowed)
assert len(original)==112,len(original)
assert set(current)-set(original)=={'dist/v016_grade_inspection.json'},set(current)-set(original)
assert len(current)==113
scene=json.loads((D/'scene_view.json').read_text());q=json.loads((D/'v016_grade_inspection.json').read_text())
assert scene['footing_v016']['sha256']==current['dist/v016_grade_inspection.json']
assert len(q['burial_samples'])==4
assert scene['grounding_v015']['sha256']==hashlib.sha256((D/'v015_post_grounding.json').read_bytes()).hexdigest()
assert abs(scene['route'][-1]['s']-231.56641497226084)<1e-7
assert scene['grounding_v015']['support_count']==8
subprocess.run(['node','--check',str(D/'app.js')],check=True)
qa={'schema':'noboribetsu-date-v016-integrity/1','status':'PASS','previous_file_count':len(original),
 'unchanged_original_files':len(original)-len(changed),'allowed_changes':sorted(changed),'unexpected_changes':[],
 'new_files':['dist/v016_grade_inspection.json'],'total_files':len(current),
 'old_v015_supports_unchanged':True,'route_m':scene['route'][-1]['s'],'collision_file_unchanged':True,
 'original_geometry_models_unchanged':True,'four_samples_are_not_four_standalone_posts':True,
 'sha256':current}
(O/'V016_integrity_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print('PASS',len(original),len(changed),len(current))