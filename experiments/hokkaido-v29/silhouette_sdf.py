"""Hokkaido v29: original 2D silhouette constrained 3D signed-distance sculpt.
Instead of lofted ellipsoid sections, intersect hand-authored SIDE and FRONT
silhouette masks; embed jaw negative space; carve face and salmon anatomy.
The contours were artist-authored after studying Hokkaido wooden bear photos,
NOT traced/reproduced from a copyrighted commercial image or 3D file.
Outputs distinct watertight PLY meshes for genuine offline Blender conversion.
"""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt,gaussian_filter
from skimage.draw import polygon2mask
from skimage.measure import marching_cubes
import trimesh

OUT=Path("candidate");OUT.mkdir(exist_ok=True,parents=True)
STEP=.021
X=np.arange(-3.04,-1.00,STEP,dtype=np.float32)
Y=np.arange(-1.58,1.59,STEP,dtype=np.float32)
Z=np.arange(.44,1.99,STEP,dtype=np.float32)
xx=X[:,None,None];yy=Y[None,:,None];zz=Z[None,None,:]
# Signed distance positive INSIDE silhouette.
def sdf_polygon(axes0,axes1,polygon):
    poly=np.asarray(polygon,dtype=np.float32)
    pix=np.column_stack(((poly[:,0]-axes0[0])/STEP,
                          (poly[:,1]-axes1[0])/STEP))
    mask=polygon2mask((len(axes0),len(axes1)),pix)
    a=distance_transform_edt(mask);b=distance_transform_edt(~mask)
    return (a-b).astype(np.float32)*STEP
def smoothmax(a,b,k=.029):
    # Smooth union of two positive-inside signed distance fields.
    return np.maximum(a,b)+np.log1p(np.exp(-np.abs(a-b)/k))*k
def smoothmin(a,b,k=.024):
    return -smoothmax(-a,-b,k)
# Author-constructed natural bear profile: forward = smaller X;
# shoulder slope, brow, descending muzzle & continuous thick rear chin.
head_side=[
 (-2.39,1.25),(-2.35,1.39),(-2.23,1.53),(-2.11,1.65),
 (-1.95,1.76),(-1.75,1.84),(-1.53,1.85),(-1.31,1.74),
 (-1.18,1.59),(-1.12,1.42),(-1.12,1.11),(-1.24,.97),
 (-1.44,.85),(-1.65,.83),(-1.86,.85),(-2.02,.94),
 (-2.14,1.04),(-2.24,1.17)]
# Anatomical broad cheeks taper to narrower lower face when viewed front.
head_front=[
 (-.21,.81),(.21,.81),(.36,.93),(.45,1.08),(.53,1.34),
 (.49,1.54),(.38,1.73),(.22,1.85),(-.22,1.85),
 (-.38,1.73),(-.49,1.54),(-.53,1.34),(-.45,1.08),(-.36,.93)]
side=headside=sdf_polygon(X,Z,head_side)[:,None,:]
front=sdf_polygon(Y,Z,head_front)[None,:,:]
head=smoothmin(side,front,.045)
# Two artist-made lip silhouette polygons in X,Z, not spherical add-ons.
upper_xz=[
 (-2.77,1.157),(-2.74,1.228),(-2.61,1.271),
 (-2.46,1.284),(-2.30,1.319),(-2.14,1.377),
 (-2.02,1.312),(-2.05,1.117),(-2.24,1.097),
 (-2.42,1.097),(-2.62,1.100)]
lower_xz=[
 (-2.77,.692),(-2.73,.660),(-2.57,.646),(-2.41,.650),
 (-2.27,.693),(-2.13,.738),(-2.01,.841),(-1.86,.984),
 (-1.83,1.097),(-2.02,1.016),(-2.18,.880),
 (-2.37,.795),(-2.57,.767),(-2.72,.769)]
lip_u=sdf_polygon(X,Z,upper_xz)[:,None,:]
lip_l=sdf_polygon(X,Z,lower_xz)[:,None,:]
# Round-edged lateral constraint: x-dependent width narrows at nose.
hwidth=np.interp(X,[-3,-2.75,-2.55,-2.32,-1.90,-1.00],
                 [.10,.14,.19,.26,.38,.45]).astype(np.float32)[:,None,None]
lateral=hwidth-np.abs(yy)
head=smoothmax(head,smoothmin(lip_u,lateral,.023),.024)
head=smoothmax(head,smoothmin(lip_l,lateral*.95,.023),.024)
# Physically OPEN C-shaped mouth by subtracting a space through the front
# between the two lips, with cavity reaching part way through the cheek.
mouth_outline=[
 (-2.92,.800),(-2.74,.794),(-2.53,.805),(-2.38,.838),
 (-2.20,.905),(-2.09,.971),(-2.08,1.068),(-2.30,1.056),
 (-2.51,1.055),(-2.77,1.068),(-2.92,1.077)]
mouth2d=sdf_polygon(X,Z,mouth_outline)[:,None,:]
mouthside=.26-np.abs(yy)
cavity=smoothmin(mouth2d,mouthside,.016)
head=smoothmin(head,-cavity,.011)
# Small integrated ears, not floating buttons.
for side_ear in [-1,1]:
    ear=(1.-np.sqrt(((xx+1.81)/.135)**2+
                     ((yy-side_ear*.37)/.12)**2+
                     ((zz-1.74)/.145)**2))*.12
    head=smoothmax(head,ear,.023)
# Carve true eye hollows on flanks, avoiding detached pupil spheres.
for sign in [-1,1]:
    hole=(.062-np.sqrt(((xx+2.25)/.064)**2*.062**2+
                       ((yy-sign*.383)/.068)**2*.062**2+
                       ((zz-1.425)/.061)**2*.062**2))
    head=smoothmin(head,-hole,.009)
head=gaussian_filter(head,sigma=.65)
# Salmon PROFILE mask Y/Z: definite tapered head, gill, thick belly, pinched
# central bite waist and a sharply narrowing tail peduncle.
fish_profile=[
 (-1.36,.884),(-1.31,.936),(-1.20,1.003),(-1.07,1.086),
 (-.91,1.135),(-.72,1.153),(-.51,1.156),(-.32,1.117),
 (-.17,1.060),(-.065,1.041),(.065,1.051),
 (.22,1.122),(.41,1.111),(.60,1.061),(.77,1.001),
 (.93,.986),(1.10,.974),
 (1.10,.924),(.93,.909),(.77,.870),(.60,.832),(.41,.757),
 (.22,.711),(.065,.737),(-.065,.752),(-.17,.706),
 (-.32,.658),(-.51,.625),(-.73,.635),(-.92,.679),
 (-1.08,.738),(-1.25,.796),(-1.36,.861)]
silhou=sdf_polygon(Y,Z,fish_profile)[None,:,:]
mid_x=(-2.61+.042*np.sin(yy*2.0))
half_x=np.interp(Y,[-1.58,-1.36,-1.20,-.95,-.65,-.31,0,
                     .2,.43,.68,.94,1.1,1.58],
                [.02,.033,.09,.164,.190,.183,.139,.172,.165,
                 .123,.060,.030,.005]).astype(np.float32)[None,:,None]
thickness=half_x-np.abs(xx-mid_x)
fish=smoothmin(silhou,thickness,.022)
# The caudal fin is an integral thin forked volume, not a flat detached decal.
tail_profile=[
 (1.02,.954),(1.27,1.116),(1.48,1.205),(1.34,1.014),
 (1.23,.951),(1.34,.887),(1.48,.720),(1.27,.790)]
tail_mask=sdf_polygon(Y,Z,tail_profile)[None,:,:]
twidth=.039-np.abs(xx+2.59)
fish=smoothmax(fish,smoothmin(tail_mask,twidth,.018),.012)
# Dorsal and pectoral fins are curved volumes penetrating the fish.
dorsal=[(.15,1.08),(.26,1.218),(.39,1.244),(.52,1.082)]
anal=[(.39,.776),(.49,.636),(.64,.804)]
for profile,width in [(dorsal,.038),(anal,.031)]:
    surface=sdf_polygon(Y,Z,profile)[None,:,:]
    sheet=width-np.abs(xx+2.6)
    fish=smoothmax(fish,smoothmin(surface,sheet,.013),.016)
for sign in [-1,1]:
    pectoral=[(-.93,.893),(-.70,.684),(-.52,.818),(-.71,.935)]
    mask=sdf_polygon(Y,Z,pectoral)[None,:,:]
    sheet=.050-np.abs(xx-(-2.61+sign*.145))
    fish=smoothmax(fish,smoothmin(mask,sheet,.016),.015)
# Carve salmon ocular depressions and two unmistakable oblique operculum
# grooves into highpoly mesh; do not paint fake floating pupils.
for sign in [-1,1]:
    eye=(.031-np.sqrt(((xx-(-2.61+sign*.159))/.92)**2+
                        ((yy+1.153)/1.00)**2+
                        ((zz-.909)/1.00)**2))
    fish=smoothmin(fish,-eye,.003)
    for gy in [-.932,-.850]:
        angleline=gy + .18*(zz-.90)
        side_cut=.026-np.abs(xx-(-2.61+sign*.172))
        gill_cut=.018-np.abs(yy-angleline)
        zlimit=np.minimum(zz-.722,1.083-zz)
        carving=smoothmin(smoothmin(side_cut,gill_cut,.007),zlimit,.006)
        fish=smoothmin(fish,-carving,.002)
fish=gaussian_filter(fish,sigma=.56)
def extract(name,field):
    verts,faces,normals,values=marching_cubes(field,level=0.0,spacing=(STEP,STEP,STEP),
                                             allow_degenerate=False)
    verts+=np.array([X[0],Y[0],Z[0]])
    m=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
    trimesh.repair.fix_normals(m)
    parts=m.split(only_watertight=False)
    # Never silently remove a substantial disconnected sculpt feature.
    if len(parts)>1:
        sizes=sorted([len(p.vertices) for p in parts],reverse=True)
        if sum(sizes[1:])>20:
            raise RuntimeError("%s detached geometry: %s"%(name,sizes))
        m=max(parts,key=lambda p:len(p.vertices))
    assert m.is_watertight, (name,"open edges")
    assert len(m.faces)>1500,name
    dest=OUT/(name+".ply")
    m.export(str(dest))
    return {"ply":dest.name,"vertices":len(m.vertices),"triangles":len(m.faces),
            "watertight":bool(m.is_watertight),"components":1,
            "bbox":[list(map(lambda n:round(float(n),3),row)) for row in m.bounds]}
headq=extract("v29_bear_head",head)
fishq=extract("v29_salmon",fish)
report={
 "pipeline":"two 2D outline masks + signed-distance intersection/union -> marching cubes -> Blender",
 "stage":"v29 reference silhouette sculpt experiment, not game approved",
 "source":"experiments/hokkaido-v29/silhouette_sdf.py",
 "original_control_points":True,
 "reference_only_no_copied_model":True,
 "grid_step":STEP,
 "bear_head":headq,"salmon":fishq,
 "art_quality":"UNREVIEWED","approved_for_game":False
}
(OUT/"shape_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
print("V29_SILHOUETTE_SDF_SUCCESS",json.dumps(report),flush=True)
