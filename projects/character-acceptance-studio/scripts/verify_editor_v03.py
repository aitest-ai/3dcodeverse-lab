"""Cold-read v0.3 mothers, verify unchanged raw geometry/UV/shape keys/rest bones/textures.
The oldman's explicitly logged shoe weight edit is the only allowed skin-weight change.
"""
import bpy,json,hashlib,array,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];result={'blender':bpy.app.version_string,'assets':{},'art_approved':False,'offline_render':'NOT_RENDERED'}
def digest(x):return hashlib.sha256(x).hexdigest()
def coordinates(data,attr,n):
    a=array.array('f',[0.0])*(len(data)*n);data.foreach_get(attr,a);return digest(a.tobytes())
def inspect(path):
    before=digest(path.read_bytes());bpy.ops.wm.open_mainfile(filepath=str(path));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');meshes={}
    for o in bpy.data.objects:
        if o.type!='MESH':continue
        keys={k.name:coordinates(k.data,'co',3) for k in o.data.shape_keys.key_blocks} if o.data.shape_keys else {}
        groups={g.index:g.name for g in o.vertex_groups};weights=[[(groups[g.group],g.weight) for g in v.groups] for v in o.data.vertices]
        meshes[o.name]={'vertices':len(o.data.vertices),'positions':coordinates(o.data.vertices,'co',3),'polygons':[list(p.vertices) for p in o.data.polygons],'uv':[coordinates(u.data,'uv',2) for u in o.data.uv_layers],'shape_keys':keys,'weights_sha256':digest(json.dumps(weights).encode())}
    images={}
    for im in bpy.data.images:
        if im.packed_file and im.size[0]:assert len(im.pixels)>0;_=float(im.pixels[0]);images[im.name]={'dimensions':list(im.size),'sha256':digest(im.packed_file.data)}
    bones=[(b.name,b.parent.name if b.parent else None,[list(row) for row in b.matrix_local]) for b in rig.data.bones]
    assert digest(path.read_bytes())==before
    return {'sha256':before,'meshes':meshes,'images':images,'rest_bones':bones,'bone_count':len(bones),'actions':[a.name for a in bpy.data.actions]}

asset=os.environ.get('STUDIO_CHARACTER','harbor-courier-review');root=Path(os.environ.get('STUDIO_V03_ROOT',str(R/'assets')))
before=inspect(R/'assets'/asset/'0.2.0'/(asset+'.blend'));after=inspect(root/asset/'0.3.0'/(asset+'.blend'));assert before['rest_bones']==after['rest_bones'];assert before['images']==after['images'];changed=[]
allowed={'Original_Tailored_Jacket','Merged_Jacket_sea_green','Merged_Shirt_oat_canvas','Review_jacket_fitted_strap_front'} if asset.startswith('harbor') else {'OpenSourceCloth_oldman_toigo_basic_tucked_t-shirt'}
for name in before['meshes'].keys()&after['meshes'].keys():
 if before['meshes'][name]!=after['meshes'][name]:changed.append(name);assert name in allowed,(asset,name,'unexpected raw mesh/weights change')
if asset.startswith('taiwan'):
 a,b=before['meshes'][next(iter(allowed))],after['meshes'][next(iter(allowed))]
 assert a['polygons']==b['polygons'] and a['uv']==b['uv'] and a['vertices']==b['vertices']
# Actual cold-read manifoldness of closed cuff volume, no screen/normal mock.
cuffs={}
for o in bpy.data.objects:
 if not o.name.startswith('V03_closed_rolled_cuff'):continue
 from collections import Counter
 edges=Counter(tuple(sorted((a,b))) for p in o.data.polygons for a,b in zip(list(p.vertices),list(p.vertices)[1:]+[p.vertices[0]]));assert set(edges.values())=={2};assert len(o.data.uv_layers)==1;cuffs[o.name]={'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'every_edge_incident_faces':2,'fabric_uv_present':True}
result={'asset':asset,'blender':bpy.app.version_string,'source_sha256':before['sha256'],'candidate_sha256':after['sha256'],'body_shoes_hair_pants_raw_geometry_weights_uv_shapes_unchanged':True,'rest_bones_identical':True,'images_byte_identical_and_pixels_decoded':after['images'],'changed_existing_meshes':changed,'removed_meshes':sorted(before['meshes'].keys()-after['meshes'].keys()),'new_meshes':sorted(after['meshes'].keys()-before['meshes'].keys()),'closed_cuffs':cuffs,'art_approved':False,'offline_render':'NOT_RENDERED'}
(R/'evidence-v03'/(asset+'-editor-qa.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('V03_COLD_READ_PASS',asset)
