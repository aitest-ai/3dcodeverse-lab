import math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'/'blender5'))
from trajectory_math_v85 import *
def tube():
    return [(math.cos(i*2*math.pi/24)*.05,y,math.sin(i*2*math.pi/24)*.05)
        for y in (-.94,-.81) for i in range(24)]
b=tube();ids=ring_indices(b)
assert measure_frame((0,-.948,0),(0,-1,0),b,ids)['pass']
assert not measure_frame((.1,-.948,0),(0,-1,0),b,ids)['pass']
assert not measure_frame((0,-.948,0),(1,0,0),b,ids)['pass']
rows=[{'clip':clip,'frame':f,'gap_m':.008,'angle_deg':.3} for clip in CLIPS for f in FRAMES]
assert summarize_samples(rows)['passed']
rows[0]['gap_m']=.05
assert not summarize_samples(rows)['passed']
try:summarize_samples(rows[:-1]);raise AssertionError('Missing frame accepted')
except ValueError:pass
print('PASS v8.5 trajectory math: gap, angle, 288 original NLA frames, incomplete coverage')
