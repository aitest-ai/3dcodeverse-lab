"""A rejected experiment cannot be selected through the exact-version reuse path."""
import json,tempfile
from pathlib import Path
from types import SimpleNamespace
from pin_surface_v19 import pin
R=Path(__file__).resolve().parents[1];cat=json.loads((R/'library-v19/catalog.json').read_text());result=[]
with tempfile.TemporaryDirectory(prefix='studio-v19-pin-') as temp:
 for e in cat['entries']:
  args=SimpleNamespace(id=e['asset_id'],version=e['version'],sha256=e['model']['sha256'],review_candidate=True,dest=str(Path(temp)/e['asset_id']));pin(args);result.append({'id':e['id'],'exact_pin':True})
 e=cat['entries'][0]
 for i,(id,ver,sha,review) in enumerate([(e['asset_id'],'experiment-v19-rejected',e['model']['sha256'],True),(e['asset_id'],e['version'],'0'*64,True),(e['asset_id'],e['version'],e['model']['sha256'],False)]):
  try:pin(SimpleNamespace(id=id,version=ver,sha256=sha,review_candidate=review,dest=str(Path(temp)/('rejected'+str(i)))));raise AssertionError('Invalid pin accepted')
  except ValueError:pass
(R/'evidence-v19/pin-checks.json').write_text(json.dumps({'entries':result,'trial_rejected':True,'wrong_sha_rejected':True,'production_without_review_rejected':True},indent=2)+'\n')
