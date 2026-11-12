"""Independent geometric fixtures for alpha-supported intersection classification."""
import numpy as np
from mathutils import Vector
from v19.visibility import SurfaceAlpha

def run():
 s=SurfaceAlpha.__new__(SurfaceAlpha);s.tris=[{'vertices':[0,1,2],'material':0},{'vertices':[3,4,5],'material':1}];s.uv=np.full((6,2),.25);v=[Vector(x) for x in [(-1,-1,0),(1,-1,0),(0,1,0),(0,-.5,-1),(0,-.5,1),(0,.5,0)]]
 s.materials={0:(1,.5,np.ones((4,4))),1:(1,.5,np.ones((4,4)))};assert s.crossing_visible(v,0,1)
 s.materials[1]=(1,.5,np.zeros((4,4)));assert not s.crossing_visible(v,0,1)
 # A visible texel elsewhere in the triangle's texture tile cannot make this intersection opaque.
 image=np.zeros((4,4));image[3,3]=1;s.materials[1]=(1,.5,image);assert not s.crossing_visible(v,0,1)
 s.materials[1]=(1,.5,np.full((4,4),.49));assert not s.crossing_visible(v,0,1)
 s.materials[1]=(1,.5,np.full((4,4),.51));assert s.crossing_visible(v,0,1)
 far=v[:3]+[p+Vector((10,0,0)) for p in v[3:]];assert not s.crossing_visible(far,0,1)
 s.materials[1]=(2,0,np.full((4,4),.01));assert s.crossing_visible(v,0,1)
 print('V19_ALPHA_FIXTURES_PASS',flush=True)
