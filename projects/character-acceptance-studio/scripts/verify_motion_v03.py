"""Independent v0.2 evidence gates. Structural/numerical pass is not human art approval."""
import argparse,hashlib,json,math,sys,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts/vendor'))
from inspect_glb import inspect_glb
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=R/'assets');p.add_argument('--out',type=Path,default=R/'evidence-v03/numerical-qa.json');a=p.parse_args()
def rotate(v,y):return [math.cos(y)*v[0]-math.sin(y)*v[1],math.sin(y)*v[0]+math.cos(y)*v[1],v[2]]
reports={}
for asset in ['harbor-courier-review','taiwan-oldman-review']:
    folder=a.root/asset/'0.3.0';manifest=json.loads((folder/'asset_manifest.json').read_text());glb=folder/manifest['model_file'];assert hashlib.sha256(glb.read_bytes()).hexdigest()==manifest['sha256'];decoded=inspect_glb(glb);assert decoded['structural_pass'];audit=json.loads((folder/'motion-audit.json').read_text())['clips'];assert set(audit)=={'Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight'}
    report={'clips':{},'joins':{},'glb_sha256':manifest['sha256'],'decoded_structure_pass':True}
    for name,clip in audit.items():
        assert clip['minimum_sole_z_m']>.0025,(asset,name,'sampled ground penetration')
        assert clip['max_contact_planar_error_m']<.0005,(asset,name,'support anchor residual')
        assert clip.get('max_final_ik_clamp_m',clip['max_ik_clamp_m'])<.001,(asset,name,'unreachable final target')
        assert clip['max_reach_lowering_m']<.10,(asset,name,'excessive reach lowering; not a visual quality threshold')
        assert clip['stance_reference_speed_max_mps']<.002,(asset,name,'contact slip')
        rows=clip['samples'];yawdrift=[];knees=[];torso=[]
        for row in rows:
            for s,f in row['feet'].items():
                if f['contact']:knees.append(row['knee_flex_deg'][s])
            v=[row['points']['neck_01'][i]-row['points']['pelvis'][i] for i in range(3)];forward=[math.sin(row['heading_rad']),-math.cos(row['heading_rad']),0];torso.append(math.degrees(math.atan2(sum(x*y for x,y in zip(v,forward)),v[2])))
        if name in ['Idle','Walk','Run']:
            first,last=rows[0],rows[-1];travel=[last['root_m'][i]-first['root_m'][i] for i in range(3)];loop=max(math.dist(last['points'][n],[first['points'][n][i]+travel[i] for i in range(3)]) for n in first['points']);assert loop<.0005,(asset,name,'loop seam',loop)
        else:loop=None
        if name.startswith('Turn'):assert abs(abs(clip['heading_end_deg'])-90)<.001
        report['clips'][name]={k:v for k,v in clip.items() if k not in ['samples']};report['clips'][name].update(loop_max_joint_error_m=loop,stance_knee_flex_range_deg=[min(knees),max(knees)],actual_torso_lean_range_deg=[min(torso),max(torso)])
    for before,after in [('Idle','Start'),('Start','Walk'),('Walk','Stop'),('Stop','Idle'),('TurnLeft','Idle'),('TurnRight','Idle')]:
        x,y=audit[before]['samples'][-1],audit[after]['samples'][0];turn=x['heading_rad'];offset=[x['root_m'][i]-y['root_m'][i] for i in range(3)];errors=[]
        for n,point in y['points'].items():
            rotated=rotate(point,turn);pred=[rotated[i]+offset[i] for i in range(3)];errors.append(math.dist(x['points'][n],pred))
        maximum=max(errors);assert maximum<.001,(asset,before,after,'clip boundary mismatch',maximum);report['joins'][before+'->'+after]={'max_joint_position_error_m':maximum,'blend_used':False}
    report['source_master_unchanged']=hashlib.sha256((R/json.loads((folder/'report.json').read_text())['source_blend']).read_bytes()).hexdigest()==json.loads((folder/'report.json').read_text())['source_sha256'];assert report['source_master_unchanged']
    reports[asset]=report
result={'status':'NUMERICAL_AND_STRUCTURE_PASS_ONLY','assets':reports,'sample_rate_hz':60,'scope':'Actual evaluated shoe geometry at bake samples, decoded delivered GLB, root-compensated joint seams and unblended endpoint matching. Does not certify subframe/browser/cloth/human quality.','art_approved':False,'game_ready':False}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('V03_NUMERICAL_PASS',len(reports),'assets',len(reports)*7,'clips')
