#!/usr/bin/env python3
"""V004 candidate: extend existing V003 R3 Date Jidaimura to the first merchant-street east leg.

Non-destructive. OpenStreetMap coordinates are inherited from frozen V002 source.
Three.js and GLB use EUS x=east, y=up, z=south; Blender source is ENU.
Real-world geometry and facade/roof measurements beyond OSM polygons are NOT survey data.
The roof, windows, porch, sign placement are artist-estimated, exterior-only.
"""
from __future__ import annotations
import json, math, hashlib, os, random
from pathlib import Path
from collections import defaultdict
import numpy as np
import trimesh
from trimesh.visual.texture import TextureVisuals
from trimesh.visual.material import PBRMaterial
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(os.environ.get("NOBORIBETSU_V004_WORKDIR", Path(__file__).resolve().parent)).resolve()
BASE = ROOT/'baseline/data'
DST = ROOT/'runtime/dist'
OUT = DST/'assets'
OUT.mkdir(parents=True,exist_ok=True)
GEOM=json.loads((BASE/'scene_geometry.json').read_text())
BASE_VIEW=json.loads((ROOT/'baseline/scene_view_R3.json').read_text())
BASE_COLL=json.loads((DST/'collision.json').read_text())
BASE_ROUTE=list(BASE_VIEW['route'])
BUILDINGS={a['id']:a for a in GEOM['buildings']}
assert abs(BASE_ROUTE[-1]['s']-82.87701578450043)<1e-4, 'Expect V002 frozen 82.877m path'
assert abs(BASE_ROUTE[-1]['x']+4.854636931250531)<1e-4

# Frozen V002 source route after current end. OSM geometry values, not a resurvey.
anchors=[BASE_ROUTE[-1],
    {'x':35.841255078045144,'y':1.3999999999999915,'z':60.78413805394349},
    {'x':42.12494461926742,'y':1.5008070047490634,'z':61.89492582438763},
]
route=list(BASE_ROUTE)
for a,b in zip(anchors,anchors[1:]):
    dist=math.hypot(b['x']-a['x'],b['z']-a['z'])
    n=math.ceil(dist/.55)
    for i in range(1,n+1):
        t=i/n
        q={k:float(a[k]*(1-t)+b[k]*t) for k in ['x','y','z']}
        q['s']=route[-1]['s']+math.hypot(q['x']-route[-1]['x'],q['z']-route[-1]['z'])
        route.append(q)
assert 129 < route[-1]['s'] < 132,route[-1]['s']

MATERIALS={
    'road_asphalt': ((0.345,.344,.320,1),.98),
    'road_patinated_edge': ((.365,.365,.331,1),1),
    'stone_warm_grey': ((.58,.563,.520,1),.96),
    'stone_foot': ((.47,.468,.435,1),.94),
    'plaster_offwhite': ((.775,.750,.677,1),1),
    'plaster_warm': ((.725,.660,.505,1),1),
    'plaster_lower': ((.658,.629,.560,1),1),
    'wood_timber': ((.235,.167,.113,1),.92),
    'wood_dark': ((.119,.093,.077,1),.91),
    'wood_lintel': ((.295,.206,.137,1),.87),
    'wood_patina': ((.193,.158,.126,1),.96),
    'wood_grain_light': ((.38,.267,.18,1),.92),
    'panel_black': ((.100,.101,.095,1),.91),
    'paper_panels': ((.720,.700,.621,1),1),
    'tile_ash': ((.264,.289,.287,1),.94),
    'tile_slate': ((.304,.337,.342,1),.95),
    'tile_variation': ((.229,.258,.265,1),.96),
    'tile_lit': ((.369,.380,.363,1),.92),
    'ridge_tile': ((.242,.264,.273,1),.92),
    'metal_old': ((.174,.162,.124,1),.85),
}

class Geometry:
    def __init__(self):
        self.groups=defaultdict(lambda:{'vs':[],'fs':[]})
        self.counts=defaultdict(int)
    def poly(self,mat,coords,faces):
        g=self.groups[mat];b=len(g['vs']);g['vs'].extend([tuple(map(float,v)) for v in coords]);g['fs'].extend(tuple(b+int(i) for i in f) for f in faces);self.counts[mat]+=len(faces)
    def quad(self,mat,a,b,c,d,twosided=False):
        fs=[(0,1,2),(0,2,3)]
        if twosided:fs += [(2,1,0),(3,2,0)]
        self.poly(mat,[a,b,c,d],fs)
    def tri(self,mat,a,b,c):self.poly(mat,[a,b,c],[(0,1,2)])
    def box(self,mat,x,y,z,dx,dy,dz,theta=0):
        hx,hy,hz=dx/2,dy/2,dz/2; c,s=math.cos(theta),math.sin(theta)
        vs=[]
        for px,py,pz in [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]:
            vs.append((x+px*c+pz*s,y+py,z-px*s+pz*c))
        fs=[(0,3,2),(0,2,1),(4,5,6),(4,6,7),(0,4,7),(0,7,3),(1,2,6),(1,6,5),(3,7,6),(3,6,2),(0,1,5),(0,5,4)]
        self.poly(mat,vs,fs)
    def cylinder_x(self,mat,x0,x1,y,z,r=.10,n=8):
        vs=[(x0,y+math.sin(2*math.pi*i/n)*r,z+math.cos(2*math.pi*i/n)*r) for i in range(n)]
        vs+=[(x1,y+math.sin(2*math.pi*i/n)*r,z+math.cos(2*math.pi*i/n)*r) for i in range(n)]
        fs=[]
        for i in range(n):
            j=(i+1)%n;fs.extend(((i,j,n+j),(i,n+j,n+i)))
        fs.extend((0,i+1,i) for i in range(1,n-1))
        fs.extend((n,n+i,n+i+1) for i in range(1,n-1))
        self.poly(mat,vs,fs)
    def save(self,path:Path):
        scene=trimesh.Scene()
        summary={}
        for name,g in self.groups.items():
            v=np.asarray(g['vs'],dtype=np.float32);f=np.asarray(g['fs'],dtype=np.int64)
            col,rough=MATERIALS[name]; mat=PBRMaterial(name=name,baseColorFactor=[int(max(0,min(1,c))*255) for c in col],metallicFactor=0.0,roughnessFactor=rough)
            mesh=trimesh.Trimesh(vertices=v,faces=f,process=False)
            mesh.visual=TextureVisuals(material=mat)
            scene.add_geometry(mesh,geom_name=name,node_name=name)
            summary[name]={'triangles':len(f),'vertices':len(v)}
        path.write_bytes(scene.export(file_type='glb'))
        return summary

road_mesh=Geometry()
# Physical collision top at survey-derived OSM/DEM anchor elevations;
# a slight render-only lift avoids flicker at old/new overlap without claiming centimetre accuracy.
def sample_cross(q, tangent_x,tangent_z,w,offset=0):
    d=math.hypot(tangent_x,tangent_z);dx,dz=tangent_x/d,tangent_z/d
    nx,nz=-dz,dx
    return (q['x']+nx*w,q['y']+offset,q['z']+nz*w)
newseg=route[len(BASE_ROUTE)-1:]
# Road width 6m is an explicit author estimate. The original tail is 6.8m; taper 2m into extension.
for idx in range(len(newseg)-1):
    a,b=newseg[idx:idx+2];px=b['x']-a['x'];pz=b['z']-a['z']
    elapsed=math.hypot(a['x']-newseg[0]['x'],a['z']-newseg[0]['z'])
    w=3.4-.4*min(elapsed/2.0,1)
    left0=sample_cross(a,px,pz,w,.018);right0=sample_cross(a,px,pz,-w,.018)
    left1=sample_cross(b,px,pz,w,.018);right1=sample_cross(b,px,pz,-w,.018)
    road_mesh.quad('road_asphalt',left0,left1,right1,right0,twosided=True)
    for side in (-1,1):
        e0=sample_cross(a,px,pz,side*(w+.09),.020)
        e1=sample_cross(b,px,pz,side*(w+.09),.020)
        road_mesh.quad('road_patinated_edge', sample_cross(a,px,pz,side*w,.019),e0,e1,sample_cross(b,px,pz,side*w,.019),twosided=True)
# Narrow articulated stone edges, not a surveyed drainage channel.
for i in range(0,len(newseg)-2,2):
    a,b=newseg[i],newseg[min(i+2,len(newseg)-1)];dx=b['x']-a['x'];dz=b['z']-a['z'];d=math.hypot(dx,dz)
    if d<.03:continue
    nx,nz=-dz/d,dx/d
    for side in (-1,1):
        mx=(a['x']+b['x'])/2+nx*side*3.18;mz=(a['z']+b['z'])/2+nz*side*3.18
        road_mesh.box('stone_warm_grey',mx,(a['y']+b['y'])/2+.016,mz,d-.02,.027,.14,math.atan2(-dz,dx))
# Transition pad: fan projected from the original road end; connects existing southbound road cross section to eastward extension.
# It is also provided as collision geometry; not a claim of site curb height.
a=newseg[0];center=(a['x'],a['y']+.014,a['z'])
for i in range(24):
    ang0=i*2*math.pi/24;ang1=(i+1)*2*math.pi/24
    p0=(a['x']+3.1*math.cos(ang0),a['y']+.014,a['z']+3.1*math.sin(ang0))
    p1=(a['x']+3.1*math.cos(ang1),a['y']+.014,a['z']+3.1*math.sin(ang1))
    road_mesh.tri('road_asphalt',center,p0,p1)
road_info=road_mesh.save(OUT/'v004_merchant_road.glb')

facade=Geometry()
rng=random.Random(2026110104)
# Only these named facades are advanced in V004. Names and polygons are OSM; all details remain artist estimates.
BUILD_PLAN=[
    ('way/283905599','高等学問所',+1,'plaster_offwhite','gallery'),
    ('way/283905598','北京亭',+1,'plaster_warm','restaurant'),
    ('way/283905593','七万石',-1,'plaster_offwhite','shop'),
]
post_polys=[];building_reports=[]

def front_porch_masses(xmin,xmax,face_z,front_sign,base,tone,sty):
    L=xmax-xmin
    # facade screen in front of immutable grey OSM polygon, opaque from street
    facade.box(tone,(xmin+xmax)/2,base+2.74,face_z+front_sign*.28,L+.45,4.65,.62)
    facade.box('stone_foot',(xmin+xmax)/2,base+.28,face_z+front_sign*.68,L+.5,.55,1.18)
    # dark inset window/door group; black insets have independent timber grille
    facade.box('wood_dark',(xmin+xmax)/2,base+2.02,face_z+front_sign*.68,L-.78,2.72,.10)
    facade.box('paper_panels',(xmin+xmax)/2,base+2.18,face_z+front_sign*.735,L-1.18,1.96,.022)
    # recessed door silhouettes (interiors explicitly NOT built)
    dw=min(1.65,L/6)
    facade.box('panel_black',(xmin+xmax)/2+L*.14,base+1.55,face_z+front_sign*.77,dw,2.74,.023)
    facade.box('wood_lintel',(xmin+xmax)/2+L*.14,base+2.91,face_z+front_sign*.79,dw+.28,.10,.09)
    facade.box('wood_timber',(xmin+xmax)/2,base+3.42,face_z+front_sign*.76,L+.14,.17,.2)
    # grid on lower frontage
    n=max(5,round(L/.44))
    for i in range(n+1):
        x=xmin+.35+(L-.7)*i/n
        facade.box('wood_timber',x,base+2.13,face_z+front_sign*.80,.075,2.60,.11)
        if i%4==0:
            facade.box('wood_patina',x,base+3.52,face_z+front_sign*.81,.12,.19,.14)
    for yy in [1.35,2.52,3.15]:
        facade.box('wood_timber',(xmin+xmax)/2,base+yy,face_z+front_sign*.83,L-.40,.078,.13)
    for yy in [4.15,4.96]:
        facade.box('wood_dark',(xmin+xmax)/2,base+yy,face_z+front_sign*.77,L+.22,.15,.16)
    # upstairs narrow lattice, visually distinctive rather than generic empty blocks
    facade.box('panel_black',(xmin+xmax)/2,base+4.29,face_z+front_sign*.77,L-.85,.88,.045)
    count=max(6,round(L/.28))
    for i in range(count+1):
        facade.box('wood_patina',xmin+.42+(L-.84)*i/count,base+4.31,face_z+front_sign*.82,.045,.84,.07)
    # clear shallow colonnade/porch
    porch_z=face_z+front_sign*1.56
    facade.box('wood_timber',(xmin+xmax)/2,base+3.68,porch_z,L+.82,.16,.24)
    facade.box('wood_lintel',(xmin+xmax)/2,base+3.88,face_z+front_sign*.84,L+.85,.14,1.64)
    posts=[]
    n=max(3,round(L/2.8))
    for i in range(n+1):
        x=xmin+.33+(L-.66)*i/n
        facade.box('stone_warm_grey',x,base+.16,porch_z,.46,.31,.46)
        facade.box('wood_timber',x,base+1.98,porch_z,.19,3.64,.19)
        facade.box('wood_dark',x,base+3.72,porch_z,.31,.26,.31)
        # original-looking but nonsurveyed short wooden bracket
        facade.box('wood_lintel',x,base+3.56,porch_z-front_sign*.22,.14,.15,.62)
        post_polys.append({'id':f'V004_{sty}_porchpost_{i}', 'stage':'B','polygon':[[x-.15,porch_z-.15],[x+.15,porch_z-.15],[x+.15,porch_z+.15],[x-.15,porch_z+.15]],'minY':base,'maxY':base+3.84,'provenance':'artist-estimated porch post'})
        posts.append(x)
    # floor with restrained irregular stone cut lines, original content only
    for k in range(max(2,round(L/1.0))):
        x=xmin+.48+(L-.96)*(k+.5)/max(2,round(L/1.0))
        facade.box('stone_warm_grey',x,base+.028,face_z+front_sign*1.05,.75,.055,.48)
    return posts

def roof(xmin,xmax,zmin,zmax,base,color='tile_ash'):
    ex=.55;ez=.62
    xmin-=ex;xmax+=ex;zmin-=ez;zmax+=ez
    zmid=(zmin+zmax)/2
    y_eave=base+5.19;y_ridge=base+7.07
    # Wooden deck under a true two-plane sloped roof.
    for zl,zr in [(zmin,zmid),(zmid,zmax)]:
        facade.quad('wood_dark',(xmin,y_eave,zl),(xmax,y_eave,zl),(xmax,y_ridge,zmid),(xmin,y_ridge,zmid),twosided=True) if zl==zmin else facade.quad('wood_dark',(xmin,y_ridge,zmid),(xmax,y_ridge,zmid),(xmax,y_eave,zr),(xmin,y_eave,zr),twosided=True)
    for x in (xmin,xmax):
        facade.tri('plaster_lower',(x,base+5.05,zmin),(x,base+5.05,zmax),(x,y_ridge,zmid))
        for z0 in np.linspace(zmin,zmax,9):
            yy=base+5.08+(y_ridge-(base+5.08))*(1-abs(z0-zmid)/((zmax-zmin)/2))
            facade.box('wood_lintel',x+(0.03 if x==xmax else -.03),base+5.00+(yy-(base+5.08))/2,z0,.09,max(.1,yy-(base+5.08)),.07)
    # Fine independent overlay on each original gabled roof, no copied photo texture.
    for side in (-1,1):
        z_end=zmin if side==-1 else zmax
        steps=math.ceil(abs(z_end-zmid)/.37)
        cols=math.ceil((xmax-xmin)/.31)
        for row in range(steps):
            t0=row/steps;t1=(row+1)/steps
            za=zmid+(z_end-zmid)*t0;zb=zmid+(z_end-zmid)*t1
            ya=y_ridge+(y_eave-y_ridge)*t0;yb=y_ridge+(y_eave-y_ridge)*t1
            for ci in range(cols):
                x0=xmin+(xmax-xmin)*ci/cols;x1=xmin+(xmax-xmin)*(ci+1)/cols
                colmat=['tile_ash','tile_slate','tile_variation','tile_ash','tile_ash','tile_lit'][rng.randrange(6)]
                p=[]
                for x in [x0,x0+(x1-x0)/2,x1]:
                    for zz,yy in [(za,ya),(zb,yb)]:
                        hump=.037*(1-abs(2*(x-x0)/(x1-x0)-1))
                        p.append((x,yy+.028+hump,zz))
                facade.poly(colmat,p,[(0,1,3),(0,3,2),(2,3,5),(2,5,4)])
        facade.cylinder_x('ridge_tile',xmin,xmax,y_eave+.03,z_end,.10,8)
    facade.cylinder_x('ridge_tile',xmin,xmax,y_ridge+.035,zmid,.16,10)
    # Ridge coping in distinct sections, subdued silver edging.
    for i in range(math.ceil((xmax-xmin)/.54)):
        x0=xmin+i*(xmax-xmin)/math.ceil((xmax-xmin)/.54)
        x1=min(xmax,x0+(xmax-xmin)/math.ceil((xmax-xmin)/.54))
        facade.cylinder_x('tile_slate',x0,x1,y_ridge+.08,zmid,.145,8)
        facade.box('ridge_tile',(x0+x1)/2,y_ridge+.22,zmid,x1-x0,.075,.20)
    # Roof tips curled slightly, not a claimed faithful reproduction of ridge finials.
    for x in [xmin+.10,xmax-.10]:
        facade.box('ridge_tile',x,y_ridge+.21,zmid,.25,.22,.30)

def porch_roof(xmin,xmax,face_z,front_sign,base):
    # second lower lean-to roof over the walkway side
    z0=face_z-front_sign*.14;z1=face_z+front_sign*2.06
    x0=xmin-.5;x1=xmax+.5
    facade.quad('wood_dark',(x0,base+4.04,z0),(x1,base+4.04,z0),(x1,base+3.57,z1),(x0,base+3.57,z1),twosided=True)
    cols=max(10,math.ceil((x1-x0)/.29));rows=6
    for ci in range(cols):
        xl=x0+(x1-x0)*ci/cols;xr=x0+(x1-x0)*(ci+1)/cols
        for row in range(rows):
            t0=row/rows;t1=(row+1)/rows
            a=z0+(z1-z0)*t0;b=z0+(z1-z0)*t1
            yy0=base+4.055-.47*t0;yy1=base+4.055-.47*t1
            mat='tile_variation' if (ci*7+row*13)%11==0 else 'tile_slate'
            facade.quad(mat,(xl,yy0,a),(xr,yy0+.023,a),(xr,yy1+.012,b),(xl,yy1,b),twosided=True)
    facade.cylinder_x('ridge_tile',x0,x1,base+3.60,z1,.095,8)
    for i in range(max(5,int((x1-x0)/.75))):
        x=x0+(x1-x0)*(i+.5)/max(5,int((x1-x0)/.75))
        facade.box('wood_lintel',x,base+3.49,z1-front_sign*.14,.065,.35,.33)

def sign_mesh(text,style,x,y,z,face_sign,size=(.64,1.55)):
    w,h=size
    img=Image.new('RGBA',(384,768),(39,32,23,255));d=ImageDraw.Draw(img)
    d.rounded_rectangle((20,20,364,748),radius=15,fill=(208,164,86,255),outline=(43,32,23,255),width=18)
    d.rectangle((36,36,348,732),outline=(80,58,27,255),width=3)
    font_path='/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
    font=ImageFont.truetype(font_path,108,index=0)
    tw=''.join(c+'\n' for c in text).rstrip('\n')
    bb=d.multiline_textbbox((0,0),tw,font=font,spacing=3,stroke_width=0)
    height=bb[3]-bb[1]
    d.multiline_text((192-bb[2]/2,384-height/2),tw,font=font,fill=(36,31,26),spacing=2)
    # Geometric, original decorative corners. No copyrighted logos.
    for xx in (55,329):
        for yy in (63,705):d.ellipse((xx-5,yy-5,xx+5,yy+5),fill=(63,51,35,255))
    v=[(x-w/2,y-h/2,z),(x+w/2,y-h/2,z),(x+w/2,y+h/2,z),(x-w/2,y+h/2,z)]
    if face_sign==-1:
        v=[v[1],v[0],v[3],v[2]]
    visual=TextureVisuals(uv=np.array([[0,0],[1,0],[1,1],[0,1]],dtype=np.float32),material=PBRMaterial(name=f'V004_original_sign_{style}',baseColorTexture=img,metallicFactor=0,roughnessFactor=.9,doubleSided=True))
    m=trimesh.Trimesh(vertices=v,faces=np.array([[0,1,2],[0,2,3]]),process=False,visual=visual)
    return m

signage=trimesh.Scene()
for id,name,sgn,tone,style in BUILD_PLAN:
    b=BUILDINGS[id];poly=b['polygon'];xmin=min(p[0] for p in poly);xmax=max(p[0] for p in poly)
    zvalues=[-p[1] for p in poly];zmin=min(zvalues);zmax=max(zvalues)
    base=float(b['base']); face_z=zmax if sgn==1 else zmin
    # Protect existing named OSM footprint. Opaque shell behind new exterior facade.
    facade.box(tone,(xmin+xmax)/2,base+2.9,(zmin+zmax)/2,(xmax-xmin)+.40,5.40,(zmax-zmin)+.40)
    # Variations in wall plasters avoid three identical facades.
    facade.box('plaster_lower',(xmin+xmax)/2,base+.66,face_z+sgn*.3,xmax-xmin+.50,1.12,.59)
    facade.box('wood_dark',(xmin+xmax)/2,base+4.98,face_z+sgn*.38,xmax-xmin+.56,.18,.34)
    # Vertical timber courses on wall face and ends.
    for x in np.linspace(xmin+.1,xmax-.1,max(4,int((xmax-xmin)/2.0)+1)):
        facade.box('wood_timber',x,base+2.85,face_z+sgn*.62,.15,5.40,.18)
    for z in (zmin+.3,zmax-.3):
        for x in [xmin+.25,xmax-.25]:
            facade.box('wood_dark',x,base+2.9,z,.15,5.30,.20)
    # Treat all EXPOSED side walls as architectural facades, not bare cuboid ends.
    # These side window and joint layouts are original proposals awaiting photographic checks.
    for x,extsign in ((xmin,-1),(xmax,+1)):
        side_x=x+extsign*.31
        side_width=zmax-zmin
        for yy in (.63,2.65,4.72,5.05):
            facade.box('wood_timber',side_x,base+yy,(zmin+zmax)/2,.12,.14,side_width+.26)
        for i in range(max(3,int(side_width/1.7))):
            zz=zmin+.37+(side_width-.74)*(i+.5)/max(3,int(side_width/1.7))
            facade.box('wood_dark',side_x,base+2.83,zz,.12,4.74,.15)
        # A dark paper-panel window split by handmade mullions, no invented interior.
        wz=(zmin+zmax)/2
        facade.box('wood_dark',side_x+extsign*.08,base+3.45,wz,.075,1.12,min(3.5,side_width-.9))
        facade.box('paper_panels',side_x+extsign*.13,base+3.45,wz,.035,.87,min(3.24,side_width-1.10))
        for zz in np.linspace(wz-min(1.5,side_width/2-.6),wz+min(1.5,side_width/2-.6),8):
            facade.box('wood_patina',side_x+extsign*.17,base+3.45,zz,.06,1.0,.06)
        facade.box('wood_timber',side_x+extsign*.17,base+3.50,wz,.065,.09,min(3.3,side_width-1.0))
        # Vertical gable slats, not claimed to reproduce a specific documented ornament.
        zmid=(zmin+zmax)/2
        for zz in np.linspace(zmin+.75,zmax-.75,9):
            height=1.72*(1-abs(zz-zmid)/max(.01,(zmax-zmin)/2))
            if height>.15:
                facade.box('wood_lintel',side_x+extsign*.08,base+5.1+height/2,zz,.12,height,.09)
        # Small original wooden joints and cross-brace marks, deliberately restrained.
        for zz in np.linspace(zmin+.9,zmax-.9,6):
            facade.box('wood_grain_light',side_x+extsign*.11,base+2.65,zz,.023,.040,.20)
    # Rear elevations are not documented, so use subdued timber framing rather than
    # falsely inventing doors, decorative signs or open interiors.
    rear_z=(zmin if sgn==1 else zmax)-sgn*.31
    facade.box('wood_dark',(xmin+xmax)/2,base+4.91,rear_z,(xmax-xmin)+.38,.17,.15)
    for xx in np.linspace(xmin+.22,xmax-.22,max(5,int((xmax-xmin)/1.8)+1)):
        facade.box('wood_timber',xx,base+2.90,rear_z,.115,5.15,.10)
    for yy in (1.10,2.72,4.36):
        facade.box('wood_patina',(xmin+xmax)/2,base+yy,rear_z,(xmax-xmin)+.18,.09,.10)
    # Narrow high windows imply no accessible building interior.
    facade.box('panel_black',(xmin+xmax)/2,base+3.75,rear_z-sgn*.045,(xmax-xmin)*.70,.64,.03)
    for xx in np.linspace(xmin+(xmax-xmin)*.15,xmax-(xmax-xmin)*.15,max(9,int((xmax-xmin)/.48))):
        facade.box('wood_timber',xx,base+3.75,rear_z-sgn*.095,.065,.66,.055)
    posts=front_porch_masses(xmin,xmax,face_z,sgn,base,tone,style)
    roof(xmin,xmax,zmin,zmax,base)
    porch_roof(xmin,xmax,face_z,sgn,base)
    # Traditional hanging name signage (location/size estimated), not copied from photographs.
    if style in ('restaurant','shop'):
        sx=xmax-.9 if style=='restaurant' else xmin+.9
        sz=face_z+sgn*2.13
        facade.box('wood_dark',sx,base+3.45,sz,.09,2.2,.09)
        facade.box('wood_lintel',sx,base+4.42,sz-sgn*.19,.89,.12,.52)
        signage.add_geometry(sign_mesh(name,style,sx,base+2.72,sz+sgn*.13,sgn))
    building_reports.append({'osm_id':id,'name':name,'evidence':'OSM name/footprint; generic photographs and official site, NOT measured elevation','footprint_enu_m':poly,'floor_base_m':base,'roof_height_estimated_m':7.07,'road_facing_side':('south' if sgn==1 else 'north'),'porch_posts':len(posts),'interior':'not_modelled','sign_position':'author_estimate' if style!='gallery' else 'none'})
# More subtle street character: site-safe standalone small wooden lamp along new edge,
# kept out of the walking corridor and labelled artist-proposed, not survey.
for x,z,y in [(19.5,57.20,1.26),(39.9,65.65,1.52)]:
    facade.box('stone_foot',x,y+.22,z,.51,.44,.51)
    facade.box('wood_timber',x,y+1.55,z,.20,2.8,.20)
    facade.box('wood_dark',x,y+3.10,z,.70,.19,.65)
    for sg in (-1,1):
        facade.box('paper_panels',x+sg*.26,y+2.74,z,.025,.56,.42)
        facade.box('wood_dark',x+sg*.26,y+2.75,z,.035,.68,.06)
        facade.box('paper_panels',x,y+2.74,z+sg*.25,.45,.56,.02)
    facade.box('wood_timber',x,y+3.28,z,.84,.10,.73)
    post_polys.append({'id':f'V004_author_lantern_{x}', 'stage':'B','polygon':[[x-.26,z-.26],[x+.26,z-.26],[x+.26,z+.26],[x-.26,z+.26]],'minY':y,'maxY':y+3.45,'provenance':'author-estimated lantern position'})

facade_info=facade.save(OUT/'v004_merchant_facades.glb')
# Add original (self-made) textured signs as an immutable append-only GLB scene.
# This scene is not the full B model, and is B-only in runtime.
for name,mesh in signage.geometry.items():
    # Reopening facade GLB and appending scenes would recompute original buffers;
    # a separate texture-sign GLB avoids touching facades or V003 models.
    pass
(OUT/'v004_merchant_signs.glb').write_bytes(signage.export(file_type='glb'))

# Render mesh follows EUS, road & collision surfaces share same design coordinates.
road_collision_vertices=[];road_collision_tris=[]
for i in range(len(newseg)-1):
    a,b=newseg[i:i+2];dx=b['x']-a['x'];dz=b['z']-a['z']
    elapsed=math.hypot(a['x']-newseg[0]['x'],a['z']-newseg[0]['z'])
    w=3.4-.4*min(elapsed/2,1)
    aa=sample_cross(a,dx,dz,+w,0);ab=sample_cross(a,dx,dz,-w,0)
    ba=sample_cross(b,dx,dz,+w,0);bb=sample_cross(b,dx,dz,-w,0)
    t=len(road_collision_vertices);road_collision_vertices.extend([aa,ab,ba,bb]);road_collision_tris.extend([[t,t+1,t+2],[t+2,t+1,t+3]])
# Shared turn footprint overlap at start prevents tiny seam gaps. Disc constant elevation is author approximation;
# the angular road turning area is not a claim of original survey geometry.
t=len(road_collision_vertices)
a=newseg[0]
road_collision_vertices.append((a['x'],a['y'],a['z']))
for i in range(32):
    t0=i*2*math.pi/32
    road_collision_vertices.append((a['x']+3.1*math.cos(t0),a['y'],a['z']+3.1*math.sin(t0)))
for i in range(32):road_collision_tris.append([t,t+1+i,t+1+(i+1)%32])
# Collision triangles, not new surveyed geography; old walkable and obstacle values remain intact.
assert len(BASE_COLL['walkable'])==3 and len(BASE_COLL['obstacles'])==58
extension_collision={
    'schema':'noboribetsu-date-v004-merchant-extension/1',
    'axes':'Three EUS',
    'walkable':[{'id':'V004_east_lane_author_width','stage':'both','vertices':[list(p) for p in road_collision_vertices],'triangles':road_collision_tris,
         'provenance':'OSM centerline + GSI interpolated end elevations; 6m author-estimated cross section'}],
    'obstacles':post_polys,
    'untouched_base_collision_sha256':hashlib.sha256((DST/'collision.json').read_bytes()).hexdigest(),
    'note':'No new building interiors or drainage. Named building original OSM footprint obstacles inherited unchanged.'
}
(DST/'extension_collision.json').write_text(json.dumps(extension_collision,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

model_paths=['v004_merchant_road.glb','v004_merchant_facades.glb','v004_merchant_signs.glb']
models={}
for name in model_paths:
    path=OUT/name
    models[name]={'path':'assets/'+name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}

ext={
 'schema':'noboribetsu-date-v004-merchant/1',
 'status':'candidate_not_blender_native_or_android_verified',
 'base_source':'V003 R3 Runtime (unchanged 40 model/transport assets)',
 'route_previous_length_m':BASE_ROUTE[-1]['s'],
 'route_new_length_m':route[-1]['s'],
 'added_length_m':route[-1]['s']-BASE_ROUTE[-1]['s'],
 'full_original_osm_length_m':231.0737488061252,
 'new_segment_start_eus':{k:anchors[0][k] for k in ['x','y','z']},
 'new_segment_end_eus':{k:anchors[-1][k] for k in ['x','y','z']},
 'road_visual_width_m':'estimated 6m (taper from prior 6.8m); not surveyed',
 'known_buildings':building_reports,
 'models':models,
 'geometry_stats':{'road':road_info,'facades':facade_info},
 'collision':{'path':'extension_collision.json','sha256':hashlib.sha256((DST/'extension_collision.json').read_bytes()).hexdigest(),'new_walkable_triangles':len(road_collision_tris),'new_obstacles':len(post_polys)},
 'provenance':{
   'osm':'OSM way/284064756, snapshot 2026-10-31, © OpenStreetMap contributors, ODbL',
   'terrain':'GSI DEM1A in V002 source; heights at route endpoints/interpolated, not surveyed',
   'official_map':'https://edo-trip.jp/map/ (reference only, not redistributed)',
   'site_evidence':'https://edo-trip.jp/tw/eat/ ; https://edo-trip.jp/buy/ (identity only)',
   'appearance':'original procedurally authored extrapolation from generic public street photos; NOT a faithful measured elevation',
   'textures':'All tiles, structures, signs original procedural and locally generated; no third-party photographs packed',
   'license':'V002 original source and 3rd-party attributions remain in separate V002 Complete ZIP',
 },
 'verification':{'source_route':'frozen V002','source_building_names':'frozen V002 OSM','blender_native':'not run','render_in_browser':'not run','Android':'not run','private_CDN':'not run'}
}
(DST/'extension_manifest.json').write_text(json.dumps(ext,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Inherited view is kept separate in a V004 manifest; no mutation of the V003 R3 source archive.
view=dict(BASE_VIEW)
view['version']='V004-merchant-candidate-r1'
view['route']=route
view['scope']='First eastward merchant-street segment: OSM route + three named, author-estimated exteriors; no interiors; B full-quality V003 unchanged.'
view['extension']={'manifest':'extension_manifest.json','models':models,'collision':'extension_collision.json','building_ids':[b['osm_id'] for b in building_reports],
    'added_length_m':ext['added_length_m'],'stage_A':'Existing unrefined baseline plus common extension road', 'stage_B':'Existing B refinement plus V004 merchant exterior overlay'}
(DST/'scene_view.json').write_text(json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
(DST/'qa_v004_build.json').write_text(json.dumps({'status':'models_generated_not_browser_tested','extension':ext},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'length_old':BASE_ROUTE[-1]['s'],'length_new':route[-1]['s'],'new_route_points':len(route)-len(BASE_ROUTE),'models':models,'facades':len(building_reports),'extension_ground_triangles':len(road_collision_tris),'extension_obstacles':len(post_polys),'facade_triangles':sum(x['triangles'] for x in facade_info.values())},ensure_ascii=False,indent=2))