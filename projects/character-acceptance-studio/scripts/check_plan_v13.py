"""Independent scalar/path boundary checks; no bpy dependency."""
import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v13.plan import distance,speed,foot_target,schedule,body_weight
p=json.loads((R/'config-v12/walk-plan.json').read_text());T=p['duration_s'];v=p['candidate_speed_m_s'];events=sorted({0,8*T,*[t for k in p['feet'] for row in schedule(p,k) for t in [row['off'],row['on']]]});intervals=[]
for a,b in zip(events,events[1:]):
    t=(a+b)/2;stance=[k for k in p['feet'] if foot_target(t,p,k)['stance']];assert len(stance)>=2
    for k in stance:
        left=foot_target(a+(b-a)*.2,p,k);right=foot_target(a+(b-a)*.8,p,k);assert abs(left['world_y']-right['world_y'])<1e-12 and left['sole']==right['sole']==.003
    intervals.append({'start':a,'end':b,'stance':stance})
for t in [0,2*T,3*T,5*T,6*T,8*T]:
    h=1e-6;numeric=(distance(t+h,p)-distance(t-h,p))/(2*h);assert abs(numeric-speed(t,p))<1e-6
assert distance(0,p)==0 and abs(distance(8*T,p)-5.6)<1e-12
assert speed(0,p)==speed(8*T,p)==0 and body_weight(0,p)==body_weight(8*T,p)==0
assert all(foot_target(t,p,k)['stance'] for t in [0,8*T] for k in p['feet'])
(R/'evidence-v13/plan-check.json').write_text(json.dumps({'finite_duration_s':8*T,'distance_m':distance(8*T,p),'minimum_planned_support':min(len(x['stance']) for x in intervals),'start_stop_all_four_grounded':True,'root_position_and_velocity_boundaries':'pass','stance_anchor_constancy':'pass','intervals':intervals},indent=2)+'\n');print('V13_PLAN_PASS')
