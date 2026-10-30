"""Fetch authoritative MakeHuman CC0 packs and inspect per-asset metadata.

No 3rd-party assets are committed into the repository. The build downloads
original public archives and emits a reproducible manifest with source URLs.
"""
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from pathlib import Path
import json, hashlib, zipfile, os, sys, shutil

NAMES=("shirts01","pants01","cheek01","nose01","faceunits01")
OFFICIAL="https://www.makehumancommunity.org/assets/assetpacks/"
class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href=None; self.lines=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":self.href=dict(attrs).get("href")
    def handle_data(self,data):
        if self.href:self.lines.append((data.strip(),self.href))
    def handle_endtag(self,tag):
        if tag=="a":self.href=None
def get(url,timeout=65):
    req=Request(url,headers={"User-Agent":"Mozilla/5.0 (licensed asset verification; research)"})
    return urlopen(req,timeout=timeout)
def sources(name):
    page=OFFICIAL+name+".html"
    with get(page) as r: markup=r.read().decode("utf-8","replace")
    p=Anchors();p.feed(markup)
    a=[urljoin(page,h) for title,h in p.lines if "mirror" in title.lower()]
    # Some static page templates place the label inside a span with an anchor,
    # so fall back to linked .zip files from the official page.
    if not a:
        a=[urljoin(page,h) for title,h in p.lines if ".zip" in h.lower()]
    unique=list(dict.fromkeys(a))
    if not unique:raise RuntimeError("No official mirror links on "+page+"; refuse invented URL")
    return page,unique
def download_pack(name,root):
    page,mirrors=sources(name)
    out=root/(name+".zip")
    tried=[]
    for url in mirrors:
        try:
            print("ASSET_PACK_MIRROR",name,url,flush=True)
            with get(url,110) as r:
                with out.open("wb") as f:
                    while True:
                        chunk=r.read(2<<20)
                        if not chunk:break
                        f.write(chunk)
            if not zipfile.is_zipfile(out):raise RuntimeError("Invalid ZIP from mirror")
            with zipfile.ZipFile(out) as z:
                assert z.testzip() is None
                names=z.namelist()
                assets=[x for x in names if x.lower().endswith((".mhclo",".target",".target.gz"))]
                if not assets:raise RuntimeError("No .mhclo or target in pack")
                for item in z.infolist():
                    if Path(item.filename).is_absolute() or ".." in Path(item.filename).parts:
                        raise RuntimeError("Unsafe path in CC0 archive")
                    if item.file_size>200_000_000:raise RuntimeError("Unreasonable asset member")
                z.extractall(root/"original"/name)
            return dict(pack=name, official_page=page, download_url=url,
                        sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
                        bytes=out.stat().st_size, members=assets)
        except Exception as e:
            tried.append((url,str(e)))
            if out.exists():out.unlink()
            print("MIRROR_ERROR",name,url,str(e),flush=True)
    raise RuntimeError("Could not download verified pack "+name+" "+repr(tried))
def main():
    root=Path(os.getenv("MH_PACK_OUT",".deps/mh_extra"))
    root.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for name in NAMES:
        manifest.append(download_pack(name,root))
    keys=("namuhekam_male_polo_shirt","toigo_fisherman_sweater",
          "joepal_crude_t-shirt_female","cortu_cargo_pants","toigo_wool_pants")
    found={k:[] for k in keys}
    for p in (root/"original").rglob("*.mhclo"):
        for k in keys:
            if p.stem==k:found[k].append(str(p))
    for name,paths in found.items():
        if not paths:raise RuntimeError("Original fitted clothing asset missing "+name)
    (root/"pack_manifest.json").write_text(json.dumps(
        dict(packs=manifest,required_clothing=found,license_statement="The official CC0 pack collection and per-asset source license must both be checked before production release. Third-party CC-BY/AGPL are not silently promoted."),
        ensure_ascii=False,indent=2),encoding="utf-8")
    print("DOWNLOADED_LICENSED_MHCLO_AND_TARGETS",json.dumps(
        {k:len(x) for k,x in found.items()}),flush=True)
if __name__=="__main__":main()
