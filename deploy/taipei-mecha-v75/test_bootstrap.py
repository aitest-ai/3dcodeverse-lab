import importlib.util,io,os,pathlib,sys,tempfile,zipfile
root=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("bootstrap",root/"build_from_release.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
good="https://github.com/aitest-ai/3dcodeverse-lab/releases/download/example/game.zip"
assert m.safe_url(good)==good
for bad in ["http://github.com/aitest-ai/3dcodeverse-lab/releases/download/example/game.zip",
 "https://example.com/assets/game.zip",
 "https://github.com/other/repo/releases/download/test/game.zip",
 "https://github.com/aitest-ai/3dcodeverse-lab/archive/refs/tags/v75.zip"]:
 try:m.safe_url(bad);raise AssertionError("Unsafe URL accepted")
 except RuntimeError:pass
with tempfile.TemporaryDirectory() as work:
 p=pathlib.Path(work)/"bad.zip"
 with zipfile.ZipFile(p,"w") as z:z.writestr("../escape.txt","invalid")
 try:m.inspect_and_extract(p,pathlib.Path(work)/"dest");raise AssertionError("ZIP path traversal accepted")
 except RuntimeError:pass
 with zipfile.ZipFile(p,"w") as z:z.writestr("taipei-mecha-web/readme.txt","incomplete")
 try:m.inspect_and_extract(p,pathlib.Path(work)/"dest");raise AssertionError("Missing required overlay accepted")
 except RuntimeError:pass
print("PASS: release bootstrap URL filters, ZIP path traversal and missing-asset rejection; no real deploy implied")
