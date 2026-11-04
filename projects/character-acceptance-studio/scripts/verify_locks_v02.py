"""Exercise exact identity, candidate permission and overwrite guards using isolated copies."""
import hashlib,json,tempfile
from pathlib import Path
from pin_asset_v02 import pull
R=Path(__file__).resolve().parents[1];registry=json.loads((R/'assets/registry-v02.json').read_text());checks=[]
with tempfile.TemporaryDirectory(prefix='studio-v02-lock-') as temp:
    base=Path(temp)
    for c in registry['characters']:
        common=(c['id'],c['version'],c['candidate']['sha256']);dest=base/c['id']
        def rejected(label,args,allow):
            try:pull(*args,dest,allow)
            except ValueError as e:checks.append({'id':c['id'],'case':label,'rejected':True,'reason':str(e)})
            else:raise AssertionError(label+' unexpectedly accepted')
        rejected('unapproved production install',common,False)
        rejected('wrong ID',(c['id']+'-missing',*common[1:]),True)
        rejected('wrong version',(c['id'],'9.9.9',common[2]),True)
        rejected('wrong hash',(*common[:2],'0'*64),True)
        assert not dest.exists()
        lock=pull(*common,dest,True);assert hashlib.sha256((dest/lock['model_file']).read_bytes()).hexdigest()==common[2]
        assert hashlib.sha256((dest/'skeleton-profile.json').read_bytes()).hexdigest()==c['profile_sha256']
        checks.append({'id':c['id'],'case':'exact review-only copy and native profile hash','passed':True})
        rejected('destination exists',common,True)
result={'status':'PIN_LOCK_GUARDS_PASS','checks':checks,'automatic_update':False,'art_approved':False}
(R/'evidence-v02/pin-lock-qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(result['status'],len(checks),'checks')
