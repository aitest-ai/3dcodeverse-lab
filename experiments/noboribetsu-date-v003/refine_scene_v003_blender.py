"""Blender-native V003 refinements applied on top of the frozen V002 master.

Scope is deliberately narrow:
1. subtle material multiplier / roughness calibration;
2. Yugi-kan noren and seam drape;
3. render-only broken soil/moss transition on the existing road perimeter.

No route, DEM, collision, tile roof, column-foot, building footprint or survey claim is changed.
This module is meant to be called from promote_master_v003.py inside Blender 5.2.x.
"""
from __future__ import annotations
import json, math, os, random
from collections import Counter
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(os.environ.get("NOBORIBETSU_PROJECT_ROOT", Path.cwd())).resolve()
VERSION = "V003"

MATERIAL_FACTORS = {
    "朱塗り_原創木目": ((0.94, 0.91, 0.87, 1.0), 0.84),
    "白壁_原創石灰表面": ((0.94, 0.93, 0.88, 1.0), 0.98),
    "LM_Yugi_ochre_plaster": ((0.96, 0.93, 0.86, 1.0), 0.99),
    "LM_Yugi_aged_timber": ((0.91, 0.86, 0.78, 1.0), 0.96),
    "LM_Yugi_cloth_hems": ((0.78, 0.88, 0.90, 1.0), 0.98),
    "LM_Yugi_blue_noren": ((0.84, 0.93, 0.94, 1.0), 0.97),
}


def _principled(mat):
    assert mat and mat.use_nodes, f"Material missing nodes: {getattr(mat, 'name', None)}"
    p = mat.node_tree.nodes.get("Principled BSDF")
    assert p is not None, f"Principled BSDF missing: {mat.name}"
    return p


def _insert_color_multiplier(mat, factor):
    p = _principled(mat)
    sock = p.inputs["Base Color"]
    nt = mat.node_tree
    links = list(sock.links)
    if nt.nodes.get("V003_BaseColorMultiplier") is not None:
        raise RuntimeError(f"V003 color already applied to {mat.name}")
    if links:
        src = links[0].from_socket
        nt.links.remove(links[0])
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.name = "V003_BaseColorMultiplier"
        mix.label = "V003 subtle weathering multiplier (author-estimated)"
        mix.blend_type = "MULTIPLY"
        mix.inputs[0].default_value = 1.0
        mix.inputs[2].default_value = factor
        nt.links.new(src, mix.inputs[1])
        nt.links.new(mix.outputs[0], sock)
    else:
        old = tuple(sock.default_value)
        sock.default_value = tuple(old[i] * factor[i] for i in range(4))


def _insert_roughness_multiplier(mat, factor):
    p = _principled(mat)
    sock = p.inputs["Roughness"]
    nt = mat.node_tree
    links = list(sock.links)
    if nt.nodes.get("V003_RoughnessMultiplier") is not None:
        raise RuntimeError(f"V003 roughness already applied to {mat.name}")
    if links:
        src = links[0].from_socket
        nt.links.remove(links[0])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.name = "V003_RoughnessMultiplier"
        mul.label = "V003 subtle roughness multiplier (author-estimated)"
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = factor
        nt.links.new(src, mul.inputs[0])
        nt.links.new(mul.outputs[0], sock)
    else:
        # Preserve the V002 authored roughness; a multiplier is not an absolute value.
        sock.default_value = max(0.0, min(1.0, float(sock.default_value) * factor))


def apply_material_balance():
    records = []
    for name, (color_factor, roughness) in MATERIAL_FACTORS.items():
        mat = bpy.data.materials.get(name)
        assert mat is not None, f"Required V002 material missing: {name}"
        if "v003_provenance" in mat:
            raise RuntimeError(f"V003 refinement already present on material: {name}")
        _insert_color_multiplier(mat, color_factor)
        _insert_roughness_multiplier(mat, roughness)
        mat["v003_provenance"] = (
            "Subtle photo-guided visual calibration only; no measured paint age or species claim. "
            "Original embedded texture pixels and resolution unchanged."
        )
        records.append({
            "material": name,
            "base_color_multiplier": list(color_factor),
            "roughness_factor": roughness,
        })
    return records


def _material_vertex_refs(mat_name):
    """Return only vertices actually referenced by faces using mat_name.

    V002 may contain multi-material meshes. Never deform every vertex on an
    object merely because one material slot matches the noren material.
    """
    pts = []
    refs = []
    # Never modify A_DATA_SKELETON even if a material name is shared.
    B = bpy.data.collections.get("B_SITE_REFINEMENT")
    assert B is not None, "V002 B_SITE_REFINEMENT collection missing"
    for ob in B.all_objects:
        if ob.type != "MESH" or not ob.data:
            continue
        if ob.get("v003_noren_" + mat_name):
            raise RuntimeError(f"V003 noren material already applied: {ob.name} / {mat_name}")
        slot_ids = {
            i for i, mat in enumerate(ob.data.materials)
            if mat and mat.name == mat_name
        }
        if not slot_ids:
            continue
        vertex_ids = set()
        for poly in ob.data.polygons:
            if poly.material_index in slot_ids:
                vertex_ids.update(poly.vertices)
        if not vertex_ids:
            continue
        mw = ob.matrix_world.copy()
        for vi in sorted(vertex_ids):
            w = mw @ ob.data.vertices[vi].co
            pts.append((float(w.x), float(-w.y), float(w.z)))
            refs.append((ob, vi))
    return pts, refs


def _pca_long_axis_2d(points):
    n = len(points)
    mx = sum(p[0] for p in points) / n
    mz = sum(p[1] for p in points) / n
    a = sum((p[0]-mx)**2 for p in points) / n
    b = sum((p[0]-mx)*(p[1]-mz) for p in points) / n
    c = sum((p[1]-mz)**2 for p in points) / n
    tr = a + c
    disc = math.sqrt(max(0.0, (a-c)*(a-c) + 4*b*b))
    lam = (tr + disc) / 2
    if abs(b) > 1e-12:
        vx, vz = lam - c, b
    elif a >= c:
        vx, vz = 1.0, 0.0
    else:
        vx, vz = 0.0, 1.0
    length = math.hypot(vx, vz)
    vx, vz = vx/length, vz/length
    if vz < 0:
        vx, vz = -vx, -vz
    return (mx, mz), (vx, vz)


def _deform_material_group(mat_name, fold_amplitude):
    points, refs = _material_vertex_refs(mat_name)
    assert refs, f"No faces use material {mat_name}"
    center, long = _pca_long_axis_2d(points)
    normal = (-long[1], long[0])
    s = [(p[0]-center[0])*long[0] + (p[1]-center[1])*long[1] for p in points]
    smin, smax = min(s), max(s)
    span = max(1e-6, smax-smin)
    pw = span/20.0
    ytop = max(p[2] for p in points)
    ybot = min(p[2] for p in points)
    yr = max(0.001, ytop-ybot)
    offsets = [-.006,.012,-.014,.018,-.010,.006,-.020,.014,-.004,.010,-.012,.016,-.008,.004,-.018,.012,-.006,.020,-.010,.006]
    max_disp = 0.0
    for i, ((ob, vi), p) in enumerate(zip(refs, points)):
        panel = max(0, min(19, int((s[i]-smin)/pw)))
        t = max(0.0, min(1.0, (ytop-p[2])/yr))
        local = ((s[i]-smin)-panel*pw)/pw
        fold = math.sin(local*math.tau + panel*.73) * fold_amplitude * (t**1.25)
        new_world = Vector((
            p[0] + normal[0]*fold,
            -(p[1] + normal[1]*fold),
            p[2] - offsets[panel]*(t**1.8),
        ))
        old_world = ob.matrix_world @ ob.data.vertices[vi].co
        max_disp = max(max_disp, (new_world-old_world).length)
        if (new_world-old_world).length > 0.05:
            raise RuntimeError(f"Noren edit exceeds 5 cm at {ob.name} vertex {vi}")
        ob.data.vertices[vi].co = ob.matrix_world.inverted() @ new_world
        ob.data.update()
        ob["v003_noren_" + mat_name] = "author-estimated drape; no official motif copied"
    return {
        "material": mat_name,
        "objects": len({id(ob) for ob, _ in refs}),
        "vertices": len(points),
        "max_vertex_displacement_m": max_disp,
    }


def apply_noren_drape():
    return [
        _deform_material_group("LM_Yugi_cloth_hems", 0.004),
        _deform_material_group("LM_Yugi_blue_noren", 0.010),
    ]


def _mesh_object(name, verts, faces, material, collection):
    me = bpy.data.meshes.new(name + "_mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    me.materials.append(material)
    return ob


def add_ground_edge_blend(collection):
    geo = json.loads((ROOT/"data"/"scene_geometry.json").read_text())
    road = geo["road"]
    vs, tris = road["vertices"], road["triangles"]
    counts, directed = Counter(), {}
    for tri in tris:
        for a,b in zip(tri, tri[1:]+tri[:1]):
            key = tuple(sorted((a,b)))
            counts[key] += 1
            directed[key] = (a,b)
    rng = random.Random(2026110103)
    positions, faces = [], []
    widths = []
    segs = 0
    for key, count in counts.items():
        if count != 1:
            continue
        ia, ib = directed[key]
        a, b = Vector(vs[ia]), Vector(vs[ib])
        mid = (a+b)/2
        if not (-13 <= mid.x <= 15 and -46 <= mid.y <= 26):
            continue
        d = Vector((b.x-a.x, b.y-a.y, 0))
        L = d.length
        if L < .06 or (ia*31+ib*17)%5 == 0:
            continue
        perp = Vector((-d.y, d.x, 0)).normalized()
        w = .045 + rng.random()*.035
        lift_a = .006 + rng.uniform(0,.003)
        lift_b = .006 + rng.uniform(0,.003)
        k = len(positions)
        positions.extend([
            (a + perp*(-w) + Vector((0,0,lift_a)))[:],
            (a + perp*( w) + Vector((0,0,lift_a)))[:],
            (b + perp*( w) + Vector((0,0,lift_b)))[:],
            (b + perp*(-w) + Vector((0,0,lift_b)))[:],
        ])
        faces.extend([(k,k+1,k+2), (k,k+2,k+3)])
        widths.append(w)
        segs += 1
    mat = bpy.data.materials.get("V003_inferred_edge_blend_NOT_drain")
    if mat is None:
        mat = bpy.data.materials.new("V003_inferred_edge_blend_NOT_drain")
        mat.use_nodes = True
        p = mat.node_tree.nodes.get("Principled BSDF")
        p.inputs["Base Color"].default_value = (.17,.14,.095,1)
        p.inputs["Roughness"].default_value = 1.0
        p.inputs["Metallic"].default_value = 0.0
    if not segs or len(faces) != 2 * segs:
        raise RuntimeError("V003 ground edge overlay unexpectedly empty or malformed")
    if bpy.data.objects.get("V003_inferred_edge_blend_NOT_drain") is not None:
        raise RuntimeError("V003 ground edge overlay already exists")
    ob = _mesh_object("V003_inferred_edge_blend_NOT_drain", positions, faces, mat, collection)
    ob["provenance"] = (
        "Render-only thin soil/moss-toned broken strip on EXISTING road perimeter. "
        "Not a surveyed curb, drain, trench or new geography. Collision and walk top unchanged."
    )
    return {
        "segments": segs,
        "vertices": len(positions),
        "triangles": len(faces),
        "half_width_m_range": [min(widths) if widths else None, max(widths) if widths else None],
        "collision_changed": False,
        "drain_claimed": False,
    }


def apply_all():
    B = bpy.data.collections.get("B_SITE_REFINEMENT")
    assert B is not None, "V002 B_SITE_REFINEMENT collection missing"
    return {
        "version": VERSION,
        "material_balance": apply_material_balance(),
        "noren": apply_noren_drape(),
        "ground_edge": add_ground_edge_blend(B),
        "constraints": {
            "geography_changed": False,
            "collision_changed": False,
            "route_changed": False,
            "tile_roof_redone": False,
            "column_feet_redone": False,
            "new_buildings": 0,
            "new_drain_channels": 0,
        },
    }
