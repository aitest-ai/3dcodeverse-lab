#!/usr/bin/env python3
"""Deterministic V005 A3H-B hedge-shape preview (NOT PROMOTED).

Input must be the pinned browser-validated FinalPolish A3 GLB. Output changes only the
POSITION accessors of the two post-office hedge leaf/twig groups.

This is an EXPERIMENTAL layer. It must not silently replace FinalPolish A3.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import struct
from pathlib import Path

PARENT_SHA = "8df3ada77443c390556e71c873d43dd65fe67996716e08ecfaff4e5faf60e27f"
OUTPUT_SHA = "09decb57caeb803cefd13bcd2ddf77bb0a2c31f80dc761458caafa778caa4a89"
GROUPS = {
    "14 Left entrance hedge": [
        "14 Left entrance hedge branching twigs",
        "14 Left entrance hedge leaves",
    ],
    "14 Right postal hedge": [
        "14 Right postal hedge branching twigs",
        "14 Right postal hedge leaves",
    ],
}

def sha(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def read_glb(path: Path):
    data = path.read_bytes()
    magic, version, total = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or total != len(data):
        raise ValueError("Invalid GLB 2.0")
    off, chunks = 12, []
    while off < len(data):
        length, kind = struct.unpack_from("<II", data, off)
        off += 8
        chunks.append((kind, bytearray(data[off:off + length])))
        off += length
    doc = json.loads(chunks[0][1].decode().rstrip(" \t\r\n\x00"))
    return doc, chunks

def pack(doc, chunks) -> bytes:
    jb = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode()
    jb += b" " * ((4 - len(jb) % 4) % 4)
    out = [struct.pack("<4sII", b"glTF", 2, 0), struct.pack("<II", len(jb), 0x4E4F534A), jb]
    for kind, data in chunks[1:]:
        bb = bytes(data)
        bb += b"\0" * ((4 - len(bb) % 4) % 4)
        out.extend([struct.pack("<II", len(bb), kind), bb])
    blob = b"".join(out)
    return blob[:8] + struct.pack("<I", len(blob)) + blob[12:]

def pos_meta(doc, accessor_index):
    a = doc["accessors"][accessor_index]
    bv = doc["bufferViews"][a["bufferView"]]
    if a["componentType"] != 5126 or a["type"] != "VEC3":
        raise ValueError("Expected FLOAT VEC3 position accessor")
    return a, bv, bv.get("byteOffset", 0) + a.get("byteOffset", 0), bv.get("byteStride", 12)

def read_positions(doc, buf, accessor_index):
    a, _, off, stride = pos_meta(doc, accessor_index)
    return [struct.unpack_from("<fff", buf, off + i * stride) for i in range(a["count"])]

def write_positions(doc, buf, accessor_index, points):
    a, _, off, stride = pos_meta(doc, accessor_index)
    for i, point in enumerate(points):
        struct.pack_into("<fff", buf, off + i * stride, *point)
    a["min"] = [min(p[k] for p in points) for k in range(3)]
    a["max"] = [max(p[k] for p in points) for k in range(3)]

def envelope(t, phase, group_index):
    # The entrance-side hedge is more rounded in the local reference photo.
    # The postbox-side hedge remains more upright. This is an unsurveyed
    # artistic refinement limited strictly to foliage/twig POSITION accessors.
    if group_index == 0:
        core = 0.80 + 0.20 * (math.sin(math.pi * t) ** 0.67)
    else:
        core = 0.89 + 0.11 * (math.sin(math.pi * t) ** 0.72)
    wave = (
        1.0
        + 0.025 * math.sin(2 * math.pi * (2.15 * t) + phase)
        + 0.014 * math.sin(2 * math.pi * (4.70 * t) - 0.7 * phase)
    )
    return max(0.74 if group_index == 0 else 0.83, min(1.030, core * wave))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    if source == output:
        raise SystemExit("Refuse to overwrite FinalPolish A3")
    if sha(source) != PARENT_SHA:
        raise SystemExit("Unexpected parent FinalPolish A3 SHA-256")

    doc, chunks = read_glb(source)
    buf = chunks[1][1]
    changes = []

    for group_index, (group, prefixes) in enumerate(GROUPS.items()):
        records, all_points = [], []
        for node in doc["nodes"]:
            name = node.get("name", "")
            if any(name == p or name.startswith(p + ".") for p in prefixes):
                mesh = doc["meshes"][node["mesh"]]
                if len(mesh["primitives"]) != 1:
                    raise SystemExit("Unexpected hedge primitive count")
                ai = mesh["primitives"][0]["attributes"]["POSITION"]
                points = read_positions(doc, buf, ai)
                records.append((name, ai, points))
                all_points += points
        if len(records) != 6:
            raise SystemExit(f"Expected 6 nodes for {group}, found {len(records)}")

        xmin = min(p[0] for p in all_points)
        xmax = max(p[0] for p in all_points)
        ymin = min(p[1] for p in all_points)
        zmin = min(p[2] for p in all_points)
        zmax = max(p[2] for p in all_points)
        zcenter = (zmin + zmax) / 2
        phase = 0.4 + group_index * 1.7

        for name, ai, points in records:
            shaped, max_dy, max_dz = [], 0.0, 0.0
            for x, y, z in points:
                t = 0.5 if xmax == xmin else max(0, min(1, (x - xmin) / (xmax - xmin)))
                env = envelope(t, phase, group_index)
                height_weight = max(0, min(1, (y - (ymin + 0.05)) / 0.72))
                new_y = y + (y - ymin) * (env - 1.0) * height_weight
                depth_env = 0.945 + 0.055 * (math.sin(math.pi * t) ** 0.75)
                depth_weight = max(0, min(1, (y - (ymin + 0.10)) / 0.55))
                new_z = z + (z - zcenter) * (depth_env - 1.0) * depth_weight
                shaped.append((x, new_y, new_z))
                max_dy = max(max_dy, abs(new_y - y))
                max_dz = max(max_dz, abs(new_z - z))
            write_positions(doc, buf, ai, shaped)
            changes.append({
                "node": name,
                "position_accessor": ai,
                "max_abs_vertical_change_m": max_dy,
                "max_abs_depth_change_m": max_dz,
            })

    blob = pack(doc, chunks)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    temp.write_bytes(blob)
    os.replace(temp, output)
    digest = sha(output)
    if digest != OUTPUT_SHA:
        raise SystemExit(f"Deterministic A3H-B SHA mismatch: {digest}")

    report = {
        "variant": "A3H_B_hedge_photo_guided",
        "status": "EXPERIMENTAL_NOT_PROMOTED",
        "parent_sha256": PARENT_SHA,
        "output_sha256": digest,
        "bytes": output.stat().st_size,
        "changed_nodes": changes,
        "protected": (
            "No planting soil, postbox, postal passage, kerb, building, grass, glass, roof, "
            "stair, node transform, material or index accessor is edited."
        ),
        "visual": (
            "Geometry-only matched-camera review shows more rounded hedge ends; full-scene "
            "Blender Cycles and Android have not run for A3H-B; final in-scene "
            "visual acceptance is pending."
        ),
    }
    report_path = args.report or output.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
