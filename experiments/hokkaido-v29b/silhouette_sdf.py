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
# Turn hand-authored FRONT/SIDE silhouettes into a rounded surface rather
# than intersecting two squared extrusions (which made v29 a shoebox).
# Head radius at every Z must simultaneously match the hand-drawn X/Z
# bounds and Y/Z bounds. The cross-section is smooth/rounded, unlike v29.
def rounded_head_from_two_profiles(sxz,syz):
    xmid=np.empty(len(Z),dtype=np.float32)
    xrad=np.empty(len(Z),dtype=np.float32)
    yrad=np.empty(len(Z),dtype=np.float32)
    validz=np.zeros(len(Z),dtype=bool)
    for k in range(len(Z)):
        a=np.flatnonzero(sxz[:,k]>0)
        b=np.flatnonzero(syz[:,k]>0)
        if len(a)>1 and len(b)>1:
            validz[k]=True
            xmid[k]=(X[a[0]]+X[a[-1]])*.5
            xrad[k]=max((X[a[-1]]-X[a[0]])*.5,.001)
            yrad[k]=max((Y[b[-1]]-Y[b[0]])*.5,.001)
        else:
            xmid[k]=-1.83
            xrad[k]=.001
            yrad[k]=.001
    cx=xmid[None,None,:];rx=xrad[None,None,:];ry=yrad[None,None,:]
    ellipse=np.sqrt(((xx-cx)/rx)**2+(yy/ry)**2)
    return np.where(validz[None,None,:],
                    (1-ellipse)*np.minimum(rx,ry),-2.)
# Turn a jaw side PROFILE into a rounded, not extruded, asymmetric 3D
# surface. The cheek hinge overlaps skull and stays physically fused.
def jaw_from_side_profile(polygon,width_stations):
    sd=sdf_polygon(X,Z,polygon)
    zmid=np.empty(len(X),dtype=np.float32)
    zrad=np.empty(len(X),dtype=np.float32)
    validx=np.zeros(len(X),dtype=bool)
    for i in range(len(X)):
        vals=np.flatnonzero(sd[i,:]>0)
        if len(vals)>1:
            validx[i]=True
            zmid[i]=(Z[vals[0]]+Z[vals[-1]])*.5
            zrad[i]=max((Z[vals[-1]]-Z[vals[0]])*.5,.001)
        else:
            zmid[i]=1.
            zrad[i]=.001
    width=np.interp(X,*width_stations).astype(np.float32)
    zc=zmid[:,None,None];zr=zrad[:,None,None]
    wy=width[:,None,None]
    r=np.sqrt((yy/wy)**2+((zz-zc)/zr)**2)
    return np.where(validx[:,None,None],
                    (1-r)*np.minimum(wy,zr),-2.)

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
side2=sdf_polygon(X,Z,head_side)
front2=sdf_polygon(Y,Z,head_front)
head=rounded_head_from_two_profiles(side2,front2)
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
lip_u=jaw_from_side_profile(upper_xz,(
    [-3,-2.75,-2.55,-2.32,-1.90,-1.0],[.10,.14,.20,.265,.36,.41]))
lip_l=jaw_from_side_profile(lower_xz,(
    [-3,-2.75,-2.55,-2.32,-1.90,-1.0],[.10,.12,.17,.23,.29,.36]))
head=smoothmax(head,lip_u,.036)
head=smoothmax(head,lip_l,.037)
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
head=gaussian_filter(head,sigma=1.25)
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
fish=smoothmax(fish,smoothmin(tail_mask,twidth,.018),.038)
# A broad physical caudal-peduncle bridge ensures a fin cannot float.
# Unlike a glued visual decal, this bridge is part of the same SDF volume.
caudal_bridge=sdf_polygon(Y,Z,[(.935,.904),(1.230,.917),
                              (1.255,.966),(.935,1.002)])[None,:,:]
caudal_width=.053-np.abs(xx+2.590)
fish=smoothmax(fish,smoothmin(caudal_bridge,caudal_width,.015),.031)
# Dorsal and pectoral fins are curved volumes penetrating the fish.
dorsal=[(.15,1.08),(.26,1.218),(.39,1.244),(.52,1.082)]
anal=[(.39,.776),(.49,.636),(.64,.804)]
for profile,width in [(dorsal,.038),(anal,.031)]:
    surface=sdf_polygon(Y,Z,profile)[None,:,:]
    sheet=width-np.abs(xx+2.6)
    fish=smoothmax(fish,smoothmin(surface,sheet,.013),.030)
for sign in [-1,1]:
    pectoral=[(-.93,.893),(-.70,.684),(-.52,.818),(-.71,.935)]
    mask=sdf_polygon(Y,Z,pectoral)[None,:,:]
    # Move pectoral fin ROOT inside flank; its outside wing still projects.
    sheet=.066-np.abs(xx-(-2.61+sign*.104))
    fish=smoothmax(fish,smoothmin(mask,sheet,.016),.035)
# Carve salmon ocular depressions and two unmistakable oblique operculum
# grooves into highpoly mesh; do not paint fake floating pupils.
for sign in [-1,1]:
    eye=(.031-np.sqrt(((xx-(-2.61+sign*.159))/.92)**2+
                        ((yy+1.153)/1.00)**2+
                        ((zz-.909)/1.00)**2))
    fish=smoothmin(fish,-eye,.003)
    # Gill incisions will be carved via local vertex-normal displacement
    # AFTER marching cubes; subtractive VDB cutters here previously carved
    # off a 116-vertex fish-flank strip, failing component integrity QA.
fish=gaussian_filter(fish,sigma=1.13)
def extract(name,field):
    verts,faces,normals,values=marching_cubes(field,level=0.0,spacing=(STEP,STEP,STEP),
                                             allow_degenerate=False)
    verts+=np.array([X[0],Y[0],Z[0]])
    m=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
    trimesh.smoothing.filter_taubin(m,lamb=.43,nu=-.49,iterations=7)
    trimesh.repair.fix_normals(m)
    if name=="v29b_salmon":
        # Surface-only nonsevering incisions: deform existing fish skin,
        # preserving original faces/edge connectivity exactly.
        normals=m.vertex_normals.copy()
        vv=m.vertices.copy()
        affected=0
        for i,p in enumerate(vv):
            x,y,z=p
            if -.99<y<-.66 and .70<z<1.09 and abs(normals[i,0])>.37:
                for gy in [-.931,-.848]:
                    target=gy+.17*(z-.90)
                    d=abs(y-target)
                    if d<.018:
                        depth=.011*(1-d/.018)
                        vv[i,0]-=np.sign(normals[i,0])*depth
                        affected+=1
        m.vertices=vv
        print("V29B_REAL_GILL_VERTEX_STROKES",affected,flush=True)
    parts=m.split(only_watertight=False)
    # Never silently remove a substantial disconnected sculpt feature.
    if len(parts)>1:
        sizes=sorted([len(p.vertices) for p in parts],reverse=True)
        if sum(sizes[1:])>20:
            raise RuntimeError("%s detached geometry: %s; bounds: %s"%(name,sizes,
                [np.round(p.bounds,3).tolist() for p in parts]))
        m=max(parts,key=lambda p:len(p.vertices))
    assert m.is_watertight, (name,"open edges")
    assert len(m.faces)>1500,name
    dest=OUT/(name+".ply")
    m.export(str(dest))
    return {"ply":dest.name,"vertices":len(m.vertices),"triangles":len(m.faces),
            "watertight":bool(m.is_watertight),"components":1,
            "bbox":[list(map(lambda n:round(float(n),3),row)) for row in m.bounds]}
headq=extract("v29b_bear_head",head)
fishq=extract("v29b_salmon",fish)
report={
 "pipeline":"two 2D outline masks + signed-distance intersection/union -> marching cubes -> Blender",
 "stage":"v29b rounded cross-section silhouette experiment, not game approved",
 "source":"experiments/hokkaido-v29b/silhouette_sdf.py",
 "original_control_points":True,
 "reference_only_no_copied_model":True,
 "grid_step":STEP,
 "round_volume_from_2d_profiles":True,
 "taubin_mesh_smoothing_iterations":7,
 "bear_head":headq,"salmon":fishq,
 "art_quality":"UNREVIEWED","approved_for_game":False
}
(OUT/"shape_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
print("V29B_SILHOUETTE_SDF_SUCCESS",json.dumps(report),flush=True)
