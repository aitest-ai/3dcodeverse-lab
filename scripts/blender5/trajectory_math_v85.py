"""Read-only animated cannon ring math for original v8.4 candidate.
Rest-ring vertex indices must be carried across the actual armature-evaluated mesh.
"""
import math
CLIPS=('Idle','Run','Punch','Dodge','Fire','Hit')
FRAMES=tuple(range(1,49))
MAX_GAP_METERS=.025
MAX_ANGLE_DEGREES=9.0

def vec(v):
    try:a=tuple(float(x) for x in v)
    except (ValueError,TypeError) as e:raise ValueError('Invalid 3D coordinate') from e
    if len(a)!=3 or not all(math.isfinite(x) for x in a):raise ValueError('Non-finite 3D coordinate')
    return a

def center(items):
    p=[vec(v) for v in items]
    if not p:raise ValueError('Missing end-ring points')
    return tuple(sum(v[i] for v in p)/len(p) for i in range(3))

def unit(v):
    a=vec(v);n=math.sqrt(sum(x*x for x in a))
    if n<1.e-8:raise ValueError('Degenerate forward axis')
    return tuple(x/n for x in a)

def ring_indices(vertices):
    pts=[vec(x) for x in vertices]
    if len(pts)<12:raise ValueError('Incomplete tube geometry')
    low=min(x[1] for x in pts);high=max(x[1] for x in pts)
    if not .04<=high-low<=2.:raise ValueError('Unexpected barrel length')
    tol=min(.003,max(.0002,(high-low)*.008))
    a=[i for i,p in enumerate(pts) if p[1]<=low+tol]
    b=[i for i,p in enumerate(pts) if p[1]>=high-tol]
    if min(len(a),len(b))<6:raise ValueError('Incomplete end rings')
    return {'front':a,'back':b,'vertex_count':len(pts)}

def measure_frame(marker_tip,marker_forward,evaluated_vertices,indices,lip=.008):
    if not 0<=lip<=.025:raise ValueError('Invalid lip extension')
    if len(evaluated_vertices)!=indices['vertex_count']:raise ValueError('Topology changed')
    front=center(evaluated_vertices[i] for i in indices['front'])
    back=center(evaluated_vertices[i] for i in indices['back'])
    forward=unit(tuple(front[i]-back[i] for i in range(3)))
    goal=tuple(front[i]+lip*forward[i] for i in range(3))
    gap=math.dist(goal,vec(marker_tip))
    aim=unit(marker_forward)
    angle=math.degrees(math.acos(max(-1.,min(1.,sum(forward[i]*aim[i] for i in range(3))))))
    return {'gap_m':round(gap,6),'angle_deg':round(angle,4),
            'pass':gap<=MAX_GAP_METERS and angle<=MAX_ANGLE_DEGREES}

def summarize_samples(samples):
    if not isinstance(samples,list) or len(samples)!=288:raise ValueError('All 288 frames required')
    unique=set();groups={c:[] for c in CLIPS}
    for s in samples:
        if not isinstance(s,dict) or s.get('clip') not in groups or s.get('frame') not in FRAMES:
            raise ValueError('Invalid clip/frame')
        key=(s['clip'],s['frame'])
        if key in unique:raise ValueError('Duplicate frame')
        unique.add(key)
        if not all(isinstance(s.get(k),(float,int)) and math.isfinite(s[k]) and s[k]>=0 for k in ('gap_m','angle_deg')):
            raise ValueError('Invalid angle/gap')
        groups[s['clip']].append(s)
    if any(len(a)!=48 for a in groups.values()):raise ValueError('Incomplete original action')
    summary={}
    for clip,rows in groups.items():
        worst_gap=max(rows,key=lambda x:x['gap_m']);worst_angle=max(rows,key=lambda x:x['angle_deg'])
        summary[clip]={'sample_count':len(rows),'worst_gap_m':worst_gap['gap_m'],
            'worst_gap_frame':worst_gap['frame'],'worst_angle_deg':worst_angle['angle_deg'],
            'worst_angle_frame':worst_angle['frame'],
            'passed':all(x['gap_m']<=MAX_GAP_METERS and x['angle_deg']<=MAX_ANGLE_DEGREES for x in rows)}
    return {'passed':all(s['passed'] for s in summary.values()),'total_samples':len(samples),
        'max_gap_threshold_m':MAX_GAP_METERS,'max_angle_threshold_deg':MAX_ANGLE_DEGREES,'clips':summary}
