"""Real Blender neutral-pose bust occlusion sampling for fitted MPFB CC0 sweater.

World -Y front-camera rays hit the garment and body separately.
This is *not* animation or art acceptance.
"""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def _ray(obj,bvh,world_start,world_direction):
    inverse=obj.matrix_world.inverted()
    start=inverse@world_start
    direction=(inverse.to_3x3()@world_direction).normalized()
    hit,normal,face_index,distance=bvh.ray_cast(start,direction,6.0)
    if hit is None:return None
    return obj.matrix_world@hit

def torso_visibility(body,sweater,top,grid=41):
    if grid<9 or grid%2==0:raise ValueError("Expected odd grid>=9")
    bpy.context.view_layer.update()
    deps=bpy.context.evaluated_depsgraph_get()
    body_bvh=BVHTree.FromObject(body,deps)
    cloth_bvh=BVHTree.FromObject(sweater,deps)
    direction=Vector((0,1,0))
    samples=0; covered=0; cloth_hits=0; exposed=[]; no_fabric=[]
    # Upper central torso, excluding cuffs, arms, collar and side seams.
    for iz in range(grid):
        z=top-.44+iz*(.16/(grid-1))
        for ix in range(grid):
            x=-.135+ix*(.27/(grid-1))
            origin=Vector((x,-2.0,z))
            skin=_ray(body,body_bvh,origin,direction)
            knit=_ray(sweater,cloth_bvh,origin,direction)
            if knit is not None:cloth_hits+=1
            if skin is None:continue
            samples+=1
            if knit is None:
                no_fabric.append((round(x,5),round(z,5)))
                exposed.append((round(x,5),round(z,5),"no knit"))
            elif skin.y < knit.y-.0015:
                exposed.append((round(x,5),round(z,5),round(knit.y-skin.y,5)))
            else:covered+=1
    if samples<grid*grid*.6:
        raise RuntimeError("Chest ray QA failed to cover torso geometry")
    return {"grid":grid,"body_hitting_rays":samples,"cloth_hitting_rays":cloth_hits,
      "skin_covered_samples":covered,
      "front_exposed_body_samples":len(exposed),
      "front_uncovered_body_samples":len(no_fabric),
      "first_exposure_positions":exposed[:30],
      "measurement":"Neutral pose world -Y camera rays; 1.5 mm depth tolerance",
      "art_approval":False,"animation_approved":False}
