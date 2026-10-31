#!/usr/bin/env python3
"""Reproduce the isolated, pinned Blender/MPFB stage-01 gray review runtime.

Python 3.12+ standard library only. No pip, account login, credential creation,
HOME changes, system installs, or downloads of the existing character ZIPs.
The seven original eye/license files are the complete first-stage asset scope.
Teeth, tongue, expressions, clothing, motion, and game validation are unfinished.

  python3 -B scripts/character_studio/bootstrap.py --runtime runtime
  python3 -B scripts/character_studio/bootstrap.py --check-locks

Use a dedicated empty runtime on its first run. Reuse is allowed only for
hash-verified downloads and directories carrying this bootstrap's own stamp.
The script writes runtime/bootstrap_state.json for subsequent build commands.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

BLENDER_VERSION = "5.2.3"
BLENDER_DIR = "blender-5.2.3-linux-x64"
BLENDER_URL = "https://download.blender.org/release/Blender5.2/blender-5.2.3-linux-x64.tar.xz"
BLENDER_SHA256 = "78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec"
MPFB_COMMIT = "6ff1eb358f6c1959ced77e79e6dd2406d9a71f49"
MPFB_VERSION = "2.0.18"
MPFB_DIR = "mpfb2-" + MPFB_COMMIT
MPFB_URL = "https://codeload.github.com/makehumancommunity/mpfb2/zip/" + MPFB_COMMIT
MPFB_SHA256 = "066f83f98add0e11065296a5ffc10291f28677240008891becb20cc9a2b22766"
MAKEHUMAN_REPOSITORY = "makehumancommunity/makehuman"
MAKEHUMAN_COMMIT = "a8bc2d54ff0ac92e78ff71431b1023eda42bf482"
ASSET_BASE_URL = "https://raw.githubusercontent.com/" + MAKEHUMAN_REPOSITORY + "/" + MAKEHUMAN_COMMIT + "/"

# Exact records from the independently retrieved official_minimal_assets manifest
# (2026-10-31). Original bytes and license texts are preserved, never relabeled.
_ASSET_RECORDS = [
    ("makehuman/data/eyes/high-poly/high-poly.mhclo", 72490,
     "b183cfe37120ab726f9b3f2ea6cd3a64c44ce7b4bd91a77c841cf70c04f83a0d", "22bc5f77f398c59088804f7f4c9bb0e39d38661d"),
    ("makehuman/data/eyes/high-poly/high-poly.obj", 100882,
     "da2493215b708a344c33dc72f2a9a5b8fa985dcc5a70ad3b208995cf871da8e1", "01562a9caf4dca9ebb1fd5c24db083c17e724330"),
    ("makehuman/data/eyes/materials/brown.mhmat", 1247,
     "4abad93ce50541c08127721e77bce035640c9f16bed16cd0f5524b1cd5908465", "4935d95e41a628307ed01278908c0fe48220b031"),
    ("makehuman/data/eyes/materials/brown_eye.png", 610817,
     "4659691c7295ad6206c78b003e5fd0e5f91dcd53032fa914a229bb48cabe424b", "bda1b4b0d94f4b7b34ca4f58063eab04f05cd2e7"),
    ("makehuman/data/litspheres/skinmat_eye.png", 52077,
     "3046b4d2c938b3d7d6a5aa2a4d217ded728fe5d3a89e7b74e2e2cee0038de987", "f2ce22b598f801366d3a3e784a1b3d80c2d0a627"),
    ("LICENSE.ASSETS.md", 6962,
     "f6089cba01cb570a24712b41ab8a586ccd3cc5ef53dc266ca50b95c288956d2c", "f3ede1fc3318f8d794e2cb51924186c62f02f71a"),
    ("LICENSE.md", 3598,
     "edd99571ca62698f78c943fd4fffb159a413c315fa0d4819d3cec5cadaf8b4f1", "5d1a49d31ebdaa46b06c52eae2c005c678a63ffa"),
]
ASSET_LOCK = {
    "schema_version": 1,
    "source_repository": MAKEHUMAN_REPOSITORY,
    "source_commit": MAKEHUMAN_COMMIT,
    "asset_root_relative": "makehuman/data",
    "asset_name": "HighPolyEyes", "mhclo_uuid": "2c12f43b-1303-432c-b7ce-d78346baf2e6", "basemesh": "hm08",
    "license_evidence_files": ["LICENSE.ASSETS.md", "LICENSE.md"],
    "core_graphical_asset_license": "CC0-1.0",
    "scope": "Official original eyes and their material dependencies only; no teeth or tongue. Closed-mouth gray review only.",
    "files": [{"path": p, "source_url": ASSET_BASE_URL + p, "size_bytes": n, "sha256": s, "git_blob_sha1": b}
              for p, n, s, b in _ASSET_RECORDS],
}


class BootstrapError(RuntimeError):
    pass


def sha256(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def _relative(path):
    """Validate an archive/manifest path before joining it to a destination."""
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        raise BootstrapError("Invalid archive/asset path")
    value = PurePosixPath(path)
    if value.is_absolute() or any(part in ("..", "") for part in value.parts) or re.match(r"^[A-Za-z]:", path):
        raise BootstrapError("Unsafe archive/asset path: " + path)
    if not value.parts or value == PurePosixPath("."):
        raise BootstrapError("Empty archive/asset path")
    return value


def _target(root, relative):
    p = _relative(relative)
    target = root.joinpath(*p.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise BootstrapError("Destination escapes its runtime root: " + relative)
    return target


def _assert_url(url):
    parsed = urlparse(url)
    allowed = {"download.blender.org", "codeload.github.com", "raw.githubusercontent.com"}
    if parsed.scheme != "https" or parsed.hostname not in allowed or parsed.username or parsed.password:
        raise BootstrapError("Expected an HTTPS official source URL")


class _HTTPSRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlparse(newurl).scheme != "https":
            raise BootstrapError("Refusing an HTTPS-to-HTTP redirect")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download_verified(url, expected_sha256, destination, expected_size=None):
    """TLS/proxy defaults are retained; hash drift never triggers a fallback."""
    _assert_url(url)
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise BootstrapError("Invalid pinned SHA-256")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if destination.is_symlink() or not destination.is_file():
            raise BootstrapError("Cached download is not a regular file: " + str(destination))
        if sha256(destination) != expected_sha256 or (expected_size is not None and destination.stat().st_size != expected_size):
            raise BootstrapError("Cached bytes differ from the lock; preserve them and choose a new runtime directory: " + str(destination))
        print("VERIFIED_CACHE", destination.name, flush=True)
        return destination
    print("DOWNLOAD_PINNED", destination.name, flush=True)
    opener = build_opener(_HTTPSRedirects())  # Keeps standard HTTPS CA and proxy handling.
    request = Request(url, headers={"User-Agent": "3dcodeverse-character-studio-bootstrap/1.0"})
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=destination.name + ".part-", delete=False) as output:
            temporary = Path(output.name)
            digest = hashlib.sha256()
            count, started = 0, time.monotonic()
            with opener.open(request, timeout=90) as response:
                while True:
                    chunk = response.read(1 << 20)
                    if not chunk:
                        break
                    if time.monotonic() - started > 1200:
                        raise BootstrapError("Download exceeded twenty minutes")
                    output.write(chunk); digest.update(chunk); count += len(chunk)
            output.flush(); os.fsync(output.fileno())
        if digest.hexdigest() != expected_sha256:
            raise BootstrapError("Downloaded SHA-256 differs from the locked source: " + destination.name)
        if expected_size is not None and count != expected_size:
            raise BootstrapError("Downloaded size differs from the locked source: " + destination.name)
        # A racing invocation must never replace a completed cache item.
        if destination.exists():
            if sha256(destination) != expected_sha256:
                raise BootstrapError("Concurrent download produced different bytes")
        else:
            os.link(temporary, destination)
        print("DOWNLOAD_VERIFIED", destination.name, count, flush=True)
        return destination
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def extract_verified(archive, runtime, expected_root, expected_sha256, archive_kind):
    """Extract a verified archive atomically into its own top-level directory."""
    archive, runtime = Path(archive), Path(runtime)
    if sha256(archive) != expected_sha256:
        raise BootstrapError("Archive changed after download verification")
    destination = _target(runtime, expected_root)
    stamp = runtime / ("." + expected_root + ".source.json")
    expected = {"sha256": expected_sha256, "root": expected_root, "archive_kind": archive_kind}
    if destination.exists():
        if destination.is_symlink() or not stamp.is_file() or json.loads(stamp.read_text()) != expected:
            raise BootstrapError("Existing extracted directory is not owned by this pinned bootstrap; use a fresh runtime: " + str(destination))
        return destination
    temp = Path(tempfile.mkdtemp(prefix=".extract-", dir=runtime))
    try:
        if archive_kind == "tar.xz":
            if not hasattr(tarfile, "data_filter"):
                raise BootstrapError("Safe Blender extraction requires Python 3.12+")
            with tarfile.open(archive, "r:xz") as package:
                members = package.getmembers()
                for member in members:
                    parts = _relative(member.name).parts
                    if parts[0] != expected_root:
                        raise BootstrapError("Unexpected tar top-level directory")
                    if not (member.isdir() or member.isfile() or member.issym() or member.islnk()):
                        raise BootstrapError("Devices, sockets and FIFOs are forbidden in the runtime archive")
                # Python's data filter rejects path traversal, escaping links,
                # special files and unsafe ownership/mode metadata.
                package.extractall(temp, members=members, filter="data")
        elif archive_kind == "zip":
            with zipfile.ZipFile(archive) as package:
                bad = package.testzip()
                if bad is not None:
                    raise BootstrapError("ZIP CRC failure: " + bad)
                seen = set()
                for member in package.infolist():
                    relative = _relative(member.filename)
                    if relative.parts[0] != expected_root or str(relative) in seen:
                        raise BootstrapError("Unexpected ZIP root or duplicate member")
                    seen.add(str(relative))
                    mode = member.external_attr >> 16
                    if stat.S_ISLNK(mode) or stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                        raise BootstrapError("ZIP links and special files are not accepted")
                    target = _target(temp, str(relative))
                    if member.is_dir():
                        target.mkdir(parents=True, exist_ok=True)
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with package.open(member) as source, target.open("xb") as output:
                        shutil.copyfileobj(source, output, 1 << 20)
                    target.chmod(0o755 if mode & 0o111 else 0o644)
        else:
            raise BootstrapError("Unknown archive kind")
        source = temp / expected_root
        if not source.is_dir() or source.is_symlink() or destination.exists():
            raise BootstrapError("Extraction destination changed or is invalid")
        source.rename(destination)
        stamp.write_text(json.dumps(expected, sort_keys=True) + "\n")
        print("EXTRACTED_PINNED", expected_root, flush=True)
    finally:
        shutil.rmtree(temp, ignore_errors=True)
    return destination


def prepare_assets(runtime):
    root = runtime / "official_minimal_assets"
    root.mkdir(parents=True, exist_ok=True)
    verified = []
    for record in ASSET_LOCK["files"]:
        target = _target(root, record["path"])
        download_verified(record["source_url"], record["sha256"], target, record["size_bytes"])
        data = target.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        if blob != record["git_blob_sha1"]:
            raise BootstrapError("Official pinned Git blob differs: " + record["path"])
        verified.append({**record, "pinned_git_blob_verified": True})
    manifest = {**ASSET_LOCK, "retrieved_at_utc": utc_now(), "files": verified,
                "verification": {"all_seven_git_blobs_match_pinned_commit": True, "source_files_unchanged": True,
                                 "texture_pixels_decoded_in_this_bootstrap": False, "blender_fit_test_performed": False},
                "fitting_note": "Fit original eyes to full HM08 before helper removal. This stage is closed-mouth; teeth/tongue and expression adaptation are unfinished."}
    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        current = json.loads(manifest_path.read_text())
        old = {(f["path"], f["sha256"], f["size_bytes"], f["git_blob_sha1"]) for f in current.get("files", [])}
        new = {(f["path"], f["sha256"], f["size_bytes"], f["git_blob_sha1"]) for f in verified}
        if current.get("source_commit") != MAKEHUMAN_COMMIT or old != new:
            raise BootstrapError("Existing source manifest differs; no overwrite performed")
    else:
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return root


def run_command(command, env):
    print("RUNTIME_COMMAND", json.dumps([str(x) for x in command]), flush=True)
    subprocess.run([str(x) for x in command], env=env, check=True)


def check_locks():
    """Pure checks, no downloads or filesystem writes."""
    for digest in (BLENDER_SHA256, MPFB_SHA256):
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise BootstrapError("Invalid runtime hash")
    _assert_url(BLENDER_URL); _assert_url(MPFB_URL)
    for record in ASSET_LOCK["files"]:
        _relative(record["path"]); _assert_url(record["source_url"])
        if not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]) or not re.fullmatch(r"[0-9a-f]{40}", record["git_blob_sha1"]):
            raise BootstrapError("Invalid asset hash")
    for bad in ("../escape", "/absolute", "C:/absolute", "dir/../../escape", "dir\\escape"):
        try:
            _relative(bad)
        except BootstrapError:
            continue
        raise BootstrapError("Unsafe path regression: " + bad)
    return {"status": "LOCKS_AND_PATH_GUARDS_PASS", "asset_files": len(ASSET_LOCK["files"]),
            "asset_bytes": sum(r["size_bytes"] for r in ASSET_LOCK["files"]), "network_used": False}


def bootstrap(runtime, github_env=None):
    check_locks()
    if sys.version_info < (3, 12):
        raise BootstrapError("Use Python 3.12+ for safe tar extraction")
    runtime = Path(runtime).resolve()
    if any(c in str(runtime) for c in ("\n", "\r")):
        raise BootstrapError("Runtime path cannot contain newlines")
    runtime.mkdir(parents=True, exist_ok=True)
    downloads = runtime / "downloads"
    blender_archive = download_verified(BLENDER_URL, BLENDER_SHA256, downloads / (BLENDER_DIR + ".tar.xz"))
    mpfb_archive = download_verified(MPFB_URL, MPFB_SHA256, downloads / (MPFB_DIR + ".zip"))
    blender_root = extract_verified(blender_archive, runtime, BLENDER_DIR, BLENDER_SHA256, "tar.xz")
    mpfb_root = extract_verified(mpfb_archive, runtime, MPFB_DIR, MPFB_SHA256, "zip")
    blender = blender_root / "blender"
    if not blender.is_file() or not os.access(blender, os.X_OK):
        raise BootstrapError("Pinned Blender executable is missing")
    source = mpfb_root / "src/mpfb"
    manifest = source / "blender_manifest.toml"
    if not manifest.is_file() or not re.search(r'^version\s*=\s*"2\.0\.18"', manifest.read_text(), re.M):
        raise BootstrapError("Pinned MPFB manifest version differs")
    assets = prepare_assets(runtime)
    config, extensions, repository = runtime / "blender_user_config", runtime / "blender_user_extensions", runtime / "mpfb_extensions"
    config.mkdir(exist_ok=True); extensions.mkdir(exist_ok=True); repository.mkdir(exist_ok=True)
    env = os.environ.copy()
    env.update(BLENDER_USER_CONFIG=str(config), BLENDER_USER_EXTENSIONS=str(extensions))
    # Never assign HOME, USERPROFILE, CODEX_HOME, or replace proxy/CA settings.
    state_path = runtime / "bootstrap_state.json"
    pins = {"blender_version": BLENDER_VERSION, "blender_archive_sha256": BLENDER_SHA256,
            "mpfb_commit": MPFB_COMMIT, "mpfb_archive_sha256": MPFB_SHA256, "makehuman_commit": MAKEHUMAN_COMMIT}
    previous = json.loads(state_path.read_text()) if state_path.exists() else None
    installed_manifest = repository / "mpfb/blender_manifest.toml"
    ready = previous is not None and previous.get("pins") == pins and installed_manifest.is_file() and sha256(installed_manifest) == sha256(manifest)
    if previous is not None and not ready:
        raise BootstrapError("Existing bootstrap state/installed manifest differs; use a fresh runtime")
    extension_zip = runtime / "mpfb.zip"
    if not ready:
        if extension_zip.exists():
            raise BootstrapError("Untracked built extension ZIP already exists; use a fresh runtime")
        run_command([blender, "-b", "--command", "extension", "build", "--source-dir", source, "--output-filepath", extension_zip], env)
        run_command([blender, "-b", "--command", "extension", "repo-add", "local_mpfb", "--directory", repository], env)
        run_command([blender, "-b", "--command", "extension", "install-file", "--repo", "local_mpfb", "--enable", extension_zip], env)
    # Test the actual isolated config/add-on, not just the existence of a ZIP.
    expression = (
        "import bpy; "
        "assert bpy.app.version[:3] == (5, 2, 3), bpy.app.version_string; "
        "module = 'bl_ext.local_mpfb.mpfb'; "
        "bpy.ops.preferences.addon_enable(module=module) if module not in bpy.context.preferences.addons else None; "
        "assert module in bpy.context.preferences.addons, 'Pinned MPFB failed to enable'; "
        "print('PINNED_MPFB_RUNTIME_READY', bpy.app.version_string)"
    )
    run_command([blender, "-b", "--python-exit-code", "1", "--python-expr", expression], env)
    exported = {"BLENDER_BIN": str(blender), "BLENDER_USER_CONFIG": str(config),
                "BLENDER_USER_EXTENSIONS": str(extensions), "CHARACTER_STUDIO_ASSETS": str(assets)}
    state = {"schema_version": 1, "status": "RUNTIME_READY_NOT_CHARACTER_APPROVAL", "pins": pins,
             "created_at_utc": previous.get("created_at_utc", utc_now()) if previous else utc_now(),
             "verified_at_utc": utc_now(), "environment": exported,
             "extension_zip_sha256": sha256(extension_zip), "source_manifest": str(assets / "manifest.json"),
             "asset_lock": ASSET_LOCK, "art_approved": False, "game_ready": False,
             "scope": "Stage 01 closed-mouth gray identity only; no teeth/tongue, facial expressions, wardrobe, animations or device testing."}
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    if github_env is not None:
        with Path(github_env).open("a", encoding="utf-8") as handle:
            for key, value in exported.items():
                handle.write(key + "=" + value + "\n")
    print("BOOTSTRAP_READY", json.dumps({"state": str(state_path), "environment": exported, "art_approved": False}), flush=True)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, default=Path("runtime"))
    parser.add_argument("--github-env", type=Path, help="Append only task-specific runtime paths to the runner's GITHUB_ENV file")
    parser.add_argument("--check-locks", action="store_true")
    args = parser.parse_args()
    try:
        if args.check_locks:
            print(json.dumps(check_locks(), indent=2))
        else:
            bootstrap(args.runtime, args.github_env)
        return 0
    except (BootstrapError, OSError, ValueError, subprocess.CalledProcessError, tarfile.TarError, zipfile.BadZipFile) as exc:
        print("BOOTSTRAP_FAILED", str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
