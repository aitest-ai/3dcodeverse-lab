"""Offline contract tests for safe 3D tool selection and GLB readiness reports."""
import importlib.util
import io
import json
import struct
import tempfile
import unittest
from pathlib import Path


def load_module(name):
    path = Path(__file__).with_name(name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


catalog = load_module("tool_catalog")
polyhaven = load_module("polyhaven_search")
quality = load_module("glb_quality_report")


class CatalogTests(unittest.TestCase):
    def test_catalog_all_entries_valid(self):
        data = catalog.load_catalog()
        self.assertGreaterEqual(catalog.validate(data), 10)

    def test_animal_gpu_filter(self):
        data = catalog.load_catalog()
        matches = catalog.select(data["items"], category="animal", gpu="gpu")
        self.assertIn("unirig", {x["id"] for x in matches})
        self.assertTrue(all(x["automation"].startswith("gpu_") for x in matches))

    def test_cpu_has_non_gpu_options(self):
        data = catalog.load_catalog()
        matches = catalog.select(data["items"], category="human", gpu="cpu")
        self.assertIn("mpfb", {x["id"] for x in matches})
        self.assertNotIn("trellis2", {x["id"] for x in matches})


class PolyHavenTests(unittest.TestCase):
    def test_fake_api_filters_without_downloading(self):
        fake = {
            "granite_rock": {"name": "Granite Rock", "tags": ["stone", "grey"], "category": "Nature"},
            "studio": {"name": "Studio Night", "tags": ["night"], "category": "Light"}
        }
        def opener(req, timeout):
            self.assertTrue(req.get_header("User-agent"))
            return io.BytesIO(json.dumps(fake).encode())
        result = polyhaven.search("stone", kind="models", opener=opener)
        self.assertEqual([x["id"] for x in result], ["granite_rock"])
        self.assertTrue(result[0]["source_url"].startswith("https://polyhaven.com/a/"))

    def test_query_rejects_blank(self):
        with self.assertRaises(ValueError):
            polyhaven.search("  ")


class GLBAuditTests(unittest.TestCase):
    def make_glb(self, folder):
        d = {"asset": {"version": "2.0"},
             "meshes": [{"primitives": [{
                 "attributes": {"POSITION": 0, "NORMAL": 0, "TEXCOORD_0": 0},
                 "indices": 1, "material": 0
             }]}],
             "accessors": [{"count": 24}, {"count": 36}],
             "skins": [{"joints": [0]}],
             "animations": [{"name": "Walk"}],
             "materials": [{"pbrMetallicRoughness": {"baseColorFactor": [1,1,1,1]}}],
             "nodes": [{"name": "root"}]}
        raw = json.dumps(d).encode()
        raw += b" " * (-len(raw) % 4)
        data = struct.pack("<I4s", len(raw), b"JSON") + raw
        path = folder / "rigged.glb"
        path.write_bytes(struct.pack("<4sII", b"glTF", 2, 12+len(data)) + data)
        return path

    def test_rigged_asset_counts(self):
        with tempfile.TemporaryDirectory() as folder:
            report = quality.audit(self.make_glb(Path(folder)), kind="animal")
            self.assertEqual(report["triangles_estimate"], 12)
            self.assertEqual(report["skins"], 1)
            self.assertEqual(report["animations"], ["Walk"])
            self.assertTrue(report["artistic_review_required"])

    def test_artistic_quality_not_automatically_asserted(self):
        with tempfile.TemporaryDirectory() as folder:
            report = quality.audit(self.make_glb(Path(folder)), kind="human")
            self.assertIn("NO_FACIAL_MORPH_TARGETS_CHECK_EXPRESSIONS_MANUALLY",
                          report["potential_issues"])
            self.assertTrue(report["artistic_review_required"])


if __name__ == "__main__":
    unittest.main()
