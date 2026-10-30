#!/usr/bin/env python3
"""Validate actual Blender-generated full-frame grounding report."""
import json,sys
from pathlib import Path
folder=Path(sys.argv[1] if len(sys.argv)>1 else "outputs")
doc=json.loads((folder/"fullframe_gait_qa.json").read_text())
records=doc["samples"]
assert doc["sample_count"]==288==len(records), "Expected 6 clips * 48 frames"
assert {x["clip"] for x in records}=={"Idle","Run","Punch","Dodge","Fire","Hit"}
assert all({x["frame"] for x in records if x["clip"]==clip}==set(range(1,49)) for clip in doc["clip_names"])
assert all(x["clearance"]>=-.009 for x in records), "Ground penetration at an unsampled frame"
assert doc["min_clearance_m"]>=-.009
assert "not runtime planted-foot IK" in doc["limitation"]
manifest=json.loads((folder/"asset_manifest.json").read_text())
assert manifest["model_file"]=="mecha_v50.glb"
report=json.loads((folder/"report.json").read_text())
assert len(report["full_frame_grounding"])==288
print("V50_FULLFRAME_GROUND_PASS",{"frames":len(records),"minimum":doc["min_clearance_m"],"max_root_adjust":doc["max_abs_root_adjust_m"]})
