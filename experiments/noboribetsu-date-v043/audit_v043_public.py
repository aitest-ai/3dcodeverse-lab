#!/usr/bin/env python3
"""Read-only V043 model-space whole-cap check, no mesh edits.
Usage: python audit_v043_public.py /path/to/V042_Inspector/assets
Dependencies: numpy, trimesh, shapely. Results are model coordinates, not site measurements.
Complete replay and Chromium QA are in the user\u0027s independent V043 SourceQA.zip.
"""
from pathlib import Path
import sys,hashlib,json
import numpy as np
import trimesh
from shapely.geometry import box,Polygon
ROOT_SHA="9d6ec28e7844c3b522b6b1453426334f36da580808ad78bd4bc3e7c5969463f4"
CAP_PAIRS=((20,21),(32,33),(44,45),(56,57))
WOOD=("wood_lintel","wood_timber")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(directory):
    p=Path(directory)/"v041_v004_integrated_roof_posts_H.glb"
    assert sha(p)==ROOT_SHA,"Invalid sealed H GLB"
    m=trimesh.load(p,force="scene").geometry
    assert len(m)==17
    output=[]
    for index,pair in enumerate(CAP_PAIRS,1):
        cap_verts=m["wood_dark"].triangles[list(pair)].reshape(-1,3)
        lo,hi=cap_verts.min(axis=0),cap_verts.max(axis=0)
        assert abs(lo[1]-hi[1])<1e-5
        cap=box(lo[0],lo[2],hi[0],hi[2])
        assert abs(cap.area-.03)<1e-5
        row={"post":f"P{index}","cap_area_model_units_squared":cap.area,"beams":{}}
        for beam in WOOD:
            tris=m[beam].triangles
            xy=tris[:,:,[0,2]]
            mn=xy.min(axis=1);mx=xy.max(axis=1)
            nearby=(mn[:,0]<=hi[0]+3)&(mx[:,0]>=lo[0]-3)&(mn[:,1]<=hi[2]+3)&(mx[:,1]>=lo[2]-3)
            indices=np.flatnonzero(nearby)
            gap=min(float(cap.distance(Polygon(xy[k]))) for k in indices)
            overlap=any(cap.intersection(Polygon(xy[k])).area>1e-10 for k in indices)
            assert gap>0.2 and not overlap
            upper=(mn[:,0]<=hi[0]+2)&(mx[:,0]>=lo[0]-2)&(mn[:,1]<=hi[2]+2)&(mx[:,1]>=lo[2]-2)&(tris[:,:,1].max(axis=1)>=hi[1]-.01)
            sample_tris=tris[upper]
            assert len(sample_tris)
            sample_min=float("inf")
            for x in np.linspace(lo[0],hi[0],11):
                for z in np.linspace(lo[2],hi[2],11):
                    pt=np.array([x,hi[1],z])
                    near=trimesh.triangles.closest_point(sample_tris,np.broadcast_to(pt,(len(sample_tris),3)))
                    sample_min=min(sample_min,float(np.linalg.norm(near-pt,axis=1).min()))
            row["beams"][beam]={"overlap":False,"exact_projected_xz_gap":gap,
                "sampled_3d_nearest_11x11":sample_min,"sampled_not_global_min":True}
        output.append(row)
    assert len(output)==4
    return {"status":"PASS","source_h_sha256":ROOT_SHA,
        "onsite_dimensions_verified":False,"structural_approval":False,
        "all_eight_projected_overlaps_zero":True,"posts":output}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit(__doc__)
    print(json.dumps(check(sys.argv[1]),ensure_ascii=False,indent=2))
