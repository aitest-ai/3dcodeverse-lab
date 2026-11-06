#!/usr/bin/env python3
"""Offline tests for the source_file rule in validate_glb.py (standard library only)."""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_glb import validate  # noqa: E402


def write_glb(path):
    doc = json.dumps({"asset": {"version": "2.0"}, "meshes": [{"primitives": []}]}).encode()
    doc += b" " * (-len(doc) % 4)
    path.write_bytes(struct.pack("<4sII", b"glTF", 2, 20 + len(doc)) + struct.pack("<I4s", len(doc), b"JSON") + doc)


class SourceFileRule(unittest.TestCase):
    def package(self, folder, **fields):
        write_glb(folder / "a.glb")
        manifest = {"schema_version": 1, "asset_id": "a", "model_file": "a.glb", **fields}
        (folder / "asset_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    def test_missing_blend_fails_by_default(self):
        with tempfile.TemporaryDirectory() as d:
            self.package(Path(d), source_file="a.blend")
            with self.assertRaisesRegex(ValueError, "a.blend"):
                validate(d)

    def test_omitted_source_file_fails_by_default(self):
        with tempfile.TemporaryDirectory() as d:
            self.package(Path(d))
            with self.assertRaisesRegex(ValueError, "simple basenames"):
                validate(d)

    def test_explicit_opt_out_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self.package(Path(d), requirements={"source_file": False})
            validate(d)
            self.assertTrue((Path(d) / "validation.json").is_file())

    def test_present_blend_still_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self.package(Path(d), source_file="a.blend")
            (Path(d) / "a.blend").write_bytes(b"x")
            validate(d)


if __name__ == "__main__":
    unittest.main()
