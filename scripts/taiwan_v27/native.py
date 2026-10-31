"""Genuine new MPFB source humans. No GLB mesh copying or neutral-face reuse.
Uses official fitting/interpolation and physical helper deletion. Original
Faceunits drive 12 single keys; two symmetric game aliases are sums, explicitly
labelled composites. Clothing and accessory quality still requires real images.
"""
import sys,os,importlib,json,hashlib,math
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from profiles import PROFILES,REQUIRED_BONES,REQUIRED_KEYS
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/taiwan_characters'))
import add_arkit_faceunits_full as faceunits


def coordinates(ob):
    return np.array([tuple(ob.matrix_world@v.co) for v in ob.data.vertices])


def material(name,color,roughness=.8,metallic=0.):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1.)
    bs.inputs['Roughness'].default_value=roughness;bs.inputs['Metallic'].default_value=metallic
    return m


def flowers(cid,color,out):
    """Original mathematical textile, generated once as packed standard PNG."""
    size=512;y,x=np.mgrid[0:size,0:size]/size
    xx=x*5;yy=y*5;cx=np.floor(xx);cy=np.floor(yy)
    u=(xx%1)-.5;v=(yy%1)-.5
    angle=(cx*1.72+cy*2.13)%6.28
    a=u*np.cos(angle)+v*np.sin(angle);b=-u*np.sin(angle)+v*np.cos(angle)
    leaf=((a/.29)**2+((b+.10)/.09)**2)<1
    petal=np.zeros((size,size),bool)
    for t in range(5):
        q=angle+t*2*math.pi/5
        petal|=(((u-.12*np.cos(q))/.095)**2+((v-.12*np.sin(q))/.095)**2)<1
    rgba=np.ones((size,size,4),dtype=np.float32);rgba[:,:,:3]=color
    rgba[leaf,:3]=(.14,.20,.10) if cid=='shui' else (.20,.14,.10)
    rgba[petal,:3]=(.72,.60,.37) if cid=='shui' else (.76,.65,.50)
    center=u*u+v*v<.0014;rgba[center,:3]=(.12,.10,.06)
    image=bpy.data.images.new(cid+'_original_floral',width=size,height=size,alpha=False)
    image.pixels.foreach_set(rgba.ravel());image.file_format='PNG'
    image.filepath_raw=str(out/(cid+'_original_floral.png'));image.save();image.pack()
    return image


def create(cid,out):
    cfg=PROFILES[cid];assets=Path(os.environ['MAKEHUMAN_ASSET_ROOT']).resolve()
    used=[]
    def need(name):
        matches=sorted(assets.rglob(name))
        if not matches:raise RuntimeError('Original licensed asset missing '+name)
        signatures={hashlib.sha256(p.read_bytes()).hexdigest() for p in matches}
        if len(signatures)!=1:raise RuntimeError('Ambiguous source filename '+name)
        p=matches[0]
        if name.endswith(('.mhclo','.mhmat')):
            used.append({'file':name,'sha256':next(iter(signatures)),
              'source_header':p.read_text(errors='replace')[:3500]})
        return str(p)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.preferences.addon_enable(module='bl_ext.local_mpfb.mpfb')
    import bl_ext.local_mpfb.mpfb
    def service(suffix,name):
        names=[x for x in sys.modules if x.endswith(suffix)]
        if len(names)!=1:raise RuntimeError('MPFB service ambiguous '+suffix)
        return getattr(importlib.import_module(names[0]),name)
    Human=service('mpfb.services.humanservice','HumanService')
    Target=service('mpfb.services.targetservice','TargetService')
    Face=service('mpfb.services.faceservice','FaceService')
    Export=service('mpfb.services.exportservice','ExportService')
    Clothes=service('mpfb.services.clothesservice','ClothesService')
    Properties=service('mpfb.entities.objectproperties','GeneralObjectProperties')
    macro=Target.get_default_macro_info_dict();macro.update(cfg['macro'])
    macro['race']={'asian':.78,'caucasian':.17,'african':.05}
    body=Human.create_human(mask_helpers=True,extra_vertex_groups=True,feet_on_ground=True,scale=.1,macro_detail_dict=macro)
    assert len(body.data.vertices)==19158
    body.name='TrueMPFBBody_'+cid
    stack=[{'target':t,'value':v} for t,v in cfg['face']]
    missing=[x['target'] for x in stack if Target.target_full_path(x['target']) is None]
    if missing:raise RuntimeError('Missing genuine face targets '+str(missing))
    Target.bulk_load_targets(body,stack);bpy.context.view_layer.update()
    rig=Human.add_builtin_rig(body,'game_engine');rig.name='RootRig_'+cid
    assert len(rig.data.bones)==53
    assert REQUIRED_BONES<=set(rig.data.bones.keys())
    Human.set_character_skin(need(cfg['skin']),body,skin_type='GAMEENGINE')
    for mat in body.data.materials:
        if not mat or not mat.use_nodes:continue
        for bs in mat.node_tree.nodes:
            if bs.type=='BSDF_PRINCIPLED':
                if not bs.inputs['Roughness'].is_linked:bs.inputs['Roughness'].default_value=.66
                if not bs.inputs['Specular IOR Level'].is_linked:bs.inputs['Specular IOR Level'].default_value=.28
    attached=[];hair=None
    for name,category in [('high-poly.mhclo','Eyes'),('eyebrow001.mhclo','Eyebrows'),('eyelashes01.mhclo','Eyelashes'),('teeth_base.mhclo','Teeth'),('tongue01.mhclo','Tongue')]:
        ob=Human.add_mhclo_asset(need(name),body,asset_type=category,subdiv_levels=0,material_type='GAMEENGINE')
        if ob is None:raise RuntimeError('Original face asset fit failed '+name)
        attached.append(ob)
    if cfg['hair']:
        hair=Human.add_mhclo_asset(need(cfg['hair']),body,asset_type='Hair',subdiv_levels=0,material_type='GAMEENGINE')
        if hair is None:raise RuntimeError('Hair fitting failed')
        hair.name='HairFitted_'+cid;attached.append(hair)
        for mat in hair.data.materials:
            if not mat or not mat.use_nodes:continue
            for bs in list(mat.node_tree.nodes):
                if bs.type!='BSDF_PRINCIPLED':continue
                color=bs.inputs['Base Color']
                if color.is_linked:
                    previous=color.links[0].from_socket;mat.node_tree.links.remove(color.links[0])
                    tint=mat.node_tree.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1.
                    tint.inputs[2].default_value=(*cfg['hair_color'],1.)
                    mat.node_tree.links.new(previous,tint.inputs[1]);mat.node_tree.links.new(tint.outputs[0],color)
                else:color.default_value=(*cfg['hair_color'],1.)
                bs.inputs['Roughness'].default_value=.77
    garments=[]
    for j,name in enumerate((cfg['shirt'],cfg['pants'])):
        ob=Human.add_mhclo_asset(need(name),body,asset_type='Clothes',subdiv_levels=0,material_type='GAMEENGINE')
        if ob is None:raise RuntimeError('Clothing fit failed '+name)
        ob.name='OpenSourceCloth_'+cid+'_'+Path(name).stem;attached.append(ob);garments.append(ob)
        mat=material(cid+('_shirt' if j==0 else '_pants'),cfg['top'] if j==0 else cfg['bottom'],.87)
        if j==0 and cfg['pattern']:
            image=flowers(cid,cfg['top'],out);node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
            mat.node_tree.links.new(node.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
        ob.data.materials.clear();ob.data.materials.append(mat)
        for poly in ob.data.polygons:poly.material_index=0;poly.use_smooth=True
    shoes=Human.add_mhclo_asset(need('shoes03.mhclo'),body,asset_type='Clothes',subdiv_levels=0,material_type='GAMEENGINE')
    if shoes is None:raise RuntimeError('Shoes fitting failed')
    attached.append(shoes)
    Target.bake_targets(body)
    # Single-source original face targets first, before official child interpolation.
    faceunits.FACE_MORPHS.update({'browDownLeft':'browDownLeft','browDownRight':'browDownRight'})
    metrics=faceunits.attach_faceunits(body,os.environ['FACEUNITS_ROOT'],Target)
    resolver=Clothes.find_clothes_absolute_path;resolved={}
    def original_lookup(obj):
        path=resolver(obj)
        if path is None:
            source=Properties.get_value('asset_source',entity_reference=obj)
            if not source:raise RuntimeError('No original MHCLO metadata '+obj.name)
            path=need(Path(str(source)).name)
        resolved[obj.name]=str(path);return path
    Clothes.find_clothes_absolute_path=staticmethod(original_lookup)
    try:Face.interpolate_targets(body)
    finally:Clothes.find_clothes_absolute_path=staticmethod(resolver)
    Export.bake_modifiers_remove_helpers(body,bake_masks=False,bake_subdiv=False,remove_helpers=True,also_proxy=False)
    for mod in tuple(body.modifiers):
        if mod.type=='MASK':body.modifiers.remove(mod)
    assert len(body.data.vertices)==13380
    for ob in [body,*attached]:
        if not ob.data.shape_keys:continue
        keys=ob.data.shape_keys.key_blocks
        if 'jawOpen' in keys:keys['jawOpen'].name='mouthOpen'
        for combined,left,right in [('mouthSmile','mouthSmileLeft','mouthSmileRight'),('mouthFrown','mouthFrownLeft','mouthFrownRight')]:
            if left not in keys or right not in keys:continue
            basis=keys[0];key=ob.shape_key_add(name=combined,from_mix=False)
            for i,v in enumerate(key.data):v.co=keys[left].data[i].co+keys[right].data[i].co-basis.data[i].co
        for key in keys[1:]:key.value=0.
    assert REQUIRED_KEYS<=set(body.data.shape_keys.key_blocks.keys())
    assert len(body.data.shape_keys.key_blocks)==15
    # Original body stays intact. Only fit cloth outward with equal offsets to Basis/keys.
    bpy.context.view_layer.update();tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    b2w=body.matrix_world.copy();inverse=b2w.inverted();normal=b2w.to_3x3().inverted().transposed();fits=[]
    for ob in garments:
        inv=ob.matrix_world.inverted();count=0;maximum=0.
        for v in ob.data.vertices:
            world=ob.matrix_world@v.co;p,n,_,dist=tree.find_nearest(inverse@world)
            if p is None or dist>.055:continue
            n=normal@n;n.normalize();signed=(world-b2w@p).dot(n)
            if signed<-.045 or signed>=.007:continue
            old=v.co.copy();new=inv@(world+n*(.007-signed));delta=new-old
            if ob.data.shape_keys:
                for k in ob.data.shape_keys.key_blocks:k.data[v.index].co+=delta
            v.co=new;count+=1;maximum=max(maximum,delta.length)
        ob.data.update();fits.append({'mesh':ob.name,'moved':count,'max_local_shift':maximum})
    # Final normalized skin weights are capped to exporter-supported top4 on new humans.
    for ob in [body,*attached]:
        names={g.index:g.name for g in ob.vertex_groups};weights=[]
        for v in ob.data.vertices:
            row=sorted([(names[g.group],g.weight) for g in v.groups if names[g.group] in rig.data.bones and g.weight>0],key=lambda p:p[1],reverse=True)[:4]
            total=sum(w for _,w in row)
            if not total:raise RuntimeError('Unweighted original source vertex '+ob.name)
            weights.append([(n,w/total) for n,w in row])
        ob.vertex_groups.clear()
        for i,row in enumerate(weights):
            for name,w in row:
                group=ob.vertex_groups.get(name) or ob.vertex_groups.new(name=name);group.add([i],w,'REPLACE')
        if ob.parent!=rig:raise RuntimeError('Unexpected source rig hierarchy '+ob.name)
    bpy.context.view_layer.update();p=coordinates(body)
    scale=cfg['height']/(p[:,2].max()-p[:,2].min());rig.scale*=scale
    bpy.context.view_layer.update();p=coordinates(body);rig.location.z-=float(p[:,2].min());bpy.context.view_layer.update()
    height=float(np.ptp(coordinates(body)[:,2]));assert abs(height-cfg['height'])<.0001
    # Force lazy source images to load before resizing, then pack their actual bytes.
    textures=[]
    for image in bpy.data.images:
        if image.source not in ('FILE','GENERATED'):continue
        if not image.has_data and image.source=='FILE':image.reload()
        if len(image.pixels):_=image.pixels[0]
        if not image.has_data:raise RuntimeError('Missing texture data '+image.name)
        factor=min(1.,512/max(image.size));before=list(image.size)
        if factor<1.:image.scale(max(1,round(before[0]*factor)),max(1,round(before[1]*factor)))
        image.pack();textures.append({'name':image.name,'size':list(image.size)})
    np.save(out/(cid+'_native_body.npy'),coordinates(body))
    return body,rig,attached,garments,hair,{'profile':cfg,'face_targets':stack,'macro':macro,
        'height_m':height,'source_vertices_before':19158,'native_body_vertices':13380,
        'helpers_physically_deleted':5778,'bones':53,'body_keys':list(body.data.shape_keys.key_blocks.keys())[1:],
        'original_faceunit_metrics':metrics,'composite_keys':{'mouthSmile':['mouthSmileLeft','mouthSmileRight'],'mouthFrown':['mouthFrownLeft','mouthFrownRight']},
        'source_files':used,'resolved_child_assets':resolved,'clothing_fit':fits,'textures':textures,
        'weights_policy':'top4 deform influences normalized before export on these newly built humans',
        'build_method':'Independent original MPFB macro + face targets, source MHCLO fit, official face interpolation, true helper deletion',
        'art_approved':False}
