#!/usr/bin/env python3
"""Validate arbitrary Blender-generated GLB packages with only Python stdlib.
This checks structure and naming, not rendering quality or physics.
"""
import json
import struct
import sys
from pathlib import Path


def validate(folder):
    folder = Path(folder)
    manifest_path = folder / "asset_manifest.json"
    if not manifest_path.is_file():
        raise ValueError("Missing asset_manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Manifest schema_version must be 1")
    asset_id = manifest.get("asset_id", "")
    if not isinstance(asset_id, str) or not asset_id:
        raise ValueError("asset_id is required")
    glb_name = manifest.get("model_file")
    src_name = manifest.get("source_file")
    if not isinstance(glb_name, str) or not glb_name.endswith(".glb"):
        raise ValueError("model_file must name a .glb")
    for name in (glb_name, src_name):
        if not isinstance(name, str) or Path(name).name != name:
            raise ValueError("File names must be simple basenames, not paths")
        if not (folder / name).is_file() or (folder / name).stat().st_size == 0:
            raise ValueError("Expected nonempty file missing: " + name)
    glb_path = folder / glb_name
    with glb_path.open("rb") as handle:
        header = handle.read(12)
        if len(header) != 12:
            raise ValueError("GLB header truncated")
        magic, version, declared_length = struct.unpack("<4sII", header)
        if magic != b"glTF" or version != 2:
            raise ValueError("Not a glTF 2.0 binary")
        if declared_length != glb_path.stat().st_size:
            raise ValueError("GLB header length does not match actual file")
        chunk_header = handle.read(8)
        if len(chunk_header) != 8:
            raise ValueError("GLB missing JSON chunk")
        length, kind = struct.unpack("<I4s", chunk_header)
        if kind != b"JSON":
            raise ValueError("GLB first chunk must be JSON")
        doc = json.loads(handle.read(length).decode("utf-8"))
    animations = [x.get("name", "") for x in doc.get("animations", [])]
    desired = manifest.get("clips", [])
    if not isinstance(desired, list) or any(not isinstance(x, str) for x in desired):
        raise ValueError("clips must be a list of names")
    if not doc.get("meshes"):
        raise ValueError("GLB contains no meshes")
    required = manifest.get("requirements", {})
    if required.get("skins", False) and not doc.get("skins"):
        raise ValueError("Manifest requires skinned geometry, but GLB contains no skins")
    minimum = manifest.get("min_animation_count", 0)
    if not isinstance(minimum, int) or minimum < 0:
        raise ValueError("min_animation_count must be nonnegative integer")
    if len(animations) < minimum:
        raise ValueError(f"Expected {minimum} animations, found {animations}")
    for clip in desired:
        if clip not in animations and not any(name.endswith("_" + clip) for name in animations):
            raise ValueError(f"Required clip '{clip}' not found in {animations}")
    if manifest.get("asset_id") == "mecha_blender5":
        nodes = [n.get("name", "") for n in doc.get("nodes", [])]
        for side in ("L", "R"):
            if "foot." + side not in nodes:
                raise ValueError("Articulated foot bone not exported: foot." + side)
        meshes = [m.get("name", "").lower() for m in doc.get("meshes", [])]
        if sum("ankle" in n or "foot" in n or "toe" in n for n in meshes) < 12:
            raise ValueError("Mecha ankle or foot geometry missing")
        report_path = folder / "report.json"
        if report_path.is_file():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            sole_samples = report.get("sole_samples", [])
            if len(sole_samples) < 20:
                raise ValueError("Not enough pose samples for ankle ground checks")
            if any(s["min_sole_z"] < -0.009 for s in sole_samples):
                raise ValueError("A sampled sole intersects the test ground")
    result = {
        "asset_id": asset_id,
        "mesh_count": len(doc["meshes"]),
        "skin_count": len(doc.get("skins", [])),
        "animation_clips": animations,
        "file_bytes": glb_path.stat().st_size,
        "verdict": "STRUCTURE_PASS (visual and all-frame checks still required)",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    (folder / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    try:
        validate(sys.argv[1] if len(sys.argv) > 1 else "outputs")
    except Exception as exc:
        print("STRUCTURE_FAIL:", exc, file=sys.stderr)
        sys.exit(1)
