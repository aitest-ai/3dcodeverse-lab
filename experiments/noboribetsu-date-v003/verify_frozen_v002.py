#!/usr/bin/env python3
"""Read-only V002 preflight for the Noboribetsu Date Jidaimura V003 replay.

Usage:
  python verify_frozen_v002.py Noboribetsu_Date_V002_Complete.zip
  python verify_frozen_v002.py /path/to/Noboribetsu_Date_V002
No Blender or third-party packages required; never writes to the source.
PASS_SOURCE_ONLY is not a V003 Blender, Android, CDN or visual acceptance.
"""
from __future__ import annotations
import argparse
from collections import Counter
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import struct
import sys
import zipfile

FROZEN = {
    "authoring/date_v002_master.blend": "1d7637c7dd98642ffbfa03074fa6f3af50339a5e965afc2feb47e1ed86567ee1",
    "data/scene_geometry.json": "75d672d5296ac28bef25b03423da395027c4b29cf804652239f40e9fc73d408a",
    "data/collision.json": "52cea1f4b65e11a09f5504c48daef3f4eda7ef180312c1a39ab4db152a30e562",
    "models/scene_A.glb": "1400aff4bccb89fbc30bb2c931a71e91f8f6faf003e01bcb0c2347a14aa95a10",
    "models/scene_B.glb": "684b0917f3bf5c2edd87e05cfb2b6f670aab6fa574bb579f6bcaa01258d81314",
}
TARGET_MATERIALS = {
    "朱塗り_原創木目", "白壁_原創石灰表面", "LM_Yugi_ochre_plaster",
    "LM_Yugi_aged_timber", "LM_Yugi_cloth_hems", "LM_Yugi_blue_noren",
}


class FrozenSource:
    def __init__(self, path: Path):
        self.path = path.resolve()
        self.zip = None
        self.prefix = ""
        if self.path.is_file() and zipfile.is_zipfile(self.path):
            self.zip = zipfile.ZipFile(self.path)
            names = set(self.zip.namelist())
            prefixes = [p for p in ("", "Noboribetsu_Date_V002/")
                        if p + "authoring/date_v002_master.blend" in names]
            if len(prefixes) != 1:
                raise ValueError("Missing or ambiguous V002 project root")
            self.prefix = prefixes[0]
        elif not self.path.is_dir():
            raise FileNotFoundError(self.path)

    @contextmanager
    def open(self, name: str):
        if name.startswith("/") or ".." in Path(name).parts:
            raise ValueError("Unsafe relative path")
        if self.zip:
            with self.zip.open(self.prefix + name) as f:
                yield f
        else:
            with (self.path / name).open("rb") as f:
                yield f

    def sha(self, name: str):
        digest, count = hashlib.sha256(), 0
        with self.open(name) as f:
            while chunk := f.read(2 * 1024 * 1024):
                digest.update(chunk)
                count += len(chunk)
        return digest.hexdigest(), count

    def read(self, name: str, limit: int = 10_000_000) -> bytes:
        with self.open(name) as f:
            data = f.read(limit + 1)
        if len(data) > limit:
            raise ValueError("Input too large to parse as JSON")
        return data

    def glb_json(self, name: str):
        with self.open(name) as f:
            hdr = f.read(20)
            if len(hdr) != 20 or hdr[:4] != b"glTF":
                raise ValueError("GLB magic invalid")
            version, total, length, kind = struct.unpack("<IIII", hdr[4:])
            if version != 2 or kind != 0x4E4F534A or not (0 < length < 30_000_000):
                raise ValueError("GLB JSON header invalid")
            raw = f.read(length)
            if len(raw) != length:
                raise ValueError("GLB JSON truncated")
            return json.loads(raw), total

    def close(self):
        if self.zip:
            self.zip.close()


def road_topology(g: dict):
    if g.get("axes") != "Blender ENU; GLB EUS":
        raise ValueError("Wrong coordinate basis")
    vs, tris = g["road"]["vertices"], g["road"]["triangles"]
    if not vs or not tris:
        raise ValueError("Empty road mesh")
    edges = Counter()
    for t in tris:
        if len(t) != 3 or len(set(t)) != 3 or any(
            not isinstance(i, int) or i < 0 or i >= len(vs) for i in t
        ):
            raise ValueError("Invalid road triangle")
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            edges[tuple(sorted((a, b)))] += 1
    boundary = sum(n == 1 for n in edges.values())
    nonmanifold = sum(n > 2 for n in edges.values())
    if not boundary or nonmanifold:
        raise ValueError("Road boundary cannot support V003 edge overlay")
    return {"vertices": len(vs), "triangles": len(tris),
            "boundary_edges": boundary, "nonmanifold_edges": nonmanifold}


def verify(path: Path):
    src = FrozenSource(path)
    result = {
        "schema": "noboribetsu-date-v003-source-preflight/1",
        "input": str(src.path), "status": "FAIL",
        "blender_native_executed": False,
        "android_tested": False, "private_site_tested": False,
        "sha256": {}
    }
    try:
        for name, expected in FROZEN.items():
            actual, size = src.sha(name)
            result["sha256"][name] = {"actual": actual, "bytes": size,
                                       "match": actual == expected}
            if actual != expected:
                raise ValueError("V002 source hash mismatch: " + name)
        with src.open("authoring/date_v002_master.blend") as f:
            if f.read(7) != b"BLENDER":
                raise ValueError("Invalid V002 Blender master")
        geo = json.loads(src.read("data/scene_geometry.json"))
        result["road"] = road_topology(geo)
        glb, total = src.glb_json("models/scene_B.glb")
        if total != result["sha256"]["models/scene_B.glb"]["bytes"]:
            raise ValueError("Wrong GLB byte length")
        mats = {m.get("name") for m in glb.get("materials", [])}
        missing = TARGET_MATERIALS - mats
        if missing:
            raise ValueError("V003 target materials missing: " + repr(sorted(missing)))
        result["target_materials_found"] = len(TARGET_MATERIALS)
        result["status"] = "PASS_SOURCE_ONLY"
    except Exception as e:
        result["error"] = type(e).__name__ + ": " + str(e)
    finally:
        src.close()
    return result


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("v002_source", type=Path)
    args = cli.parse_args()
    result = verify(args.v002_source)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["status"] == "PASS_SOURCE_ONLY" else 1)
