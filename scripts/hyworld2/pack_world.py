#!/usr/bin/env python3
"""Prepare HY-World 2.0 scene exports for a Three.js viewer without a GPU.

Never mislabel Gaussian splats/point clouds as triangle meshes. Only checks the
PLY header; it does not certify geometry, licenses, coordinates, or appearance.
"""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


def inspect_ply(path):
    """Read only the PLY header (max 256 KiB), not huge Gaussian arrays."""
    fields, elements, current = set(), {}, None
    used = 0
    with Path(path).open("rb") as stream:
        first = stream.readline(256)
        if first.strip() != b"ply":
            raise ValueError("Invalid PLY signature")
        used += len(first)
        fmt = None
        while used < 262144:
            raw = stream.readline(4096)
            used += len(raw)
            if not raw:
                raise ValueError("PLY header truncated")
            try:
                line = raw.decode("ascii").strip()
            except UnicodeDecodeError as exc:
                raise ValueError("Invalid PLY header encoding") from exc
            if line == "end_header":
                break
            parts = line.split()
            if len(parts) >= 3 and parts[0] == "format":
                fmt = parts[1]
            elif len(parts) >= 3 and parts[0] == "element":
                current = parts[1]
                try:
                    elements[current] = int(parts[2])
                except ValueError as exc:
                    raise ValueError("Invalid PLY element count") from exc
            elif len(parts) >= 3 and parts[0] == "property" and current == "vertex":
                fields.add(parts[-1])
        else:
            raise ValueError("PLY header exceeds 256 KiB")
    if fmt not in {"ascii", "binary_little_endian", "binary_big_endian"}:
        raise ValueError("Unsupported PLY format")
    if elements.get("vertex", 0) <= 0:
        raise ValueError("PLY contains no vertices")
    if elements.get("face", 0) > 0:
        asset_type = "triangle_mesh"
    elif {"opacity", "f_dc_0", "scale_0", "rot_0"}.issubset(fields):
        asset_type = "gaussian_splats"
    else:
        asset_type = "point_cloud"
    return {
        "asset_type": asset_type, "ply_format": fmt,
        "vertex_count": elements["vertex"],
        "face_count": elements.get("face", 0),
        "vertex_properties": sorted(fields),
    }


def inspect_asset(path):
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".ply":
        return inspect_ply(path)
    if suffix == ".spz":
        if path.stat().st_size < 16:
            raise ValueError("SPZ file too small")
        return {"asset_type": "gaussian_splats", "container": "spz", "verified_format": False}
    if suffix == ".glb":
        with path.open("rb") as stream:
            header = stream.read(12)
        if len(header) != 12 or header[:4] != b"glTF" or int.from_bytes(header[4:8], "little") != 2:
            raise ValueError("Invalid GLB version/signature")
        if int.from_bytes(header[8:12], "little") != path.stat().st_size:
            raise ValueError("GLB length mismatch")
        return {"asset_type": "mesh_scene", "container": "glb"}
    raise ValueError("Expected .ply, .spz or .glb")


def package(source, destination, asset_id, up_axis="unknown", meters_per_unit=None):
    source = Path(source).resolve(strict=True)
    if not source.is_file():
        raise ValueError("Source must be a file")
    if not SAFE_ID.fullmatch(asset_id):
        raise ValueError("Unsafe asset_id")
    if up_axis not in ("unknown", "Y", "Z"):
        raise ValueError("Up axis must be unknown/Y/Z")
    if meters_per_unit is not None and not (0 < meters_per_unit < 1e9):
        raise ValueError("meters_per_unit must be positive")
    info = inspect_asset(source)
    destination = Path(destination).resolve()
    if destination == source.parent or destination == source:
        raise ValueError("Use a separate output directory")
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / (asset_id + source.suffix.lower())
    manifest_file = destination / "world_manifest.json"
    if target.exists() or manifest_file.exists():
        raise FileExistsError("Output exists; choose an empty directory")
    digest = hashlib.sha256()
    with source.open("rb") as infile, target.open("wb") as outfile:
        while chunk := infile.read(1024 * 1024):
            digest.update(chunk)
            outfile.write(chunk)
    manifest = {
        "schema_version": 1,
        "asset_id": asset_id,
        "asset_type": info["asset_type"],
        "model_file": target.name,
        "sha256": digest.hexdigest(),
        "file_bytes": target.stat().st_size,
        "source_up_axis": up_axis,
        "meters_per_source_unit": meters_per_unit,
        "analysis": info,
        "collision_ready": False,
        "provenance": "User-supplied file; HY-World origin has not been independently verified",
        "license_note": "Review Tencent HY-World 2.0 Community License and input rights before use.",
    }
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Existing HY-World .ply/.spz or mesh .glb")
    parser.add_argument("--out", required=True, help="New output folder for a browser-ready package")
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--up-axis", default="unknown", choices=["unknown", "Y", "Z"])
    parser.add_argument("--meters-per-unit", type=float, default=None)
    args = parser.parse_args()
    print(json.dumps(package(args.input, args.out, args.asset_id,
                             args.up_axis, args.meters_per_unit), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
