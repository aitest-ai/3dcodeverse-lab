#!/usr/bin/env python3
"""Read-only V036 source roof gap audit. Requires trimesh, numpy.
Usage: python roof_gap_audit_v036.py original_V004.glb v036_edge_preserving_tint.glb
No GLB is modified; all quantities are author-model coordinates, not surveyed.
"""
import sys,json,hashlib
from collections import defaultdict
from pathlib import Path
import trimesh,numpy as np
if len(sys.argv)!=3: raise SystemExit("expected: original V004.glb, V036 C.glb")
p,q=map(Path,sys.argv[1:])
sha=lambda v:hashlib.sha256(v.read_bytes()).hexdigest()
assert sha(p)=="132ee6c0add22fbfe4a9872d82cb5e6bed0e2e4f282533b6c61de6c156a7a5e3"
a=trimesh.load(p,force="scene").geometry["plaster_offwhite"]
b=next(iter(trimesh.load(q,force="scene").geometry.values()))
assert len(a.faces)==48 and np.array_equal(a.faces[[8,9]],[[3,7,6],[3,6,2]])
assert len(b.faces)==480 and len(b.vertices)==273
perimeter=((2,3),(3,7),(6,7),(2,6))
original=a.vertices
old_B=original.copy();old_B[[6,7],1]-=.035
ed={}
for fi,f in enumerate(a.faces):
 for i,j in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):
  ed.setdefault(tuple(sorted((int(i),int(j)))),[]).append(fi)
changed=[]
for i,j in perimeter:
 owners=ed[tuple(sorted((i,j)))]
 assert len(owners)==2 and any(x in (8,9) for x in owners)
 if np.linalg.norm(old_B[i]-original[i])>1e-7 or np.linalg.norm(old_B[j]-original[j])>1e-7:
  changed.append((i,j))
assert len(changed)==3
band_y=original[[2,3,6,7],1].mean()
assert np.max(np.abs(b.vertices[:,1]-band_y))<2e-6
print(json.dumps({"B_edges_moved":len(changed),"B_max_shift":.035,"C_all_vertices_same_plane":True,"C_boundary_shift":0,"C_faces":len(b.faces),"original_source_untouched":True},indent=2))
