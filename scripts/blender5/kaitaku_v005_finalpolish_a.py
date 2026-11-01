#!/usr/bin/env python3
"""Apply validated V005 FinalPolish A + A3 edits to the pinned V005 Blender master.

Bounded scope only:
- lighten two neutral *unmodeled* closed-window backing/reveal materials;
- break comb-like continuity of V005 clustered roadside grass in a narrow band;
- give only the 16 Watanabe ground-floor closed storefront backing/reveal local A3 materials.

Hard exclusions: stone kerbs, postal passage, postbox/hedge, barber ladder, wood
poles/braces, stairs/threshold/landing, roof/hood geometry, and the diagnosed
upper-hood slant patch.

The source master is never overwritten. The source SHA-256 is pinned.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

EXPECTED_SOURCE_SHA256 = "7ead93b961f243c3521244a509e53546c73e27af4539a89a303a2e28c632ddbc"
ASSET_ID = "kaitaku-v005-finalpolish-a3"
SEED = 1505006
DARK_DEPTH = (0.055, 0.050, 0.044, 1.0)
INNER_REVEAL = (0.070, 0.063, 0.052, 1.0)
STORE_DARK_DEPTH = (0.075, 0.068, 0.055, 1.0)
STORE_INNER_REVEAL = (0.088, 0.080, 0.066, 1.0)

SHOTS = [
    ("01-mainstreet-overview", (24, -33, 17), (0, 2, 2), 40, 1700, 1000),
    ("02-shimauta-front", (-10.2, -14, 5), (-10.2, .4, 2.6), 45, 1500, 1150),
    ("03-shimauta-side-detail", (-16, -9, 6), (-10.2, 1.3, 2.8), 46, 1500, 1150),
    ("04-watanabe-front", (10.4, -16, 5), (10.4, 1, 2.8), 44, 1500, 1150),
    ("05-watanabe-side-detail", (20, -9, 6), (10.4, 1.5, 3), 45, 1500, 1150),
]

PROTECTED_TOKENS = [
    "kerb", "curb", "postbox", "postal hedge", "ladder", "wood pole", "brace",
    "stair", "steps", "threshold", "landing", "porch stone", "upper hood",
]


def sha256(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def geom_hash(ob) -> str:
    h = hashlib.sha256()
    for row in ob.matrix_world:
        h.update((",".join(format(v, ".9g") for v in row)).encode())
    if ob.type == "MESH":
        for v in ob.data.vertices:
            h.update((",".join(format(c, ".9g") for c in v.co)).encode())
        for p in ob.data.polygons:
            h.update((",".join(map(str, p.vertices))).encode())
    return h.hexdigest()


def components(me):
    n = len(me.vertices)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[b] = a

    for e in me.edges:
        union(e.vertices[0], e.vertices[1])
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def gap_field(x: float) -> float:
    return (
        math.sin(x * 0.73 + 0.85)
        + 0.52 * math.sin(x * 1.91 - 0.37)
        + 0.23 * math.cos(x * 3.17 + 1.1)
    )


def set_base(mat_name: str, rgba):
    mat = bpy.data.materials.get(mat_name)
    if mat is None or not mat.use_nodes:
        raise RuntimeError(f"Missing expected material: {mat_name}")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        raise RuntimeError(f"Missing Principled BSDF: {mat_name}")
    old = tuple(bsdf.inputs["Base Color"].default_value)
    bsdf.inputs["Base Color"].default_value = rgba
    return {"old": list(old), "new": list(rgba)}


def assign_local_storefront_material(object_name: str, source_material_name: str, new_name: str, rgba):
    ob = bpy.data.objects.get(object_name)
    if ob is None or ob.type != "MESH":
        raise RuntimeError(f"Missing expected storefront mesh: {object_name}")
    if len(ob.data.materials) != 1:
        raise RuntimeError(f"Expected exactly one material slot on {object_name}, found {len(ob.data.materials)}")
    source = bpy.data.materials.get(source_material_name)
    if source is None or not source.use_nodes:
        raise RuntimeError(f"Missing expected source material: {source_material_name}")
    if ob.data.users != 1:
        ob.data = ob.data.copy()
    local = source.copy()
    local.name = new_name
    bsdf = local.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        raise RuntimeError(f"Missing Principled BSDF in local copy: {new_name}")
    old = tuple(bsdf.inputs["Base Color"].default_value)
    bsdf.inputs["Base Color"].default_value = rgba
    ob.data.materials.clear()
    ob.data.materials.append(local)
    return {
        "object": object_name,
        "source_material": source_material_name,
        "local_material": local.name,
        "old": list(old),
        "new": list(rgba),
        "mesh_users_after": ob.data.users,
    }


def apply_grass_patch(scene):
    rng = random.Random(SEED)
    grass_results = []
    for ob in sorted(scene.objects, key=lambda o: o.name):
        if ob.type != "MESH" or not ob.name.startswith("V005 clustered grass "):
            continue
        me = ob.data
        comps = components(me)
        keep = []
        removed = 0
        for comp in comps:
            world = [ob.matrix_world @ me.vertices[i].co for i in comp]
            cx = sum(v.x for v in world) / len(world)
            cy = sum(v.y for v in world) / len(world)
            edge_band = -3.32 <= cy <= -3.02
            remove = edge_band and gap_field(cx) > 0.73 and rng.random() < 0.72
            if remove:
                removed += 1
            else:
                keep.append(set(comp))

        keep_vertices = set().union(*keep) if keep else set()
        old_to_new, verts = {}, []
        for old in sorted(keep_vertices):
            old_to_new[old] = len(verts)
            verts.append(tuple(me.vertices[old].co))
        faces, face_mats = [], []
        for poly in me.polygons:
            ids = list(poly.vertices)
            if all(i in keep_vertices for i in ids):
                faces.append(tuple(old_to_new[i] for i in ids))
                face_mats.append(poly.material_index)

        oldmat = list(me.materials)
        newme = bpy.data.meshes.new(me.name + " final-polish-a")
        newme.from_pydata(verts, [], faces)
        newme.update()
        for m in oldmat:
            newme.materials.append(m)
        for poly, mi in zip(newme.polygons, face_mats):
            poly.material_index = mi
        uv = newme.uv_layers.new(name="UVMap")
        for poly in newme.polygons:
            for li in poly.loop_indices:
                q = newme.vertices[newme.loops[li].vertex_index].co
                uv.data[li].uv = (q.x, q.z)
        oldme = ob.data
        ob.data = newme
        if oldme.users == 0:
            bpy.data.meshes.remove(oldme)
        grass_results.append({
            "object": ob.name,
            "components_before": len(comps),
            "components_removed": removed,
            "components_kept": len(keep),
        })

    if len(grass_results) != 5:
        raise RuntimeError(f"Expected 5 V005 clustered grass objects, found {len(grass_results)}")
    return grass_results


def configure_inspection_lighting(scene):
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 2
    scene.render.use_persistent_data = False
    scene.cycles.debug_use_compact_bvh = True
    scene.cycles.debug_use_spatial_splits = False
    if hasattr(scene.cycles, "use_auto_tile"):
        scene.cycles.use_auto_tile = True
    if hasattr(scene.cycles, "tile_size"):
        scene.cycles.tile_size = 128
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"

    world = bpy.data.worlds.get("FinalPolish A inspection world") or bpy.data.worlds.new("FinalPolish A inspection world")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (.66, .74, .78, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = .65

    for name in ["FinalPolish A inspection sun", "FinalPolish A inspection sky fill"]:
        old = bpy.data.objects.get(name)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)

    def light(name, kind, loc, energy, size=5):
        ld = bpy.data.lights.new(name, kind)
        ld.energy = energy
        ob = bpy.data.objects.new(name, ld)
        scene.collection.objects.link(ob)
        ob.location = loc
        if kind == "AREA":
            ld.shape = "DISK"
            ld.size = size
        ob.rotation_euler = (Vector((0, 2, 3)) - ob.location).to_track_quat("-Z", "Y").to_euler()
        return ob

    sun = light("FinalPolish A inspection sun", "SUN", (-8, -10, 14), 2.0)
    sun.data.angle = math.radians(5)
    light("FinalPolish A inspection sky fill", "AREA", (0, -8, 13), 2800, 24)


def render_views(scene, outdir: Path):
    configure_inspection_lighting(scene)
    cd = bpy.data.cameras.new("FinalPolish A inspection camera")
    cam = bpy.data.objects.new("FinalPolish A inspection camera", cd)
    scene.collection.objects.link(cam)
    scene.camera = cam
    results = []
    for name, pos, target, lens, width, height in SHOTS:
        cam.location = pos
        cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
        cd.lens = lens
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        path = outdir / "renders" / f"{name}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        results.append({
            "name": name,
            "file": str(path.name),
            "sha256": sha256(path),
            "camera": list(pos),
            "target": list(target),
            "lens_mm": lens,
            "width": width,
            "height": height,
            "samples": 32,
            "renderer": "Cycles CPU",
        })
    return results


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=Path("outputs"))
    p.add_argument("--skip-renders", action="store_true")
    args = p.parse_args(argv)

    source = args.source.resolve()
    outdir = args.output_dir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    outblend = outdir / f"{ASSET_ID}.blend"
    report_path = outdir / "report.json"
    manifest_path = outdir / "asset_manifest.json"

    if not source.is_file():
        raise FileNotFoundError(source)
    actual_source_sha = sha256(source)
    if actual_source_sha != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"Unexpected V005 source SHA-256: {actual_source_sha}")
    if outblend.exists():
        raise FileExistsError(f"Refuse to overwrite existing candidate: {outblend}")

    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene

    protected_hash = {
        ob.name: geom_hash(ob)
        for ob in scene.objects
        if ob.type == "MESH" and any(t in ob.name.lower() for t in PROTECTED_TOKENS)
    }

    report = {
        "asset_id": ASSET_ID,
        "source": str(source),
        "source_sha256": actual_source_sha,
        "blender": bpy.app.version_string,
        "status": "candidate; visual acceptance requires render review",
        "scope": "V005 FinalPolish A3 candidate; A base + store-local A3 overlay; no fourth building",
        "glass": {},
        "grass": {},
        "protected_geometry_count": len(protected_hash),
    }

    report["glass"]["dark_depth"] = set_base("V005 neutral unmodeled dark depth", DARK_DEPTH)
    report["glass"]["inner_reveal"] = set_base("V005 neutral closed window reveal", INNER_REVEAL)
    report["glass"]["glass_transmission_roughness_changed"] = False
    report["glass"]["invented_interior_content"] = False

    report["storefront_a3"]["dark_depth"] = assign_local_storefront_material(
        "16 Closed shallow storefront backing",
        "V005 neutral unmodeled dark depth",
        "V005 A3 store-local dark depth",
        STORE_DARK_DEPTH,
    )
    report["storefront_a3"]["inner_reveal"] = assign_local_storefront_material(
        "16 Closed shallow storefront backing V005 inner reveal",
        "V005 neutral closed window reveal",
        "V005 A3 store-local closed reveal",
        STORE_INNER_REVEAL,
    )
    report["storefront_a3"]["glass_transmission_roughness_changed"] = False
    report["storefront_a3"]["invented_interior_content"] = False
    report["storefront_a3"]["upper_windows_changed"] = False


    grass_results = apply_grass_patch(scene)
    report["grass"] = {
        "objects": grass_results,
        "scope": "Only V005 clustered grass components in Blender Y -3.32..-3.02 road-edge band",
        "components_removed_total": sum(x["components_removed"] for x in grass_results),
        "stone_kerbs_untouched": True,
        "postal_passage_untouched": True,
    }

    bpy.context.view_layer.update()
    for name, digest in protected_hash.items():
        ob = bpy.data.objects.get(name)
        if ob is None or geom_hash(ob) != digest:
            raise RuntimeError(f"Protected geometry changed: {name}")

    for im in bpy.data.images:
        if im.source == "FILE" and not im.packed_file:
            im.pack()

    bpy.ops.wm.save_as_mainfile(filepath=str(outblend), compress=True, check_existing=False, relative_remap=False)
    report["output_blend"] = str(outblend)
    report["output_blend_sha256"] = sha256(outblend)
    report["source_unchanged"] = sha256(source) == EXPECTED_SOURCE_SHA256

    if not args.skip_renders:
        report["renders"] = render_views(scene, outdir)
    else:
        report["renders"] = []
        report["render_status"] = "skipped by explicit flag"

    manifest = {
        "schema_version": 1,
        "asset_id": ASSET_ID,
        "version": "V005-FinalPolish-A3",
        "model_file": f"{ASSET_ID}.glb",
        "source_file": outblend.name,
        "clips": [],
        "min_animation_count": 0,
        "requirements": {"skins": False},
        "source_master_sha256": EXPECTED_SOURCE_SHA256,
        "candidate_blend": {"path": outblend.name, "sha256": report["output_blend_sha256"], "bytes": outblend.stat().st_size},
        "runtime_reference": {
            "validated_environment_glb_sha256": "752887763308bf71342b0d9ac292fc0f30ffa2e30d0ec6639e7373bb03cd5a55",
            "validated_environment_bytes": 380249836,
            "note": "The workflow supplies this deterministic runtime-equivalent GLB. Native candidate export parity is a separate future check.",
        },
        "renders": report.get("renders", []),
        "android": "not tested",
        "browser": "runtime A3 storefront same-camera validated separately; native candidate browser parity pending",
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "blend": str(outblend), "renders": len(report.get("renders", []))}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)
