#!/usr/bin/env python3
"""Build the visual-only V012 road-to-grass shoulder strip from frozen V002 GSI heights.

Usage: python build_v012_edge.py V002_Complete.zip V011_Runtime_dir V012_output.json
Does not modify roads, DEM, collision, V011 patch, or source model assets.
"""
import hashlib, json, math, pathlib, sys, zipfile
from statistics import mean

SCHEMA='noboribetsu-v012-road-grass-transition/1'
START_S=197.72393408812707
END_S=231.56641497226084

def read_source(path):
    with zipfile.ZipFile(path) as z:
        n=[s for s in z.namelist() if s.endswith('/data/scene_geometry.json')]
        if len(n)!=1:raise ValueError('Need exactly one V002 scene geometry')
        return json.loads(z.read(n[0]))

def create(v002zip, dist, target):
    g=read_source(v002zip)
    if g.get('axes')!='Blender ENU; GLB EUS':raise ValueError('wrong coordinate convention')
    raw=json.loads((dist/'scene_view.json').read_text())
    route=[p for p in raw['route'] if START_S-0.0001 <= p['s'] <= END_S+0.0001]
    if len(route)<75 or abs(route[0]['s']-START_S)>.02 or abs(route[-1]['s']-END_S)>.02:
        raise ValueError('Frozen V006 route unexpected; refusing approximate replacement')
    source_sha=hashlib.sha256((dist/'assets/v006_tail_road.glb').read_bytes()).hexdigest()
    if source_sha!='423a928696dadd4fcea9a516f0a854e504e8eae6209adc141706e5cbe0737642':
        raise ValueError('V006 road GLB is not frozen')
    # V002 terrain vertices are (east, north, elevation), while runtime route is (east, up, -north).
    terrain={(round(float(x),3),round(float(-y),3)):float(h) for x,y,h in g['terrain']['vertices']}
    def dem(x,z):
        x0=2*math.floor(x/2);z0=2*math.floor(z/2); u=(x-x0)/2;v=(z-z0)/2
        vals=[terrain.get((float(xx),float(zz))) for xx,zz in [(x0,z0),(x0+2,z0),(x0,z0+2),(x0+2,z0+2)]]
        if any(q is None for q in vals):return None
        a,b,c,d=vals
        return (1-u)*(1-v)*a + u*(1-v)*b+(1-u)*v*c+u*v*d
    # Each strip spans road edge to landscape, with diminishing transparent color/alpha.
    # A deliberate gap from the centreline keeps the 6m collision/road surface untouched.
    # outer ring uses sampled V002 terrain; road-side ring follows the original route.
    verts=[]; colors=[]; indices=[]; triples=[]; bounds=[]; maxdev=0
    offsets=[3.03,3.19,3.42,3.64]
    alphas=[0.32,0.28,0.17,0.0]
    # warm compact soil -> muted moss; no invented curb or drainage geometry.
    palette=[(.31,.27,.19),(.34,.30,.21),(.30,.34,.24),(.29,.38,.28)]
    sections=[]
    for i,p in enumerate(route):
        lo=route[max(0,i-1)];hi=route[min(len(route)-1,i+1)]
        dx=hi['x']-lo['x'];dz=hi['z']-lo['z']; mag=math.hypot(dx,dz)
        if mag<1e-8:raise ValueError('degenerate route tangent')
        nx,nz=-dz/mag,dx/mag
        sections.append((p,nx,nz))
    for side in (-1,1):
        side_base=len(verts)//3
        for i,(p,nx,nz) in enumerate(sections):
            for band,off in enumerate(offsets):
                # Deterministic small shoreline wobble (not random triangles) to avoid a machine-straight seam.
                # Never shift the first ring onto the road.
                wave=(0 if band==0 else (math.sin(i*.61+side*1.3)*.018+math.sin(i*1.37+1.7)*.009)*min(band,2)/2)
                radius=off+wave
                x=p['x']+side*nx*radius;z=p['z']+side*nz*radius
                h=dem(x,z)
                if h is None:raise ValueError(f'No verified V002 terrain at station {i}, ring {band}: {x,z}')
                # Limit to local shoulder where DEM and road have comparable heights.
                diff=abs(h-p['y'])
                maxdev=max(maxdev,diff)
                if diff>.50:raise ValueError(f'Unsupported steep shoulder {diff:.3f}m at station {i}, {side}')
                t=band/(len(offsets)-1)
                y=p['y']*(1-t)+h*t+(.021-.006*t)
                verts.extend([round(x,5),round(y,5),round(z,5)])
                color=palette[band];alpha=alphas[band]
                # subtle repeated variation, but bounded and low saturation
                mult=1 + .045*math.sin(i*.72+band*2.1)
                colors.extend([round(min(1,color[0]*mult),5),round(min(1,color[1]*mult),5),round(min(1,color[2]*mult),5),alpha])
                triples.append({'x':x,'z':z,'ground':h,'road':p['y'],'y':y,'band':band,'side':side})
        for i in range(len(route)-1):
            for j in range(len(offsets)-1):
                a=side_base+i*len(offsets)+j
                b=a+len(offsets);c=b+1;d=a+1
                indices.extend([a,b,d,b,c,d] if side==1 else [a,d,b,b,d,c])
    maxwidth=max(abs(q['y']-q['ground']) for q in triples)
    patch={
        'schema':SCHEMA,'version':'V012-R1','provenance':'Frozen V002 GSI DEM + frozen V006 route; appearance-only author-estimated; not drainage or surveyed shoulder',
        'v011_terrain_gap_untouched':True,'collision_enabled':False,'road_glb_sha256':source_sha,
        'route_start_s_m':START_S,'route_end_s_m':END_S,'samples':len(route),
        'rings_per_side':len(offsets),'sides':2,'triangles':len(indices)//3,
        'positions':verts,'colors':colors,'indices':indices,
        'render_material':{'type':'MeshStandardMaterial','transparent':True,'vertexColors':True,'depthWrite':False,'side':'DoubleSide','roughness':1.0,'metalness':0.0},
        'author_estimated':True
    }
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(patch,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    a={'schema':'V012-R1-edge-builder-qa/1','status':'PASS_SOURCE_GEOMETRY_ONLY','road_glb_sha256':source_sha,
        'route_samples':len(route),'first_s':route[0]['s'],'last_s':route[-1]['s'],'triangles':len(indices)//3,
        'vertices':len(verts)//3,'min_y':min(verts[1::3]),'max_y':max(verts[1::3]),
        'max_abs_dem_road_height_difference_m':maxwidth,'collision_changed':False,'terrain_gap_v011_changed':False,
        'min_inner_offset_m':min(offsets),'outer_offset_m':max(offsets),'webgl2_verified':False}
    (target.parent/'V012_geometry_qa.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(a,ensure_ascii=False,indent=2))
    return a

if __name__=='__main__':
    if len(sys.argv)!=4:raise SystemExit('usage: build_v012_edge.py V002_Complete.zip V011_Runtime_dir V012_output.json')
    create(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]),pathlib.Path(sys.argv[3]))