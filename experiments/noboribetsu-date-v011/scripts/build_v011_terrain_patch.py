#!/usr/bin/env python3
"""Create a non-destructive, source-derived terrain-gap mesh for V011.

Input: a byte-for-byte frozen V010 dist/ whose scene_B consists of 23 independent
GZIP parts. The source B GLB is not rewritten or distributed. This script
reads original grass geometry and fills exactly unoccupied 2 m terrain cells.

WARNING: the 84 interpolated vertices are visual estimates in a no-data region,
not surveyed elevations or a replacement for the original terrain source.
Collision, road, models, material pixels and old geometry remain untouched.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, struct
from pathlib import Path
import numpy as np

SCHEMA = 'noboribetsu-v011-terrain-gap-patch/1'
EXPECTED_SHA = '3feac26ec59250494330974775bda07c089c0a4642eb4471dc18fd22b2ba6715'


def load_b(dist: Path) -> bytes:
    info=json.loads((dist/'scene_view.json').read_text('utf-8'))
    model=next(m for m in info['models'] if m['stage']=='B')
    if model['sha256'] != EXPECTED_SHA or model['compression']!='gzip':
        raise ValueError('Unexpected base B model, refusing terrain edit')
    data=b''.join(gzip.decompress((dist/p).read_bytes()) for p in model['parts'])
    if len(data)!=model['bytes'] or hashlib.sha256(data).hexdigest()!=EXPECTED_SHA:
        raise ValueError('Original B digest/decoded length mismatch')
    return data


def grass_source(data: bytes):
    if data[:4]!=b'glTF' or struct.unpack_from('<I',data,4)[0]!=2:
        raise ValueError('Bad GLB header')
    json_len,tag=struct.unpack_from('<I4s',data,12)
    if tag!=b'JSON':raise ValueError('No GLB JSON')
    spec=json.loads(data[20:20+json_len])
    bin_off=20+json_len+8
    def acc(index):
        a=spec['accessors'][index];v=spec['bufferViews'][a['bufferView']]
        dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']]
        dims={'SCALAR':1,'VEC2':2,'VEC3':3}[a['type']];dt=np.dtype(dtype)
        stride=v.get('byteStride',dims*dt.itemsize)
        return np.ndarray((a['count'],dims),dtype=dt,buffer=data,
            offset=bin_off+v.get('byteOffset',0)+a.get('byteOffset',0),
            strides=(stride,dt.itemsize))
    matches=[p for mesh in spec['meshes'] for p in mesh['primitives']
             if spec['materials'][p['material']]['name']=='Original_grass']
    if len(matches)!=1:raise ValueError('Cannot uniquely identify original grass')
    p=matches[0]
    return acc(p['attributes']['POSITION']),acc(p['indices']).ravel().reshape(-1,3),acc(p['attributes']['TEXCOORD_0'])


def build_patch(dist:Path):
    data=load_b(dist)
    pts,faces,uv=grass_source(data)
    # 201x201 source grid, 2 metres, with 40,000 possible 2-triangle cells.
    grid=np.full((201,201),np.nan,dtype=np.float64)
    src_index=np.rint((pts[:,[0,2]]+160)/2).astype(np.int32)
    if np.max(np.abs(src_index*2-160-pts[:,[0,2]]))>1e-4:
        raise ValueError('Source terrain is not the required 2m grid')
    for (i,j),h in zip(src_index,pts[:,1]):
        if not 0<=i<=200 or not 0<=j<=200:raise ValueError('Unexpected coordinate')
        if np.isfinite(grid[i,j]) and abs(grid[i,j]-float(h))>1e-5:
            raise ValueError('Conflicting elevations for same source vertex')
        grid[i,j]=float(h)
    face_pts=pts[faces][:,:,[0,2]]
    face_cell=np.rint((face_pts.min(axis=1)+160)/2).astype(np.int32)
    count=np.zeros((200,200),dtype=np.uint8)
    np.add.at(count,(face_cell[:,0],face_cell[:,1]),1)
    if set(np.unique(count))!={0,2}:
        raise ValueError('Source has partial or multiply filled terrain cells')
    holes=np.argwhere(count==0)
    missing=np.argwhere(~np.isfinite(grid))
    if len(holes)!=148 or len(missing)!=84 or len(faces)!=79704:
        raise ValueError(f'Unexpected V002 terrain topology holes={len(holes)} missing={len(missing)} faces={len(faces)}')
    if not (holes[:,0].min()==138 and holes[:,0].max()==166 and
            holes[:,1].min()==138 and holes[:,1].max()==160):
        raise ValueError('Hole extent changed; require human geometry review')
    old=grid.copy()
    # Harmonic inpainting: each unknown point is the mean of its four neighbors.
    # Boundary grid heights are frozen, so there are no seams at valid edges.
    for i,j in missing:
        neigh=[old[ii,jj] for ii,jj in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)) if np.isfinite(old[ii,jj])]
        grid[i,j]=float(np.mean(neigh)) if neigh else 0.0
    converged=False
    for iteration in range(20000):
        maxchange=0
        for i,j in missing:
            new=(grid[i-1,j]+grid[i+1,j]+grid[i,j-1]+grid[i,j+1])*.25
            diff=abs(new-grid[i,j]);maxchange=max(maxchange,diff);grid[i,j]=new
        if maxchange<1e-9:
            converged=True;break
    if not converged:raise RuntimeError('Inpainting did not converge')
    if not np.allclose(grid[np.isfinite(old)],old[np.isfinite(old)],atol=0,rtol=0):
        raise ValueError('Modified original source heights')
    # Triangle order = source grid, preserving winding / grass UV scaling.
    P=[];UV=[];N=[];repaired=[]
    for ii,jj in holes:
        x,z=2*int(ii)-160,2*int(jj)-160
        corners=[(ii,jj+1),(ii+1,jj+1),(ii,jj),(ii+1,jj)]
        for tri in ((0,1,2),(1,3,2)):
            vertices=np.array([(2*int(corners[k][0])-160,float(grid[corners[k]]),2*int(corners[k][1])-160) for k in tri],dtype=np.float64)
            n=np.cross(vertices[1]-vertices[0],vertices[2]-vertices[0]);n/=np.linalg.norm(n)
            if n[1]<0.25: raise ValueError('Steep, flipped or invalid reconstructed face')
            for vertex in vertices:
                xx,yy,zz=vertex
                P.extend((float(xx),float(yy),float(zz)))
                UV.extend((float(xx/8),float(zz/8+1)))
                N.extend(map(float,n))
        repaired.append([x,z])
    if len(P)//9!=296:raise ValueError('Wrong face count')
    # Bounding, elevations, and unchanged 148 other cells are explicit QA.
    ypatch=np.asarray(P)[1::3]
    report={'schema':SCHEMA,'source_b_sha256':EXPECTED_SHA,
            'source_terrain_triangles':int(len(faces)),
            'source_grid_cells':int(count.size),'source_open_cells':int(len(holes)),
            'source_missing_height_samples':int(len(missing)),
            'patched_triangles':int(len(P)//9),'patched_vertices':int(len(P)//3),
            'cells':repaired,'hole_range_eus_m':{'x':[116,174],'z':[116,162]},
            'patch_height_range_m':[float(np.min(ypatch)),float(np.max(ypatch))],
            'interpolation':'discrete Laplace, four-neighbor fixed source boundary, author-estimated visual-only',
            'iterations':iteration+1,'max_change_last_iteration_m':maxchange,
            'terrain_original_untouched':True,'road_untouched':True,'collision_untouched':True,
            'textures_untouched':True,'material_used':'Original_grass',
            'uv_formula':{'u':'x/8','v':'z/8+1'},
            'provenance':'V002 GSI visual terrain with missing cells, not new surveyed elevation'}
    patch={'schema':SCHEMA,'source_b_sha256':EXPECTED_SHA,
           'original_grass_triangles':int(len(faces)),'gap_cells':len(holes),
           'positions':list(map(lambda x:round(x,7),P)),
           'normals':list(map(lambda x:round(x,7),N)),
           'uv':list(map(lambda x:round(x,7),UV)),
           'triangles':len(P)//9,'collision_enabled':False,
           'approximation':'Laplace interpolation on missing DEM grid; visual only'}
    return patch,report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('dist',type=Path);ap.add_argument('output',type=Path);ap.add_argument('qa',type=Path);a=ap.parse_args()
    patch,report=build_patch(a.dist)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.qa.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(patch,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    sha=hashlib.sha256(a.output.read_bytes()).hexdigest();report['patch_json_sha256']=sha;report['patch_json_bytes']=a.output.stat().st_size
    a.qa.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('source_open_cells','source_missing_height_samples','patched_triangles','patch_height_range_m','patch_json_sha256')},ensure_ascii=False))