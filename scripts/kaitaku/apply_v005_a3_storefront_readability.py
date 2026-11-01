#!/usr/bin/env python3
"""Deterministic, browser-validated V005 A3 storefront readability overlay.

Input is FinalPolish A. No binary geometry is changed.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
import struct
from pathlib import Path

PARENT_SHA = "752887763308bf71342b0d9ac292fc0f30ffa2e30d0ec6639e7373bb03cd5a55"
OUTPUT_SHA = "8df3ada77443c390556e71c873d43dd65fe67996716e08ecfaff4e5faf60e27f"
TARGETS = [
    (
        "16 Closed shallow storefront backing",
        5,
        "V005 A3 store-local dark depth",
        [0.075, 0.068, 0.055, 1.0],
    ),
    (
        "16 Closed shallow storefront backing V005 inner reveal",
        6,
        "V005 A3 store-local closed reveal",
        [0.088, 0.080, 0.066, 1.0],
    ),
]

def sha(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def read_glb(path: Path):
    data = path.read_bytes()
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
    parts = [
        struct.pack("<4sII", b"glTF", 2, 0),
        struct.pack("<II", len(jb), 0x4E4F534A),
        jb,
    ]
    for kind, data in chunks[1:]:
        bb = bytes(data)
        bb += b"\0" * ((4 - len(bb) % 4) % 4)
        parts += [struct.pack("<II", len(bb), kind), bb]
    blob = b"".join(parts)
    return blob[:8] + struct.pack("<I", len(blob)) + blob[12:]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    if source == output:
        raise SystemExit("Refuse to overwrite FinalPolish A")
    if sha(source) != PARENT_SHA:
        raise SystemExit("Unexpected FinalPolish A SHA-256")

    doc, chunks = read_glb(source)
    changes = []
    original_material_count = len(doc["materials"])

    for node_name, old_index, new_name, color in TARGETS:
        node = next((x for x in doc["nodes"] if x.get("name") == node_name), None)
        if node is None:
            raise SystemExit("Missing " + node_name)
        users = [x for x in doc["nodes"] if x.get("mesh") == node["mesh"]]
        if len(users) != 1:
            raise SystemExit("Target mesh is not uniquely owned: " + node_name)
        primitives = doc["meshes"][node["mesh"]]["primitives"]
        if len(primitives) != 1 or primitives[0].get("material") != old_index:
            raise SystemExit("Unexpected target primitive/material: " + node_name)

        material = copy.deepcopy(doc["materials"][old_index])
        material["name"] = new_name
        material["pbrMetallicRoughness"]["baseColorFactor"] = color
        new_index = len(doc["materials"])
        doc["materials"].append(material)
        primitives[0]["material"] = new_index
        changes.append({
            "node": node_name,
            "mesh": node["mesh"],
            "old_material_index": old_index,
            "new_material_index": new_index,
            "new_material_name": new_name,
            "new_baseColorFactor": color,
        })

    blob = pack(doc, chunks)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    temp.write_bytes(blob)
    os.replace(temp, output)
    digest = sha(output)
    if digest != OUTPUT_SHA:
        raise SystemExit("Deterministic A3 SHA mismatch: " + digest)

    report = {
        "variant": "A3_storefront_readability",
        "status": "BROWSER_VALIDATED_OVERLAY",
        "parent_sha256": PARENT_SHA,
        "output_sha256": digest,
        "bytes": output.stat().st_size,
        "original_material_count": original_material_count,
        "material_count_after": len(doc["materials"]),
        "changes": changes,
        "protected": (
            "Binary GLB geometry chunk is byte-identical to FinalPolish A. "
            "Nodes/accessors/transforms and all existing materials are unchanged. "
            "Only two unique 16 ground-floor storefront primitives are reassigned "
            "to duplicated local backing/reveal materials. Glass transmission/roughness, "
            "upper windows, post office and barber remain unchanged."
        ),
    }
    report_path = args.report or output.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
