#!/usr/bin/env python3
"""Package the real D03/D06 gray GLBs and an offline, pinned review viewer.

Python standard library only; no npm/pip install, credentials, model editing,
replacement assets, or writes to the source outputs. The output must not exist.

  python3 -B scripts/character_studio/prepare_review.py \
      --outputs /path/to/0.1.0-gray.2 --out /path/to/new-review-folder

Optionally pass --vendor /path/to/three-0.187.0. Its seven original files must
match the hashes independently checked against the official npm archive below.
Without --vendor the script downloads that archive and checks its exact SRI.
Browser, artistic, animation and Android acceptance are separate review steps.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import math
import re
import shutil
import struct
import sys
import tarfile
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

THREE_VERSION = "0.187.0"
THREE_URL = "https://registry.npmjs.org/three/-/three-0.187.0.tgz"
THREE_SRI = "sha512-Qiu7R+Cmh8CstZsY1uJOSWnVlfo7ZtNLV7mF8Jltk3LB3AtDu9cRZlcnRKkAk8Y4z6KKw35z7Y7Urd7jWY8etA=="
THREE_ARCHIVE_BYTES = 4795351
THREE_ARCHIVE_SHA256 = "ff540832ded0cfe919764d24a3d88f3e2a05f23303f876423e4f893841e90728"
# Verified from the actual SRI-matching official archive on 2026-10-31.
# All seven original files were also byte-identical to the V110 handoff vendor.
THREE_FILES = {
    "build/three.module.js": (658900, "104f56145899722094556490d787aae0617cc2fc3382f31df02d724ea1aee341"),
    "build/three.core.js": (1474799, "613e370f76638fdef83926642bf256dc9615684922de1ce1f63a8583e5d78578"),
    "examples/jsm/loaders/GLTFLoader.js": (119861, "532ac726e120039acbcd6cf54328c57acbf7b438176afaa6951257126d11bff1"),
    "examples/jsm/utils/BufferGeometryUtils.js": (39153, "7bda2a8ba836b2bcf67cb938d4b9e1bb5d1b1bc616817103ed858c0b58296ce7"),
    "examples/jsm/utils/SkeletonUtils.js": (11535, "b1632a703206c3d830de9fcbe515696770d04b71a15ee6b50afa6d2c3298c86f"),
    "LICENSE": (1081, "8b378ebe60e2fe500158cb0ac71cb5e8b7d92953c2abcc63a0eb90499653b5bc"),
    "package.json": (3818, "87f2c99a8718e5fdd6f5e51427fde52c6075f2f698ddf8f7b4e162882df93940"),
}
VIEWER_FILES = ("index.html", "studio.js", "style.css", "README.md")
CHARACTERS = ("d03", "d06")
EVIDENCE_FILES = ("report.json", "measurements.json", "asset_manifest.json", "profile.json", "rig_semantics.json", "binary_inspection.json", "glb_inspection.json", "validation.json")
REPOSITORY = Path(__file__).resolve().parents[2]


class ReviewPackageError(RuntimeError):
    """A source or package constraint failed; no fallback is permitted."""


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def regular_file(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ReviewPackageError("Required original regular file is missing: " + str(path))
    return path


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as target:
        target.write(data)


def verify_vendor_file(name, data):
    expected_bytes, expected_hash = THREE_FILES[name]
    if len(data) != expected_bytes or hashlib.sha256(data).hexdigest() != expected_hash:
        raise ReviewPackageError("Three.js original file differs from the official lock: " + name)


class OfficialRegistryRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname != "registry.npmjs.org" or parsed.username or parsed.password:
            raise ReviewPackageError("Unexpected redirect from the pinned official npm registry")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def read_official_archive():
    """Fetch fixed original bytes, preserving normal TLS/CA/proxy settings."""
    print("THREE_DOWNLOAD", THREE_URL, flush=True)
    request = Request(THREE_URL, headers={"User-Agent": "3dcodeverse-character-studio-review/1.0"})
    with build_opener(OfficialRegistryRedirects()).open(request, timeout=60) as response:
        data = response.read(THREE_ARCHIVE_BYTES + 1)
    if len(data) != THREE_ARCHIVE_BYTES:
        raise ReviewPackageError("Official Three.js archive size differs from the lock")
    sri = "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode("ascii")
    if sri != THREE_SRI or hashlib.sha256(data).hexdigest() != THREE_ARCHIVE_SHA256:
        raise ReviewPackageError("Official Three.js archive failed SRI/SHA-256; no alternate download or fallback used")
    print("THREE_OFFICIAL_SRI_VERIFIED", len(data), flush=True)
    return data


def vendor_from_archive(data):
    """Read only seven exact regular members; never extract paths or links."""
    if len(data) != THREE_ARCHIVE_BYTES or "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode("ascii") != THREE_SRI:
        raise ReviewPackageError("Archive input is not the SRI-locked Three.js package")
    result = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = archive.getmembers()
        for name, (expected_bytes, _) in THREE_FILES.items():
            matching = [member for member in members if member.name == "package/" + name]
            if len(matching) != 1 or not matching[0].isfile() or matching[0].size != expected_bytes:
                raise ReviewPackageError("Missing, duplicate, linked or wrong-size official tar member: " + name)
            handle = archive.extractfile(matching[0])
            if handle is None:
                raise ReviewPackageError("Cannot read official tar member: " + name)
            with handle:
                original = handle.read(expected_bytes + 1)
            verify_vendor_file(name, original)
            result[name] = original
    return result


def load_vendor(folder=None):
    if folder is None:
        originals = vendor_from_archive(read_official_archive())
        mode = "official_archive_download"
    else:
        folder = Path(folder).resolve(strict=True)
        if not folder.is_dir():
            raise ReviewPackageError("--vendor must be the three-0.187.0 directory")
        originals = {}
        for name, (expected_bytes, _) in THREE_FILES.items():
            source = regular_file(folder / name)
            if not source.resolve().is_relative_to(folder) or source.stat().st_size != expected_bytes:
                raise ReviewPackageError("Existing Three.js source escapes its directory or has wrong size: " + name)
            data = source.read_bytes()
            verify_vendor_file(name, data)
            originals[name] = data
        mode = "existing_vendor_verified_against_official_file_hashes"
    package = json.loads(originals["package.json"])
    if package.get("name") != "three" or package.get("version") != THREE_VERSION or package.get("license") != "MIT":
        raise ReviewPackageError("Official Three.js package identity/license metadata differs")
    provenance = {
        "schema_version": 1, "package": "three", "version": THREE_VERSION, "license": "MIT",
        "source_url": THREE_URL, "integrity": THREE_SRI, "archive_sha256": THREE_ARCHIVE_SHA256,
        "archive_bytes": THREE_ARCHIVE_BYTES, "acquisition": mode,
        "archive_sri_verified_this_invocation": folder is None,
        "selected_original_file_hashes_verified_this_invocation": True,
        "lock_evidence": "Official SRI-matching npm archive independently retrieved 2026-10-31; all seven files matched the V110 handoff bytes.",
        "files": [{"path": name, "bytes": size, "sha256": digest} for name, (size, digest) in THREE_FILES.items()],
    }
    return originals, provenance


def model_source(outputs, cid):
    folder = outputs / cid
    report_path = regular_file(folder / "report.json")
    report_bytes = report_path.read_bytes()
    report = json.loads(report_bytes)
    asset_id, version = report.get("asset_id"), report.get("version")
    if not isinstance(asset_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", asset_id):
        raise ReviewPackageError(cid + " report has no valid original asset_id")
    if not isinstance(version, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]*", version):
        raise ReviewPackageError(cid + " report has no valid original version")
    height = report.get("measurements", {}).get("height_surface_m")
    if isinstance(height, bool) or not isinstance(height, (int, float)) or not math.isfinite(height) or height <= 0:
        raise ReviewPackageError(cid + " has no finite, positive measured surface height; design height is not a substitute")
    if report.get("source_blend_reopened") is not True or report.get("glb_reimported") is not True:
        raise ReviewPackageError(cid + " lacks the required saved-master/GLB roundtrip record")
    name = cid + ".glb"
    source = regular_file(folder / name)
    records = [row for row in report.get("files", []) if row.get("file") == name]
    if len(records) != 1:
        raise ReviewPackageError(cid + " report must contain exactly one original GLB hash/size record")
    size, digest = source.stat().st_size, file_sha256(source)
    if records[0].get("bytes") != size or records[0].get("sha256") != digest:
        raise ReviewPackageError(cid + " actual GLB differs from its source report; registry was not rewritten to hide a mismatch")
    with source.open("rb") as handle:
        header = handle.read(12)
    if len(header) != 12 or struct.unpack("<4sII", header) != (b"glTF", 2, size):
        raise ReviewPackageError(cid + " is not a complete glTF 2.0 binary file")
    registry = {
        "id": cid, "asset_id": asset_id,
        "label": report.get("profile", {}).get("label", cid.upper()),
        "file": name, "sha256": digest, "bytes": size, "height": height, "version": version,
        "height_source": "source report measurements.height_surface_m (metres); no viewer rescaling",
    }
    evidence = {"report.json": report_bytes}
    recorded = {row.get("file"): row for row in report.get("files", [])}
    for name in EVIDENCE_FILES[1:]:
        path = folder / name
        if not path.exists():
            continue
        data = regular_file(path).read_bytes()
        row = recorded.get(name)
        if row is not None and (row.get("bytes") != len(data) or row.get("sha256") != hashlib.sha256(data).hexdigest()):
            raise ReviewPackageError(cid + " evidence differs from its source report: " + name)
        if name == "measurements.json" and json.loads(data).get("height_surface_m") != height:
            raise ReviewPackageError(cid + " measured heights disagree between source files")
        if name == "asset_manifest.json":
            manifest = json.loads(data)
            if manifest.get("asset_id") != asset_id or manifest.get("version") != version or manifest.get("model_file") != cid + ".glb":
                raise ReviewPackageError(cid + " asset manifest identifies a different candidate")
        evidence[name] = data
    return source, registry, evidence


def delivery_summary(version, assets):
    rows = "\n".join(
        "| {id} | {asset_id} | {version} | {height:.9f} | {bytes} | `{sha256}` |".format(**asset)
        for asset in assets
    )
    return f"""# 人物工作室檢視器：交付摘要

此包為 **{version}** 的 D03／D06 實際 GLB 檢視器。模型直接從同版本產物複製，位元組、材質與幾何均未修改；沒有替代模型或自動 LOD。

## 執行

在本目錄執行 `python3 -m http.server 8765 --bind 127.0.0.1`，再開啟 <http://localhost:8765/>。不要直接雙擊 HTML。第一次準備此包以外，使用本機 HTTP 執行不需連線下載相依套件或建立憑證。

原始 `README.md` 已完整保留，包含操作、量測、失敗重試與實際瀏覽器驗收方式。

## 本次實際模型

| ID | 資產識別碼 | 版本 | 表面高度（m） | 位元組 | SHA-256 |
|---|---|---|---:|---:|---|
{rows}

高度來自與 GLB 雜湊綁定的原始 `report.json` 表面量測，並非設計身高。瀏覽器仍會重新量測實際 GLB；差異過大時會停止，不會拉高、縮小或換檔。

## 來源、授權與版本保存

四個檢視器原始檔從專案 `examples/character-studio/` 原樣複製，檔案雜湊記錄於 `PACKAGE_MANIFEST.json`。使用者專案程式保留於獨立 Git 分支／Draft PR，其既有授權不因本次打包改變。

Three.js 固定使用 **0.187.0** 官方 npm 原始檔；`vendor/three-0.187.0/LICENSE` 保留 MIT 授權，`PROVENANCE.json` 記錄官方 SHA-512 SRI、每檔 SHA-256，以及本次是官方下載或既有檔案核對。所有七個檔案均通過固定雜湊核對，沒有使用 CDN。

`models/evidence/` 保留這次模型的原始報告與可用的來源證據；來源報告描述建模時的狀態，不會因製作檢視器而被改寫。GLB 與 Blender 母檔應依 **{version}** 分包封存，地圖依資產識別碼、版本與 SHA-256 取用。本檢視器包不取代可編輯 `.blend`、參數母檔、完整材質與原始來源包；這些大檔應隨同版本主交付保存，不應只保留有期限的 Actions artifact。

## 驗證範圍與限制

本腳本僅驗證來源版本、檔案大小、雜湊與封裝完整性。`SHA256SUMS.txt` 涵蓋包內檔案（不含清單本身）。打包成功不代表美術或遊戲驗收通過，也不代表已執行瀏覽器或 Android 真機測試。

此階段為無髮、中性站姿的 closed-mouth 灰模候選。牙齒、舌頭、服裝、鞋子、表情、待機／走路／轉身／坐下，以及騎車與騎馬適配仍需逐項完成與驗收。Blender 離線渲染、瀏覽器實測、完整遊戲與 Android 真機測試須分別記錄；軟體 GL 的幀率不能直接推論手機能力。
"""


def prepare_review(outputs, out, vendor=None):
    outputs = Path(outputs).resolve(strict=True)
    requested_out = Path(out).absolute()
    if requested_out.exists() or requested_out.is_symlink():
        raise ReviewPackageError("Output already exists; choose a new versioned review directory: " + str(requested_out))
    out = requested_out.resolve()
    if not outputs.is_dir():
        raise ReviewPackageError("--outputs must contain the d03 and d06 build directories")
    originals = {name: regular_file(REPOSITORY / "examples/character-studio" / name).read_bytes() for name in VIEWER_FILES}
    models = [model_source(outputs, cid) for cid in CHARACTERS]
    versions = {model[1]["version"] for model in models}
    if len(versions) != 1:
        raise ReviewPackageError("D03 and D06 belong to different candidate versions; choose one complete version")
    assets = [model[1] for model in models]
    if len({asset["asset_id"] for asset in assets}) != len(assets):
        raise ReviewPackageError("The two characters unexpectedly share the same asset_id")
    version = versions.pop()
    vendor_files, vendor_provenance = load_vendor(vendor)
    # Exclusive creation is the final gate; even an empty existing directory is
    # refused. No input file or earlier review folder is replaced or removed.
    out.mkdir(parents=True, exist_ok=False)
    for name, data in originals.items():
        write_new(out / name, data)
    vendor_out = out / "vendor" / ("three-" + THREE_VERSION)
    for name, data in vendor_files.items():
        write_new(vendor_out / name, data)
    write_new(vendor_out / "PROVENANCE.json", json_bytes(vendor_provenance))
    for source, asset, evidence in models:
        target = out / "models" / asset["file"]
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as original, target.open("xb") as copied:
            shutil.copyfileobj(original, copied, 1 << 20)
        if target.stat().st_size != asset["bytes"] or file_sha256(target) != asset["sha256"]:
            raise ReviewPackageError("GLB changed during copying; partial output must not be published: " + asset["id"])
        for name, data in evidence.items():
            write_new(out / "models/evidence" / asset["id"] / name, data)
    registry = {"schema_version": 1, "version": version, "assets": assets}
    write_new(out / "models/registry.json", json_bytes(registry))
    write_new(out / "README_交付摘要.md", delivery_summary(version, assets).encode("utf-8"))
    files = [{"file": path.relative_to(out).as_posix(), "bytes": path.stat().st_size, "sha256": file_sha256(path)}
             for path in sorted(out.rglob("*")) if path.is_file()]
    manifest = {
        "schema_version": 1, "status": "REVIEW_PACKAGE_PREPARED_NOT_CHARACTER_APPROVAL", "version": version,
        "assets": assets, "model_bytes_unchanged": True, "original_viewer_files": list(VIEWER_FILES),
        "three_source": vendor_provenance, "files": files,
        "tests_performed_by_this_script": {"file_integrity": True, "blender_render": False, "browser": False, "android_device": False},
        "art_approved": False, "game_ready": False,
        "scope": "Stage 01 closed-mouth gray viewer only. Retain editable masters and original sources in the same version's separate full archive.",
    }
    write_new(out / "PACKAGE_MANIFEST.json", json_bytes(manifest))
    sums = "".join(file_sha256(path) + "  " + path.relative_to(out).as_posix() + "\n"
                   for path in sorted(out.rglob("*")) if path.is_file())
    write_new(out / "SHA256SUMS.txt", sums.encode("utf-8"))
    result = {"status": manifest["status"], "out": str(out), "version": version, "assets": assets,
              "vendor_acquisition": vendor_provenance["acquisition"], "art_approved": False}
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, required=True, help="Build artifact root containing d03/ and d06/")
    parser.add_argument("--out", type=Path, required=True, help="New review directory; existing paths are never overwritten")
    parser.add_argument("--vendor", type=Path, help="Optional three-0.187.0 directory; all seven original file hashes are checked")
    args = parser.parse_args(argv)
    try:
        prepare_review(args.outputs, args.out, args.vendor)
        return 0
    except (ReviewPackageError, OSError, URLError, ValueError, TypeError, tarfile.TarError) as exc:
        print("PREPARE_REVIEW_FAILED: " + str(exc), file=sys.stderr)
        print("No alternate model/vendor was substituted. Preserve existing outputs and retry with correct sources and a new output directory.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
