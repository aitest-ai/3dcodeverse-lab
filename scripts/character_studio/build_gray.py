"""Stage 01: two independently modelled MPFB gray identity candidates.

Uses official morph targets before rig fitting, physically removes helpers only
on the delivered copy, and retains a separate parametric Blender mother file.
No old character is read. No skin masking, clothes, facial animation, texture
resizing or inherited animation data is performed in this stage.
"""
from __future__ import annotations
import argparse, hashlib, importlib, json, math, os, sys, time
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_SEMANTICS = {
    "root":"Root", "hips":"pelvis", "spine_lower":"spine_01",
    "spine_middle":"spine_02", "spine_upper":"spine_03",
    "neck":"neck_01", "head":"head",
    **{f"{part}_{side}":name+"_"+s for side,s in (("left","l"),("right","r"))
       for part,name in (("upper_arm","upperarm"),("forearm","lowerarm"),("hand","hand"),
                         ("thigh","thigh"),("shin","calf"),("foot","foot"))}
}
MPFB_TOPOLOGY = {"original_with_helpers":19158, "body_only":13380}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p, obj):
    p = Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
def service(suffix, name):
    modules=[s for s in sys.modules if s.endswith(suffix)]
    if len(modules)!=1: raise RuntimeError("Ambiguous MPFB service: "+suffix)
    return getattr(importlib.import_module(modules[0]),name)
def points(ob, evaluated=True):
    bpy.context.view_layer.update()
    if not evaluated:
        return np.asarray([tuple(ob.matrix_world@v.co) for v in ob.data.vertices])
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh=ev.to_mesh()
    try: return np.asarray([tuple(ev.matrix_world@v.co) for v in mesh.vertices])
    finally: ev.to_mesh_clear()
def gray_material(name, color=.41):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(color,color,color,1)
    bs.inputs["Roughness"].default_value=.72
    bs.inputs["Metallic"].default_value=0
    return mat
def smooth(ob):
    for face in ob.data.polygons: face.use_smooth=True
def preserve_images(out):
    records=[]
    for image in bpy.data.images:
        if image.source!="FILE":continue
        # Blender may defer image decoding. has_data=False is not a missing file;
        # explicitly decode before checking dimensions, then keep original bytes.
        source=Path(bpy.path.abspath(image.filepath))
        raw=source.read_bytes() if source.is_file() else (bytes(image.packed_file.data) if image.packed_file else None)
        if raw is None:raise RuntimeError("Original image is unavailable: "+image.name)
        dimensions=list(image.size)
        if len(image.pixels)==0 or min(dimensions)<=0:raise RuntimeError("Original image did not decode: "+image.name)
        _=image.pixels[0]
        relative=Path("textures")/source.name
        target=out/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=raw:raise RuntimeError("Original texture name collision: "+str(relative))
        target.write_bytes(raw)
        image.pack(data=raw,data_len=len(raw));image.filepath="//"+relative.as_posix();image.use_fake_user=True
        records.append({"name":image.name,"file":relative.as_posix(),"sha256":sha(target),
                        "original_dimensions":dimensions,"stored_dimensions":list(image.size),"resized":False,
                        "pixels_decoded":True,"used_in_gray_material":False})
    if not any(x["file"].endswith("/brown_eye.png") for x in records):
        raise RuntimeError("Expected original eye image missing from retained sources")
    return records
def clear_scene():
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
def configure_studio():
    scene=bpy.context.scene; scene.render.engine="CYCLES"
    scene.cycles.device="CPU"; scene.cycles.samples=32
    scene.cycles.use_denoising=True
    scene.render.threads_mode="FIXED"; scene.render.threads=4
    scene.render.resolution_x=800; scene.render.resolution_y=1000
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=False
    scene.view_settings.view_transform="AgX"
    scene.world=bpy.data.worlds.new("StudioGrayWorld"); scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value=(.20,.215,.23,1); bg.inputs["Strength"].default_value=.32
    data=bpy.data.cameras.new("ReviewCamera"); cam=bpy.data.objects.new("ReviewCamera",data)
    scene.collection.objects.link(cam); scene.camera=cam; data.type="ORTHO"
    cam.location=(0,-4,1.02);cam.rotation_euler=(math.pi/2,0,0)
    data.ortho_scale=2.2
    for name,pos,energy,size in [
        ("Key",(-3,-4,4),450,2.2),("Fill",(3,-3,2.5),100,3),
        ("Rim",(1,2,3.5),260,2.5)]:
        data=bpy.data.lights.new(name,"AREA");data.energy=energy;data.size=size
        ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob)
        ob.location=pos;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat("-Z","Y").to_euler()
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001))
    floor=bpy.context.object;floor.name="StudioGround"
    floor.data.materials.append(gray_material("GroundGray",.15))
    return scene,cam
def render_views(out, cid, body, rig, common, prefix):
    scene=bpy.context.scene; cam=scene.camera
    xyz=points(body)
    height=float(xyz[:,2].max()-xyz[:,2].min())
    # Both characters use these exact shared full-body camera settings.
    full_target=Vector((0,0,1.02))
    head=rig.pose.bones.get("head")
    head_z=(rig.matrix_world@head.head).z if head else height-.22
    face_target=Vector((0,-.01,(height+head_z)*.5-.032))
    views=[
      ("front",0,full_target,common["fullbody_ortho_scale_m"],800,1000),
      ("side",90,full_target,common["fullbody_ortho_scale_m"],800,1000),
      ("back",180,full_target,common["fullbody_ortho_scale_m"],800,1000),
      ("face",0,face_target,common["face_ortho_scale_m"],800,800),
      ("face_threequarter",35,face_target,common["face_ortho_scale_m"],800,800),
      ("face_side",90,face_target,common["face_ortho_scale_m"],800,800)]
    settings=[]
    for name,angle,target,scale,w,h in views:
        a=math.radians(angle)
        cam.location=target+Vector((math.sin(a)*4,-math.cos(a)*4,0))
        cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
        cam.data.ortho_scale=scale
        scene.render.resolution_x=w;scene.render.resolution_y=h
        path=out/"renders"/f"{cid}_{prefix}_{name}.png"
        path.parent.mkdir(parents=True,exist_ok=True)
        scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        settings.append({"file":str(path.relative_to(out)),"angle_degrees":angle,
                         "camera_location":list(cam.location),"target":list(target),
                         "ortho_scale_m":scale,"resolution":[w,h],
                         "vertical_pixels_per_meter":h/scale,
                         "source":"actual exported GLB reimported" if prefix=="delivered" else "editable Blender source"})
        print("RENDER_DONE",path.name,flush=True)
    return settings
def bone_report(rig):
    result={}
    for semantic,name in REQUIRED_SEMANTICS.items():
        if name not in rig.data.bones:raise RuntimeError("Required semantic bone missing: "+name)
        b=rig.data.bones[name]
        head=rig.matrix_world@b.head_local;tail=rig.matrix_world@b.tail_local
        result[semantic]={"bone":name,"head_m":list(head),"tail_m":list(tail),
                          "length_m":(tail-head).length,"parent":b.parent.name if b.parent else None,
                          "rest_matrix": [list(row) for row in b.matrix_local]}
    return result
def normalize_weights(ob, rig):
    names={g.index:g.name for g in ob.vertex_groups}; bone_names=set(rig.data.bones.keys())
    rows=[];omitted_max=0
    for v in ob.data.vertices:
        all_weights=sorted([(names[g.group],float(g.weight)) for g in v.groups
                            if names[g.group] in bone_names and g.weight>0],key=lambda x:x[1],reverse=True)
        keep=all_weights[:4];total=sum(x[1] for x in keep)
        if total<=0:raise RuntimeError(f"Unweighted vertex {ob.name}:{v.index}")
        omitted_max=max(omitted_max,sum(x[1] for x in all_weights[4:]))
        rows.append([(name,w/total) for name,w in keep])
    ob.vertex_groups.clear()
    groups={}
    for i,row in enumerate(rows):
        for name,w in row:
            if name not in groups:groups[name]=ob.vertex_groups.new(name=name)
            groups[name].add([i],w,"REPLACE")
    return {"max_discarded_weight_before_renormalization":omitted_max,"max_influences":4}
def run(args):
    started=time.time()
    package=json.loads(Path(args.profiles).read_text());cfg=package["characters"][args.character]
    common=package["common"];cid=args.character
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    if (out/"report.json").exists() and not args.replace_candidate:
        raise RuntimeError("Candidate output exists; use a new version directory")
    clear_scene()
    bpy.context.preferences.filepaths.save_version=0
    if "bl_ext.local_mpfb.mpfb" not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module="bl_ext.local_mpfb.mpfb")
    Human=service("mpfb.services.humanservice","HumanService")
    Target=service("mpfb.services.targetservice","TargetService")
    Export=service("mpfb.services.exportservice","ExportService")
    macro=Target.get_default_macro_info_dict();macro.update(cfg["macro"]);macro["race"]=common["race"]
    body=Human.create_human(mask_helpers=True,extra_vertex_groups=True,feet_on_ground=True,
                            scale=.1,macro_detail_dict=macro)
    if len(body.data.vertices)!=MPFB_TOPOLOGY["original_with_helpers"]:
        raise RuntimeError("Unexpected pinned MPFB basemesh topology")
    body.name=cid+"_Body"
    targets=[{"target":n,"value":v} for n,v in cfg["body_targets"]+cfg["face_targets"]]
    sources=[]
    for item in targets:
        path=Target.target_full_path(item["target"])
        if path is None:raise RuntimeError("Missing official target: "+item["target"])
        if Path(path).name.removesuffix(".gz").removesuffix(".target") != item["target"]:
            raise RuntimeError("Target resolver returned a prefix match instead of the exact target: "+item["target"])
        sources.append({**item,"source_file":Path(path).name,"sha256":sha(path)})
    Target.bulk_load_targets(body,targets);bpy.context.view_layer.update()
    rig=Human.add_builtin_rig(body,"game_engine");rig.name=cid+"_Rig"
    # Rig is fitted AFTER the actual phenotype/face/limb target geometry.
    attached=[];asset_sources=[];assets=Path(args.assets).resolve()
    # Closed-mouth neutral review only. The original dental/tongue fitting files
    # are a later expression-stage dependency, never improvised from another face.
    for filename,category in [("high-poly.mhclo","Eyes")]:
        found=sorted(assets.rglob(filename))
        if not found:raise RuntimeError("Required original fitting asset missing: "+filename)
        if len({sha(p) for p in found})!=1:raise RuntimeError("Ambiguous asset: "+filename)
        p=found[0];header=p.read_text(errors="replace")[:4000]
        if "cc0" not in header.lower():raise RuntimeError("CC0 asset header not confirmed: "+filename)
        ob=Human.add_mhclo_asset(str(p),body,asset_type=category,subdiv_levels=0,material_type="GAMEENGINE")
        if ob is None:raise RuntimeError("Native fitting failed: "+filename)
        ob.name=cid+"_"+category;attached.append(ob)
        asset_sources.append({"file":filename,"sha256":sha(p),"header":header})
    raw=points(body);scale=cfg["height_m"]/float(np.ptp(raw[:,2]))
    # This only calibrates absolute metres AFTER distinct anatomy is generated.
    # Ratios are independently set by macro + local official targets above.
    rig.scale*=scale;bpy.context.view_layer.update()
    xyz=points(body);rig.location.z-=float(xyz[:,2].min());bpy.context.view_layer.update()
    gray=gray_material(cid+"_Clay")
    for ob in [body,*attached]:
        # Retain original imported materials for the next stage even though the
        # current review intentionally uses one neutral clay shader.
        for original_material in ob.data.materials:
            if original_material:original_material.use_fake_user=True
        ob.data.materials.clear();ob.data.materials.append(gray)
        for poly in ob.data.polygons:poly.material_index=0
        smooth(ob)
    scene,cam=configure_studio()
    profile_path=out/"profile.json";dump(profile_path,{"schema_version":1,"version":package["version"],"common":common,"character":cfg})
    texture_records=preserve_images(out)
    # Preserve every parametric target and helper in a clearly labelled authoring
    # mother, separate from the cleaned editable delivery. No helper is exported.
    bpy.ops.file.pack_all()
    param=out/(cid+"_parametric.blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(param),compress=True)
    Target.bake_targets(body)
    Export.bake_modifiers_remove_helpers(body,bake_masks=False,bake_subdiv=False,remove_helpers=True,also_proxy=False)
    for mod in list(body.modifiers):
        if mod.type=="MASK":body.modifiers.remove(mod)
    if len(body.data.vertices)!=MPFB_TOPOLOGY["body_only"]:
        raise RuntimeError("Pinned source helper removal failed")
    weights={}
    for ob in [body,*attached]:
        weights[ob.name]=normalize_weights(ob,rig)
    # The runtime surface is a subdivision derived from this editable mother.
    # This is a stage-01 quality surface, not a fallback or independent LOD.
    sub=body.modifiers.new("SameMotherSurface","SUBSURF")
    sub.subdivision_type="CATMULL_CLARK";sub.levels=1;sub.render_levels=1
    semantics=bone_report(rig)
    xyz=points(body);height=float(np.ptp(xyz[:,2]))
    def joint_distance(a,b):
        return float(np.linalg.norm(np.asarray(semantics[a]["head_m"])-np.asarray(semantics[b]["head_m"])))
    thigh=semantics["thigh_left"]["length_m"];shin=semantics["shin_left"]["length_m"]
    measures={"height_target_m":cfg["height_m"],"height_surface_m":height,
      "height_calibration_factor":scale,"calibration_scope":"absolute metres after independent anatomy",
      "bounds_m":{"min":xyz.min(axis=0).tolist(),"max":xyz.max(axis=0).tolist()},
      "shoulder_joint_span_m":joint_distance("upper_arm_left","upper_arm_right"),
      "hip_joint_span_m":joint_distance("thigh_left","thigh_right"),
      "thigh_m":thigh,"shin_m":shin,"leg_bones_to_height":(thigh+shin)/height,
      "upper_arm_m":semantics["upper_arm_left"]["length_m"],
      "forearm_m":semantics["forearm_left"]["length_m"],
      "forearm_to_upper_arm":semantics["forearm_left"]["length_m"]/semantics["upper_arm_left"]["length_m"],
      "measurement_note":"joint spans are bone-center distances, not skin/clothing shoulder or hip widths"}
    clean=out/(cid+".blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(clean),compress=True)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in [rig,body,*attached]:ob.select_set(True)
    bpy.context.view_layer.objects.active=rig
    glb=out/(cid+".glb")
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True,
        export_apply=True,export_skins=True,export_animations=False,export_morph=True,
        export_normals=True,export_morph_normal=True,export_cameras=False,export_lights=False,export_extras=True)
    dump(out/"rig_semantics.json",{"schema_version":1,"adapter":"mpfb_game_engine","unit":"metre",
        "source_coordinates":"Blender Z-up, forward -Y","runtime_coordinates":"glTF Y-up",
        "joint_count_observed":len(rig.data.bones),"semantics":semantics,
        "extra_bones":[b.name for b in rig.data.bones if b.name not in REQUIRED_SEMANTICS.values()],
        "retarget_status":"not yet adapted; copying legacy translations or bind matrices is prohibited"})
    dump(out/"measurements.json",measures)
    # Real reimport with original stage lights. The delivered images all come
    # from GLB after deleting every source MESH and ARMATURE in this scene.
    for ob in list(scene.objects):
        if ob.type in ("MESH","ARMATURE") and ob.name!="StudioGround":bpy.data.objects.remove(ob,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    rig2=next(ob for ob in scene.objects if ob.type=="ARMATURE")
    meshes=[ob for ob in scene.objects if ob.type=="MESH"]
    body2=next(ob for ob in meshes if ob.name.startswith(cid+"_Body"))
    rexyz=points(body2)
    delta=max(float(np.max(np.abs(xyz.min(axis=0)-rexyz.min(axis=0)))),
              float(np.max(np.abs(xyz.max(axis=0)-rexyz.max(axis=0)))))
    if delta>0.001:raise RuntimeError("Reimported body bounds differ by more than 1mm: "+str(delta))
    renders=render_views(out,cid,body2,rig2,common,"delivered") if not args.skip_renders else []
    bpy.ops.wm.open_mainfile(filepath=str(clean))
    clean_body=bpy.data.objects[cid+"_Body"]
    if len(clean_body.data.vertices)!=MPFB_TOPOLOGY["body_only"]:raise RuntimeError("Reopened source body differs")
    cold_images=[]
    for record in texture_records:
        image=bpy.data.images.get(record["name"])
        if image is None or image.packed_file is None or list(image.size)!=record["original_dimensions"]:
            raise RuntimeError("Cold-reopened mother did not retain original image: "+record["name"])
        if hashlib.sha256(bytes(image.packed_file.data)).hexdigest()!=record["sha256"]:
            raise RuntimeError("Packed original image bytes changed: "+image.name)
        if len(image.pixels)==0:raise RuntimeError("Packed original image did not decode: "+image.name)
        cold_images.append({"name":image.name,"dimensions":list(image.size),"packed":True,
                            "sha256":record["sha256"],"decoded_pixel_count":len(image.pixels)//image.channels})
    files=[param,clean,glb,profile_path,out/"rig_semantics.json",out/"measurements.json"]
    report={"schema_version":1,"asset_id":cfg["asset_id"],"version":package["version"],"stage":package["stage"],
      "status":"GRAY_IDENTITY_REVIEW_CANDIDATE","art_approved":False,"game_ready":False,
      "build_environment":{"blender":bpy.app.version_string,"build_hash":bpy.app.build_hash.decode(),
        "runtime":"headless Cycles CPU","git_commit":os.getenv("GITHUB_SHA","local-uncommitted-candidate"),
        "build_script_sha256":sha(__file__),"profiles_sha256":sha(args.profiles),
        "elapsed_seconds":time.time()-started},
      "profile":cfg,"common":common,"measurements":measures,"official_target_sources":sources,
      "native_asset_sources":asset_sources,"weights":weights,"textures":texture_records,
      "native_body_vertices":len(clean_body.data.vertices),"helpers_physically_removed":19158-len(clean_body.data.vertices),
      "body_mask_or_clothing_deletion":False,"gray_surface_subdivision_level":1,
      "source_blend_reopened":True,"glb_reimported":True,"roundtrip_bounds_max_error_m":delta,
      "cold_reopened_original_images":cold_images,
      "renders":renders,"files":[{"file":str(p.relative_to(out)),"bytes":p.stat().st_size,"sha256":sha(p)} for p in files],
      "not_completed":["hair","wardrobe","dental and tongue fitting sources","facial expression adaptation","idle","walk","turn","sit and stand",
                       "game/browser validation","Android measurements","cycling","horse riding"],
      "appearance_note":"This stage is an anatomical gray identity review. Technical checks do not approve naturalness."}
    dump(out/"report.json",report)
    dump(out/"asset_manifest.json",{"schema_version":1,"asset_id":cfg["asset_id"],"version":package["version"],
      "format":"glTF 2.0 GLB","unit":"meter","source":"MPFB2 original phenotype and official local targets",
      "model_file":glb.name,"source_file":clean.name,"parametric_source_file":param.name,"clips":[],
      "min_animation_count":0,"requirements":{"skins":True,"animated":False,"visual_review":True},
      "license_note":"MakeHuman core base/targets/system body parts CC0; exact headers and hashes in report",
      "stage":"gray_identity","art_approved":False,"game_ready":False})
    print("GRAY_CANDIDATE_COMPLETE",cid,json.dumps(measures),flush=True)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--character",choices=["d03","d06"],required=True)
    parser.add_argument("--profiles",default=str(ROOT/"assets/characters/studio/profiles.json"))
    parser.add_argument("--assets",required=True);parser.add_argument("--out",required=True)
    parser.add_argument("--skip-renders",action="store_true")
    parser.add_argument("--replace-candidate",action="store_true")
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    run(args)
if __name__=="__main__":main()

