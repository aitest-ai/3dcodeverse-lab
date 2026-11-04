"""Portable integrity, motion-seam/stance diagnostics and exact-lock negative checks.
No test here can award visual, device, cloth or human art approval.
"""
import json,hashlib,math,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'vendor'))
from inspect_glb import inspect_glb,GLB
from pin_asset import pull
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def movement(points):return max(v[1] for v in points)-min(v[1] for v in points)
registry=json.loads((R/'assets/registry.json').read_text());checks=[];diagnostics={}
for c in registry['characters']:
    assert not c['art_approved'] and not c['game_ready']
    profile=(R/'web'/c['profile']).resolve();assert sha(profile)==c['profile_sha256']
    p=json.loads(profile.read_text());assert len({b['name'] for b in p['bones']})==len(p['bones'])
    for variant in ['source','candidate']:
        a=c[variant];path=(R/'web'/a['url']).resolve();assert path.stat().st_size==a['bytes'] and sha(path)==a['sha256']
        report=inspect_glb(path);assert report['structural_pass'],report
        checks.append(c['id']+'/'+variant+': full SHA/bytes and decoded GLB structure')
    folder=(R/'web'/c['candidate']['url']).resolve().parent
    manifest=json.loads((folder/'asset_manifest.json').read_text());assert manifest['asset_id']==c['id'] and manifest['version']==c['version'] and manifest['sha256']==c['candidate']['sha256']
    model=GLB((R/'web'/c['candidate']['url']).resolve());doc=model.doc
    if c['id']=='taiwan-oldman-review':
        materials={m['name']:m for m in doc['materials']}
        assert materials['oldman_V28_AgedSkin_DerivedCC0'].get('alphaMode','OPAQUE')=='OPAQUE'
        assert materials['TrueMPFBBody_oldman.shoes03']['alphaMode']=='MASK'
        checks.append('Oldman opaque skin + masked sandal alpha export regression')
    audit=json.loads((folder/'motion-audit.json').read_text());clips=audit.get('clips',audit.get('variants',{}).get('candidate'))
    diagnostics[c['id']]={}
    for name,clip in clips.items():
        samples=clip['samples'];points=[s['points']['foot_l'] for s in samples]
        if name in ['Walk','Run']:assert movement(points)>.2,(c['id'],name,'static animation')
        seam=max(math.dist(samples[0]['points'][n],samples[-1]['points'][n]) for n in samples[0]['points'])
        if name in ['Idle','Walk','Run']:assert seam<.025,(c['id'],name,'loop seam exceeds 25mm',seam)
        speed=clip['speed_mps'];residual=[]
        for side in ['l','r']:
            floor=min(s['soles'][side] for s in samples)
            for a,b in zip(samples,samples[1:]):
                if max(a['soles'][side],b['soles'][side])<floor+.023:
                    dt=b['time_s']-a['time_s'];v=(b['points']['foot_'+side][1]-a['points']['foot_'+side][1])/dt
                    if v>.1:residual.append(abs(v-speed))
        diagnostics[c['id']][name]={'minimum_sampled_sole_z_m':clip['minimum_sole_z_m'],'max_lowest_sole_z_m':clip['max_lowest_sole_z_m'],'max_joint_loop_seam_m':seam,'stance_residual_mean_mps':sum(residual)/len(residual) if residual and name in ['Walk','Run'] else None,'stance_samples':len(residual),'method':'low evaluated shoe height (< per-foot min +23mm), forward foot velocity >0.1m/s, residual versus constant treadmill speed; diagnostic only','status':'measured_not_art_approved'}
        if name in ['Idle','Walk']:assert clip['minimum_sole_z_m']>=.0038
    checks.append(c['id']+': actual animated bone travel and sampled grounding')
    with tempfile.TemporaryDirectory() as temp:
        target=Path(temp)/'review'
        for badid,badver,badhash,allow in [(c['id'],c['version'],'0'*64,True),(c['id'],'latest',c['candidate']['sha256'],True),(c['id'],c['version'],c['candidate']['sha256'],False)]:
            try:pull(badid,badver,badhash,target,allow)
            except ValueError:pass
            else:raise AssertionError('Invalid/production candidate pin was accepted')
        lock=pull(c['id'],c['version'],c['candidate']['sha256'],target,True);assert lock['automatic_update'] is False
        try:pull(c['id'],c['version'],c['candidate']['sha256'],target,True)
        except ValueError:pass
        else:raise AssertionError('Existing destination overwritten')
    checks.append(c['id']+': exact lock and four negative identity/approval/overwrite gates')
result={'status':'PROGRAM_AND_STRUCTURE_PASS_ONLY','checks':checks,'diagnostics':diagnostics,'art_approved':False,'game_ready':False,'not_tested':['Human art acceptance','Physical phone','Full cloth collisions','Map/gameplay integration']}
(R/'evidence').mkdir(exist_ok=True);(R/'evidence/program-qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':len(checks),'report':'evidence/program-qa.json'}))
