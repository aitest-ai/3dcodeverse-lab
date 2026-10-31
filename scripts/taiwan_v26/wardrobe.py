"""V26 role identity candidates from genuine native V20 characters.
Original accessories and CC0-source-derived outer garment. Never change the
source body/face, original garments, their weights, or embedded textures.
No real delivery brand, personal data, protected insignia, or image overlays.
"""
import math
from collections import Counter,defaultdict
import numpy as np
import bpy,bmesh
from mathutils import Vector,Matrix
from belt import WeightSource,material,mesh
from apron import tree,finalize,ribbon,cord,grid_sheet
from source_waist import coordinates


def box(name,location,size,mat,rig,weights,bevel=.006):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location)
    ob=bpy.context.object;ob.name=name;ob.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=ob.modifiers.new('BakedSoftEdges','BEVEL');mod.width=bevel;mod.segments=3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
    ob.data.materials.append(mat)
    return finalize(ob,rig,weights)


def smooth_path(points,subdivisions=5):
    p=[Vector(q) for q in points];out=[]
    for i in range(len(p)-1):
        a=p[max(0,i-1)];b=p[i];c=p[i+1];d=p[min(len(p)-1,i+2)]
        for j in range(subdivisions):
            t=j/subdivisions
            out.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
    out.append(tuple(p[-1]));return out


def source_boundaries(obj):
    edges=Counter()
    for face in obj.data.polygons:
        vs=list(face.vertices)
        for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))]+=1
    adj=defaultdict(set)
    for (a,b),n in edges.items():
        if n==1:adj[a].add(b);adj[b].add(a)
    seen=set();loops=[]
    for start in adj:
        if start in seen:continue
        component=[];pending=[start];seen.add(start)
        while pending:
            v=pending.pop();component.append(v)
            for w in adj[v]:
                if w not in seen:seen.add(w);pending.append(w)
        if len(component)<8 or any(len(adj[v])!=2 for v in component):continue
        order=[component[0]];previous=None;now=component[0]
        for _ in range(len(component)-1):
            nxt=next(v for v in sorted(adj[now]) if v!=previous and v not in order)
            order.append(nxt);previous,now=now,nxt
        loops.append(order)
    return loops


def build(role,body,shirt,pants,hair,rig):
    h=float(coordinates(body)[:,2].max())
    added=[];groups={};prefix='V26_'+role+'_'
    torso=tree(shirt,rig,True);skin=tree(body,rig,True)
    shirt_weights=WeightSource(shirt,rig);body_weights=WeightSource(body,rig)
    def add(ob,group):
        ob['asset_role']=role+' V26 wardrobe';ob['geometry_license']='CC0-1.0'
        ob['accessory_group']=group;added.append(ob);groups.setdefault(group,[]).append(ob.name)
        return ob
    def surface(x,z,back=False,extra=.012):
        start=Vector((x,1 if back else -1,z));direction=Vector((0,-1 if back else 1,0));ys=[]
        for t in (torso,skin):
            p,_,_,_=t.ray_cast(start,direction,2)
            if p is not None:ys.append(p.y)
        if not ys:raise RuntimeError('No torso surface '+str((x,z,back)))
        return (max(ys)+extra) if back else (min(ys)-extra)
    def strap_surface(x,z,back=False):return (x,surface(x,z,back,.020),z)
    fabric=material(prefix+'Softshell_BlueGrey' if role=='you' else prefix+'Softshell_Teal',
                    (.105,.155,.205) if role=='you' else (.035,.22,.18),.87)
    knit=material(prefix+'Ribbed_Cuffs',(.043,.061,.074) if role=='you' else (.018,.080,.067),.92)
    seam=material(prefix+'Seams',(.028,.044,.061),.92)
    webbing=material(prefix+'Charcoal_Webbing',(.018,.023,.028),.94)
    metal=material(prefix+'BrushedMetal',(.26,.28,.30),.32,.80)
    cream=material(prefix+'Reflective_LightGrey',(.58,.62,.60),.55)
    white=material(prefix+'WarmWhite',(.74,.75,.71),.65)

    # Independent copy of the existing lawful garment. Source object, data and
    # material are never altered. Preserve its actual skin weights and UVs.
    outer=shirt.copy();outer.data=shirt.data.copy();outer.name=prefix+'HoodedLayer_Base'
    bpy.context.scene.collection.objects.link(outer)
    outer.data.materials.clear();outer.data.materials.append(fabric)
    for f in outer.data.polygons:f.material_index=0;f.use_smooth=True
    # Uniform source-normal offset, synchronized to all copied keys.
    old=np.array([tuple(v.co) for v in outer.data.vertices]);norm=np.array([tuple(v.normal) for v in outer.data.vertices])
    delta=norm*.006
    keys=list(outer.data.shape_keys.key_blocks) if outer.data.shape_keys else []
    snapshots=[np.array([tuple(v.co) for v in k.data]) for k in keys]
    outer.data.vertices.foreach_set('co',np.asarray(old+delta,dtype='f4').ravel())
    for k,p in zip(keys,snapshots):k.data.foreach_set('co',np.asarray(p+delta,dtype='f4').ravel())
    outer.data.update();add(outer,'hooded_layer')
    outer['source']='Independent fitted derivative of original CC0 '+shirt.name

    # Extend genuine short-sleeve opening to wrists, using original seam ring
    # positions and original body weights rather than a static cylinder.
    loops=source_boundaries(outer);points=coordinates(outer);sleeve_notes=[]
    for sign,side in ((1,'l'),(-1,'r')):
        options=[loop for loop in loops if sign*points[loop,0].mean()>.17]
        if not options:
            sleeve_notes.append({'side':side,'status':'no_native_closed_opening_kept_short'});continue
        loop=max(options,key=lambda q:sign*points[q,0].mean());ring=points[loop]
        start=ring.mean(0);wrist=np.array(rig.matrix_world@rig.pose.bones['hand_'+side].head)
        elbow=np.array(rig.matrix_world@rig.pose.bones['lowerarm_'+side].head)
        axis=Vector(wrist-start).normalized();basis=Vector((0,1,0));basis=(basis-axis*basis.dot(axis)).normalized();second=axis.cross(basis)
        vec=ring-start;angles=np.arctan2(vec@np.array(second),vec@np.array(basis))
        angles=np.unwrap(angles);radii=np.linalg.norm(vec-(vec@np.array(axis))[:,None]*np.array(axis),axis=1)
        verts=[];uv=[];count=len(loop);rows=11
        for j,t in enumerate(np.linspace(0,1,rows)):
            c=(1-t)*start+t*wrist
            for i,a in enumerate(angles):
                radius=(1-t)*radii[i]+t*.037
                q=c+radius*(math.cos(a)*np.array(basis)+math.sin(a)*np.array(second))
                if j==0:q=ring[i]
                verts.append(tuple(q));uv.append((i/count,t))
        faces=[]
        for j in range(rows-1):
            for i in range(count):faces.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
        sleeve=finalize(mesh(prefix+'Sleeve_'+side,verts,faces,fabric,uv),rig,body_weights.at);add(sleeve,'hooded_layer')
        # Visible knit cuff is a separate source-bound soft band, not a glove.
        vs=[]
        for t in (.94,1.025):
            c=start+(wrist-start)*t
            for i,a in enumerate(angles):vs.append(tuple(c+.038*(math.cos(a)*np.array(basis)+math.sin(a)*np.array(second))))
        fs=[(i,(i+1)%count,count+(i+1)%count,count+i) for i in range(count)]
        add(finalize(mesh(prefix+'Cuff_'+side,vs,fs,knit),rig,body_weights.at),'hooded_layer')
        sleeve_notes.append({'side':side,'native_seam_vertices':count,'status':'long_sleeve_added'})

    # Folded hood: a genuine recessed cloth bowl behind the neck, not a head cap.
    # Its narrow front ends stay at the collar, and the rear hangs down the back.
    verts=[];uv=[];rows=12;cols=41
    for j,v in enumerate(np.linspace(0,1,rows)):
        for i,a in enumerate(np.linspace(-math.pi/2,3*math.pi/2,cols)):
            rx=.071+v*.060;ry=.067+v*.070
            x=rx*math.cos(a);y=.022+ry*math.sin(a)
            rear=max(0.,math.sin(a));z=h-.260-v*(.018+.105*rear)+.012*math.sin(math.pi*v)
            verts.append((x,y,z));uv.append((i/(cols-1),v))
    hood=grid_sheet(prefix+'FoldedHood',verts,rows,cols,fabric,rig,shirt_weights.at,uv,.002)
    add(hood,'hooded_layer')
    rim=[verts[(rows-1)*cols+i] for i in range(cols)]
    add(cord(prefix+'Hood_Rim',rim,knit,rig,shirt_weights.at,.0025),'hooded_layer')
    # Central zipper and two understated pocket seams on the fitted front.
    zs=np.linspace(h-.71,h-.31,25);zip_path=[]
    for z in zs:
        try:zip_path.append((0,surface(0,float(z),extra=.014),float(z)))
        except RuntimeError:pass
    if len(zip_path)>8:
        add(ribbon(prefix+'ZipperTape',zip_path,.014,seam,rig,shirt_weights.at),'hooded_layer')
        add(cord(prefix+'ZipperTeeth',[(x,y-.001,z) for x,y,z in zip_path],metal,rig,shirt_weights.at,.001),'hooded_layer')
    for side in (-1,1):
        path=[]
        for t in np.linspace(0,1,14):
            x=side*(.065+.055*t);z=h-.62+.08*t
            path.append((x,surface(x,z,extra=.014),z))
        add(cord(prefix+'PocketSeam_'+str(side),path,knit,rig,shirt_weights.at,.0015),'hooded_layer')

    if role=='you':
        # Blank illustrated badge: no real employer, personal information or logo.
        badge_z=h-.49;badge_y=surface(0,badge_z,extra=.030);badge_weights={'spine_02':1.}
        for side in (-1,1):
            path=[strap_surface(side*.049,h-.275),strap_surface(side*.058,h-.34),
                  strap_surface(side*.043,h-.405),(side*.008,badge_y,badge_z+.041)]
            add(ribbon(prefix+'Badge_Lanyard_'+str(side),smooth_path(path),.010,webbing,rig,shirt_weights.at),'identity_badge')
        add(box(prefix+'Badge_Holder',(0,badge_y,badge_z),(.061,.005,.087),webbing,rig,badge_weights,.004),'identity_badge')
        add(box(prefix+'Badge_Card',(0,badge_y-.0036,badge_z),(.054,.0015,.077),white,rig,badge_weights,.002),'identity_badge')
        add(box(prefix+'Badge_ColorBand',(0,badge_y-.0046,badge_z+.025),(.049,.001,.012),fabric,rig,badge_weights,.001),'identity_badge')
        # Generic photo silhouette and three information bars, not text or identity.
        add(box(prefix+'Badge_Photo',(-.013,badge_y-.0046,badge_z+.002),(.017,.001,.022),cream,rig,badge_weights,.002),'identity_badge')
        for j,w in enumerate((.021,.017,.036)):
            add(box(prefix+'Badge_Line_'+str(j),(.006 if j<2 else 0,badge_y-.0046,badge_z-.005-j*.009),(w,.001,.0023),seam,rig,badge_weights,.0005),'identity_badge')
    else:
        hp=coordinates(hair);cx=float((hp[:,0].min()+hp[:,0].max())/2);cy=float((hp[:,1].min()+hp[:,1].max())/2)
        rx=float(np.ptp(hp[:,0])/2+.017);ry=float(np.ptp(hp[:,1])/2+.017)
        cz=h-.092;rz=float(hp[:,2].max()+.023-cz)
        shellmat=material(prefix+'Helmet_OffWhite',(.70,.73,.69),.32)
        padding=material(prefix+'Helmet_Padding',(.012,.017,.020),.90)
        helmet_weights={'head':1.}
        N=64;R=15;verts=[];uv=[]
        for inner in (False,True):
            for j in range(R):
                s=j/(R-1)
                for i in range(N):
                    a=2*math.pi*i/N;pmax=1.56+.19*math.sin(a);polar=.035+s*(pmax-.035)
                    shrink=.0045 if inner else 0.
                    verts.append((cx+(rx-shrink)*math.sin(polar)*math.cos(a),
                        cy+(ry-shrink)*math.sin(polar)*math.sin(a),cz+(rz-shrink)*math.cos(polar)))
                    uv.append((i/N,s))
        faces=[];count=R*N
        for offset in (0,count):
            for j in range(R-1):
                for i in range(N):
                    a=offset+j*N+i;b=offset+j*N+(i+1)%N;c=b+N;d=a+N
                    faces.append((a,b,c,d) if offset==0 else (a,d,c,b))
        for j in (0,R-1):
            for i in range(N):
                a=j*N+i;b=j*N+(i+1)%N;faces.append((a,a+count,b+count,b))
        # Close the tiny crown openings rather than leave a polar puncture.
        faces.extend([tuple(range(N-1,-1,-1)),tuple(range(count,count+N))])
        add(finalize(mesh(prefix+'Helmet_Shell',verts,faces,shellmat,uv),rig,helmet_weights),'helmet')
        border=[verts[(R-1)*N+i] for i in range(N)]+[verts[(R-1)*N]]
        add(cord(prefix+'Helmet_Rim',border,padding,rig,helmet_weights,.005),'helmet')
        # Low front peak, short enough to keep face readable from normal view.
        points=[];nr=3;nc=31
        for j,t in enumerate(np.linspace(0,1,nr)):
            for a in np.linspace(-2.40,-.74,nc):
                pmax=1.56+.19*math.sin(a);x=cx+rx*math.sin(pmax)*math.cos(a)
                y=cy+ry*math.sin(pmax)*math.sin(a)-.030*t;z=cz+rz*math.cos(pmax)-.006*t
                points.append((x,y,z))
        add(grid_sheet(prefix+'Helmet_Peak',points,nr,nc,fabric,rig,helmet_weights,thickness=.003),'helmet')
        # Jaw straps fit close to the head; mask sits below the mouth.
        for sign in (-1,1):
            path=[(sign*rx*.94,cy,cz+.002),(sign*.076,cy-.025,h-.185),(sign*.035,cy-.060,h-.257)]
            add(ribbon(prefix+'Helmet_Strap_'+str(sign),smooth_path(path),.009,padding,rig,helmet_weights),'helmet')
        maskmat=material(prefix+'Mask_Fabric',(.17,.22,.23),.94)
        pts=[];mr=9;mc=23
        for j,t in enumerate(np.linspace(0,1,mr)):
            for i,u in enumerate(np.linspace(-1,1,mc)):
                x=.066*u;y=cy-.112+.032*u*u-.003*math.sin(math.pi*t)
                z=h-.219-.038*t+.006*u*u
                pts.append((x,y,z))
        add(grid_sheet(prefix+'ChinMask_Fabric',pts,mr,mc,maskmat,rig,helmet_weights,thickness=.001),'chin_mask')
        for j in (2,4,6):add(cord(prefix+'Mask_Pleat_'+str(j),[(x,y-.001,z) for x,y,z in pts[j*mc:(j+1)*mc]],maskmat,rig,helmet_weights,.0006),'chin_mask')
        for sign in (-1,1):
            path=[(sign*.063,cy-.080,h-.218),(sign*.083,cy-.025,h-.16),(sign*.079,cy+.003,h-.182),(sign*.064,cy-.078,h-.245)]
            add(cord(prefix+'Mask_Earloop_'+str(sign),smooth_path(path),white,rig,helmet_weights,.0011),'chin_mask')
        # Structured insulated backpack: real beveled shell, padded back, top
        # lid, reflective stripes, seam piping and fitted shoulder straps.
        packmat=material(prefix+'Pack_TealCanvas',(.035,.19,.16),.85)
        packedge=material(prefix+'Pack_DarkBinding',(.015,.042,.037),.90)
        packw={'spine_02':1.};pz=h-.54
        back=surface(0,pz,True,.028);py=back+.125
        add(box(prefix+'Pack_Main',(0,py,pz),(.342,.250,.390),packmat,rig,packw,.018),'delivery_pack')
        add(box(prefix+'Pack_BackPad',(0,back-.007,pz),(.268,.021,.323),webbing,rig,packw,.014),'delivery_pack')
        add(box(prefix+'Pack_Lid',(0,py,pz+.195),(.349,.257,.033),packmat,rig,packw,.013),'delivery_pack')
        add(box(prefix+'Pack_ZipperBand',(0,py+.126,pz+.167),(.317,.004,.012),packedge,rig,packw,.002),'delivery_pack')
        add(box(prefix+'Pack_Reflector',(0,py+.128,pz-.08),(.282,.003,.029),cream,rig,packw,.004),'delivery_pack')
        # Rounded seam path on outward-facing back panel.
        path=[]
        for x,z in ((-.15,pz-.168),(.15,pz-.168),(.15,pz+.145),(-.15,pz+.145),(-.15,pz-.168)):
            path.append((x,py+.127,z))
        add(cord(prefix+'Pack_Piping',path,packedge,rig,packw,.0025),'delivery_pack')
        handle=smooth_path([(-.065,py,pz+.209),(-.058,py,pz+.235),(.058,py,pz+.235),(.065,py,pz+.209)])
        add(ribbon(prefix+'Pack_TopHandle',handle,.018,webbing,rig,packw),'delivery_pack')
        for sign in (-1,1):
            # True shoulder height from downward torso ray; exclude sleeves.
            hit,_,_,_=torso.ray_cast(Vector((sign*.113,0,h+.1)),Vector((0,0,-1)),.6)
            if hit is None:raise RuntimeError('Shoulder fit missing')
            path=[(sign*.112,back+.010,pz+.163),(sign*.112,surface(sign*.112,h-.32,True,.025),h-.32),
                  (sign*.113,.0,hit.z+.016),strap_surface(sign*.113,h-.34),strap_surface(sign*.120,h-.48),
                  strap_surface(sign*.147,h-.64),(sign*.14,back+.015,pz-.15)]
            add(ribbon(prefix+'Pack_ShoulderStrap_'+str(sign),smooth_path(path),.034,webbing,rig,shirt_weights.at),'delivery_pack')
            add(box(prefix+'Pack_SideReflector_'+str(sign),(sign*.172,py,pz-.078),(.003,.155,.026),cream,rig,packw,.002),'delivery_pack')
        # Small center clasp across straps, follows chest without stretching box.
        zz=h-.44;yy=surface(0,zz,extra=.038)
        add(box(prefix+'Pack_ChestClasp',(0,yy,zz),(.024,.007,.016),webbing,rig,packw,.003),'delivery_pack')

    for ob in added:
        ob['accessory_visibility_note']='Hide this named group with its related objects, original character remains'
    return added,{'role':role,'groups':groups,'new_geometry_license':'CC0-1.0',
       'outer_garment_source':'Independent copy of original licensed CC0 shirt; fitted normal-offset shell and original long-sleeve extensions',
       'sleeve_construction':sleeve_notes,'body_face_hair_unchanged':True,
       'original_pants_unchanged':True,'no_real_brand_or_personal_data':True,
       'objects':[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'group':o['accessory_group']} for o in added],
       'limitations':['Cloth is armature-driven, not physical simulation','Hero denim and face/hair polish remain pending','Hood geometry is a folded-hood styling candidate, not hand-tailored clothing']}
