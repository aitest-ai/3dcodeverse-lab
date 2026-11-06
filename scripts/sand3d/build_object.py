#!/usr/bin/env python3
"""Build a sand3d object into the package validate_glb.py expects.

  build_object.py --dataset simready --id simready-pail_screwTop_white_glossy_a01 --out outputs
  build_object.py --program scripts/sand3d/programs/my_thing.py --entry build --id my_thing --out outputs

Dataset programs are third-party Python and this runs them, so use it only in a throwaway environment
such as GitHub Actions. Needs Python 3.13, bpy 5.2, sand3d and pyarrow; bpy has no Linux ARM build.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def dataset_row(dataset, row_id, work):
    import pyarrow.parquet as pq

    repo = f"Sandflow/sand3d-{dataset}"
    listing = json.loads(subprocess.run(
        ["curl", "-4", "-sSfL", f"https://huggingface.co/api/datasets/{repo}/tree/main/data?recursive=true"],
        capture_output=True, text=True, check=True).stdout)
    for entry in listing:
        if entry["type"] != "file" or not entry["path"].endswith(".parquet"):
            continue
        local = work / Path(entry["path"]).name
        subprocess.run(["curl", "-4", "-sSfL", "--retry", "5", "-o", str(local),
                        f"https://huggingface.co/datasets/{repo}/resolve/main/{entry['path']}"], check=True)
        rows = pq.read_table(local, filters=[("id", "=", row_id)],
                             columns=["id", "program", "entry", "n_joints", "f_score", "family", "license",
                                      "source_license", "attribution", "sand3d_version"]).to_pylist()
        local.unlink()
        if rows:
            return rows[0]
    sys.exit(f"{row_id}: not found in {repo}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", help="simready, articraft, objaverse, cad or automate")
    ap.add_argument("--id", required=True)
    ap.add_argument("--program", help="a local sand3d program instead of a dataset row")
    ap.add_argument("--entry", help="function in --program that builds the object")
    ap.add_argument("--out", default="outputs")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    if a.program:
        row = {"id": a.id, "program": Path(a.program).read_text(encoding="utf-8"), "entry": a.entry,
               "license": "original", "attribution": "Original sand3d program in this repository."}
    elif a.dataset:
        row = dataset_row(a.dataset, a.id, out)
    else:
        sys.exit("give --dataset or --program")

    import bpy
    import sand3d as s3d

    bpy.ops.wm.read_factory_settings(use_empty=True)
    namespace = {}
    exec(row["program"], namespace)  # noqa: S102  see the module docstring
    if row.get("entry"):
        obj = namespace[row["entry"]]()
    else:
        roots = [o for o in bpy.context.scene.objects if o.parent is None]
        obj = roots[0] if len(roots) == 1 else s3d.group("object", *roots)

    asset_id = re.sub(r"[^A-Za-z0-9_-]+", "_", a.id)[:80]
    s3d.export(obj, str(out / f"{asset_id}.glb"))
    bpy.ops.wm.save_as_mainfile(filepath=str((out / f"{asset_id}.blend").resolve()))

    (out / "asset_manifest.json").write_text(json.dumps({
        "schema_version": 1,
        "asset_id": asset_id,
        "format": "glTF 2.0 GLB",
        "source": f"sand3d program ({a.dataset or 'original'})",
        "unit": "meter",
        "coordinate_system": "Y-up in the GLB",
        "model_file": f"{asset_id}.glb",
        "source_file": f"{asset_id}.blend",
        "clips": [],
        "min_animation_count": 0,
        "requirements": {"skins": False, "animated": False, "visual_review": True},
        "license_note": row["attribution"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "report.json").write_text(json.dumps({
        k: row.get(k) for k in ("id", "family", "n_joints", "f_score", "license", "source_license", "attribution", "sand3d_version")
    } | {"sand3d_used": s3d.__version__ if hasattr(s3d, "__version__") else None,
         "unverified": "f_score is the dataset's own measure. Look at the model before using it."},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {asset_id}")


if __name__ == "__main__":
    main()
