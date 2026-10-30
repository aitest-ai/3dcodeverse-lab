#!/usr/bin/env python3
"""Read/validate curated open 3D resources; does NOT install untrusted code.

Examples:
 python3 scripts/assets/tool_catalog.py --category animal
 python3 scripts/assets/tool_catalog.py --category human --stage base_mesh
 python3 scripts/assets/tool_catalog.py --category animal --gpu cpu
 python3 scripts/assets/tool_catalog.py --validate
"""
import argparse
import json
import pathlib
from urllib.parse import urlsplit

CATALOG = pathlib.Path(__file__).resolve().parents[2] / "resources" / "open_3d_tool_catalog.json"
CATEGORIES = {"human", "animal", "mecha", "prop", "environment"}
STAGES = {"reference", "base_mesh", "assets", "generation", "retopology",
          "pbr", "lighting", "rigging", "skinning", "physics_reference",
          "optimization", "validation"}
AUTOMATION = {"gpu_external", "gpu_external_license_review",
              "blender_extension_manual_until_tested", "manual_review",
              "external_authoring", "api_metadata_ready", "reference_only",
              "license_check_per_asset", "cpu_optional"}


def load_catalog(path=CATALOG):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def validate(data):
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported schema_version")
    items = data.get("items")
    if not isinstance(items, list) or len(items) < 10:
        raise ValueError("At least ten curated resources are expected")
    seen = set()
    for item in items:
        required = ("id", "name", "role", "targets", "stages", "url",
                    "license", "license_scope", "hardware", "automation",
                    "status", "notes")
        if any(k not in item or not item[k] for k in required):
            raise ValueError("Missing metadata in resource " + repr(item))
        rid = item["id"]
        if rid in seen:
            raise ValueError("Duplicate resource ID: " + rid)
        seen.add(rid)
        url = urlsplit(item["url"])
        if url.scheme != "https" or not url.netloc or url.username or url.password:
            raise ValueError("Unsafe/non-HTTPS URL: " + item["url"])
        if not set(item["targets"]) <= CATEGORIES:
            raise ValueError("Unknown target for " + rid)
        if not set(item["stages"]) <= STAGES:
            raise ValueError("Unknown stage for " + rid)
        if item["automation"] not in AUTOMATION:
            raise ValueError("Unknown automation mode for " + rid)
        if item["status"] not in ("research_verified", "installed_tested"):
            raise ValueError("Never mark tools installed unless tested")
    return len(items)


def select(items, category=None, stage=None, gpu="all"):
    found = []
    for item in items:
        if category and category not in item["targets"]:
            continue
        if stage and stage not in item["stages"]:
            continue
        if gpu == "cpu" and item["automation"].startswith("gpu_"):
            continue
        if gpu == "gpu" and not item["automation"].startswith("gpu_"):
            continue
        found.append(item)
    return found


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--validate", action="store_true", help="Check metadata integrity")
    p.add_argument("--category", choices=sorted(CATEGORIES))
    p.add_argument("--stage", choices=sorted(STAGES))
    p.add_argument("--gpu", choices=("all", "cpu", "gpu"), default="all")
    p.add_argument("--json", action="store_true", help="Machine-readable filtered entries")
    opts = p.parse_args(argv)
    data = load_catalog()
    total = validate(data)
    if opts.validate:
        print(f"PASS: {total} metadata-only resource entries; none auto-installed.")
        return
    results = select(data["items"], opts.category, opts.stage, opts.gpu)
    if opts.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(f"{len(results)} of {total} candidates (not installed, not quality-tested here)")
        for x in results:
            print(f"\n[{x['id']}] {x['name']} | {x['role']} | {x['license']}")
            print("Stages:", ", ".join(x["stages"]))
            print("Compute:", x["hardware"], "| Mode:", x["automation"])
            print("URL:", x["url"])
            print("Caution:", x["license_scope"])
            print("Quality:", x["notes"])


if __name__ == "__main__":
    main()
