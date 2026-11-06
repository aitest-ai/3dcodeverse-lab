"""Finite start/walk/stop path and planted-foot schedule, in calibrated metres.

Blender forward is -Y. Ground anchors are immutable world points. Existing
v12 WalkWorld is reached after three cycles and left at phase zero.
"""
import math


def smooth(x):
    x = max(0., min(1., x))
    return x*x*x*(10+x*(-15+6*x))


def distance(t, plan):
    T = plan['duration_s']; v = plan['candidate_speed_m_s']; a = 2*T
    t = max(0., min(8*T, t))
    if t < a:
        x = t/a
        return v*a*(x**3-.5*x**4)
    if t <= 6*T:
        return v*(t-T)
    x = (t-6*T)/a
    return v*5*T+v*a*(x-x**3+.5*x**4)


def speed(t, plan):
    T = plan['duration_s']; v = plan['candidate_speed_m_s']
    if t <= 0 or t >= 8*T:
        return 0.
    if t < 2*T:
        x = t/(2*T)
        return v*(3*x*x-2*x*x*x)
    if t <= 6*T:
        return v
    x = (t-6*T)/(2*T)
    return v*(1-3*x*x+2*x*x*x)


def body_weight(t, plan):
    T = plan['duration_s']
    return smooth(t/T)*smooth((8*T-t)/T)


def schedule(plan, foot):
    T = plan['duration_s']; p = plan['feet'][foot]
    rows = []
    for k in range(-1, 9):
        off = (k+p['phase']+p['duty'])*T
        on = (k+p['phase']+1)*T
        if off >= 0 and on <= 8*T:
            mid = (k+1+p['phase']+p['duty']/2)*T
            rows.append({'off': off, 'on': on, 'anchor': p['source_stance_mean_m'][1]-distance(mid, plan)})
    return rows


def foot_target(t, plan, foot):
    p = plan['feet'][foot]; anchor = p['source_stance_mean_m'][1]
    for row in schedule(plan, foot):
        if t < row['off']:
            break
        if t < row['on']:
            s = (t-row['off'])/(row['on']-row['off'])
            lift = math.sin(math.pi*s)**2
            world = anchor+(row['anchor']-anchor)*smooth(s)
            return {'stance': False, 'phase': s, 'world_y': world, 'x': p['source_stance_mean_m'][0], 'y': world+distance(t, plan), 'sole': .003+p['source_max_lift_m']*lift, 'rotation_blend': lift}
        anchor = row['anchor']
    return {'stance': True, 'phase': 0., 'world_y': anchor, 'x': p['source_stance_mean_m'][0], 'y': anchor+distance(t, plan), 'sole': .003, 'rotation_blend': 0.}


def clip_specs(plan):
    T = plan['duration_s']
    return {'StandReady': (0., 0.), 'StartWalk': (0., 3*T), 'StopWalk': (5*T, 8*T), 'StandStopped': (8*T, 8*T)}
