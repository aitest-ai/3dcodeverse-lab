import importlib.util, json, pathlib, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("contact_v29",ROOT/"scripts/research/onomichi_v29_contact_gate.py")
gate=importlib.util.module_from_spec(spec);sys.modules["contact_v29"]=gate;spec.loader.exec_module(gate)
FIXTURE=pathlib.Path(__file__).with_name("onomichi-v29-synthetic-contact.json")
class TestContactGate(unittest.TestCase):
 def setUp(self):self.d=json.loads(FIXTURE.read_text())
 def test_synthetic_only(self):
  r=gate.analyse_capture(self.d)
  self.assertEqual(r["status"],"SYNTHETIC_UNIT_TEST_ONLY")
  self.assertAlmostEqual(r["distances_mm"]["left_hand_to_grip"]["median_mm"],20)
  self.assertAlmostEqual(r["distances_mm"]["right_hand_to_grip"]["p95_mm"],10)
  self.assertFalse(r["review_only"]["rideable_route_approved"])
 def test_missing_marker_rejected(self):
  del self.d["frames"][2]["markers"]["bike_grip_left"]
  with self.assertRaises(ValueError):gate.analyse_capture(self.d)
 def test_nonfinite_rejected(self):
  self.d["frames"][0]["markers"]["bike_grip_left"][0]=float("nan")
  with self.assertRaises(ValueError):gate.analyse_capture(self.d)
 def test_nonmonotonic_rejected(self):
  self.d["frames"][1]["t_s"]=0
  with self.assertRaises(ValueError):gate.analyse_capture(self.d)
 def test_fake_webgl_rejected(self):
  self.d["source"]="runtime_capture"
  self.d["environment"]={"webgl2":False,"capture_method":"dom_set_content","browser":"Chromium"}
  with self.assertRaises(ValueError):gate.analyse_capture(self.d)
 def test_real_short_not_accepted(self):
  self.d["source"]="runtime_capture"
  self.d["environment"]={"webgl2":True,"capture_method":"live_scene_world_matrices","browser":"Chromium 154"}
  self.assertEqual(gate.analyse_capture(self.d)["status"],"REAL_CAPTURE_INSUFFICIENT_FRAMES_NOT_APPROVED")
 def test_wrong_actor_sha_rejected(self):
  self.d["asset_sha256"]["actor_glb"]="unknown"
  with self.assertRaises(ValueError):gate.analyse_capture(self.d)
 def test_private_model_bytes_cannot_be_faked(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/"not-real.glb";p.write_bytes(b"glTF"+b"\0"*10)
   with self.assertRaises(ValueError):gate.inspect_glb(p,gate.ACTOR_SHA,"actor")
if __name__=="__main__":unittest.main()
