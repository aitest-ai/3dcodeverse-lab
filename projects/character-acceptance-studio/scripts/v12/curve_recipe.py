"""Portable, reviewable native TRS curves. Fresh solver output must agree before frozen export.
Float32 baked values are explicit text motion source, not a generated GLB hidden as text.
"""
import json,hashlib
from pathlib import Path
RECIPE_SHA='ec2ec6535264b7c131aba68f4b842695b73a839d128fcca2a076537ccb923f1b'
def load_recipe(root,doc):
 path=Path(root)/'motion-v12/horse-support-curves.json';assert hashlib.sha256(path.read_bytes()).hexdigest()==RECIPE_SHA,'Reviewed curve source changed';data=json.loads(path.read_text());out={}
 for clip in data['clips']:
  frames=[{} for _ in clip['times']]
  for track in clip['nodes']:
   i=track['node'];assert doc['nodes'][i]['name']==track['name'],'Native node semantics changed'
   for j,frame in enumerate(frames):frame[i]={k:list(track[k].get('constant') or track[k]['values'][j]) for k in ['translation','rotation','scale']}
  out[clip['name']]={'times':clip['times'],'frames':frames}
 return out

def compare_curve(actual,reference):
 assert len(actual)==len(reference);maximum=0
 for a,b in zip(actual,reference):
  assert a.keys()==b.keys()
  for n in a:
   for p in ['translation','rotation','scale']:
    error=max(abs(x-y) for x,y in zip(a[n][p],b[n][p]));opposite=max(abs(x+y) for x,y in zip(a[n][p],b[n][p])) if p=='rotation' else error;maximum=max(maximum,min(error,opposite))
 if maximum>1e-5:raise RuntimeError('Fresh native solver differs from reviewed curve source: '+str(maximum))
 return maximum
