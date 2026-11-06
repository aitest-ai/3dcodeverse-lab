#!/usr/bin/env python3
"""Find and fetch open 3D models. Standard library plus curl, so it runs on the GX10 and in GitHub Actions.

  library.py search --type chair --text wood --limit 10
  library.py pull B07H376LF5 --dest public/models     # the largest version within the budget + its credit
  library.py sync                                     # mirror the whole library to ~/asset-library (15 GB)
  library.py check                                    # compare the mirror with the catalogue

Sources: Amazon Berkeley Objects as packed by CodePawl, CC BY 4.0. Credit must stay with every model, so
pull always writes <id>.credit.json next to it. curl -4: Python's HTTP clients hang on IPv6 on the GX10.
"""
import argparse
import concurrent.futures as cf
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE = "https://huggingface.co/datasets/codepawl/abo-glb/resolve/main"
ROOT = Path(os.environ.get("ASSET_LIBRARY", Path.home() / "asset-library")) / "abo"
BUDGETS = {  # same numbers as asset-factory tools/budgets.json
    "normal": {"triangles": 30000, "bytes": 5242880, "materials": 8},
    "hero": {"triangles": 60000, "bytes": 5242880, "materials": 12},
}


def fetch(rel, dest, want_bytes=None):
    """Download one file through a temporary name; a partial file never looks finished."""
    dest = Path(dest)
    if dest.exists() and (want_bytes is None or dest.stat().st_size == want_bytes):
        return "kept"
    local = ROOT / rel
    if local.exists() and local.resolve() != dest.resolve() and (want_bytes is None or local.stat().st_size == want_bytes):
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(local, dest)
        return "copied"
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    r = subprocess.run(["curl", "-4", "-sSfL", "--retry", "8", "--retry-delay", "20", "--retry-all-errors",
                        "--connect-timeout", "30", "--max-time", "600", "-o", str(tmp), f"{BASE}/{rel}"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"{rel}: {r.stderr.strip()[-200:]}")
    if want_bytes is not None and tmp.stat().st_size != want_bytes:
        got = tmp.stat().st_size
        tmp.unlink()
        raise RuntimeError(f"{rel}: got {got} bytes, catalogue says {want_bytes}")
    tmp.replace(dest)
    return "downloaded"


def catalogue():
    path = ROOT / "metadata.jsonl"
    if not path.exists():
        fetch("metadata.jsonl", path)
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def choose(row, budget, lod=False):
    """The most detailed version that fits, or None. Returns (path, triangles, bytes).

    The simplified versions use KTX2 textures, so a viewer needs KTX2Loader: only offered with lod=True.
    """
    lim = BUDGETS[budget]
    if row["materials"] > lim["materials"]:
        return None
    if row["triangles"] <= lim["triangles"] and row["pack_bytes"] <= lim["bytes"]:
        return row["file"], row["triangles"], row["pack_bytes"]
    if lod:
        for level in row["lods"]:
            if level["triangles"] <= lim["triangles"] and level["bytes"] <= lim["bytes"]:
                return level["file"], level["triangles"], level["bytes"]
    return None


def credit(row):
    name = row.get("name") or row["id"]
    return {
        "id": row["id"],
        "license": "CC-BY-4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "source_url": f"https://huggingface.co/datasets/codepawl/abo-glb/tree/main/objects/{row['id']}",
        "attribution": f'"{name}" by Amazon.com, from Amazon Berkeley Objects '
                       "(https://amazon-berkeley-objects.s3.amazonaws.com/index.html), CC BY 4.0; "
                       "textures and geometry re-encoded by CodePawl. Amazon does not endorse this use.",
        "brand": row.get("brand"),
        "note": "CC BY covers the 3D data, not brand names or logos: check the model for logos before publishing.",
    }


def cmd_search(a):
    words = [w.lower() for w in (a.text or "").split()]
    n = 0
    for row in catalogue():
        hay = " ".join(str(row.get(k) or "") for k in ("name", "product_type", "color", "material", "style")).lower()
        if a.type and row.get("product_type") != a.type:
            continue
        if any(w not in hay for w in words):
            continue
        pick = choose(row, a.budget, a.lod)
        if pick is None:
            continue
        size = "x".join(f"{v:.2f}" for v in row["size_metres"])
        print(f"{row['id']}\t{row['product_type']}\t{size} m\t{pick[1]} tris\t{pick[2] // 1024} KB\t{(row.get('name') or '')[:70]}")
        n += 1
        if n >= a.limit:
            break
    print(f"{n} shown", file=sys.stderr)


def cmd_pull(a):
    rows = {r["id"]: r for r in catalogue()}
    if a.id not in rows:
        sys.exit(f"{a.id}: not in the catalogue")
    row = rows[a.id]
    pick = choose(row, a.budget, a.lod)
    if pick is None:
        sys.exit(f"{a.id}: no version fits the {a.budget} budget" + ("" if a.lod else "; --lod allows simpler versions, which need KTX2Loader"))
    dest = Path(a.dest)
    print(fetch(pick[0], dest / f"{a.id}.glb", pick[2]), pick[0], f"{pick[1]} tris")
    if pick[0].startswith("lods/"):
        print("this version has KTX2 textures: the viewer must call setKTX2Loader")
    (dest / f"{a.id}.credit.json").write_text(json.dumps(credit(row), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def wanted():
    """Every full model and thumbnail, plus the one simpler version of each model that needs it."""
    jobs = [("LICENSE-CC-BY-4.0.txt", None), ("README.md", None)]
    for row in catalogue():
        jobs.append((row["file"], row["pack_bytes"]))
        jobs.append((f"thumbs/{row['id']}.webp", None))
        pick = choose(row, "normal", lod=True)
        if pick and pick[0] != row["file"]:
            jobs.append((pick[0], pick[2]))
    return jobs


def cmd_sync(a):
    jobs = wanted()
    counts, failed = {}, []

    def one(job):
        return fetch(job[0], ROOT / job[0], job[1])

    with cf.ThreadPoolExecutor(a.workers) as pool:
        for i, (job, fut) in enumerate(zip(jobs, [pool.submit(one, j) for j in jobs]), 1):
            try:
                k = fut.result()
                counts[k] = counts.get(k, 0) + 1
            except RuntimeError as e:
                failed.append(str(e))
            if i % 200 == 0 or i == len(jobs):
                print(f"{i}/{len(jobs)} {counts} failed={len(failed)}", flush=True)
    for line in failed[:20]:
        print("FAILED", line)
    sys.exit(1 if failed else 0)


def cmd_check(_):
    jobs = wanted()
    bad = [rel for rel, want in jobs if not (ROOT / rel).exists() or (want is not None and (ROOT / rel).stat().st_size != want)]
    print(f"{len(jobs) - len(bad)}/{len(jobs)} files present with the right size")
    for rel in bad[:20]:
        print("MISSING", rel)
    sys.exit(1 if bad else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("--type")
    s.add_argument("--text")
    s.add_argument("--budget", choices=BUDGETS, default="normal")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--lod", action="store_true", help="include simplified versions (KTX2 textures)")
    s.set_defaults(func=cmd_search)
    p = sub.add_parser("pull")
    p.add_argument("id")
    p.add_argument("--dest", default=".")
    p.add_argument("--budget", choices=BUDGETS, default="normal")
    p.add_argument("--lod", action="store_true", help="allow a simplified version (KTX2 textures)")
    p.set_defaults(func=cmd_pull)
    y = sub.add_parser("sync")
    y.add_argument("--workers", type=int, default=6)
    y.set_defaults(func=cmd_sync)
    c = sub.add_parser("check")
    c.set_defaults(func=cmd_check)
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
