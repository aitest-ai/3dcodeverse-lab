#!/usr/bin/env python3
"""Fail-closed deployment bootstrap for the ORIGINAL v7.5 mecha web bundle.
The 60 MB source ZIP is downloaded ONLY after its GitHub Release URL is set.
Never substitute fake assets or deploy the QA-only page as a playable game.
"""
from __future__ import annotations
import argparse,hashlib,os,shutil,subprocess,sys,tempfile,urllib.parse,urllib.request,zipfile
from pathlib import Path

ASSET_SHA256="6896daa50d799bf292ba298c347134aec8a55e6986bb4bbe50c560ecea9c0e7e"
ASSET_BYTES=59898586
CITY_PIN="1d70708fc92a088b779c8c0e22677adb64966a1b"
BASE=Path(__file__).resolve().parent
LIMIT=110_000_000

def safe_url(raw:str)->str:
    parsed=urllib.parse.urlsplit(str(raw).strip())
    if parsed.scheme!="https" or parsed.hostname!="github.com" or parsed.username or parsed.password:
        raise RuntimeError("Only HTTPS GitHub Release asset URLs are allowed")
    if not parsed.path.startswith("/aitest-ai/3dcodeverse-lab/releases/download/") or parsed.query or parsed.fragment:
        raise RuntimeError("Expected an exact public GitHub release asset URL")
    return raw

def stream_release(url:str,path:Path):
    req=urllib.request.Request(safe_url(url),headers={"User-Agent":"Taipei-Mecha-v7.5-Vercel-Bootstrap"})
    digest=hashlib.sha256()
    count=0
    with urllib.request.urlopen(req,timeout=180) as resp,path.open("wb") as output:
        final_host=urllib.parse.urlsplit(resp.url).hostname
        if final_host not in {"github.com","release-assets.githubusercontent.com","objects.githubusercontent.com"}:
            raise RuntimeError("Unexpected artifact redirect host")
        while True:
            buf=resp.read(1024*1024)
            if not buf:break
            count+=len(buf)
            if count>LIMIT:raise RuntimeError("Asset download exceeds safe upper bound")
            digest.update(buf);output.write(buf)
    if count!=ASSET_BYTES or digest.hexdigest()!=ASSET_SHA256:
        raise RuntimeError(f"Original v7.5 source integrity mismatch: bytes={count}, sha256={digest.hexdigest()}")
    return count

def inspect_and_extract(archive:Path,out:Path):
    # Verify CRC, paths and archive size BEFORE writing to the build directory.
    with zipfile.ZipFile(archive,"r") as z:
        paths=z.infolist()
        if z.testzip() is not None:raise RuntimeError("Archive CRC validation failed")
        for item in paths:
            name=item.filename
            if name.startswith("/") or ".." in Path(name).parts or "\\" in name or item.file_size>30_000_000:
                raise RuntimeError("Unsafe archive member")
            if (item.external_attr >> 16) & 0o170000 == 0o120000:
                raise RuntimeError("Symbolic links not permitted in the asset bundle")
            if not name.startswith("taipei-mecha-web/"):
                raise RuntimeError("Unexpected source ZIP root")
        if sum(x.file_size for x in paths)>140_000_000:raise RuntimeError("Expanded asset bundle too large")
        z.extractall(out)
    root=out/"taipei-mecha-web"
    for required in ("build_web.py","verify_source.py","Taipei_Mech_v7.5/patch_slop.py",
                     "Taipei_Mech_v7.5/assets/mecha_v50.glb",
                     "Taipei_Mech_v7.5/assets/enemy_assault_v63.glb",
                     "Taipei_Mech_v7.5/assets/enemy_ranger_v63.glb",
                     "Taipei_Mech_v7.5/assets/enemy_heavy_v63.glb"):
        if not (root/required).is_file():raise RuntimeError("Missing original game file: "+required)
    return root

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive",help="Local original 60MB ZIP, for offline verification only")
    parser.add_argument("--verify-only",action="store_true")
    args=parser.parse_args()
    if args.archive and not args.verify_only:
        raise RuntimeError("--archive is allowed only with --verify-only to avoid accidental local deployment")
    if sys.version_info<(3,10):raise RuntimeError("Python 3.10+ required")
    with tempfile.TemporaryDirectory(prefix="taipei_mecha_release_v75_") as temporary:
        temp=Path(temporary)
        archive=temp/"asset.zip"
        if args.archive:
            shutil.copyfile(args.archive,archive)
            if archive.stat().st_size!=ASSET_BYTES or hashlib.sha256(archive.read_bytes()).hexdigest()!=ASSET_SHA256:
                raise RuntimeError("Local archive checksum mismatch")
        else:
            url=os.getenv("TAIPEI_MECHA_ASSET_RELEASE_URL","")
            if not url:raise RuntimeError("Not deployed: TAIPEI_MECHA_ASSET_RELEASE_URL is required")
            stream_release(url,archive)
        source=inspect_and_extract(archive,temp/"source")
        subprocess.run([sys.executable,"verify_source.py"],cwd=source,check=True,timeout=150)
        if args.verify_only:
            print("PASS: original v7.5 ZIP, GLB and 49 source modules verified; NOT a live deployment")
            return
        dest=BASE/"dist"
        if dest.exists():raise RuntimeError("dist exists: refusing stale/in-place build")
        # Original builder obtains pinned source from Github at build time and
        # runs original v7.5 patch_slop.py without changing the game hit logic.
        subprocess.run([sys.executable,"build_web.py","--output",str(dest)],
                       cwd=source,check=True,timeout=330)
        for name in ("index.html","js/main.js","js/mech-addon.js","js/mech-combat.js",
                     "js/taipei-geodata.js","models/mecha_v50.glb",
                     "models/enemy_assault_v63.glb","models/enemy_ranger_v63.glb",
                     "models/enemy_heavy_v63.glb","mech-build-report.json"):
            if not (dest/name).is_file():raise RuntimeError("Incomplete built game: "+name)
        report=(dest/"mech-build-report.json").read_text()
        if "real-original-v7.5-WebGPU-game" not in report or CITY_PIN not in report:
            raise RuntimeError("Missing pinned real-game build evidence")
        print("PASS original Taipei Mecha v7.5 website build:",dest)
if __name__=="__main__":
    main()
