"""Install the exact public Godot binary in project-local tools, verifying release asset SHA-256."""
from pathlib import Path
import urllib.request,hashlib,zipfile
R=Path(__file__).resolve().parents[1];tools=R/'tools/engine';tools.mkdir(parents=True,exist_ok=True)
url='https://github.com/godotengine/godot/releases/download/4.6.3-stable/Godot_v4.6.3-stable_linux.x86_64.zip'
expected='d0bc2113065e481c9c2c2b2c37daa4e8be3fe9e27f0ab9ab0b6096e9a37907f3'
p=tools/'godot.zip';urllib.request.urlretrieve(url,p)
assert hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()==expected
with zipfile.ZipFile(p) as z:
 for n in z.namelist():assert not Path(n).is_absolute() and '..' not in Path(n).parts
 z.extractall(tools)
binary=tools/'Godot_v4.6.3-stable_linux.x86_64';binary.chmod(0o755);print(binary)
