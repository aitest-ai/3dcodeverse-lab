"""V31 protects the *real* V28 ZIP: these are synthetic-only CI fixtures."""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,stat,tempfile,unittest,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
GATE=ROOT/"scripts/research/onomichi_v31_local_runtime_gate.py"
spec=importlib.util.spec_from_file_location("v31_gate",GATE)
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)

def make_fixture(root,path="fixture.zip",*,entries=None,index=None):
 zpath=root/path
 source='export class AvatarDriver {update(){return 1}}\nexport class BicycleDriver {cycle(){return true}}\n'
 base={name:(source if name=="src/avatar.mjs" else "synthetic-"+name).encode() for name in gate.PROTECTED}
 base["index.html"]=index or (
  '<!doctype html><html><head><meta charset="utf-8"></head><body>'
  '<h1>FIXTURE ONLY - NEVER THE ORIGINAL GAME</h1><button id="bike">模擬騎車</button>'
  '<canvas id="fake-world" width="360" height="200"></canvas>'
  '<script>window.__fixtureGameLoaded=true;document.getElementById("bike").addEventListener("click",()=>window.__fixtureBikeClicks=(window.__fixtureBikeClicks||0)+1);'
  '</script></body></html>').encode()
 if entries:
  base.update(entries)
 with zipfile.ZipFile(zpath,"w",compression=zipfile.ZIP_DEFLATED) as z:
  for k,v in base.items():z.writestr("onomichi-cycling-v28/"+k,v)
 return zpath,base

class V31Guard(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.addCleanup(self.tmp.cleanup)
  self.base=pathlib.Path(self.tmp.name)
 def test_registry_has_real_full_hex_digests(self):
  self.assertEqual(len(gate.PROTECTED),12)
  for digest in gate.PROTECTED.values():
   self.assertEqual(len(digest),64)
   int(digest,16)
  self.assertEqual(len(gate.V28_ZIP_SHA),64)
 def test_authentic_cli_refuses_synthetic_zip_before_copying(self):
  archive,_=make_fixture(self.base)
  with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
   gate.prepare(archive,self.base/"no_fake_public_runtime")
  self.assertFalse((self.base/"no_fake_public_runtime").exists())
 def test_test_fixture_copy_isolated_and_original_sources_unchanged(self):
  archive,original=make_fixture(self.base)
  result=gate.prepare(archive,self.base/"candidate",fixture_mode=True)
  self.assertEqual(result["status"],gate.TEST_LABEL)
  self.assertFalse(result["core_hashes_verified"])
  self.assertFalse(result["original_game_core_changed"])
  self.assertEqual(len(result["observed_core_sha256"]),12)
  self.assertTrue((self.base/"candidate/review/onomichi-v31/observer_ui.html").is_file())
  for path in gate.PROTECTED:
   self.assertEqual((self.base/"candidate"/path).read_bytes(),original[path])
  index=(self.base/"candidate/index.html").read_text()
  self.assertEqual(index.count('ONOMICHI_V31_OBSERVER_INJECTION'),1)
  self.assertIn('src="./review/onomichi-v31/observer.mjs"',index)
  self.assertEqual(original["index.html"],zipfile.ZipFile(archive).read("onomichi-cycling-v28/index.html"))
 def test_no_original_zip_modified(self):
  archive,_=make_fixture(self.base)
  before=gate.sha256_file(archive)
  gate.prepare(archive,self.base/"candidate",fixture_mode=True)
  self.assertEqual(gate.sha256_file(archive),before)
 def test_reject_existing_output(self):
  archive,_=make_fixture(self.base)
  dest=self.base/"existing";dest.mkdir()
  with self.assertRaisesRegex(ValueError,"Output exists"):
   gate.prepare(archive,dest,fixture_mode=True)
 def test_reject_traversal_member(self):
  archive,_=make_fixture(self.base,entries={"../../evil.txt":b"bad"})
  with zipfile.ZipFile(archive) as z:
   with self.assertRaisesRegex(ValueError,"traversal"):
    gate.inspect_archive(z)
 def test_reject_case_insensitive_duplicate(self):
  archive,_=make_fixture(self.base,entries={"SRC/Main.mjs":b"x"})
  with zipfile.ZipFile(archive) as z:
   with self.assertRaisesRegex(ValueError,"case-colliding"):
    gate.inspect_archive(z)
 def test_reject_linux_symlink(self):
  bad=zipfile.ZipInfo("bundle/a")
  bad.create_system=3
  bad.external_attr=(stat.S_IFLNK|0o777)<<16
  with self.assertRaisesRegex(ValueError,"links"):
   gate.validate_member(bad)
 def test_reject_compression_oversize(self):
  bad=zipfile.ZipInfo("bundle/huge.glb")
  bad.file_size=gate.MAX_FILE_UNCOMPRESSED+1
  with self.assertRaisesRegex(ValueError,"Oversized"):
   gate.validate_member(bad)
 def test_reject_modified_ambiguous_index(self):
  with self.assertRaisesRegex(ValueError,"exactly one"):
   gate.inject_observer(b"<html>missing body")
  with self.assertRaisesRegex(ValueError,"Already instrumented"):
   gate.inject_observer(b"<!-- ONOMICHI_V31_OBSERVER_INJECTION --></body>")
 def test_source_inspection_does_not_pretend_dynamic_engine_hook(self):
  d=gate.inspector("export class AvatarDriver{ } export class BicycleDriver { }")
  self.assertFalse(d["actual_driver_instantiated_by_v31"])
  self.assertTrue(d["expected_exports_present"]["AvatarDriver"])
 def test_no_network_or_runtime_mutation_in_observer(self):
  s=(ROOT/"apps/onomichi-v31-original-runtime/observer.mjs").read_text()
  self.assertNotIn("fetch('https://",s)
  self.assertNotIn("src/main.mjs",s)
  self.assertNotIn("document.cookie",s)
  self.assertIn("original_site_modified:false",s)
if __name__=="__main__":unittest.main()
