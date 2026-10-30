"""Offline tests for HY-World 2.0 file-type bridge; no AI model or GPU required."""
import importlib.util
import json
import struct
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts/hyworld2/pack_world.py"
spec = importlib.util.spec_from_file_location("hyworld_pack", MODULE)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def ply(self, name, header, data=b""):
        path = self.root / name
        path.write_bytes(("ply\nformat ascii 1.0\n" + header + "end_header\n").encode() + data)
        return path

    def test_triangle_mesh_is_not_splats(self):
        file = self.ply("global_mesh.ply",
            "element vertex 3\nproperty float x\nproperty float y\nproperty float z\n"
            "element face 1\nproperty list uchar int vertex_indices\n")
        result = bridge.inspect_asset(file)
        self.assertEqual(result["asset_type"], "triangle_mesh")
        self.assertEqual(result["face_count"], 1)

    def test_gaussian_properties(self):
        file = self.ply("gaussians.ply",
            "element vertex 1\nproperty float x\nproperty float y\n"
            "property float opacity\nproperty float f_dc_0\n"
            "property float scale_0\nproperty float rot_0\n")
        self.assertEqual(bridge.inspect_asset(file)["asset_type"], "gaussian_splats")
        output = self.root / "package"
        manifest = bridge.package(file, output, "sample_scene")
        self.assertEqual(json.loads((output / "world_manifest.json").read_text())["asset_type"], "gaussian_splats")
        self.assertTrue((output / manifest["model_file"]).exists())
        self.assertIsNone(manifest["meters_per_source_unit"])

    def test_pointcloud_not_marked_as_triangle_mesh(self):
        file = self.ply("points.ply", "element vertex 2\nproperty float x\n")
        self.assertEqual(bridge.inspect_asset(file)["asset_type"], "point_cloud")

    def test_reject_invalid_ply_and_identifiers(self):
        invalid = self.root / "invalid.ply"
        invalid.write_text("not a ply")
        with self.assertRaises(ValueError):
            bridge.inspect_asset(invalid)
        file = self.ply("points.ply", "element vertex 1\nproperty float x\n")
        with self.assertRaises(ValueError):
            bridge.package(file, self.root / "package", "../unsafe")

    def test_reject_output_overwrite(self):
        file = self.ply("points.ply", "element vertex 1\nproperty float x\n")
        bridge.package(file, self.root / "output", "safe")
        with self.assertRaises(FileExistsError):
            bridge.package(file, self.root / "output", "safe")

    def test_glb_header(self):
        file = self.root / "test.glb"
        file.write_bytes(struct.pack("<4sII", b"glTF", 2, 12))
        self.assertEqual(bridge.inspect_asset(file)["asset_type"], "mesh_scene")

    def test_truncated_ply(self):
        file = self.root / "bad.ply"
        file.write_bytes(b"ply\nformat ascii 1.0\nelement vertex 1\n")
        with self.assertRaises(ValueError):
            bridge.inspect_asset(file)


if __name__ == "__main__":
    unittest.main()
