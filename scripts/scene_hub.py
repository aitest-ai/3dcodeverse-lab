#!/usr/bin/env python3
"""Safe Git-backed 3D scene exchange for AI agents. Python >=3.10, no pip deps."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

DEFAULT_HUB = Path(__file__).resolve().parents[1]
ID = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
GITHUB_URL = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?$")
SAFE_REF = re.compile(r"^[A-Za-z0-9_./-]{1,128}$")
ALLOWED_SUFFIX = {".ply", ".glb", ".spz", ".blend", ".png", ".jpg", ".jpeg", ".json", ".mp4"}
MAX_COMMITTED = 20 * 1024 * 1024

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def valid_id(value: str) -> str:
    if not ID.fullmatch(value) or value in {"main", "master", "assets", "catalog"}:
        raise ValueError("Scene IDs must be lowercase letters/numbers/hyphens (3-64 chars), not reserved words")
    return value

def safe_relative(hub: Path, name: str) -> Path:
    rel = Path(name)
    if rel.is_absolute() or not rel.parts or ".." in rel.parts or "\\" in name:
        raise ValueError("Unsafe path: " + name)
    path = (hub / rel).resolve()
    if not path.is_relative_to(hub.resolve()):
        raise ValueError("File escapes repository: " + name)
    return path

def read_scene(hub: Path, scene_id: str, verify: bool = False) -> dict:
    valid_id(scene_id)
    catalog = hub / "scenes" / "catalog" / (scene_id + ".json")
    if not catalog.is_file():
        raise FileNotFoundError("Scene not found: " + scene_id)
    manifest = json.loads(catalog.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("scene_id") != scene_id:
        raise ValueError("Invalid schema/id")
    if not isinstance(manifest.get("title"), str) or not manifest["title"].strip():
        raise ValueError("Missing title")
    if not isinstance(manifest.get("license"), str) or not manifest["license"].strip():
        raise ValueError("Missing license")
    if manifest.get("review_status") not in ("unverified", "structure_pass", "visual_reviewed"):
        raise ValueError("Invalid review status")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("A scene needs at least one asset")
    seen = set()
    for obj in files:
        if not isinstance(obj, dict) or not isinstance(obj.get("path"), str):
            raise ValueError("Bad asset entry")
        name = obj["path"]
        if not name.startswith(f"scenes/assets/{scene_id}/") or name in seen:
            raise ValueError("Asset path outside scene directory or duplicate")
        seen.add(name)
        path = safe_relative(hub, name)
        sha = obj.get("sha256")
        if not isinstance(sha, str) or re.fullmatch("[0-9a-f]{64}", sha) is None:
            raise ValueError("Missing/invalid SHA-256")
        if type(obj.get("bytes")) is not int or obj["bytes"] <= 0:
            raise ValueError("Missing file size")
        if verify:
            if not path.is_file() or path.stat().st_size != obj["bytes"]:
                raise ValueError("Missing or wrong length: " + name)
            if digest(path) != sha:
                raise ValueError("SHA-256 mismatch: " + name)
    return manifest

@contextmanager
def hub_checkout(repo: str | None, ref: str):
    if repo is None:
        yield DEFAULT_HUB
    elif Path(repo).is_dir():
        yield Path(repo).resolve()
    else:
        if not GITHUB_URL.fullmatch(repo):
            raise ValueError("Only local directory or HTTPS github.com repo is allowed")
        if not SAFE_REF.fullmatch(ref) or ".." in ref or ref.startswith("-"):
            raise ValueError("Invalid ref")
        with tempfile.TemporaryDirectory(prefix="scene-hub-") as temp:
            subprocess.run(["git", "clone", "--quiet", "--depth", "1",
                            "--single-branch", "--branch", ref, repo, temp],
                           check=True, timeout=180)
            yield Path(temp)

def cmd_list(args):
    with hub_checkout(args.repo, args.ref) as hub:
        for path in sorted((hub / "scenes/catalog").glob("*.json")):
            entry = read_scene(hub, path.stem)
            print(f"{entry['scene_id']:<26} {entry['review_status']:<16} {entry['title']}")

def cmd_inspect(args):
    with hub_checkout(args.repo, args.ref) as hub:
        print(json.dumps(read_scene(hub, args.scene_id, verify=args.verify),
                         ensure_ascii=False, indent=2))

def cmd_verify(args):
    with hub_checkout(args.repo, args.ref) as hub:
        files = (sorted((hub / "scenes/catalog").glob("*.json")) if args.all else
                 [hub / "scenes/catalog" / (valid_id(args.scene_id) + ".json")])
        if not files:
            raise ValueError("No scene manifests")
        for item in files:
            entry = read_scene(hub, item.stem, verify=True)
            print(f"PASS {entry['scene_id']}: {len(entry['files'])} SHA-256 checked files")

def cmd_pull(args):
    scene_id = valid_id(args.scene_id)
    root = Path(args.output).resolve()
    target = root / scene_id
    if target.exists():
        raise FileExistsError("Output exists, won't overwrite: " + str(target))
    with hub_checkout(args.repo, args.ref) as hub:
        entry = read_scene(hub, scene_id, verify=True)
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root, prefix=".scene-tmp-") as temp:
            dest = Path(temp)
            for item in entry["files"]:
                src = safe_relative(hub, item["path"])
                out = dest / src.name
                if out.exists():
                    raise ValueError("Duplicate asset basenames")
                shutil.copyfile(src, out)
                if digest(out) != item["sha256"]:
                    raise ValueError("File changed during copy")
            (dest / "scene_manifest.json").write_text(
                json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            dest.rename(target)
    print(f"Pulled {scene_id} -> {target} (file hashes verified; visual review remains separate)")

def cmd_stage(args):
    hub = Path(args.hub).resolve() if args.hub else DEFAULT_HUB
    scene_id = valid_id(args.scene_id)
    if not args.title.strip() or not args.source.strip() or not args.license.strip():
        raise ValueError("Title, source and license are required")
    catalog = hub / "scenes/catalog" / (scene_id + ".json")
    folder = hub / "scenes/assets" / scene_id
    if catalog.exists() or folder.exists():
        raise FileExistsError("Scene already registered; do not overwrite another AI's assets")
    seen = set()
    sources = []
    for s in args.files:
        original = Path(s)
        if original.is_symlink():
            raise ValueError("Symlink sources are not allowed")
        path = original.resolve(strict=True)
        if not path.is_file() or path.suffix.lower() not in ALLOWED_SUFFIX:
            raise ValueError("Not a supported regular asset: " + str(path))
        if path.name in seen or not 0 < path.stat().st_size <= MAX_COMMITTED:
            raise ValueError("Duplicate, empty or >20MiB asset: " + path.name)
        sources.append(path); seen.add(path.name)
    catalog.parent.mkdir(parents=True, exist_ok=True)
    folder.parent.mkdir(parents=True, exist_ok=True)
    folder.mkdir()
    assets = []
    try:
        for path in sources:
            out = folder / path.name
            shutil.copyfile(path, out)
            assets.append({"path": f"scenes/assets/{scene_id}/{path.name}",
                           "sha256": digest(out), "bytes": out.stat().st_size})
        record = {"schema_version": 1, "scene_id": scene_id, "title": args.title,
                  "description": args.description, "asset_kind": args.kind,
                  "review_status": "unverified", "source": args.source,
                  "license": args.license,
                  "created_at": dt.datetime.now(dt.timezone.utc).date().isoformat(),
                  "files": assets, "preview_url": args.preview_url,
                  "notes": "New upload, no automatic visual/physics/licensing certification."}
        catalog.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
        read_scene(hub, scene_id, verify=True)
    except BaseException:
        shutil.rmtree(folder, ignore_errors=True)
        catalog.unlink(missing_ok=True)
        raise
    print(f"Staged: {scene_id}; review and verify, then push on a feature branch.")

def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True, timeout=180).stdout.strip()

def cmd_push(args):
    if not args.confirm:
        raise ValueError("Use --confirm after reviewing scene/license")
    root = Path(args.hub).resolve() if args.hub else DEFAULT_HUB
    scene_id = valid_id(args.scene_id)
    read_scene(root, scene_id, verify=True)
    branch = git(root, "branch", "--show-current")
    if not branch or branch in ("main", "master") or branch.startswith("release/"):
        raise ValueError("Never push on main/master/release or detached HEAD")
    if git(root, "diff", "--cached", "--name-only"):
        raise ValueError("Index contains unrelated staged files")
    paths = (f"scenes/catalog/{scene_id}.json", f"scenes/assets/{scene_id}")
    git(root, "add", "--", *paths)
    staged = git(root, "diff", "--cached", "--name-only").splitlines()
    if not staged or any(p != paths[0] and not p.startswith(paths[1] + "/") for p in staged):
        raise ValueError("Nothing to commit, or unexpected staged files")
    git(root, "commit", "-m", "assets(scene): add " + scene_id)
    git(root, "push", "--set-upstream", "origin", branch)
    print("Pushed feature branch " + branch + "; create a PR for review.")

def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in [("list", cmd_list), ("inspect", cmd_inspect),
                       ("verify", cmd_verify), ("pull", cmd_pull)]:
        p = sub.add_parser(name)
        p.add_argument("--repo", help="Local folder or HTTPS GitHub repository URL")
        p.add_argument("--ref", default="main")
        if name in ("inspect", "pull"):
            p.add_argument("scene_id")
        if name == "inspect":
            p.add_argument("--verify", action="store_true")
        if name == "verify":
            group = p.add_mutually_exclusive_group(required=True)
            group.add_argument("--all", action="store_true")
            group.add_argument("--scene-id")
        if name == "pull":
            p.add_argument("--output", required=True)
        p.set_defaults(func=func)
    p = sub.add_parser("stage")
    p.add_argument("scene_id")
    p.add_argument("--hub")
    p.add_argument("--title", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--license", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--kind", required=True,
                   choices=["triangle_mesh", "gaussian_splats", "point_cloud", "mixed_scene", "other"])
    p.add_argument("--file", dest="files", action="append", required=True)
    p.add_argument("--preview-url")
    p.set_defaults(func=cmd_stage)
    p = sub.add_parser("push")
    p.add_argument("scene_id")
    p.add_argument("--hub")
    p.add_argument("--confirm", action="store_true")
    p.set_defaults(func=cmd_push)
    return parser

def main():
    try:
        args = build_parser().parse_args()
        args.func(args)
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired,
            json.JSONDecodeError) as exc:
        print("SCENE_HUB_ERROR:", exc, file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
