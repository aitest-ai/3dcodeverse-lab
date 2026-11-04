"""Optional exact Blender download to a task-specific work/ directory. No credentials or paid service."""
import argparse,hashlib,urllib.request,tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--dest',type=Path,default=Path('work/tools'));a=p.parse_args()
name='blender-5.2.3-linux-x64.tar.xz';wanted='78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec';a.dest.mkdir(parents=True,exist_ok=True);archive=a.dest/name
if not archive.exists():urllib.request.urlretrieve('https://download.blender.org/release/Blender5.2/'+name,archive)
with archive.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
if actual!=wanted:raise SystemExit('Official pinned Blender archive SHA-256 mismatch')
with tarfile.open(archive) as t:t.extractall(a.dest,filter='data')
print(a.dest/'blender-5.2.3-linux-x64/blender')
