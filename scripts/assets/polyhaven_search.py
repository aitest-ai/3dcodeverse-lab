#!/usr/bin/env python3
"""Read the official Poly Haven public API (metadata only).

Deliberately does not automatically download, install or execute assets/scripts.
Any later import must keep the original URL, license and creator metadata.
"""
import argparse
import json
import urllib.request
from urllib.parse import urlsplit

API = "https://api.polyhaven.com/assets"
UA = "3dcodeverse-lab-asset-research/0.1 (+https://github.com/aitest-ai/3dcodeverse-lab)"


def search(query, kind="all", limit=10, opener=None):
    if not query.strip():
        raise ValueError("Query cannot be empty")
    if limit < 1 or limit > 30:
        raise ValueError("Choose 1 to 30 results")
    if kind not in ("all", "hdris", "textures", "models"):
        raise ValueError("Invalid asset type")
    api = API + (("?t=" + {"hdris": "hdris", "textures": "textures",
                            "models": "models"}[kind]) if kind != "all" else "")
    req = urllib.request.Request(api, headers={"User-Agent": UA, "Accept": "application/json"})
    fetch = opener or urllib.request.urlopen
    with fetch(req, timeout=25) as response:
        data = json.load(response)
    if not isinstance(data, dict):
        raise ValueError("Unexpected Poly Haven API response")
    words = query.casefold().split()
    matches = []
    for item_id, item in data.items():
        if not isinstance(item, dict):
            continue
        tags = item.get("tags") or []
        text = " ".join((item_id, str(item.get("name", "")),
                         str(item.get("category", "")), " ".join(map(str, tags)))).casefold()
        if all(word in text for word in words):
            matches.append({
                "id": item_id,
                "name": item.get("name", item_id),
                "category": item.get("category", ""),
                "source_url": "https://polyhaven.com/a/" + item_id,
                "license": "CC0 (Poly Haven asset library)",
                "source": "official Poly Haven API",
                "integration_status": "metadata_only_not_downloaded",
            })
        if len(matches) >= limit:
            break
    return matches


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("query", help="Search by English keywords, e.g. stone")
    p.add_argument("--kind", choices=("all", "hdris", "textures", "models"), default="all")
    p.add_argument("--limit", type=int, default=10)
    args = p.parse_args()
    print(json.dumps(search(args.query, args.kind, args.limit), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
