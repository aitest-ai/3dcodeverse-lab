"""Original V27 occupational accessories, with actual source-surface fitting.
No real insignia, names, brands or personal screen data. Original accessory
geometry CC0. Elder hair recolor is a derivative of the original CC0 texture.
"""
import sys,os,math,hashlib
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector,Matrix
from native import coordinates,material
ROOT=Path(__file__).resolve().parents[2]
for p in ('taiwan_v20','taiwan_v21','taiwan_v24','taiwan_v25'):sys.path.insert(0,str(ROOT/'scripts'/p))
from belt import WeightSource,mesh
from apron import tree,cord,grid_sheet


def elder_gray_hair(cid,attached):
    if cid not in ('oldman','shui'):return None
    hair=next(o for o in attached if o.name=='HairFitted_'+cid)
    filename='short04_diffuse.png' if cid=='oldman' else 'short02_diffuse.png'
    source=bpy.data.images.get(filename)
    if source is None or not source.has_data:raise RuntimeError('Actual CC0 hair texture missing '+filename)
    width,height=source.size;pixels=np.array(source.pixels[:],dtype=np.float32).reshape(height,width,4)
    original_sha=hashlib.sha256(pixels.tobytes()).hexdigest()
    # Tint multiplication could never lighten a dark source map. Recolor the
    # real albedo pixels instead, preserving source alpha and strand variation.
    luminance=pixels[:,:,:3]@np.array([.2126,.7152,.0722],dtype=np.float32)
    variation=.58+.42*np.sqrt(np.clip(luminance,0,1))
    gray=np.array((.58,.60,.62) if cid=='oldman' else (.40,.42,.43),dtype=np.float32)
    pixels[:,:,:3]=variation[:,:,None]*gray
    image=bpy.data.images.new(cid+'_cc0_hair_gray',width=width,height=height,alpha=True)
    image.pixels.foreach_set(pixels.ravel());image.file_format='PNG'
    path=Path(os.environ['V27_OUT']).resolve()/(cid+'_cc0_hair_gray.png')
    image.filepath_raw=str(path);image.save();image.pack()
    mat=material(cid+'_GrayHair_SourceTexture',(.5,.5,.5),.82)
    node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
    bs=mat.node_tree.nodes['Principled BSDF']
    mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
    mat.node_tree.links.new(node.outputs['Alpha'],bs.inputs['Alpha'])
    if hasattr(mat,'surface_render_method'):mat.surface_render_method='DITHERED'
    hair.data.materials.clear();hair.data.materials.append(mat)
    for f in hair.data.polygons:f.material_index=0
    return {'source_texture':filename,'source_decoded_pixels_sha256':original_sha,
        'derived_texture':path.name,'derived_png_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'operation':'Recolor licensed source albedo while retaining alpha and luminance variation',
        'license':'CC0 derivative, not claimed entirely original texture'}


def build(cid,body,rig,shirt,pants,attached):
    gray_report=elder_gray_hair(cid,attached)
    pts=coordinates(body);h=float(pts[:,2].max());high=pts[pts[:,2]>h-.12]
    cy=float((high[:,1].min()+high[:,1].max())/2)
    rx=max(.083,float(np.max(np.abs(high[:,0])))+.012)
    ry=max(.095,float(np.ptp(high[:,1]))/2+.014)
    weights=WeightSource(body,rig);shirtweights=WeightSource(shirt,rig)
    torso=[tree(body,rig,True),tree(shirt,rig,True)]
    added=[];groups={};fitted=[];prefix='V27_'+cid+'_'
    dark=material(prefix+'Charcoal',(.018,.025,.031),.68)
    white=material(prefix+'CottonWhite',(.70,.69,.64),.93)
    gold=material(prefix+'WarmMetal',(.55,.32,.065),.30,.85)
    cream=material(prefix+'LightTrim',(.60,.57,.45),.75)
    def add(ob,group):
        ob['geometry_license']='CC0-1.0';ob['source']='Original V27 procedural accessory'
        ob['accessory_group']=group;added.append(ob);groups.setdefault(group,[]).append(ob.name);return ob
    def bind(ob,group,bone='head',source=None):
        if source is not None:source.bind(ob)
        else:weights.bind(ob,{bone:1.})
        return add(ob,group)
    def box(name,point,size,mat,group,bone='head',source=None,bevel=.002):
        bpy.ops.mesh.primitive_cube_add(size=1,location=point)
        ob=bpy.context.object;ob.name=prefix+name;ob.dimensions=size
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        if bevel:
            mod=ob.modifiers.new('OriginalRoundedEdges','BEVEL');mod.width=bevel;mod.segments=2
            bpy.ops.object.modifier_apply(modifier=mod.name)
        ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4);ob.data.materials.append(mat)
        for f in ob.data.polygons:f.use_smooth=True
        return bind(ob,group,bone,source)
    def line(name,points,mat,group,radius=.002,bone='head',source=None):
        return add(cord(prefix+name,points,mat,rig,source.at if source else {bone:1.},radius),group)
    def surface(x,z,back=False,extra=.012):
        origin=Vector((x,1 if back else -1,z));direction=Vector((0,-1 if back else 1,0));hits=[]
        for tr in torso:
            p,_,_,_=tr.ray_cast(origin,direction,2.)
            if p is not None:hits.append(p.y)
        if not hits:raise RuntimeError('No genuine central torso surface '+str((x,z)))
        return (max(hits)+extra) if back else (min(hits)-extra)
    def fitted_tab(sign):
        for dz in (.28,.30,.32,.34):
            for xx in (.135,.12,.11):
                x=sign*xx;z=h-dz
                try:y=surface(x,z,extra=.016)
                except RuntimeError:continue
                fitted.append({'item':'uniform_tab','side':sign,'actual_world':[x,y,z]})
                return x,y,z
        raise RuntimeError('No valid original upper torso for uniform tab')
    def elliptical_band(name,z,width,radius_x,radius_y,mat,group):
        n=72;vs=[];fs=[]
        for j in range(2):
            for i in range(n):
                t=2*math.pi*i/n;vs.append((radius_x*math.cos(t),cy+radius_y*math.sin(t),z+(j-.5)*width))
        for i in range(n):fs.append((i,(i+1)%n,n+(i+1)%n,n+i))
        return bind(mesh(prefix+name,vs,fs,mat),group)
    def cap(peaked=False):
        group='peaked_cap' if peaked else 'baseball_cap'
        color=(.025,.045,.075) if peaked else (.19,.20,.17)
        capmat=material(prefix+'CapFabric',color,.88);base=h-.065
        vs=[];fs=[];n=72;rows=14
        for j in range(rows):
            phi=.008+(math.pi/2-.008)*j/(rows-1)
            for i in range(n):
                t=2*math.pi*i/n;over=1.10 if peaked else 1.
                vs.append((rx*over*math.sin(phi)*math.cos(t),cy+ry*over*math.sin(phi)*math.sin(t),base+.105*math.cos(phi)))
        for j in range(rows-1):
            for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        bind(mesh(prefix+'CapCrown',vs,fs,capmat),group)
        elliptical_band('CapBand',base+.003,.025,rx*(1.10 if peaked else 1.),ry*(1.10 if peaked else 1.),dark,group)
        vs=[];fs=[];cols=41
        for j in range(4):
            v=j/3
            for i in range(cols):
                t=-math.pi*.82+math.pi*.64*i/(cols-1);rr=1.+v*.78
                vs.append((rx*rr*math.cos(t),cy+ry*rr*math.sin(t),base-.009-v*.026))
        for j in range(3):
            for i in range(cols-1):
                a=j*cols+i;fs.append((a,a+1,a+cols+1,a+cols))
        bind(mesh(prefix+'CapVisor',vs,fs,dark if peaked else capmat),group)
        if peaked:
            box('GenericCapBadge',(0,cy-ry*1.1-.004,base+.038),(.024,.005,.025),gold,group,bevel=.005)
            line('CapThinBraid',[(-.07,cy-ry-.007,base),(0,cy-ry*1.12-.007,base-.005),(.07,cy-ry-.007,base)],cream,group,.0015)
        else:
            seams=material(prefix+'CapSeam',(.13,.14,.12),.93)
            for k in range(6):
                t=k*math.pi/3
                path=[((rx+.0007)*math.sin(p)*math.cos(t),cy+(ry+.0007)*math.sin(p)*math.sin(t),base+.1057*math.cos(p)) for p in np.linspace(.12,math.pi/2,18)]
                line('CapPanelSeam'+str(k),path,seams,group,.00065)
    if cid in ('oldman','cop'):cap(cid=='cop')
    if cid=='oldman':
        wrist=rig.matrix_world@rig.pose.bones['hand_r'].head;end=rig.matrix_world@rig.pose.bones['hand_r'].tail
        p=(wrist+end)*.5+Vector((0,-.021,-.015))
        box('PhoneBody',p,(.064,.009,.126),dark,'smartphone','hand_r',bevel=.006)
        screen=material(prefix+'BlankPhoneScreen',(.025,.060,.075),.28)
        box('PhoneScreen',p+Vector((0,-.005,0)),(.055,.0015,.111),screen,'smartphone','hand_r',bevel=.004)
    if cid=='cop':
        uniform=material(prefix+'UniformTrim',(.052,.087,.14),.85)
        for sign in (-1,1):
            x=sign*.075;z=h-.385;y=surface(x,z,extra=.014)
            box('ChestPocket_'+str(sign),(x,y,z),(.071,.004,.085),uniform,'uniform_details',source=shirtweights,bevel=.003)
            box('PocketFlap_'+str(sign),(x,y-.004,z+.036),(.073,.005,.018),cream,'uniform_details',source=shirtweights,bevel=.002)
        x=-.11;z=h-.30;y=surface(x,z,extra=.025)
        box('Radio',(x,y,z),(.043,.024,.065),dark,'radio',source=shirtweights,bevel=.005)
        line('RadioAntenna',[(x+.012,y,z+.025),(x+.012,y,z+.10)],dark,'radio',.002,source=shirtweights)
        for sign in (-1,1):
            x,y,z=fitted_tab(sign)
            box('UniformTab_'+str(sign),(x,y,z),(.052,.009,.018),uniform,'uniform_details',source=shirtweights,bevel=.002)
    if cid=='shui':
        straw=material(prefix+'NaturalStraw',(.46,.32,.13),.91);weave=material(prefix+'StrawWeave',(.26,.17,.065),.95)
        base=h-.055;n=96
        profile=[(0.,.103),(.04,.098),(.079,.083),(.105,.049),(.116,.012),(.155,0.),(.22,-.008)]
        vs=[];fs=[]
        for radius,z in profile:
            for i in range(n):
                t=2*math.pi*i/n;vs.append((radius*math.cos(t),cy+radius*1.06*math.sin(t),base+z))
        for j in range(len(profile)-1):
            for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        bind(mesh(prefix+'StrawHat',vs,fs,straw),'straw_hat')
        for k,r in enumerate((.12,.14,.16,.18,.20,.22)):
            z=base-(r-.12)*.08
            line('StrawRing'+str(k),[(r*math.cos(t),cy+r*1.06*math.sin(t),z) for t in np.linspace(0,2*math.pi,97)],weave,'straw_hat',.0009)
        elliptical_band('HatRibbon',base+.017,.023,.116,.123,dark,'straw_hat')
        eyes=next(o for o in attached if 'high-poly' in o.name.lower())
        e=coordinates(eyes);z=float((e[:,2].min()+e[:,2].max())/2);y=float(e[:,1].min())-.010
        for sign in (-1,1):
            x=sign*.032
            path=[(x+.029*math.cos(t),y,z+.020*math.sin(t)) for t in np.linspace(0,2*math.pi,49)]
            line('GlassesRim_'+str(sign),path,dark,'glasses',.0017)
            line('GlassesTemple_'+str(sign),[(sign*.061,y,z),(sign*.087,y+.06,z),(sign*.081,cy+.025,z-.012)],dark,'glasses',.0014)
        line('GlassesBridge',[(-.006,y,z+.003),(0,y-.004,z+.007),(.006,y,z+.003)],dark,'glasses',.0014)
        for sign in (-1,1):
            points=[];rows=24;cols=5
            for j,v in enumerate(np.linspace(0,1,rows)):
                x=sign*(.066+.015*math.sin(v*math.pi));z=h-.27-v*.34
                for i,u in enumerate(np.linspace(-1,1,cols)):
                    xx=x+u*.023;yy=surface(xx,float(z),extra=.025)+.002*math.cos(v*math.pi*6+u)
                    points.append((xx,yy,z))
            ob=grid_sheet(prefix+'Towel_'+str(sign),points,rows,cols,white,rig,shirtweights.at,thickness=.002)
            add(ob,'shoulder_towel')
    if cid=='bro':
        elliptical_band('WhiteHeadband',h-.067,.035,rx,ry,white,'white_headband')
        box('HeadbandKnot',(0,cy+ry+.006,h-.068),(.035,.014,.025),white,'white_headband',bevel=.005)
        for sign in (-1,1):
            points=[(sign*.005,cy+ry+.012,h-.07),(sign*.014,cy+ry+.019,h-.11),(sign*.024,cy+ry+.023,h-.17)]
            vs=[];fs=[]
            for j,p in enumerate(points):
                for u in (-.006,.006):vs.append((p[0]+u,p[1],p[2]))
                if j:fs.append((2*j-2,2*j-1,2*j+1,2*j))
            bind(mesh(prefix+'HeadbandTail_'+str(sign),vs,fs,white),'white_headband')
        path=[]
        for t in np.linspace(0,2*math.pi,65):
            z=h-.255-.105*max(0.,-math.sin(t));unit=Vector((math.cos(t),math.sin(t),0))
            origin=Vector((0,cy,z))+unit*.34;dist=[]
            for tr in torso:
                hit,_,_,_=tr.ray_cast(origin,-unit,.34)
                if hit is not None:dist.append((hit-Vector((0,cy,z))).length)
            r=max(dist)+.014 if dist else .085
            path.append(tuple(Vector((0,cy,z))+unit*r))
        line('GoldChainCore',path,gold,'gold_chain',.0032,bone='spine_03',source=shirtweights)
        for k in range(0,64,3):
            p=Vector(path[k]);tangent=(Vector(path[(k+1)%64])-Vector(path[(k-1)%64])).normalized()
            vertical=Vector((0,0,1));link=[tuple(p+tangent*(.006*math.cos(a))+vertical*(.004*math.sin(a))) for a in np.linspace(0,2*math.pi,13)]
            line('GoldLink'+str(k),link,gold,'gold_chain',.0012,source=shirtweights)
    for ob in added:
        assert any(m.type=='ARMATURE' and m.object==rig for m in ob.modifiers)
        for vertex in ob.data.vertices:
            assert 1<=len(vertex.groups)<=4
            assert abs(sum(g.weight for g in vertex.groups)-1.)<2e-6
    return added,{'accessory_groups':groups,'count':len(added),'license':'CC0-1.0 original accessory geometry and parameters',
      'gray_hair_derivative':gray_report,'actual_surface_fit':fitted,
      'limitations':['No cloth physics or final contact/hand grasp approval','Hats and metallic accessories need visual scale review','Floral shirt uses fitted CC0 polo-derived base, not final open Hawaiian shirt pattern'],
      'head_fit':{'body_top':h,'center_y':cy,'radius_x':rx,'radius_y':ry}}
