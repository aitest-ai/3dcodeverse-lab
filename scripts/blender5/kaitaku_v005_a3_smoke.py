#!/usr/bin/env python3
"""Real Blender 5.2 smoke test for V005 FinalPolish A3 helper functions.

This does NOT represent the real Kaitaku scene. It builds a tiny synthetic
fixture only to execute the same bpy/material/grass/protection code paths before
the large pinned V005 source artifact is available.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "scripts" / "blender5" / "kaitaku_v005_finalpolish_a.py"
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)


def load_target():
    spec = importlib.util.spec_from_file_location("kaitaku_v005_finalpolish_a", TARGET)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import FinalPolish A3 target")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_mat(name, rgba):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        raise RuntimeError("Principled BSDF missing in smoke material")
    bsdf.inputs["Base Color"].default_value = rgba
    return mat


def make_mesh_object(name, vertices, faces, material=None):
    mesh = bpy.data.meshes.new(name + " Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    if material is not None:
        mesh.materials.append(material)
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def make_grass(name, mod):
    xs = []
    x = -10.0
    while x <= 10.0 and len(xs) < 60:
        if mod.gap_field(x) > 0.80:
            xs.append(x)
        x += 0.08
    if len(xs) < 20:
        raise RuntimeError("Smoke fixture could not find enough deterministic gap samples")

    vertices = []
    faces = []
    for x in xs:
        base = len(vertices)
        vertices.extend([
            (x - 0.025, -3.15, 0.00),
            (x + 0.025, -3.15, 0.00),
            (x, -3.15, 0.12),
        ])
        faces.append((base, base + 1, base + 2))
    return make_mesh_object(name, vertices, faces)


def rgba(mat):
    return list(mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value)


def close4(a, b, eps=1e-6):
    return all(abs(float(x) - float(y)) <= eps for x, y in zip(a, b))


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    mod = load_target()

    dark = make_mat("V005 neutral unmodeled dark depth", (0.02, 0.02, 0.02, 1))
    reveal = make_mat("V005 neutral closed window reveal", (0.03, 0.03, 0.03, 1))

    store_dark = make_mesh_object(
        "16 Closed shallow storefront backing",
        [(0, 0, 0), (1, 0, 0), (0, 0, 1)],
        [(0, 1, 2)],
        dark,
    )
    store_reveal = make_mesh_object(
        "16 Closed shallow storefront backing V005 inner reveal",
        [(2, 0, 0), (3, 0, 0), (2, 0, 1)],
        [(0, 1, 2)],
        reveal,
    )

    protected = make_mesh_object(
        "postal hedge protected sentinel",
        [(0, 1, 0), (1, 1, 0), (0, 1, 1)],
        [(0, 1, 2)],
    )
    protected_before = mod.geom_hash(protected)

    for i in range(5):
        make_grass(f"V005 clustered grass {i}", mod)

    a_dark = mod.set_base("V005 neutral unmodeled dark depth", mod.DARK_DEPTH)
    a_reveal = mod.set_base("V005 neutral closed window reveal", mod.INNER_REVEAL)

    local_dark = mod.assign_local_storefront_material(
        store_dark.name,
        "V005 neutral unmodeled dark depth",
        "V005 A3 store-local dark depth",
        mod.STORE_DARK_DEPTH,
    )
    local_reveal = mod.assign_local_storefront_material(
        store_reveal.name,
        "V005 neutral closed window reveal",
        "V005 A3 store-local closed reveal",
        mod.STORE_INNER_REVEAL,
    )

    grass = mod.apply_grass_patch(bpy.context.scene)
    removed = sum(x["components_removed"] for x in grass)
    before = sum(x["components_before"] for x in grass)
    kept = sum(x["components_kept"] for x in grass)

    if len(grass) != 5:
        raise RuntimeError("Expected five grass results")
    if not (0 < removed < before):
        raise RuntimeError(f"Grass smoke removal is not bounded: removed={removed}, before={before}")
    if removed + kept != before:
        raise RuntimeError("Grass component accounting mismatch")

    if mod.geom_hash(protected) != protected_before:
        raise RuntimeError("Protected sentinel geometry changed")

    if not close4(rgba(bpy.data.materials["V005 neutral unmodeled dark depth"]), mod.DARK_DEPTH):
        raise RuntimeError("A dark-depth source material mismatch")
    if not close4(rgba(bpy.data.materials["V005 neutral closed window reveal"]), mod.INNER_REVEAL):
        raise RuntimeError("A reveal source material mismatch")
    if not close4(rgba(store_dark.data.materials[0]), mod.STORE_DARK_DEPTH):
        raise RuntimeError("A3 store-local dark material mismatch")
    if not close4(rgba(store_reveal.data.materials[0]), mod.STORE_INNER_REVEAL):
        raise RuntimeError("A3 store-local reveal material mismatch")
    if store_dark.data.materials[0] is dark or store_reveal.data.materials[0] is reveal:
        raise RuntimeError("Storefront local materials were not copied")

    report = {
        "status": "PASS",
        "blender": bpy.app.version_string,
        "target_asset_id": mod.ASSET_ID,
        "source_sha_lock": mod.EXPECTED_SOURCE_SHA256,
        "runtime_a_sha": mod.VALIDATED_RUNTIME_A_SHA256,
        "runtime_a3_sha": mod.VALIDATED_RUNTIME_A3_SHA256,
        "a_materials": {
            "dark_depth": a_dark,
            "inner_reveal": a_reveal,
        },
        "a3_materials": {
            "dark_depth": local_dark,
            "inner_reveal": local_reveal,
        },
        "grass": {
            "objects": len(grass),
            "components_before": before,
            "components_removed": removed,
            "components_kept": kept,
        },
        "protected_sentinel_unchanged": True,
        "note": "Synthetic bpy smoke only; not a real-scene visual or geometry acceptance.",
    }
    (OUT / "kaitaku-a3-smoke.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
