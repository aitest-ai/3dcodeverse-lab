"""Scene Hub structural checks; CPU-only, no cloud credentials required."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import scene_hub as hub

class SceneHubTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scenes/catalog").mkdir(parents=True)
        (self.root / "scenes/assets").mkdir(parents=True)

    def make_scene(self, scene_id="test-village"):
        folder = self.root / "scenes/assets" / scene_id
        folder.mkdir()
        path = folder / "scene.ply"
        path.write_bytes(b"ply\nformat ascii 1.0\nelement vertex 1\nproperty float x\nend_header\n0\n")
        manifest = {"schema_version":1,"scene_id":scene_id,"title":"Test village",
                    "license":"CC0-1.0","review_status":"unverified",
                    "files":[{"path":f"scenes/assets/{scene_id}/scene.ply",
                              "sha256":hub.digest(path),"bytes":path.stat().st_size}]}
        (self.root / "scenes/catalog" / (scene_id+".json")).write_text(json.dumps(manifest))
        return path

    def test_committed_sample_sha(self):
        entry = hub.read_scene(ROOT, "demo-forest-island", verify=True)
        self.assertEqual(entry["asset_kind"], "triangle_mesh")
        self.assertEqual(entry["review_status"], "unverified")

    def test_pull_hash_and_no_overwrite(self):
        original = self.make_scene()
        args = type("Args", (), {"scene_id":"test-village",
               "repo":str(self.root),"ref":"main","output":str(self.root/"out")})
        hub.cmd_pull(args)
        self.assertEqual((self.root/"out/test-village/scene.ply").read_bytes(), original.read_bytes())
        with self.assertRaises(FileExistsError):
            hub.cmd_pull(args)

    def test_reject_corrupted_file(self):
        file = self.make_scene()
        file.write_bytes(b"modified")
        with self.assertRaises(ValueError):
            hub.read_scene(self.root,"test-village",verify=True)

    def test_reject_traversal(self):
        self.make_scene()
        file = self.root / "scenes/catalog/test-village.json"
        manifest = json.loads(file.read_text())
        manifest["files"][0]["path"] = "scenes/assets/test-village/../../../bad.txt"
        file.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            hub.read_scene(self.root,"test-village",verify=True)

    def test_bad_ids(self):
        for bad in ["A", "../secrets", "Foo", "with spaces", "main"]:
            with self.assertRaises(ValueError):
                hub.valid_id(bad)

    def test_stage_and_immutable_ids(self):
        file = self.root/"my.glb"
        file.write_bytes(b"example-glb")
        args = type("Args", (), {"scene_id":"my-river","hub":str(self.root),
              "title":"River","source":"Original test","license":"CC0","description":"",
              "kind":"triangle_mesh","files":[str(file)],"preview_url":None})
        hub.cmd_stage(args)
        entry = hub.read_scene(self.root,"my-river",verify=True)
        self.assertEqual(entry["review_status"],"unverified")
        with self.assertRaises(FileExistsError):
            hub.cmd_stage(args)

    def test_push_needs_confirmation(self):
        args = type("Args", (), {"scene_id":"my-river","hub":str(self.root),"confirm":False})
        with self.assertRaises(ValueError):
            hub.cmd_push(args)

    def test_remote_requires_https_github(self):
        with self.assertRaises(ValueError):
            with hub.hub_checkout("http://localhost/myrepo","main"):
                pass

if __name__ == "__main__":
    unittest.main()
