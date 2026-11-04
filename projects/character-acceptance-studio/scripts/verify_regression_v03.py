"""Independently decode both GLBs: protected root/leg channels and embedded images must survive.
This gate says nothing about whether clothing/upper-body motion looks good.
"""
import argparse,hashlib,json,sys,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts/vendor'));from inspect_glb import GLB,inspect_glb
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=R/'assets');a=p.parse_args();rows=[]
def channels(g,keep):
    out={}
    for clip in g.doc['animations']:
        c={}
        for ch in clip['channels']:
            node=g.doc['nodes'][ch['target']['node']]['name'];path=ch['target']['path']
            if node not in keep:continue
            s=clip['samplers'][ch['sampler']];c[node+':'+path]={'times':g.accessor(s['input']),'values':g.accessor(s['output'])}
        out[clip['name']]=c
    return out
for asset in ['harbor-courier-review','taiwan-oldman-review']:
    old=R/'assets'/asset/'0.2.0';new=a.root/asset/'0.3.0';x,y=[GLB(f/(asset+'.glb')) for f in [old,new]];profile=json.loads((new/'skeleton-profile.json').read_text());keep={n['name'] for n in profile['bones'] if n['name']=='pelvis' or n['name']=='root' or n['name'].startswith(('thigh','calf','foot','ball'))};keep.add(profile['animated_root_node']);before,after=channels(x,keep),channels(y,keep);assert before.keys()==after.keys();maximum=0;count=0
    for clip,chs in before.items():
        assert chs.keys()==after[clip].keys()
        for name,values in chs.items():
            b=after[clip][name];assert values['times']==b['times'],(asset,clip,name,'time grid changed');assert len(values['values'])==len(b['values'])
            for v,w in zip(values['values'],b['values']):maximum=max(maximum,max(abs(i-j) for i,j in zip(v,w)))
            count+=1
    assert maximum<3e-6,(asset,'root/leg tracks changed',maximum)
    images=lambda g:sorted(hashlib.sha256(g.image_bytes(i)).hexdigest() for i in range(len(g.doc['images'])))
    assert images(x)==images(y),(asset,'embedded texture bytes changed');assert inspect_glb(new/(asset+'.glb'))['structural_pass']
    audit=json.loads((new/'motion-audit.json').read_text());posture=json.loads((new/'posture-audit.json').read_text());run=[v['after_lean_deg'] for v in posture['Run']];assert max(run)<12.1;assert min(v['before_lean_deg'] for v in posture['Run'])>17
    for name,clip in posture.items():
        assert max(abs(v['after_lean_deg']-v['target_lean_deg']) for v in clip)<.02
    rows.append({'id':asset,'version':'0.3.0','protected_channels':count,'max_root_leg_channel_component_difference':maximum,'embedded_images_byte_identical':True,'run_before_lean_range_deg':[min(v['before_lean_deg'] for v in posture['Run']),max(v['before_lean_deg'] for v in posture['Run'])],'run_after_lean_range_deg':[min(run),max(run)],'art_approved':False})
out=R/'evidence-v03/regression-qa.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps({'status':'ROOT_LEGS_TEXTURES_AND_POSTURE_NUMERICAL_PASS','assets':rows,'art_approved':False},indent=2)+'\n');print('V03_REGRESSION_PASS',rows)
