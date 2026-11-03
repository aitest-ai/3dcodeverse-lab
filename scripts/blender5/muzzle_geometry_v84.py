"""Pure-math analysis of original V50 cannon tube end rings (Blender-free tests).
Never infers muzzle from weapon_socket.R pivot or a screenshot.
"""
import math

def _vec3(v):
    p=tuple(float(n) for n in v)
    if len(p)!=3 or not all(math.isfinite(n) for n in p):
        raise ValueError('Invalid finite XYZ point')
    return p

def _avg(points):
    n=len(points)
    return tuple(sum(p[i] for p in points)/n for i in range(3))

def distance(a,b):
    return math.dist(a,b)

def tube_endrings(vertices):
    points=[_vec3(v) for v in vertices]
    if not 12<=len(points)<=250000:
        raise ValueError('Tube mesh vertex count outside guarded range')
    low=min(p[1] for p in points); high=max(p[1] for p in points)
    if not .04 <= high-low <= 2:
        raise ValueError('Cannon tube length outside expected range')
    tol=min(.003,max(.0002,(high-low)*.008))
    front=[p for p in points if p[1]<=low+tol]
    back=[p for p in points if p[1]>=high-tol]
    if min(len(front),len(back))<6:
        raise ValueError('Cannot isolate two complete cannon end rings')
    f=_avg(front); b=_avg(back)
    axial=tuple(f[i]-b[i] for i in range(3)); length=math.sqrt(sum(c*c for c in axial))
    if length<.04: raise ValueError('Degenerate barrel axis')
    direction=tuple(c/length for c in axial)
    if direction[1]>-.97:
        raise ValueError('Barrel is not original V50 forward -Y geometry')
    radius=sum(math.hypot(p[0]-f[0],p[2]-f[2]) for p in front)/len(front)
    if not .012<=radius<=.20:
        raise ValueError('Barrel end radius out of range')
    return {'front_center':f,'back_center':b,'direction':direction,'radius':radius,
            'length':length,'front_count':len(front),'back_count':len(back)}

def infer_muzzle_v84(bore_vertices,outer_vertices,lip_extension=.008):
    if not 0<=lip_extension<=.025:raise ValueError('Unsafe muzzle lip extension')
    bore=tube_endrings(bore_vertices); outer=tube_endrings(outer_vertices)
    tip=bore['front_center'];other=outer['front_center']
    if math.hypot(tip[0]-other[0],tip[2]-other[2])>.035:
        raise ValueError('Bore and outer barrel centers not aligned')
    protrusion=other[1]-tip[1]
    if not -.015<=protrusion<=.13:
        raise ValueError('Bore front does not align with original outer barrel')
    axis=bore['direction']
    muzzle=tuple(tip[i]+lip_extension*axis[i] for i in range(3))
    return {'muzzle':muzzle,'forward':axis,'bore_radius':bore['radius'],
            'bore_length':bore['length'],'outer_length':outer['length'],
            'bore_protrusion':protrusion,
            'geometry_basis':'PrimaryCannon_energy_bore + PrimaryCannon_outer_barrel'}
