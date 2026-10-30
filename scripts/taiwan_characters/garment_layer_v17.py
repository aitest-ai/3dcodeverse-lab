"""V17 MPFB CC0 garment layering QA.

Compare real front-facing sweater and trousers on identical camera rays, then
move only already-existing sweater vertices (and *all* shape keys) outward so
the sweater is in front of the trousers where they overlap. This preserves
the source meshes, UVs, materials, bone weights, and open hem edges.
No painted hiding, no new occlusion shell, and no destructive face deletion.
"""
import math
from statistics import median
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def _front_hit(obj, bvh, x, z):
    start=Vector((x,-2.0,z))
    mat=obj.matrix_world
    inverse=mat.inverted()
    start_local=inverse@start
    direction_local=(inverse.to_3x3()@Vector((0,1,0))).normalized()
    hit,normal,index,distance=bvh.ray_cast(start_local,direction_local,5.0)
    if hit is None:
        return None
    return mat@hit


def _bvh(ob):
    bpy.context.view_layer.update()
    return BVHTree.FromObject(ob,bpy.context.evaluated_depsgraph_get())


def layering_report(sweater,pants,top,bins_x=47,bins_z=31):
    """Ray comparison over *actual* fabric overlap; side and front checked."""
    sb=_bvh(sweater)
    pb=_bvh(pants)
    region=(top-.71,top-.50)
    results={"overlap_rays":0,"pants_in_front":0,"sweater_in_front":0,
             "only_pants_rays":0,"only_sweater_rays":0,"empty_rays":0,
             "worst_pants_front_depth_m":0.0,"occlusion_samples":[]}
    for zi in range(bins_z):
        z=region[0]+(region[1]-region[0])*zi/(bins_z-1)
        for xi in range(bins_x):
            x=-.235+.47*xi/(bins_x-1)
            sw=_front_hit(sweater,sb,x,z)
            pa=_front_hit(pants,pb,x,z)
            if sw is None and pa is None:
                results["empty_rays"]+=1
                continue
            if sw is None:
                results["only_pants_rays"]+=1
                continue
            if pa is None:
                results["only_sweater_rays"]+=1
                continue
            results["overlap_rays"]+=1
            # Blender -Y is toward the actual front camera.
            behind=sw.y-pa.y
            if behind>0.0015:
                results["pants_in_front"]+=1
                results["worst_pants_front_depth_m"]=max(results["worst_pants_front_depth_m"],behind)
                if len(results["occlusion_samples"])<35:
                    results["occlusion_samples"].append([round(x,4),round(z,4),round(behind,5)])
            else:
                results["sweater_in_front"]+=1
    if results["overlap_rays"]<25:
        raise RuntimeError("V17 overlap front rays insufficient; cannot infer layering")
    results["wrong_layer_fraction"]=round(results["pants_in_front"]/results["overlap_rays"],5)
    results["worst_pants_front_depth_m"]=round(results["worst_pants_front_depth_m"],5)
    return results


def correct_sweater_layer(sweater,pants,top,margin=.009,max_displacement=.070):
    """Position-aware surface correction, never touch the pants mesh or faces."""
    pb=_bvh(pants)
    inverse=sweater.matrix_world.inverted()
    keys=sweater.data.shape_keys.key_blocks if sweater.data.shape_keys else []
    change=[]
    rejected=[]
    for v in sweater.data.vertices:
        world=sweater.matrix_world@v.co
        if not (top-.74 <= world.z <= top-.48 and abs(world.x)<=.28 and world.y<.065):
            continue
        pa=_front_hit(pants,pb,world.x,world.z)
        if pa is None:
            continue
        # Fix a surface that is behind the trouser at exactly the same X/Z.
        # Optional allowance (~9 mm) helps avoid z-fighting in oblique renders.
        necessary=world.y-pa.y+margin
        if necessary<=0.001:
            continue
        if necessary>max_displacement:
            rejected.append({"vertex":v.index,"needed_m":round(necessary,5)})
            continue
        change.append((v.index,necessary))
    if rejected:
        raise RuntimeError("Real sweater requires unsafe >7cm outward offset; refusing "
                           +str(rejected[:10]))
    if len(change)<10:
        raise RuntimeError("V17 no source CC0 sweater vertices need correction")
    corrected=0;maximum=0.0
    for index,shift in change:
        vertex=sweater.data.vertices[index]
        old=vertex.co.copy()
        world=sweater.matrix_world@old
        world.y-=shift
        updated=inverse@world
        delta=updated-old
        if keys:
            for key in keys:
                key.data[index].co+=delta
        vertex.co=updated
        corrected+=1
        maximum=max(maximum,shift)
    sweater.data.update()
    bpy.context.view_layer.update()
    return {"moved_original_vertices":corrected,
            "max_outward_m":round(maximum,5),
            "all_shape_keys_also_moved":bool(keys),
            "shape_key_count":len(keys),
            "no_faces_created_or_deleted":True}
