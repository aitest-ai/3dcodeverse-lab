#!/usr/bin/env python3
"""GLB production-readiness report (objective structure, NOT artistic quality).

No external packages. Usage:
 python3 scripts/assets/glb_quality_report.py outputs/mecha_blender5.glb --kind mecha --target mobile
"""
import argparse
import json
import struct
from pathlib import Path


def audit(path, kind="prop", target="desktop"):
    path = Path(path)
    with path.open("rb") as stream:
        header = stream.read(12)
        if len(header) != 12:
            raise ValueError("Invalid GLB header")
        magic, version, byte_length = struct.unpack("<4sII", header)
        if magic != b"glTF" or version != 2 or byte_length != path.stat().st_size:
            raise ValueError("Invalid GLB file version/length")
        size, typ = struct.unpack("<I4s", stream.read(8))
        if typ != b"JSON" or size < 2:
            raise ValueError("Missing glTF JSON chunk")
        doc = json.loads(stream.read(size))
    accessors = doc.get("accessors", [])
    meshes = doc.get("meshes", [])
    materials = doc.get("materials", [])
    primitives = [p for mesh in meshes for p in mesh.get("primitives", [])]
    triangles = 0
    vertices = 0
    prim_with_uv = 0
    prim_with_normals = 0
    prim_with_morph = 0
    for p in primitives:
        mode = p.get("mode", 4)
        count = None
        if isinstance(p.get("indices"), int):
            count = accessors[p["indices"]].get("count", 0)
        position_idx = p.get("attributes", {}).get("POSITION")
        if isinstance(position_idx, int):
            vert_count = accessors[position_idx].get("count", 0)
            vertices += vert_count
            if count is None:
                count = vert_count
        count = count or 0
        if mode == 4:
            triangles += count // 3
        elif mode in (5, 6):
            triangles += max(0, count - 2)
        attrs = p.get("attributes", {})
        prim_with_uv += int("TEXCOORD_0" in attrs)
        prim_with_normals += int("NORMAL" in attrs)
        prim_with_morph += int(bool(p.get("targets")))
    pbr_count = sum("pbrMetallicRoughness" in m for m in materials)
    texture_count = len(doc.get("textures", []))
    images_count = len(doc.get("images", []))
    animations = [a.get("name") for a in doc.get("animations", [])]
    issues = []
    if not primitives:
        issues.append("NO_MESH_PRIMITIVES")
    if not materials:
        issues.append("NO_MATERIALS")
    if primitives and prim_with_normals < len(primitives):
        issues.append("SOME_PRIMITIVES_MISSING_NORMALS")
    if images_count and prim_with_uv < len(primitives):
        issues.append("SOME_PRIMITIVES_WITH_TEXTURES_LACK_UV0")
    if kind in ("human", "animal") and not doc.get("skins"):
        issues.append("NO_SKIN_FOR_POTENTIALLY_ANIMATED_CHARACTER")
    if kind == "human" and prim_with_morph == 0:
        issues.append("NO_FACIAL_MORPH_TARGETS_CHECK_EXPRESSIONS_MANUALLY")
    if images_count == 0:
        issues.append("NO_IMAGE_TEXTURES_PRESENT_CHECK_IF_INTENTIONAL")
    if target == "mobile" and triangles > 150000:
        issues.append("MOBILE_GEOMETRY_BUDGET_REVIEW")
    if target == "mobile" and path.stat().st_size > 20 * 1024 * 1024:
        issues.append("MOBILE_DOWNLOAD_SIZE_REVIEW")
    return {
        "asset": path.name,
        "kind": kind,
        "target": target,
        "file_bytes": path.stat().st_size,
        "meshes": len(meshes),
        "primitives": len(primitives),
        "vertices_sum_not_unique": vertices,
        "triangles_estimate": triangles,
        "primitives_with_uv0": prim_with_uv,
        "primitives_with_normals": prim_with_normals,
        "primitives_with_morphs": prim_with_morph,
        "materials": len(materials),
        "pbr_metallic_roughness_materials": pbr_count,
        "textures": texture_count,
        "images": images_count,
        "skins": len(doc.get("skins", [])),
        "animations": animations,
        "potential_issues": issues,
        "artistic_review_required": True,
        "limits": "Numeric topology/PBR checks cannot prove anatomical accuracy, quality, legal provenance or motion naturalness.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("glb")
    p.add_argument("--kind", choices=("human", "animal", "mecha", "prop", "environment"), default="prop")
    p.add_argument("--target", choices=("mobile", "desktop"), default="desktop")
    p.add_argument("--output", help="Optional path to write JSON report")
    args = p.parse_args()
    result = audit(args.glb, args.kind, args.target)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
