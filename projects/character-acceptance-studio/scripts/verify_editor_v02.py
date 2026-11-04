"""Cold-read v0.2 mothers, verify unchanged raw geometry/UV/shape keys/rest bones/textures.
The oldman's explicitly logged shoe weight edit is the only allowed skin-weight change.
"""
import bpy,json,hashlib,array
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
for asset,old in [('harbor-courier-review','harbor-courier-review'),('taiwan-oldman-review','oldman-retarget-candidate')]:
    before=inspect(R/'assets'/asset/'0.1.0'/(old+'.blend'));after=inspect(R/'assets'/asset/'0.2.0'/(asset+'.blend'));assert before['rest_bones']==after['rest_bones'];assert before['images']==after['images'];changed=[]
    assert before['meshes'].keys()==after['meshes'].keys()
    for n,a in before['meshes'].items():
        b=after['meshes'][n]
        for key in ['vertices','positions','polygons','uv','shape_keys']:assert a[key]==b[key],(asset,n,key)
        if a['weights_sha256']!=b['weights_sha256']:changed.append(n)
    assert changed==([] if asset.startswith('harbor') else ['TrueMPFBBody_oldman.shoes03']),changed
    assert set(after['actions'])=={'Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight'}
    result['assets'][asset]={'source_sha256':before['sha256'],'candidate_sha256':after['sha256'],'bone_count':after['bone_count'],'mesh_count':len(after['meshes']),'raw_positions_topology_uv_shape_keys_rest_bones_identical':True,'packed_images_byte_identical':after['images'],'weights_changed_meshes':changed,'cold_read_pixel_decode':True}
(R/'evidence-v02/editor-qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('EDITOR_V02_PRESERVATION_PASS')
