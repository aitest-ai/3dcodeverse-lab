import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'/'blender5'))
from muzzle_geometry_v84 import infer_muzzle_v84

def tube(y0,y1,r,n=24):
 return [(1+r*math.cos(2*math.pi*i/n),y,2+r*math.sin(2*math.pi*i/n))
         for y in (y0,y1) for i in range(n)]

candidate=infer_muzzle_v84(tube(-.85,-.70,.057),tube(-.82,-.39,.086))
assert abs(candidate['muzzle'][1]+.858)<.0001
assert candidate['forward'][1]<-.99
assert abs(candidate['bore_protrusion']-.03)<.0001
for func in [lambda:infer_muzzle_v84(tube(-.85,-.70,.057),tube(-.7,-.39,.086)),
             lambda:infer_muzzle_v84(tube(-.85,-.70,.057),tube(-.82,-.39,.086),.3)]:
 try:func();raise AssertionError('Invalid bore geometry accepted')
 except ValueError:pass
print('PASS v8.4 cannon geometry: real end-ring method on controlled synthetic tubes')
