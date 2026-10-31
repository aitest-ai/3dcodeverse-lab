"""V30 original skinned towel over untouched V29 body and shirt.
Sculpted cloth silhouette and original procedural maps, not cloth simulation.
"""
from pathlib import Path
import math
import numpy as np
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from source_waist import coordinates
from belt import WeightSource
from age_material import save_image


def smooth(x):
    t=np.clip(x,0.,1.);return t*t*(3-2*t)


def sample_curve(controls,rows):
    q=np.asarray(controls,float);dense=[]
    ext=np.vstack((2*q[0]-q[1],q,2*q[-1]-q[-2]))
    for i in range(len(q)-1):
        a,b,c,d=ext[i:i+4]
        for t in np.linspace(0,1,32,endpoint=False):
            dense.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    dense=np.vstack((dense,q[-1]));arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(dense,axis=0),axis=1))]
    target=np.linspace(0,arc[-1],rows)
    return np.column_stack([np.interp(target,arc,dense[:,k]) for k in range(3)]),float(arc[-1])


def cloth_materials(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);size=512
    rng=np.random.default_rng(30010);y,x=np.mgrid[0:size,0:size];u=(x+.5)/size;v=(y+.5)/size
    grain=rng.normal(0,1,(size,size))
    for _ in range(2):grain=(grain+np.roll(grain,1,0)+np.roll(grain,-1,0)+np.roll(grain,1,1)+np.roll(grain,-1,1))/5
    grain/=max(grain.std(),1e-9)
    height=.000022*grain+.000015*np.sin(u*2*np.pi*86)*np.sin(v*2*np.pi*173)
    gy,gx=np.gradient(height)
    n=np.stack((-gx*size/.077,-gy*size/1.0,np.ones_like(gx)),axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
    normal=np.ones((size,size,4),dtype='f4');normal[:,:,:3]=n*.5+.5
    color=np.ones_like(normal);base=np.array([.74,.72,.66])
    color[:,:,:3]=base[None,None,:]*(1+grain[:,:,None]*.013)
    end=np.minimum(v,1-v)
    band=((end>.018)&(end<.025))|((end>.037)&(end<.041))
    color[band,:3]=np.array([.13,.23,.23])*(1+grain[band,None]*.02)
    hem=(end<.008)|(u<.025)|(u>.975)
    color[hem,:3]*=.94
    ci,cr=save_image('V30_Ivory_Terry_With_Sage_Borders',color,out)
    ni,nr=save_image('V30_Terry_Fibre_Normal',normal,out,True)
    mat=bpy.data.materials.new('V30_TerryCotton_Exportable');mat.use_nodes=True
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.91;bs.inputs['Specular IOR Level'].default_value=.22
    tex=nodes.new('ShaderNodeTexImage');tex.image=ci;links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    tex=nodes.new('ShaderNodeTexImage');tex.image=ni
    norm=nodes.new('ShaderNodeNormalMap');norm.space='TANGENT';norm.inputs['Strength'].default_value=.35
    links.new(tex.outputs['Color'],norm.inputs['Color']);links.new(norm.outputs['Normal'],bs.inputs['Normal'])
    weave=.000006*(np.sin(u*2*np.pi*121)*np.sin(v*2*np.pi*117))+.000003*grain
    gy,gx=np.gradient(weave);n=np.stack((-gx*size/.45,-gy*size/.55,np.ones_like(gx)),axis=-1)
    n/=np.linalg.norm(n,axis=-1,keepdims=True);data=np.ones_like(normal);data[:,:,:3]=n*.5+.5
    wi,wr=save_image('V30_Shirt_Subtle_Woven_Normal',data,out,True)
    return mat,wi,{'towel_albedo':cr,'towel_normal':nr,'shirt_normal':wr,
        'license':'Original procedural texture pixels CC0-1.0','towel_normal_strength':.35,'shirt_normal_strength':.23}


def build(body,shirt,rig,out):
    h=float(coordinates(body)[:,2].max());trees=[]
    for obj in (body,shirt):
        trees.append(BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],[tuple(p.vertices) for p in obj.data.polygons]))
    controls=[(-.105,-.16,h-.665),(-.091,-.145,h-.535),(-.077,-.125,h-.390),
      (-.078,-.080,h-.285),(-.090,-.005,h-.245),(-.064,.065,h-.246),(0,.084,h-.249),
      (.062,.065,h-.244),(.090,-.007,h-.248),(.078,-.080,h-.292),(.086,-.13,h-.410),(.098,-.153,h-.505),(.092,-.158,h-.590)]
    rows=121;cols=15;curve,length=sample_curve(controls,rows)
    tangent=np.gradient(curve,axis=0);tangent/=np.linalg.norm(tangent,axis=1,keepdims=True)
    mat,shirt_normal,texture_info=cloth_materials(out)
    front=[];normals=[];uvs=[];fit_misses=0;neck_ray_recoveries=0
    for j,(point,tan) in enumerate(zip(curve,tangent)):
        s=j/(rows-1);x,y,z=point
        weight=float(smooth((z-(h-.34))/.065))
        radial=np.array([x,y+.005,0.]);radial/=max(np.linalg.norm(radial),1e-9)
        outward=(1-weight)*np.array([0.,-1.,0.])+weight*radial
        outward-=tan*np.dot(outward,tan);outward/=max(np.linalg.norm(outward),1e-9)
        width_axis=np.cross(tan,outward);width_axis/=max(np.linalg.norm(width_axis),1e-9)
        width=.074-.019*weight+.004*math.sin(s*5+1)
        for i,u in enumerate(np.linspace(-.5,.5,cols)):
            fold=(.0032*math.cos(2*math.pi*(u*1.3+.09*math.sin(s*9)))+
                  .0018*math.sin(2*math.pi*(u*2.1+s*.44)))*(1-.40*weight)
            edge=.0016*(abs(u)*2)**6
            q=point+width_axis*(u*width)+outward*(fold+edge)
            if weight<.55:
                origin=Vector((q[0],-1.,q[2]));hit_y=[]
                for tree in trees:
                    hit,_,_,_=tree.ray_cast(origin,Vector((0,1,0)),2.)
                    if hit is not None:hit_y.append(hit.y)
                if not hit_y:fit_misses+=1
                else:q[1]=min(hit_y)-.010-fold-edge
            else:
                # Fixed-X/Z fitting preserves designed band width. A horizontal
                # ray can miss a shoulder that is below it; use a verified local
                # closest surface, never expand to a remote torso silhouette.
                ray_missed=False;near_surface=False
                if q[1]>.020 or q[1]<-.035:
                    back=q[1]>.020
                    origin=Vector((q[0],1. if back else -1.,q[2]))
                    direction=Vector((0,-1. if back else 1.,0));hits=[]
                    for tree in trees:
                        hit,_,_,_=tree.ray_cast(origin,direction,2.)
                        if hit is not None:hits.append(hit.y)
                    if hits:q[1]=(max(hits)+.012+fold+edge) if back else (min(hits)-.012-fold-edge)
                    else:ray_missed=True
                for iteration in range(4):
                    moved=False
                    for tree in trees:
                        hit,normal,_,distance=tree.find_nearest(Vector(q))
                        if hit is None or distance>.045:continue
                        near_surface=True
                        offset=float((Vector(q)-hit).dot(normal))
                        if offset<.008:
                            q+=np.array(normal)*(.008-offset);moved=True
                    if not moved:break
                if ray_missed:
                    if near_surface:neck_ray_recoveries+=1
                    else:fit_misses+=1
            front.append(tuple(q));normals.append(tuple(outward));uvs.append((i/(cols-1),s))
    if fit_misses>8:raise RuntimeError('Towel did not fit real torso: '+str(fit_misses))
    front=np.array(front);normals=np.array(normals)
    verts=np.vstack((front,front-normals*.0022));M=len(front);faces=[];uv=uvs+uvs
    for j in range(rows-1):
        for i in range(cols-1):
            a=j*cols+i;b=a+1;c=a+cols+1;d=a+cols
            faces.extend([(a,b,c,d),(M+d,M+c,M+b,M+a)])
    boundary=list(range(cols))+[j*cols+cols-1 for j in range(1,rows)]+list(range((rows-1)*cols+cols-2,(rows-1)*cols-1,-1))+[j*cols for j in range(rows-2,0,-1)]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.append((a,M+a,M+b,b))
    data=bpy.data.meshes.new('V30_ContinuousShoulderTowel');data.from_pydata(verts.tolist(),[],faces);data.update()
    obj=bpy.data.objects.new('V30_shui_DrapedShoulderTowel',data);bpy.context.scene.collection.objects.link(obj)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    layer=data.uv_layers.new(name='TerryUV')
    for p in data.polygons:
        p.use_smooth=True
        for li in p.loop_indices:layer.data[li].uv=uv[data.loops[li].vertex_index]
    data.materials.append(mat)
    source=WeightSource(shirt,rig);source.bind(obj)
    for vertex in obj.data.vertices:
        assert 1<=len(vertex.groups)<=4
        assert abs(sum(g.weight for g in vertex.groups)-1)<2e-6
    obj['accessory_group']='shoulder_towel';obj['geometry_license']='CC0-1.0'
    obj['source']='Original V30 sculpted continuous towel with transferred V29 shirt skinning'
    obj['simulation']='None; source-sculpted drape plus original armature weights'
    old=shirt.data.materials[0];copy=old.copy();copy.name='V30_Shui_OriginalFloral_WovenCotton'
    shirt.data.materials[0]=copy;bs=next(n for n in copy.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value=.91;bs.inputs['Specular IOR Level'].default_value=.22
    for link in list(bs.inputs['Normal'].links):copy.node_tree.links.remove(link)
    tex=copy.node_tree.nodes.new('ShaderNodeTexImage');tex.image=shirt_normal
    nm=copy.node_tree.nodes.new('ShaderNodeNormalMap');nm.space='TANGENT';nm.inputs['Strength'].default_value=.23
    copy.node_tree.links.new(tex.outputs['Color'],nm.inputs['Color']);copy.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
    return obj,{'rows':rows,'columns':cols,'source_vertices':len(data.vertices),'source_polygons':len(data.polygons),
        'authored_centerline_length_m':length,'width_range_m':[.055,.078], 'thickness_m':.0022,
        'front_tail_lower_z':[float(front[0:cols,2].mean()),float(front[-cols:,2].mean())],
        'fitting_misses':fit_misses,'neck_y_ray_misses_recovered_by_nearest_surface':neck_ray_recoveries,
        'textures':texture_info,'skinning':'Barycentric nearest original shirt triangles, normalized top4 weights',
        'original_shirt_geometry_unchanged':True,'shirt_color_texture_unchanged':True,
        'neck_fit_revision':'Fixed-XZ front/back plus verified nearest-surface recovery; no relaxation of unresolved-miss ceiling',
        'not_physics_simulation':True,'original_accessory_license':'CC0-1.0'}
