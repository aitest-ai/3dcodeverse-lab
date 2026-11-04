#!/usr/bin/env python3
"""Read-only, shareable version of the V034 mesh attribution check.
Usage: python audit_roof_mesh_v034.py /path/to/v004_merchant_facades.glb
Requires numpy, trimesh. Does not edit GLB or deploy anything.
"""
import sys, io, hashlib, json
import numpy as np, trimesh
from pathlib import Path
if len(sys.argv)!=2: raise SystemExit("Usage: audit_roof_mesh_v034.py V004_GLb")
p=Path(sys.argv[1]); content=p.read_bytes()
s=trimesh.load(io.BytesIO(content),file_type="glb",force="scene")
assert len(s.geometry)==17
m=s.geometry["plaster_offwhite"]
matches=[]
for i, tri in enumerate(m.triangles):
  x,y,z=tri[:,0],tri[:,1],tri[:,2]
  if np.ptp(y)<1e-4 and abs(float(y[0])-6.194)<0.015 and np.ptp(x)>15 and x.min()>1 and x.max()<23 and z.min()>56.6 and z.max()<57.5:
    matches.append(int(i))
assert len(matches)==2, matches
print(json.dumps({"glb_sha256":hashlib.sha256(content).hexdigest(),"mesh_count":len(s.geometry),"plaster_offwhite_triangles":len(m.faces),"candidate_large_roof_band_triangles_trimesh":matches,"geometry_changed":False},indent=2))
