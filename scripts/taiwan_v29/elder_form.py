"""V29 bounded elder face-form and real glTF hair-map study.
Original topology, rig, UV and morph deltas are preserved. These are artistic
local changes on fictional characters, not a biological age estimator.
"""
from pathlib import Path
import hashlib
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from source_waist import coordinates
from age_material import decoded_source,save_image


def smooth(x):
    t=np.clip(x,0.,1.);return t*t*(3.-2.*t)


def add_rest_offset(obj,world_delta,limit):
    world_delta=np.asarray(world_delta,float)
    lengths=np.linalg.norm(world_delta,axis=1)
    if not np.isfinite(world_delta).all() or lengths.max()>limit:
        raise RuntimeError('Unsafe source offset '+obj.name+' '+str(lengths.max()))
    local_delta=world_delta@np.asarray(obj.matrix_world.inverted().to_3x3()).T
    old=np.asarray([tuple(v.co) for v in obj.data.vertices])
    keys=list(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else []
    snapshots=[np.asarray([tuple(v.co) for v in k.data]) for k in keys]
    obj.data.vertices.foreach_set('co',np.asarray(old+local_delta,dtype='f4').ravel())
    for key,points in zip(keys,snapshots):key.data.foreach_set('co',np.asarray(points+local_delta,dtype='f4').ravel())
    obj.data.update();obj.update_tag(refresh={'DATA'});bpy.context.view_layer.update()
    errors=[]
    if keys:
        new_basis=np.asarray([tuple(v.co) for v in keys[0].data])
        for k,s in zip(keys[1:],snapshots[1:]):
            now=np.asarray([tuple(v.co) for v in k.data])-new_basis
            errors.append(float(np.abs(now-(s-snapshots[0])).max()))
    err=max(errors,default=0.)
    if err>4e-7:raise RuntimeError('Existing relative expression was not preserved')
    return {'changed_source_vertices':int((lengths>1e-7).sum()),
            'maximum_world_displacement_m':float(lengths.max()),
            'relative_morph_max_error_m':err,'existing_relative_shape_count':max(len(keys)-1,0)}


def face_form(body,eyes,cid):
    pts=coordinates(body);ep=coordinates(eyes)
    ex=float(np.mean(np.abs(ep[:,0])));ey=float(np.median(ep[:,1]));ez=float(np.median(ep[:,2]))
    x,y,z=pts.T;ax=np.abs(x)
    front=smooth((ey+.022-y)/.025)
    height=smooth((z-(ez-.125))/.022)*smooth(((ez+.025)-z)/.020)
    lateral=smooth((ax-.018)/.014)*smooth((.085-ax)/.020)
    normals=np.asarray([tuple(v.normal) for v in body.data.vertices])@np.asarray(body.matrix_world.to_3x3()).T
    facing=smooth((-normals[:,1]-.05)/.40)
    safe=front*height*lateral*facing
    eye_guard=1.-np.exp(-.5*(((ax-ex)/.022)**2+((z-ez)/.0085)**2))
    mouth_guard=1.-np.exp(-.5*((x/.027)**4+((z-(ez-.078))/.016)**4))
    safe*=eye_guard*mouth_guard
    def patch(cx,cz,wx,wz):return np.exp(-.5*((ax-cx)/wx)**2-.5*((z-cz)/wz)**2)*safe
    under=patch(ex,ez-.018,.018,.0085)
    hollow=patch(.046,ez-.045,.016,.017)
    jowl=patch(.049,ez-.087,.015,.018)
    temple=patch(.062,ez+.002,.012,.024)
    delta=np.zeros_like(pts)
    if cid=='oldman':
        delta[:,1]=-.0017*under+.0038*hollow-.0018*jowl+.0014*temple
        delta[:,2]=-.0010*under-.0030*jowl
        delta[:,0]=np.sign(x)*(-.0014*hollow+.0010*jowl-.0010*temple)
    else:
        delta[:,1]=-.0015*under+.0016*hollow-.0026*jowl+.0006*temple
        delta[:,2]=-.0010*under-.0035*jowl
        delta[:,0]=np.sign(x)*(.0017*jowl-.0005*hollow)
    delta[safe<.004]=0.
    protected=(np.abs(z-ez)<.0095)&(np.abs(ax-ex)<.024)
    delta[protected]=0.
    report=add_rest_offset(body,delta,.006)
    report.update({'fitted_eye_center':[ex,ey,ez],'scope':'under-eye/cheek/jowl artistic form; eye/nose/lip centre protected',
        'method':'bounded smooth displacement, identical offset applied to Basis and every existing shape',
        'target_age_claim':False,'new_expression_keys':False})
    return report


def hair_form(hair,body,eyes,cid):
    pts=coordinates(hair);ep=coordinates(eyes);ez=float(np.median(ep[:,2]));top=float(pts[:,2].max())
    if cid=='oldman':return {'changed_source_vertices':0,'maximum_world_displacement_m':0.,'scope':'source swept-back silhouette retained'}
    center=np.array([0.,.006,ez+.018]);v=pts-center
    radial=v/np.maximum(np.linalg.norm(v,axis=1)[:,None],1e-9)
    upper=smooth((pts[:,2]-ez-.020)/.047)
    part=np.exp(-.5*((pts[:,0]+.025)/.009)**2)*smooth((pts[:,2]-ez-.040)/.030)
    amount=.0015*upper+.0012*part
    target=pts-radial*amount[:,None]
    verts=[body.matrix_world@v.co for v in body.data.vertices]
    tree=BVHTree.FromPolygons(verts,[tuple(p.vertices) for p in body.data.polygons])
    clipped=0
    for i,p in enumerate(target):
        hit,n,_,dist=tree.find_nearest(Vector(p))
        if hit is None:continue
        if dist<.003:target[i]=pts[i];clipped+=1
    r=add_rest_offset(hair,target-pts,.0031)
    r.update({'scope':'small crown de-puff and side-part; same original hair topology', 'skin_clearance_rejections':clipped})
    return r


def hair_maps(hair,eyes,cid,out):
    """Use irregular strand flow already present in the licensed source image.
    The first-pass periodic pattern was visually rejected, not silently passed.
    """
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    original=hair.data.materials[0]
    bs=next(n for n in original.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    if not bs.inputs['Base Color'].is_linked:raise RuntimeError('No original CC0 hair image')
    node=bs.inputs['Base Color'].links[0].from_node
    if node.type!='TEX_IMAGE':raise RuntimeError('Expected source texture link')
    src=node.image;old,w,h=decoded_source(src,out,cid+'_hair')
    pts=coordinates(hair);ep=coordinates(eyes);ez=float(np.median(ep[:,2]))
    pos=np.zeros((h,w,3));tu=np.ones((h,w));tv=np.ones((h,w));valid=np.zeros((h,w),bool)
    uv=hair.data.uv_layers.active
    if uv is None:raise RuntimeError('Original hair UV missing')
    hair.data.calc_loop_triangles()
    for tri in hair.data.loop_triangles:
        p=pts[list(tri.vertices)];q=np.array([tuple(uv.data[i].uv) for i in tri.loops])
        e1=q[1]-q[0];e2=q[2]-q[0];det=e1[0]*e2[1]-e2[0]*e1[1]
        if abs(det)<1e-12:continue
        u=((p[1]-p[0])*e2[1]-(p[2]-p[0])*e1[1])/det
        v=(-(p[1]-p[0])*e2[0]+(p[2]-p[0])*e1[0])/det
        x0=max(0,int(np.floor(q[:,0].min()*w)));x1=min(w-1,int(np.ceil(q[:,0].max()*w)))
        y0=max(0,int(np.floor(q[:,1].min()*h)));y1=min(h-1,int(np.ceil(q[:,1].max()*h)))
        if x1<x0 or y1<y0:continue
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1];a=(xx+.5)/w-q[0,0];b=(yy+.5)/h-q[0,1]
        b1=(a*e2[1]-b*e2[0])/det;b2=(e1[0]*b-e1[1]*a)/det
        inside=(b1>=-1e-6)&(b2>=-1e-6)&(b1+b2<=1.000001)
        rr=yy[inside];cc=xx[inside]
        pos[rr,cc]=p[0]+b1[inside,None]*(p[1]-p[0])+b2[inside,None]*(p[2]-p[0])
        tu[rr,cc]=max(float(np.linalg.norm(u)),.04);tv[rr,cc]=max(float(np.linalg.norm(v)),.04);valid[rr,cc]=True
    opaque=(old[:,:,3]>.90)&valid
    if opaque.sum()<1000:raise RuntimeError('Hair texture/raster coverage insufficient')
    lum=old[:,:,:3]@np.asarray([.2126,.7152,.0722])
    blur=np.zeros_like(lum)
    for iy in range(-2,3):
        for ix in range(-2,3):blur+=np.roll(np.roll(lum,iy,axis=0),ix,axis=1)/25.
    fine=lum-blur;fine_sd=max(float(fine[opaque].std()),1e-5)
    broad_sd=max(float(blur[opaque].std()),1e-5);broad_mean=float(blur[opaque].mean())
    detail=np.tanh(fine/(fine_sd*2.2));broad=np.tanh((blur-broad_mean)/(broad_sd*1.6))
    height=.000085*detail
    gy,gx=np.gradient(height)
    nx=np.clip(-gx*w/tu,-.38,.38);ny=np.clip(-gy*h/tv,-.38,.38)
    safe=opaque.copy()
    for iy,ix in ((-2,0),(2,0),(0,-2),(0,2)):
        safe &=np.roll(np.roll(opaque,iy,axis=0),ix,axis=1)
    nx[~safe]=0.;ny[~safe]=0.
    n=np.stack((nx,ny,np.ones_like(nx)),axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
    rgba=np.ones((h,w,4),dtype='f4');rgba[:,:,:3]=n*.5+.5
    temple=smooth((np.abs(pos[:,:,0])-.037)/.025)*smooth((ez+.072-pos[:,:,2])/.045)
    multiplier=(.94 if cid=='oldman' else .88)+.15*detail+.11*broad+.045*temple
    color=old.copy();color[:,:,:3]*=np.where(valid,multiplier,1.)[:,:,None]
    color[:,:,:3]*=np.asarray([1.015,1.,.98])[None,None,:]
    color[:,:,:3]=np.clip(color[:,:,:3],0,1)
    ci,cinfo=save_image(cid+'_v29_cc0_hair_tone',color,out)
    ni,ninfo=save_image(cid+'_v29_strand_normal',rgba,out,True)
    m=original.copy();m.name=cid+'_V29_GrayHair_SourceFlow';hair.data.materials[0]=m
    tree=m.node_tree;p=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
    for socket in ('Base Color','Normal'):
        for l in list(p.inputs[socket].links):tree.links.remove(l)
    c=tree.nodes.new('ShaderNodeTexImage');c.image=ci;tree.links.new(c.outputs['Color'],p.inputs['Base Color'])
    tex=tree.nodes.new('ShaderNodeTexImage');tex.image=ni
    normal=tree.nodes.new('ShaderNodeNormalMap');normal.space='TANGENT';normal.inputs['Strength'].default_value=.48
    tree.links.new(tex.outputs['Color'],normal.inputs['Color']);tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
    p.inputs['Roughness'].default_value=.73
    if p.inputs.get('Specular IOR Level'):p.inputs['Specular IOR Level'].default_value=.24
    return {'source_cc0_image':src.name,'source_decoded_sha256':hashlib.sha256(old.tobytes()).hexdigest(),
        'derived_hair_albedo':cinfo,'source_flow_normal':ninfo,'valid_hair_texels':int(valid.sum()),
        'normal_strength':.48,'source_detail_std':fine_sd,'source_broad_std':broad_sd,
        'method':'source-UV native irregular hair flow, local contrast and restrained standard tangent normal',
        'periodic_procedural_pattern_removed':True,'not_individual_hair_strands':True,'no_hair_card_simulation':True,
        'license':'CC0 hair color and normal derivatives of original licensed source'}
