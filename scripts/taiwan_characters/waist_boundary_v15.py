"""V15 neutral-pose garment boundary QA, additive to the verified V14 MPFB pipeline.

Uses *real mesh boundary edges*, not global lowest shirt / highest trousers Z.
Neutral-pose front faces camera from world -Y.  Never reports animation approval.
"""
from collections import Counter, defaultdict
from statistics import median
import math

def clamp(v, low=0.0, high=1.0):
    return max(low, min(high, v))

def smoothstep01(v):
    t = clamp(v)
    return t*t*(3.0-2.0*t)

def percentile(values, f):
    seq = sorted(values)
    if not seq:
        raise ValueError("empty values")
    pos = clamp(f)*(len(seq)-1)
    lo = int(pos)
    hi = min(lo+1,len(seq)-1)
    if hi == lo:
        return seq[lo]
    return seq[lo]*(hi-pos)+seq[hi]*(pos-lo)

def boundary_components(obj):
    """Return vertex index components from open boundary edges of source mesh."""
    edges = Counter()
    for poly in obj.data.polygons:
        ids = list(poly.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):
            edges[tuple(sorted((int(a),int(b))))] += 1
    neighbors = defaultdict(set)
    for (a,b),count in edges.items():
        if count == 1:
            neighbors[a].add(b)
            neighbors[b].add(a)
    seen = set()
    result = []
    for first in neighbors:
        if first in seen:
            continue
        pending=[first]; seen.add(first); comp=[]
        while pending:
            v=pending.pop()
            comp.append(v)
            for nxt in neighbors[v]:
                if nxt not in seen:
                    seen.add(nxt); pending.append(nxt)
        if len(comp)>=8:
            result.append(comp)
    return result

def world_loop(obj, indices):
    return [(i, tuple(obj.matrix_world@obj.data.vertices[i].co)) for i in indices]

def select_waist_loop(obj, mode):
    """Choose wide waist opening, excluding narrow sleeves and trouser cuffs."""
    candidates=[]
    for ids in boundary_components(obj):
        points=world_loop(obj,ids)
        x=[p[1][0] for p in points]
        z=[p[1][2] for p in points]
        width=max(x)-min(x)
        if width < .17 or len(points)<12:
            continue
        candidates.append((median(z),width,points))
    if not candidates:
        raise RuntimeError("No authentic wide garment boundary loop on "+obj.name)
    # Lower wide loop is shirt hem; upper wide loop is trouser waist.
    selected=min(candidates,key=lambda x:x[0]) if mode=="shirt" else max(candidates,key=lambda x:x[0])
    return selected[2]

def front_points(loop):
    """Front half of the actual opening, not loose sleeves or the rear hem."""
    middle=median(p[1][1] for p in loop)
    front=[p for p in loop if p[1][1] <= middle + .008]
    if len(front)<8:
        raise RuntimeError("Not enough front-facing true garment boundary points")
    return front

def sampled_height(points, x):
    # Use nearest original boundary vertices, resistant to one jagged corner.
    ordered=sorted(points,key=lambda p:abs(p[1][0]-x))
    nearest=ordered[:min(7,len(ordered))]
    if not nearest or abs(nearest[0][1][0]-x)>.055:
        raise RuntimeError("Insufficient waist geometry near x="+str(x))
    return median(v[1][2] for v in nearest)

def waist_profile(shirt, trousers, bins=11, desired_overlap_m=.018):
    shirt_loop=select_waist_loop(shirt,"shirt")
    pants_loop=select_waist_loop(trousers,"pants")
    shirt_front=front_points(shirt_loop)
    pants_front=front_points(pants_loop)
    sx=[p[1][0] for p in shirt_front]
    px=[p[1][0] for p in pants_front]
    # Keep only central overlapping front width: no sleeve openings or side seams.
    left=max(percentile(sx,.08),percentile(px,.08))
    right=min(percentile(sx,.92),percentile(px,.92))
    if right-left < .10:
        raise RuntimeError("Shirt/pants front boundary widths do not overlap")
    samples=[]
    for i in range(bins):
        x=left+(right-left)*i/(bins-1)
        hem=sampled_height(shirt_front,x)
        waistband=sampled_height(pants_front,x)
        bare_gap=max(0.0,hem-waistband)
        required=max(0.0,hem+desired_overlap_m-waistband)
        samples.append({"x_m":round(x,5),"shirt_front_hem_z_m":round(hem,5),
            "pants_front_edge_z_m":round(waistband,5),
            "bare_gap_m":round(bare_gap,5),"needed_rise_m":round(required,5)})
    return {"samples":samples,"front_max_bare_gap_m":max(x["bare_gap_m"] for x in samples),
        "front_max_required_rise_m":max(x["needed_rise_m"] for x in samples),
        "shirt_loop_vertices":len(shirt_loop),"trouser_loop_vertices":len(pants_loop),
        "waist_z_m":median(s["pants_front_edge_z_m"] for s in samples),
        "front_pants_median_y_m":median(p[1][1] for p in pants_loop)}

def interpolate_field(samples, x, key):
    if x <= samples[0]["x_m"]:
        return samples[0][key]
    if x >= samples[-1]["x_m"]:
        return samples[-1][key]
    for a,b in zip(samples,samples[1:]):
        if a["x_m"] <= x <= b["x_m"]:
            w=(x-a["x_m"])/(b["x_m"]-a["x_m"])
            return a[key]*(1-w)+b[key]*w
    raise AssertionError("non-monotonic samples")

def repair_waistband(trousers, profile, project_outside=None):
    """Raise original skinned trouser verts smoothly; never synthesize geometry."""
    samples=profile["samples"]
    max_rise=profile["front_max_required_rise_m"]
    if max_rise>.12:
        raise RuntimeError("Required waist rise exceeds safety 12cm; refusing fake fix: "+str(max_rise))
    if max_rise < .0005:
        return {"moved_vertices":0,"maximum_applied_rise_m":0.0,"already_overlapped":True}
    inv=trousers.matrix_world.inverted()
    base_y=profile["front_pants_median_y_m"]
    moved=0; max_applied=0.0
    for v in trousers.data.vertices:
        world=trousers.matrix_world@v.co
        edge_z=interpolate_field(samples,world.x,"pants_front_edge_z_m")
        falloff=smoothstep01((world.z-(edge_z-.19))/.19)
        if falloff<=0:
            continue
        # Preserve continuous rear waistband, prioritizing visible front.
        front_factor=1.0 if world.y<=base_y else .75
        rise=interpolate_field(samples,world.x,"needed_rise_m")*falloff*front_factor
        if rise<.0002:
            continue
        candidate=world.copy()
        candidate.z+=rise
        if project_outside is not None:
            candidate=project_outside(candidate)
        v.co=inv@candidate
        moved+=1;max_applied=max(max_applied,rise)
    trousers.data.update()
    return {"moved_vertices":moved,"maximum_applied_rise_m":round(max_applied,5),
            "already_overlapped":False}

def chest_depth_diagnostic(sweater, head_top_m):
    """Measure front sweater outline only; no unsupported automatic bust sculpt."""
    z_mid=head_top_m-.52
    points=[tuple(sweater.matrix_world@v.co) for v in sweater.data.vertices
            if abs((sweater.matrix_world@v.co).z-z_mid)<=.13]
    if len(points)<16:
        return {"measurement":"unavailable","reason":"insufficient genuine chest vertices"}
    center_x=median(p[0] for p in points)
    torso=[p for p in points if abs(p[0]-center_x)<.19]
    if len(torso)<16:
        return {"measurement":"unavailable","reason":"insufficient central chest vertices"}
    front_edge=[]
    for i in range(9):
        x=center_x-.15+i*.30/8
        near=sorted(torso,key=lambda p:abs(p[0]-x))[:10]
        front_edge.append({"x_m":round(x,4),"front_y_m":round(percentile([p[1] for p in near],.12),5)})
    depths=[p["front_y_m"] for p in front_edge]
    return {"measurement":"source_mesh_neutral_front_depth",
            "center_height_m":round(z_mid,4),"samples":front_edge,
            "front_depth_range_m":round(max(depths)-min(depths),5),
            "art_approval":False}
