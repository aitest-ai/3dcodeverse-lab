"""Compare two cold-opened native gray candidates; never save a Blender file.

Run in a fresh background Blender process:
  blender --background --factory-startup --python compare_gray.py -- \
    --d03 d03/d03.blend --d06 d06/d06.blend --out comparison.json

The 13,380-vertex requirement belongs only to this pinned MPFB game-engine
adapter. Correspondence is verified by ordered polygon connectivity, not by
vertex count alone. Measurements use native rest-surface vertices, before
armature/subdivision modifiers, transformed into Blender world coordinates.
Head vertices are the intersection of indices with head weight > 0.5 in BOTH
models. This includes ears and the cranium: it is not a face-only measurement.
Geometric difference does not establish naturalness, age, or artistic quality.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

import bpy
import numpy as np


ADAPTER = "mpfb_game_engine"
PINNED_MPFB_COMMIT = "6ff1eb358f6c1959ced77e79e6dd2406d9a71f49"
EXPECTED_NATIVE_VERTICES = 13380
HEAD_WEIGHT_THRESHOLD = 0.5
NUMERICAL_COPY_TOLERANCE_M = 1e-5
REQUIRED_BONES = (
    "Root", "pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "head",
    "upperarm_l", "lowerarm_l", "hand_l", "upperarm_r", "lowerarm_r", "hand_r",
    "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r",
)


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def array_sha256(values, dtype):
    """Canonical C-order bytes; dtype explicitly specifies little endian."""
    array = np.ascontiguousarray(values, dtype=dtype)
    return hashlib.sha256(array.tobytes(order="C")).hexdigest()


def bounds(values):
    low = values.min(axis=0)
    high = values.max(axis=0)
    span = high - low
    return {
        "min_m": low.tolist(), "max_m": high.tolist(), "extent_xyz_m": span.tolist(),
        "height_z_m": float(span[2]), "aabb_diagonal_m": float(np.linalg.norm(span)),
    }


def world_positions(body):
    local = np.asarray([tuple(v.co) for v in body.data.vertices], dtype=np.float64)
    matrix = np.asarray(body.matrix_world, dtype=np.float64)
    world = local @ matrix[:3, :3].T + matrix[:3, 3]
    if not np.isfinite(world).all():
        raise RuntimeError("Native body contains non-finite world coordinates")
    return world


def ordered_topology(body):
    """Encode face lengths and vertex indices, preserving face order/winding."""
    data = [len(body.data.vertices), len(body.data.polygons)]
    for polygon in body.data.polygons:
        data.append(len(polygon.vertices))
        data.extend(polygon.vertices)
    return np.asarray(data, dtype="<u4")


def head_indices(body):
    group = body.vertex_groups.get("head")
    if group is None:
        raise RuntimeError("Pinned adapter requires a head vertex group")
    indices = [v.index for v in body.data.vertices
               if any(g.group == group.index and g.weight > HEAD_WEIGHT_THRESHOLD
                      for g in v.groups)]
    if len(indices) < 4:
        raise RuntimeError("Too few head-weighted native vertices")
    return np.asarray(indices, dtype=np.int64)


def bone_metrics(rig, height):
    matrix = np.asarray(rig.matrix_world, dtype=np.float64)
    lengths = {}
    for name in REQUIRED_BONES:
        bone = rig.data.bones[name]
        delta = np.asarray(bone.tail_local, dtype=np.float64) - np.asarray(bone.head_local, dtype=np.float64)
        lengths[name] = float(np.linalg.norm(matrix[:3, :3] @ delta))
    ratios = {}
    for side in ("l", "r"):
        upper = lengths["upperarm_" + side]
        forearm = lengths["lowerarm_" + side]
        thigh = lengths["thigh_" + side]
        shin = lengths["calf_" + side]
        if min(upper, forearm, thigh, shin) <= 0:
            raise RuntimeError("Invalid zero-length limb in pinned adapter")
        ratios["forearm_to_upper_arm_" + side] = forearm / upper
        ratios["thigh_to_shin_" + side] = thigh / shin
        ratios["leg_chain_to_body_height_" + side] = (thigh + shin) / height
        ratios["arm_chain_to_body_height_" + side] = (upper + forearm) / height
    ratios["head_bone_to_body_height"] = lengths["head"] / height
    return {"rest_bone_lengths_m": lengths, "dimensionless_ratios": ratios,
            "note": "Bone centerline lengths, not skin or clothing widths."}


def cold_read(path, role, output_parent):
    before_sha = file_sha256(path)
    # Each open replaces the preceding scene. No save, render, target changes,
    # modifier application, object edits, or external asset loading is done.
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    bpy.context.view_layer.update()
    if not np.isclose(bpy.context.scene.unit_settings.scale_length, 1.0):
        raise RuntimeError("Pinned adapter requires one Blender unit per metre")
    body = bpy.data.objects.get(role + "_Body")
    rig = bpy.data.objects.get(role + "_Rig")
    if body is None or body.type != "MESH" or rig is None or rig.type != "ARMATURE":
        raise RuntimeError("Expected named clean body and game-engine rig are missing")
    if len(body.data.vertices) != EXPECTED_NATIVE_VERTICES:
        raise RuntimeError("Only the pinned 13,380-vertex native clean body is supported")
    missing = [name for name in REQUIRED_BONES if name not in rig.data.bones]
    if missing:
        raise RuntimeError("Pinned game-engine rig semantics missing: " + ", ".join(missing))
    if not any(mod.type == "ARMATURE" and mod.object == rig for mod in body.modifiers):
        raise RuntimeError("Body is not bound to its expected game-engine rig")
    if any(mod.type == "MASK" for mod in body.modifiers):
        raise RuntimeError("Clean body must not contain a body mask")
    if body.data.shape_keys:
        live = [key.name for key in body.data.shape_keys.key_blocks[1:]
                if abs(key.value) > 1e-8]
        if live:
            raise RuntimeError("Live shape keys would invalidate native-basis comparison: " + ", ".join(live))
    points = world_positions(body)
    topology = ordered_topology(body)
    selected = head_indices(body)
    measured_bounds = bounds(points)
    if measured_bounds["height_z_m"] <= 0:
        raise RuntimeError("Native body height must be positive")
    report = {
        "role": role,
        "source_blend": os.path.relpath(path, output_parent),
        "source_blend_sha256": before_sha,
        "source_blend_bytes": path.stat().st_size,
        "cold_opened": True,
        "body_object": body.name,
        "rig_object": rig.name,
        "native_vertex_count": len(points),
        "native_polygon_count": len(body.data.polygons),
        "rig_bone_count_observed": len(rig.data.bones),
        "topology_sha256_uint32_le": array_sha256(topology, "<u4"),
        "body_world_array_sha256_float32_le": array_sha256(points, "<f4"),
        "body_world_array_shape": [len(points), 3],
        "body_world_matrix": np.asarray(body.matrix_world, dtype=np.float64).tolist(),
        "actual_native_world_bounds": measured_bounds,
        "head_group_selected_count": len(selected),
        "head_group_selected_indices_sha256_uint32_le": array_sha256(selected, "<u4"),
        "bone_metrics": bone_metrics(rig, measured_bounds["height_z_m"]),
        "native_surface_scope": "Unmodified mesh vertices in rest-surface correspondence; not subdivision or posed evaluated vertices.",
    }
    if file_sha256(path) != before_sha:
        raise RuntimeError("Source Blender file changed while being read")
    return {"points": points, "topology": topology, "head_indices": selected, "report": report}


def procrustes(source, target, normalization_m, normalization_name):
    """Least-squares proper similarity: target = scale * (source @ R.T) + t."""
    if source.shape != target.shape or source.shape[1:] != (3,) or len(source) < 4:
        raise RuntimeError("Procrustes requires corresponding N by 3 arrays")
    if normalization_m <= 0:
        raise RuntimeError("Normalization extent must be positive")
    center_source = source.mean(axis=0)
    center_target = target.mean(axis=0)
    x = source - center_source
    y = target - center_target
    variance = float(np.sum(x * x))
    if variance <= 0 or np.linalg.matrix_rank(x) < 2:
        raise RuntimeError("Degenerate source geometry cannot be fitted")
    u, singular, vt = np.linalg.svd(x.T @ y)
    correction = np.ones(3, dtype=np.float64)
    if np.linalg.det(u @ vt) < 0:
        correction[-1] = -1.0
    row_rotation = (u * correction) @ vt
    rotation = row_rotation.T
    scale = float(np.dot(singular, correction) / variance)
    if scale <= 0 or not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-10):
        raise RuntimeError("Invalid proper similarity solution")
    translation = center_target - scale * (center_source @ row_rotation)
    aligned = scale * (source @ row_rotation) + translation
    distances = np.linalg.norm(aligned - target, axis=1)
    rms = float(np.sqrt(np.mean(distances * distances)))
    maximum = float(distances.max())
    return {
        "n_corresponding_vertices": len(source),
        "source": "d03", "target": "d06",
        "method": "Least-squares similarity Procrustes via SVD; uniform positive scale, proper rotation (det +1), translation; no reflection, nonuniform scaling, or vertex rematching.",
        "transform_convention": "target_fit = uniform_scale * (source_row_vectors @ rotation_matrix.T) + translation_m",
        "uniform_scale": scale,
        "rotation_matrix": rotation.tolist(),
        "rotation_determinant": float(np.linalg.det(rotation)),
        "translation_m": translation.tolist(),
        "rms_vertex_distance_m": rms,
        "max_vertex_distance_m": maximum,
        "normalization": {"name": normalization_name, "extent_m": normalization_m,
                          "rms_divided_by_extent": rms / normalization_m,
                          "max_divided_by_extent": maximum / normalization_m},
        "numerical_copy_tolerance_m": NUMERICAL_COPY_TOLERANCE_M,
        "all_vertices_match_similarity_within_numerical_tolerance": maximum <= NUMERICAL_COPY_TOLERANCE_M,
        "tolerance_note": "10 micrometres is a numerical-copy check only, not a visual or anatomical quality threshold.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--d03", type=Path, required=True)
    parser.add_argument("--d06", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    paths = {role: getattr(args, role).resolve(strict=True) for role in ("d03", "d06")}
    output = args.out.resolve()
    if paths["d03"] == paths["d06"] or output in paths.values():
        raise RuntimeError("Distinct source Blender files and a separate JSON output are required")
    if output.suffix.lower() != ".json":
        raise RuntimeError("Output must be JSON; this tool never writes Blender files")
    if output.exists():
        raise RuntimeError("Comparison output already exists; preserve it and use a new version or filename")
    sources = {role: cold_read(path, role, output.parent) for role, path in paths.items()}
    d03, d06 = sources["d03"], sources["d06"]
    if not np.array_equal(d03["topology"], d06["topology"]):
        raise RuntimeError("Native ordered polygon connectivity differs; vertex-index correspondence is invalid")
    common_head = np.intersect1d(d03["head_indices"], d06["head_indices"], assume_unique=True)
    if len(common_head) < 4:
        raise RuntimeError("Too few common head-weighted vertices")
    head_arrays = {role: item["points"][common_head] for role, item in sources.items()}
    head_bounds = {role: bounds(points) for role, points in head_arrays.items()}
    body_fit = procrustes(d03["points"], d06["points"],
                          d06["report"]["actual_native_world_bounds"]["height_z_m"],
                          "target d06 measured native body Z height")
    head_fit = procrustes(head_arrays["d03"], head_arrays["d06"],
                          head_bounds["d06"]["aabb_diagonal_m"],
                          "target d06 common-head native AABB diagonal")
    for role, path in paths.items():
        if file_sha256(path) != sources[role]["report"]["source_blend_sha256"]:
            raise RuntimeError("Source Blender file changed before comparison completed")
        sources[role]["report"]["source_sha256_unchanged_after_comparison"] = True
    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "stage": "gray_identity_geometry_comparison",
        "read_mode": "Fresh background Blender comparison process; each .blend cold-opened separately; no renders or source writes.",
        "environment": {"blender": bpy.app.version_string,
                        "blender_build_hash": bpy.app.build_hash.decode(),
                        "numpy": np.__version__},
        "script_sha256": file_sha256(__file__),
        "adapter": {"name": ADAPTER, "pinned_mpfb_commit": PINNED_MPFB_COMMIT,
                    "native_body_vertices": EXPECTED_NATIVE_VERTICES,
                    "validation": "Named clean body, required game-engine bones, armature binding, no mask or live shape keys, and identical ordered polygon topology.",
                    "scope_note": "13,380 vertices is specific to this adapter, not a universal human-model requirement; this comparison does not independently prove upstream source provenance."},
        "coordinate_system": "Blender world coordinates, right-handed Z-up, forward -Y; one Blender unit = one metre by this adapter's build contract.",
        "array_hash_encoding": "Native vertex-index order, N by 3 xyz, IEEE-754 float32 little-endian, C-order; calculations use float64.",
        "topology_hash_encoding": "uint32 little-endian: vertex count, polygon count, then each polygon length followed by ordered vertex indices.",
        "sources": {role: item["report"] for role, item in sources.items()},
        "same_ordered_native_topology": True,
        "full_body": body_fit,
        "head_including_ears_and_cranium": {
            "selection": "Intersection of native indices whose head vertex-group weight is strictly > 0.5 in both sources.",
            "weight_threshold_exclusive": HEAD_WEIGHT_THRESHOLD,
            "common_vertex_count": len(common_head),
            "common_indices_sha256_uint32_le": array_sha256(common_head, "<u4"),
            "actual_common_head_bounds": head_bounds,
            "fit": head_fit,
            "scope_note": "This region includes the cranium and ears; it is not a face-only measurement.",
        },
        "interpretation": {
            "body_is_not_a_uniform_similarity_copy_within_tolerance": not body_fit["all_vertices_match_similarity_within_numerical_tolerance"],
            "head_is_not_a_uniform_similarity_copy_within_tolerance": not head_fit["all_vertices_match_similarity_within_numerical_tolerance"],
            "art_approval_performed": False,
            "age_or_identity_classification_performed": False,
            "quality_judgment_performed": False,
            "limitations": [
                "Residuals establish geometric differences under fixed native vertex correspondence, not naturalness or design success.",
                "Native rest surfaces are measured; this is not a test of subdivided GLB rendering, clothing fit, expressions, or animation.",
                "Bone ratios are rest-bone centerline measurements, not anthropometric skin measurements.",
            ],
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation preserves earlier comparison evidence. This is the only
    # file written; neither input .blend is ever saved or modified.
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print("GRAY_COMPARISON_COMPLETE", json.dumps({
        "output": output.name,
        "body_rms_m": body_fit["rms_vertex_distance_m"],
        "head_rms_m": head_fit["rms_vertex_distance_m"],
        "common_head_vertices": len(common_head),
    }), flush=True)


if __name__ == "__main__":
    main()
