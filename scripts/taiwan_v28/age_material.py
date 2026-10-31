"""V28 restrained age-surface study on existing fictional elder characters.
Derived CC0 skin albedo + original procedural crease height, rasterized through
actual source UV triangles. Standard packed tangent normal PNG, not a Blender-
only Noise node. No new body topology, facial geometry or changed morph deltas.
"""
import math,hashlib
from pathlib import Path
import numpy as np
import bpy


def smooth(x):
    v=np.clip(x,0,1);return v*v*(3-2*v)


def save_image(name,pixels,out,noncolor=False):
    h,w=pixels.shape[:2]
    im=bpy.data.images.new(name,width=w,height=h,alpha=True,float_buffer=False)
    if noncolor:im.colorspace_settings.name='Non-Color'
    im.pixels.foreach_set(np.asarray(pixels,dtype='f4').ravel());im.file_format='PNG'
    path=out/(name+'.png');im.filepath_raw=str(path);im.save();im.pack()
    return im,{'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'width':w,'height':h}


def apply(body,eyes,cid,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    original=body.data.materials[0]
    if original is None or not original.use_nodes:raise RuntimeError('No actual source skin material')
    bs=next(n for n in original.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    link=bs.inputs['Base Color'].links[0] if bs.inputs['Base Color'].is_linked else None
    if link is None or link.from_node.type!='TEX_IMAGE':raise RuntimeError('Skin source must be a real image')
    source=link.from_node.image
    if source is None or not source.has_data:raise RuntimeError('No decoded CC0 skin pixels')
    w,h=source.size
    if w!=h or w>512:raise RuntimeError('Expected original square skin <=512')
    old=np.array(source.pixels[:],dtype='f4').reshape(h,w,4)
    source_hash=hashlib.sha256(old.tobytes()).hexdigest()
    points=np.array([tuple(body.matrix_world@v.co) for v in body.data.vertices])
    ep=np.array([tuple(eyes.matrix_world@v.co) for v in eyes.data.vertices])
    eye_z=float(np.median(ep[:,2]));eye_y=float(np.median(ep[:,1]));eye_x=float(np.mean(np.abs(ep[:,0])))
    top=float(points[:,2].max())
    # Rasterize source positions and metric lengths in the existing UV layout.
    pos=np.zeros((h,w,3));tu=np.ones((h,w));tv=np.ones((h,w));valid=np.zeros((h,w),bool)
    body.data.calc_loop_triangles();uv=body.data.uv_layers.active
    if uv is None:raise RuntimeError('Original body UV absent')
    for tri in body.data.loop_triangles:
        ids=list(tri.vertices);p=points[ids]
        normal=np.cross(p[1]-p[0],p[2]-p[0]);ln=np.linalg.norm(normal)
        if ln<1e-12 or normal[1]/ln>-.12 or p[:,2].max()<top-.28 or p[:,1].min()>eye_y+.035:continue
        q=np.array([tuple(uv.data[i].uv) for i in tri.loops])
        e1=q[1]-q[0];e2=q[2]-q[0];det=e1[0]*e2[1]-e2[0]*e1[1]
        if abs(det)<1e-12:continue
        u=(p[1]-p[0])*e2[1]-(p[2]-p[0])*e1[1];u/=det
        v=(-(p[1]-p[0])*e2[0]+(p[2]-p[0])*e1[0])/det
        x0=max(0,int(np.floor(q[:,0].min()*w)));x1=min(w-1,int(np.ceil(q[:,0].max()*w)))
        y0=max(0,int(np.floor(q[:,1].min()*h)));y1=min(h-1,int(np.ceil(q[:,1].max()*h)))
        if x1<x0 or y1<y0:continue
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1];a=(xx+.5)/w-q[0,0];b=(yy+.5)/h-q[0,1]
        b1=(a*e2[1]-b*e2[0])/det;b2=(e1[0]*b-e1[1]*a)/det
        inside=(b1>=-1e-6)&(b2>=-1e-6)&(b1+b2<=1.000001)
        rr=yy[inside];cc=xx[inside]
        pos[rr,cc]=p[0]+b1[inside,None]*(p[1]-p[0])+b2[inside,None]*(p[2]-p[0])
        tu[rr,cc]=max(np.linalg.norm(u),.01);tv[rr,cc]=max(np.linalg.norm(v),.01);valid[rr,cc]=True
    x=pos[:,:,0];y=pos[:,:,1];z=pos[:,:,2]
    face=valid*smooth((z-(top-.27))/.018)*smooth((eye_y+.028-y)/.022)
    face*=smooth((.091-np.abs(x))/.018)
    if int((face>.3).sum())<300:raise RuntimeError('Actual UV face coverage insufficient')
    strength=1. if cid=='oldman' else .68
    height=np.zeros((h,w));crease=np.zeros((h,w))
    def line(distance,mask,depth,width=.00115):
        nonlocal height,crease
        g=np.exp(-.5*(distance/width)**2)*mask*face
        height-=g*depth*strength
        crease+=g
    # Broken forehead creases, not perfectly parallel drawn black lines.
    forehead_window=np.exp(-((x/.056)**6))
    for k in range(3):
        zz=eye_z+.028+k*.012+.0035*(x/.06)**2+.0014*np.sin(x*85+k*.9)
        line(z-zz,forehead_window,.00018 if k!=1 else .00024)
    # Crow's feet and lower eyelid folds follow actual fitted eye centres.
    for sign in (-1,1):
        outer=sign*(eye_x+.013);outward=sign*(x-outer)
        for slope,offset in ((.22,0.),(-.24,-.002),(-.60,-.004)):
            distance=z-(eye_z+offset+slope*outward)
            mask=smooth(outward/.006)*smooth((.025-outward)/.010)
            line(distance,mask,.00016,.0010)
        dx=x-sign*eye_x
        arc=eye_z-.015+.006*(dx/.018)**2
        line(z-arc,np.exp(-((dx/.020)**6)),.00020,.0015)
        # Short smile folds terminate before the chin rather than becoming scars.
        t=np.clip((eye_z-.025-z)/.055,0,1)
        xx=sign*(.018+.018*t+.003*np.sin(t*math.pi))
        window=smooth((eye_z-.022-z)/.012)*smooth((z-(eye_z-.086))/.016)
        line(x-xx,window,.00016,.0016)
    # Low-amplitude pores and scattered warm/cool variation, skin-only.
    pore=.000012*np.sin(x*2650+np.sin(z*210))*np.sin(z*2300+x*73)*face
    height+=pore
    # 512px cap: subtle optical detail only, not an anatomical face sculpt.
    gy,gx=np.gradient(height)
    nx=-gx*w/tu;ny=-gy*h/tv
    normal=np.stack((nx,ny,np.ones_like(nx)),axis=-1)
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    rgba=np.ones((h,w,4),dtype='f4');rgba[:,:,:3]=normal*.5+.5
    albedo=old.copy();variation=(np.sin(x*124+z*98)*np.sin(z*154-x*86))*.012*face
    factor=1.-np.minimum(crease,.9)*.075*strength+variation
    albedo[:,:,:3]*=factor[:,:,None]
    # Very restrained cheek speckling, not large dark age spots or painted shadows.
    rng=np.random.default_rng(2801 if cid=='oldman' else 2802)
    pigment=np.zeros((h,w))
    for _ in range(28):
        sx=rng.choice((-1,1))*rng.uniform(.031,.069);sz=eye_z-rng.uniform(.018,.060)
        sigma=rng.uniform(.0008,.0017)
        pigment+=np.exp(-((x-sx)**2+(z-sz)**2)/(2*sigma*sigma))*rng.uniform(.01,.025)
    albedo[:,:,:3]*=(1.-pigment*face*strength)[:,:,None]
    albedo[:,:,:3]=np.clip(albedo[:,:,:3],0,1)
    color_img,color_info=save_image(cid+'_v28_cc0_skin_detail',albedo,out)
    normal_img,normal_info=save_image(cid+'_v28_age_normal',rgba,out,True)
    m=original.copy();m.name=cid+'_V28_AgedSkin_DerivedCC0'
    body.data.materials[0]=m;tree=m.node_tree
    p=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
    for l in list(p.inputs['Base Color'].links):tree.links.remove(l)
    color=tree.nodes.new('ShaderNodeTexImage');color.image=color_img
    tree.links.new(color.outputs['Color'],p.inputs['Base Color'])
    ntex=tree.nodes.new('ShaderNodeTexImage');ntex.image=normal_img
    nm=tree.nodes.new('ShaderNodeNormalMap');nm.space='TANGENT';nm.inputs['Strength'].default_value=.85
    tree.links.new(ntex.outputs['Color'],nm.inputs['Color']);tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
    if not p.inputs['Roughness'].is_linked:p.inputs['Roughness'].default_value=.71
    if not p.inputs['Specular IOR Level'].is_linked:p.inputs['Specular IOR Level'].default_value=.24
    return {'method':'source-UV raster of original crease field and restrained albedo variation',
      'source_cc0_texture':source.name,'source_decoded_rgba_sha256':source_hash,
      'derived_albedo':color_info,'original_normal_texture':normal_info,
      'face_texels':int((face>.3).sum()),'fitted_eye_center':[eye_x,eye_y,eye_z],
      'maximum_height_field_m':float(abs(height).max()),'normal_strength':.85,
      'body_geometry_and_morphs_changed':False,'limitation':'Surface-age detail study; no anatomical age sculpt or new hairstyle',
      'license':'CC0 source skin derivative; authored crease normal CC0-1.0'}
