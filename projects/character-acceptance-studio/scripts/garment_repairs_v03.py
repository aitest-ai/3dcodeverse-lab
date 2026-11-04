"""Editable, character-specific garment pattern corrections. Original v0.2 is never edited.
New lapels/scarf sample the actual jacket and barycentric skin weights. No clothing service/simulation.
"""
import bpy,bmesh,math,hashlib,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
def snapshot(o):
    return {'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'weights':{str(v.index):{o.vertex_groups[g.group].name:g.weight for g in v.groups} for v in o.data.vertices}}
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def components(o):
    adj={v.index:set() for v in o.data.vertices}
    for e in o.data.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
    seen=set();out=[]
    for v in o.data.vertices:
        if v.index in seen:continue
        q=[v.index];seen.add(v.index);c=[]
        while q:
            k=q.pop();c.append(k)
            for n in adj[k]:
                if n not in seen:seen.add(n);q.append(n)
        out.append(c)
    return out
def remove_vertices(o,indices):
    bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in indices],context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update()
def weights(o,i,row):
    for g in o.vertex_groups:
        try:g.remove([i])
        except RuntimeError:pass
    row=sorted(((n,max(0,w)) for n,w in row.items() if w>1e-7),key=lambda x:x[1],reverse=True)[:4];total=sum(w for _,w in row)
    for n,w in row:(o.vertex_groups.get(n) or o.vertex_groups.new(name=n)).add([i],w/total,'REPLACE')
def finish_mesh(o):
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for p in o.data.polygons:p.use_smooth=True
def new_mesh(rig,name,vs,fs,material):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.parent=rig;o.data.materials.append(material);m=o.modifiers.new('Editable_skin','ARMATURE');m.object=rig;finish_mesh(o)
    uv=me.uv_layers.new(name='Editable_fabric_UV')
    for loop in me.loops:
        p=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(p.x*24,p.z*24)
    return o
def harbor(rig):
    touched={};removed=[];created=[]
    def mark(o):touched.setdefault(o.name,snapshot(o))
    jacket=bpy.data.objects['Original_Tailored_Jacket'];mark(jacket)
    # Woven cloth bridges the cleavage and softens the fitted breast/waist silhouette.
    # This is a local pattern edit, not a uniform rescale of the character or garment.
    adj={v.index:set() for v in jacket.data.vertices}
    for e in jacket.data.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
    for _ in range(10):
        targets={}
        for v in jacket.data.vertices:
            x,y,z=v.co;w=smooth((z-1.13)/.07)*smooth((1.46-z)/.06)*smooth((.205-abs(x))/.055)*smooth((-y-.015)/.04)
            if w and adj[v.index]:targets[v.index]=v.co.y*.65+sum(jacket.data.vertices[i].co.y for i in adj[v.index])/len(adj[v.index])*.35
        for i,y in targets.items():jacket.data.vertices[i].co.y+=(y-jacket.data.vertices[i].co.y)*.7
    for v in jacket.data.vertices:
        x,y,z=v.co
        if y<-.015 and abs(x)<.20:
            w=smooth((z-1.15)/.08)*smooth((1.455-z)/.05)*smooth((.20-abs(x))/.06)
            # Across-center support under the inset shirt; keep outside bust clearance.
            target=-.151*math.sqrt(max(.08,1-(x/.235)**2))+.004
            if target<y:v.co.y+=(target-y)*w*.9
        if z<1.11 and abs(x)<.28:
            w=smooth((1.11-z)/.075);v.co.x*=1+.025*w;v.co.y*=1+.045*w
    for p in jacket.data.polygons:p.material_index=0
    jacket.data.update();jacket.data.calc_loop_triangles();tris=list(jacket.data.loop_triangles);coords=[v.co.copy() for v in jacket.data.vertices];tree=BVHTree.FromPolygons(coords,[list(t.vertices) for t in tris],all_triangles=True);names={g.index:g.name for g in jacket.vertex_groups}
    def surface(x,z,offset=.002):
        p,n,i,d=tree.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
        if p is None or p.y>.06:raise RuntimeError(f'No front jacket at {x},{z}')
        a,b,c=[coords[k] for k in tris[i].vertices];bary=barycentric_transform(p,a,b,c,Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)));row={}
        for vi,w in zip(tris[i].vertices,bary):
            for g in jacket.data.vertices[vi].groups:row[names[g.group]]=row.get(names[g.group],0)+max(0,w)*g.weight
        return Vector((x,p.y-offset,z)),row
    cream=bpy.data.objects['Merged_Shirt_oat_canvas'];mark(cream);ids=[]
    for c in components(cream):
        if min(cream.data.vertices[i].co.z for i in c)>1.39:ids+=c
    removed.append({'object':cream.name,'reason':'eight rigid neck-only flat collar vertices','indices':ids});remove_vertices(cream,ids)
    scarf=bpy.data.objects['Original_coral_neckerchief'];removed.append({'object':scarf.name,'reason':'five-vertex neck-only floating scarf','original':snapshot(scarf)});bpy.data.objects.remove(scarf,do_unlink=True)
    # Refit floating pocket and its stitches to the corrected front, transfer actual garment skin.
    pocket=bpy.data.objects['Merged_Jacket_sea_green'];mark(pocket)
    band_ids=[i for c in components(pocket) if min(pocket.data.vertices[j].co.z for j in c)>1.40 for i in c]
    removed.append({'object':pocket.name,'reason':'oversized rigid neck band replaced by original fitted garment neckline','indices':band_ids});remove_vertices(pocket,band_ids)
    for c in components(pocket):
        if max(pocket.data.vertices[i].co.z for i in c)<1.35:
            for i in c:
                v=pocket.data.vertices[i];v.co,row=surface(v.co.x,v.co.z,.0035);weights(pocket,i,row)
        else:
            for i in c:weights(pocket,i,{'spine_03':.85,'neck_01':.15})
    for c in components(cream):
        if min(cream.data.vertices[i].co.z for i in c)>1.2:
            for i in c:
                v=cream.data.vertices[i];v.co,row=surface(v.co.x,v.co.z,.005);weights(cream,i,row)
    # A continuous inset shirt panel replaces the coarse material-face partition.
    vs=[];fs=[];rows=[]
    for j in range(33):
        t=j/32;width=.042+.007*math.sin(t*math.pi)
        for k in range(13):
            q=k/12*2-1;z=1.039+(1.431+.017*q*q-1.039)*t;p,row=surface(q*width,z,.008);vs.append(list(p));rows.append(row)
    for j in range(32):
        for k in range(12):a=j*13+k;fs.append((a,a+1,a+14,a+13))
    o=new_mesh(rig,'V03_continuous_shirt_inset',vs,fs,bpy.data.materials['Shirt_oat_canvas'])
    for i,row in enumerate(rows):weights(o,i,row)
    m=o.modifiers.new('Editable_fabric_thickness','SOLIDIFY');m.thickness=.0012;m.offset=-1;created.append(o.name)
    # Surface-fitted narrow collar folds; unlike old flat plates these follow chest skinning.
    for side in [-1,1]:
        vs=[];fs=[];rows=[]
        for j in range(17):
            t=j/16;cx=side*(.064+.009*math.sin(t*math.pi)-.024*t);z=1.454-.066*t;width=.007+.003*math.sin(t*math.pi)
            for k in range(5):
                q=k/4;p,row=surface(cx+side*(q-.5)*width*2,z,.011+.002*math.sin(q*math.pi));vs.append(list(p));rows.append(row)
        for j in range(16):
            for k in range(4):a=j*5+k;fs.append((a,a+1,a+6,a+5))
        o=new_mesh(rig,'V03_surface_lapel_'+str(side),vs,fs,bpy.data.materials['Shirt_oat_canvas'])
        for i,row in enumerate(rows):weights(o,i,row)
        m=o.modifiers.new('Editable_fabric_thickness','SOLIDIFY');m.thickness=.0015;m.offset=-1;created.append(o.name)
    vs=[];fs=[];rows=[]
    for j in range(17):
        t=j/16;z=1.445-.078*t;width=.027*(1-t)+.002
        for k in range(7):
            q=k/6;p,row=surface((q-.5)*2*width,z,.016+.003*math.sin(q*math.pi));vs.append(list(p));rows.append(row)
    for j in range(16):
        for k in range(6):a=j*7+k;fs.append((a,a+1,a+8,a+7))
    o=new_mesh(rig,'V03_surface_neckerchief',vs,fs,bpy.data.materials['Ribbon_coral'])
    for i,row in enumerate(rows):weights(o,i,row)
    m=o.modifiers.new('Editable_fabric_thickness','SOLIDIFY');m.thickness=.0012;m.offset=-1;created.append(o.name)
    # Closed rolled cuffs, real inner/outer faces before skinning, no post-skin solidify rim spikes.
    for side,label in [(1,'l'),(-1,'r')]:
        old=bpy.data.objects['Review_continuous_cuff_'+label];removed.append({'object':old.name,'reason':'open sleeve, post-armature Solidify and wrist intersections','original':snapshot(old)});bpy.data.objects.remove(old,do_unlink=True)
        ring=[(.535,.056,.052),(.544,.055,.050),(.552,.050,.045),(.577,.042,.034),(.599,.034,.026),(.605,.035,.027),(.610,.033,.025)]
        vs=[];fs=[];N=40;L=len(ring)
        for inner in [False,True]:
            for x,ry,rz in ring:
                for k in range(N):a=k/N*math.tau;d=.002 if inner else 0;vs.append((side*x,.054+math.cos(a)*(ry-d),1.417+math.sin(a)*(rz-d)))
        for layer in [0,1]:
            for j in range(L-1):
                for k in range(N):a=layer*L*N+j*N+k;b=layer*L*N+j*N+(k+1)%N;fs.append((a,b,b+N,a+N))
        for j in [0,L-1]:
            for k in range(N):a=j*N+k;b=j*N+(k+1)%N;fs.append((a,b,b+L*N,a+L*N))
        o=new_mesh(rig,'V03_closed_rolled_cuff_'+label,vs,fs,bpy.data.materials['Shirt_oat_canvas']);created.append(o.name)
        for v in o.data.vertices:w=.85*smooth((abs(v.co.x)-.568)/.042);weights(o,v.index,{'lowerarm_'+label:1-w,'hand_'+label:w})
    # Keep straps/pocket attached after cloth fitting; match source garment skinning at each point.
    for name in ['Review_jacket_fitted_strap_front']:
        o=bpy.data.objects[name];mark(o)
        for v in o.data.vertices:v.co,row=surface(v.co.x,v.co.z,.020);weights(o,v.index,row)
    changes=[]
    for name,before in touched.items():
        o=bpy.data.objects[name];after=snapshot(o);changes.append({'mesh':name,'before_counts':[len(before['vertices']),len(before['faces'])],'after_counts':[len(after['vertices']),len(after['faces'])],'before_sha256':digest(before),'after_sha256':digest(after),'before':before,'after':after})
    return {'method':'local woven-cloth pattern, surface-fitted lapels/scarf/pocket, closed rolled cuffs; no cloth simulation','changes':changes,'removed_original_components':removed,'created_meshes':created,'body_geometry_changed':False,'source_topology_preserved_in_version':'0.2.0','texture_bytes_changed':False,'art_approved':False}
def oldman(rig):
    shirt=bpy.data.objects['OpenSourceCloth_oldman_toigo_basic_tucked_t-shirt'];before=snapshot(shirt);mw=shirt.matrix_world;inv=mw.inverted();rows=[]
    # Ray from the torso center to the actual outer body/pants. This avoids signed
    # nearest-normal projection jumping across folds or an open pants waistband.
    surfaces=[]
    for name in ['TrueMPFBBody_oldman','OpenSourceCloth_oldman_toigo_wool_pants']:
        base=bpy.data.objects[name];co=[base.matrix_world@v.co for v in base.data.vertices];surfaces.append((name,BVHTree.FromPolygons(co,[list(p.vertices) for p in base.data.polygons])))
    for v in shirt.data.vertices:
        p=mw@v.co;original=p.copy();w=smooth((1.215-p.z)/.16)
        if not w:continue
        hem_w=smooth((1.115-p.z)/.11);p.z-=.018*hem_w;center=Vector((0,-.012,p.z));radial=p-center;radial.z=0;radius=radial.length
        if radius<.001:continue
        direction=radial.normalized();wanted=radius
        for name,tree in surfaces:
            hit,n,idx,d=tree.ray_cast(center,direction)
            if hit is not None:wanted=max(wanted,(hit-center).length+(.012 if name.startswith('True') else .014))
        wanted=min(wanted,radius+.055);p=center+direction*(radius+(wanted-radius)*w);v.co=inv@p
        rows.append({'vertex':v.index,'before_world':list(original),'after_world':list(p),'hem_extension_m':.018*hem_w,'radial_allowance_added_m':(wanted-radius)*w})
    # Restrained circumferential smoothing of the refitted lower pattern; no UV or topology changes.
    adjacency={v.index:set() for v in shirt.data.vertices}
    for e in shirt.data.edges:a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
    for _ in range(3):
        targets={}
        for row in rows:
            i=row['vertex'];v=shirt.data.vertices[i];z=row['before_world'][2];w=smooth((1.105-z)/.10)
            near=[j for j in adjacency[i] if abs((mw@shirt.data.vertices[j].co).z-(mw@v.co).z)<.008]
            if near:targets[i]=v.co.lerp(sum((shirt.data.vertices[j].co for j in near),Vector())/len(near),.12*w)
        for i,p in targets.items():shirt.data.vertices[i].co=p
    # Match the same character's underlying skin field at the refitted abdomen.
    # Geometry projection and weight transfer are separate; normals never move the pattern.
    body=bpy.data.objects['TrueMPFBBody_oldman'];body.data.calc_loop_triangles();tri=list(body.data.loop_triangles);co=[body.matrix_world@v.co for v in body.data.vertices];tree=BVHTree.FromPolygons(co,[list(t.vertices) for t in tri],all_triangles=True);transfers=[]
    for v in shirt.data.vertices:
        old_z=(mw@Vector(before['vertices'][v.index])).z;blend=smooth((1.22-old_z)/.14)
        if not blend:continue
        p=mw@v.co;hit,n,idx,d=tree.find_nearest(p)
        if d>.065:continue
        a,b,c=[co[k] for k in tri[idx].vertices];bary=barycentric_transform(hit,a,b,c,Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)));field={}
        for vi,w in zip(tri[idx].vertices,bary):
            for g in body.data.vertices[vi].groups:name=body.vertex_groups[g.group].name;field[name]=field.get(name,0)+max(0,w)*g.weight
        old={shirt.vertex_groups[g.group].name:g.weight for g in v.groups};row={n:w*(1-blend) for n,w in old.items()}
        for n,w in field.items():row[n]=row.get(n,0)+w*blend
        weights(shirt,v.index,row);transfers.append({'vertex':v.index,'body_field_blend':blend,'surface_distance_m':d})
    shirt.data.update();after=snapshot(shirt)
    return {'method':'Original MRT topology/UV preserved. Local 18mm hem extension plus bounded radial fit over actual body/pants; same-character body skin field transfer at abdomen/waist. No body masking or signed-normal geometry projection','changes':[{'mesh':shirt.name,'before':before,'after':after,'before_sha256':digest(before),'after_sha256':digest(after)}],'hem_vertex_changes':rows,'weight_field_transfers':transfers,'body_geometry_changed':False,'texture_bytes_changed':False,'art_approved':False}
