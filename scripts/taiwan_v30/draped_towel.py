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
    # Intentional single-shoulder style: one front and one rear tail, not a forced collar.
    controls=[(-.14,-.16,h-.665),(-.14,-.15,h-.52),(-.14,-.13,h-.38),
      (-.14,-.09,h-.29),(-.14,-.035,h-.22),(-.14,.025,h-.22),
      (-.14,.08,h-.29),(-.14,.11,h-.43),(-.14,.12,h-.56)]
    rows=121;cols=15;curve,length=sample_curve(controls,rows)
    tangent=np.gradient(curve,axis=0);tangent/=np.linalg.norm(tangent,axis=1,keepdims=True)
    width_axis=np.array([1.,0.,0.]);outward=np.cross(width_axis,tangent)
    outward/=np.linalg.norm(outward,axis=1,keepdims=True)
    widths=.077+.003*np.sin(np.linspace(0,5,rows))
    shifts=[];missed_points=0;unsupported_rows=0;hit_counts=[]
    for point,normal,width in zip(curve,outward,widths):
        required=[]
        for u in np.linspace(-.5,.5,cols):
            q=point+width_axis*(u*width);start=Vector(q+normal*.12);dist=[]
            for tree in trees:
                hit,_,_,d=tree.ray_cast(start,Vector(-normal),.30)
                if hit is not None:dist.append(d)
            if dist:required.append(.12-min(dist)+.010)
            else:missed_points+=1
        hit_counts.append(len(required))
        if len(required)<3:unsupported_rows+=1
        shifts.append(max(required) if required else 0.)
    if unsupported_rows:raise RuntimeError('Shoulder row lacks genuine support: '+str(unsupported_rows))
    shifts=np.asarray(shifts)
    if np.abs(shifts).max()>.06:raise RuntimeError('Support projection would distort the towel')
    # Fit whole cross-sections, not individual points, preserving original width.
    for _ in range(4):
        padded=np.pad(shifts,2,mode='edge')
        avg=sum(padded[k:k+rows]*w for k,w in enumerate((1,2,3,2,1)))/9
        shifts=np.maximum(shifts,avg)
    centers=curve+outward*shifts[:,None]
    mat,shirt_normal,texture_info=cloth_materials(out)
    front=[];normals=[];uvs=[]
    for j,(point,normal,width) in enumerate(zip(centers,outward,widths)):
        s=j/(rows-1)
        for i,u in enumerate(np.linspace(-.5,.5,cols)):
            fold=.0026*math.cos(2*math.pi*(u*1.35+.10*math.sin(s*7)))+.0013*math.sin(2*math.pi*(u*2.1+s*.5))
            edge=.0011*(abs(u)*2)**6
            q=point+width_axis*(u*width)+normal*(fold+edge)
            front.append(tuple(q));normals.append(tuple(normal));uvs.append((i/(cols-1),s))
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
    obj['source']='Original V30 sculpted single-shoulder towel; transferred original shirt skinning'
    obj['simulation']='None; source-sculpted drape plus original armature weights'
    old=shirt.data.materials[0];copy=old.copy();copy.name='V30_Shui_OriginalFloral_WovenCotton'
    shirt.data.materials[0]=copy;bs=next(n for n in copy.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value=.91;bs.inputs['Specular IOR Level'].default_value=.22
    for link in list(bs.inputs['Normal'].links):copy.node_tree.links.remove(link)
    tex=copy.node_tree.nodes.new('ShaderNodeTexImage');tex.image=shirt_normal
    nm=copy.node_tree.nodes.new('ShaderNodeNormalMap');nm.space='TANGENT';nm.inputs['Strength'].default_value=.23
    copy.node_tree.links.new(tex.outputs['Color'],nm.inputs['Color']);copy.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
    return obj,{'rows':rows,'columns':cols,'source_vertices':len(data.vertices),'source_polygons':len(data.polygons),
        'wearing_style':'single left shoulder, one front and one back tail; rejected neck-wrap versions not selected',
        'authored_centerline_length_m':length,'width_range_m':[float(widths.min()),float(widths.max())], 'thickness_m':.0022,
        'tail_lower_z':[float(front[0:cols,2].mean()),float(front[-cols:,2].mean())],
        'unsupported_rows':unsupported_rows,'individual_support_ray_misses':missed_points,
        'minimum_hits_per_row':min(hit_counts),'max_row_fit_displacement_m':float(np.abs(shifts).max()),
        'textures':texture_info,'skinning':'Barycentric nearest original shirt triangles, normalized top4 weights',
        'original_shirt_geometry_unchanged':True,'shirt_color_texture_unchanged':True,
        'fit_revision':'whole-width supported cross-sections with conservative smoothing, not per-point radial stretch',
        'not_physics_simulation':True,'original_accessory_license':'CC0-1.0'}
