#!/usr/bin/env python3
"""Convert a HY-World *triangle mesh* PLY to the existing Blender/GLB deliverable.

Run with Blender, not regular Python:
blender -b --factory-startup --python scripts/blender5/hyworld_mesh_to_glb.py -- \
  --input /path/to/global_mesh.ply --out outputs/hyworld-test \
  --asset-id hyworld-test --up-axis Z --meters-per-unit 1.0

Gaussian splats and point-only PLY inputs are deliberately rejected.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.hyworld2.pack_world import SAFE_ID, inspect_ply  # noqa: E402


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--up-axis", required=True, choices=["Y", "Z"],
                        help="Must be verified from the upstream dataset")
    parser.add_argument("--meters-per-unit", type=float, required=True,
                        help="Measured number of meters per source unit")
    params = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(params)


def main():
    args = parse_args()
    if not SAFE_ID.fullmatch(args.asset_id):
        raise ValueError("Invalid asset id")
    if not math.isfinite(args.meters_per_unit) or args.meters_per_unit <= 0:
        raise ValueError("Invalid scale")
    source = Path(args.input).resolve(strict=True)
    if source.suffix.lower() != ".ply":
        raise ValueError("This importer only accepts PLY triangle meshes")
    info = inspect_ply(source)
    if info["asset_type"] != "triangle_mesh":
        raise ValueError("Not a triangle mesh! Do NOT convert Gaussian splats or points to mesh.")
    output = Path(args.out).resolve()
    output.mkdir(parents=True, exist_ok=True)
    base = args.asset_id
    blend = output / (base + ".blend")
    glb = output / (base + ".glb")
    for file in [blend, glb, output / "asset_manifest.json", output / "report.json"]:
        if file.exists():
            raise FileExistsError("Output already exists: " + str(file))

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0

    # Blender 5.2 built-in PLY importer (not a Gaussian splat importer).
    forward = "NEGATIVE_Z" if args.up_axis == "Y" else "Y"
    bpy.ops.wm.ply_import(filepath=str(source), forward_axis=forward, up_axis=args.up_axis)
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes or not sum(len(obj.data.polygons) for obj in meshes):
        raise ValueError("Blender imported no mesh faces")
    for obj in meshes:
        obj.scale = [v * args.meters_per_unit for v in obj.scale]

    bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB")
    report = {
        "generator": "Blender 5.2 PLY mesh import -> GLB export",
        "input_type": info["asset_type"],
        "source_file": str(source),
        "mesh_objects": len(meshes),
        "vertices": sum(len(obj.data.vertices) for obj in meshes),
        "polygons": sum(len(obj.data.polygons) for obj in meshes),
        "source_up_axis": args.up_axis,
        "meters_per_source_unit": args.meters_per_unit,
        "collision_ready": False,
        "visual_quality_verified": False,
        "warnings": [
            "Original coordinate frame and scale must be verified independently",
            "Mesh topology, textures, normals, physics and real-world accuracy require review",
            "Only mesh geometry was converted; no Gaussian splat appearance is preserved",
        ],
    }
    manifest = {
        "schema_version": 1,
        "asset_id": base,
        "format": "glTF 2.0 GLB",
        "source": "User supplied HY-World triangle mesh PLY; provenance unverified",
        "unit": "meter (requires source scale verification)",
        "coordinate_system": "Blender Z-up; glTF Y-up",
        "model_file": glb.name,
        "source_file": blend.name,
        "clips": [],
        "min_animation_count": 0,
        "requirements": {"skins": False, "animated": False, "visual_review": True},
        "license_note": "Check all original assets and Tencent HY-World 2.0 Community License.",
    }
    for filename, obj in [("report.json", report), ("asset_manifest.json", manifest)]:
        (output / filename).write_text(
            json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
