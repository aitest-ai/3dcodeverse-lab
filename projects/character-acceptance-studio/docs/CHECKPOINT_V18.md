# V18 handoff

Isolated branch from V17 PR166. Selected scope: local MToon outline-width mask on two native body types. Geometry, topology, rig and all 7 animations unchanged. Source pins: INPUTS_V18.json.

Cuff subdivision was REJECTED after new intersections in 6 of 7 Vivi clips. Vita full collision regression incomplete. Rejected algorithms in scripts/v18/experimental; numeric evidence in CUFF_REJECTED_V18.json. Not part of the build or catalog.

Mask removes the dark backface-outline artifact, not geometric folds. Skin self-intersections, shoulder folds, original cuffs remain. Next work: actual shoulder/garment topology and weight repairs with per-pose tests and human art review, then more body types/animals.

Fresh validation: BLENDER_BIN=... NODE_PATH=... python scripts/run_validation_v18.py. Final canonical assets and pins are taken from the actual CI artifact. Never overwrite fixed asset versions or silently use local preflight mothers with different hashes.
