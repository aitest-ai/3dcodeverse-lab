"""Pure Python regression tests for the external GLB validator.
No Blender install is required to run these tests.
"""
import importlib.util
import json
import struct
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("validate_glb.py")
spec = importlib.util.spec_from_file_location("validate_glb", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class AssetContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest = {
            "schema_version": 1, "asset_id": "qa_test",
            "model_file": "qa_test.glb", "source_file": "qa_test.blend",
            "clips": ["Idle"], "min_animation_count": 1,
            "requirements": {"skins": True},
        }
        (self.root / "qa_test.blend").write_bytes(b"BLENDERtest")
        self.doc = {
            "asset": {"version": "2.0"},
            "meshes": [{"name": "body"}],
            "skins": [{"joints": [0]}],
            "nodes": [{"name": "bone"}],
            "animations": [{"name": "Mecha_Idle"}],
        }

    def tearDown(self):
        self.temp.cleanup()

    def write_asset(self):
        (self.root / "asset_manifest.json").write_text(
            json.dumps(self.manifest), encoding="utf-8")
        raw = json.dumps(self.doc).encode("utf-8")
        raw += b" " * (-len(raw) % 4)
        body = struct.pack("<I4s", len(raw), b"JSON") + raw
        (self.root / self.manifest["model_file"]).write_bytes(
            struct.pack("<4sII", b"glTF", 2, 12 + len(body)) + body)

    def test_valid_asset_passes(self):
        self.write_asset()
        validator.validate(self.root)
        self.assertTrue((self.root / "validation.json").exists())

    def test_missing_animation_is_rejected(self):
        self.doc["animations"] = []
        self.write_asset()
        with self.assertRaisesRegex(ValueError, "Expected 1 animations"):
            validator.validate(self.root)

    def test_missing_skin_is_rejected(self):
        self.doc["skins"] = []
        self.write_asset()
        with self.assertRaisesRegex(ValueError, "contains no skins"):
            validator.validate(self.root)

    def test_corrupt_magic_is_rejected(self):
        self.write_asset()
        f = self.root / "qa_test.glb"
        raw = f.read_bytes()
        f.write_bytes(b"XXXX" + raw[4:])
        with self.assertRaisesRegex(ValueError, "Not a glTF 2.0"):
            validator.validate(self.root)


if __name__ == "__main__":
    unittest.main()
