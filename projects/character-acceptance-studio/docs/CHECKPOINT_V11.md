# v0.11 handoff — 2026-11-05 Asia/Taipei

Base: v10 `b8f734b66c148be2b960203b3de63a096f74a931`, Draft PR #156. Isolated branch `feat/character-studio-v11-horse-world-walk-20261105`. No main edits, merges, official releases, production registry updates or website deployment.

Completed review candidate: append WalkWorld to two native horse colors, preserving all thirteen v10 clips and 50 joints. Exact old BIN/nodes/rest/meshes/materials/textures remain intact; new outer travel wrapper is explicit. Speed 0.8 m/s at inherited display calibration, stride 0.933333 m. Fixed world stance includes flat patch vertices, not just a selected bone tip. Native link lengths and bend half-plane preserved. Body pose lowers by 20 mm; all this is candidate motion, not art-approved gait.

Local available hardware: four CPU quota, 16 GiB, no GPU; actual Blender 5.2.3 LTS e13b728c6880 and Chromium SwiftShader. No paid accounts, model training or GPU claims. Current official Blender archive SHA is pinned in the v11 workflow.

Failures are retained as text experiment records, not registered models: original fore/hind slopes differ; constant orientation with unchanged body is unreachable near toe-off; smaller speed or earlier toe-off alone still fails. First browser trial also exposed double application of parent/child hoof translation; corrected by snapshotting both matrices before applying the common delta. Failed brown GLB `9d055f267c97e19bfa799066f0c388064c76ef646bc52bec1672c138ab9eaf02` must not be used. Final IDs/SHAs are only those in config-v11/horses.lock.json.

Browser 240 Hz × three accumulated world cycles: trial A maximum planned-stance patch drift 334.304835 mm, candidate B <1 mm (local ~0.000402 mm); lowest candidate hoof +2.999930 mm; seam <0.1 mm. Cold Blender × 6548 body vertices × five phases × two horses agrees with browser within 0.03 mm (local max 0.001679 mm). Re-export and rejection of unsupported geometry edits are tested. These are numerical tolerances, not physical precision or artistic approval.

130 browser frames cover front, side, back, front/back hoof close-ups, plus two real browser WebM recordings. No v11 offline render; no mobile hardware, Godot/game/map integration or human art review. CPU recording may drop frames. About 2.14% of cycle has one planned support hoof, 82.14% has two, 15.72% has three. This is not COM or force balance; single-support interval and 20mm posture change require next-stage gait work.

White shares the brown anatomical surface/weights after native vertex correspondence, with different primitive/material partitions and mane. It is not a second body shape. All new binaries are artifact-only, 90-day retention. Original source, v10 prerequisite, v11 mothers and original textures ship together in the source/runtime pair. Shipped script can rebuild without downloading an expired previous-stage artifact. Every GLB is pinned; Blender serialized files have artifact-specific hashes.

Next: review support ordering and body balance against suitable equine reference, address the short single-support interval without hiding sliding, then start/stop transitions. Keep these candidates out of official map templates until visual approval. Existing humanoid/garment work stays at its prior checkpoint; this horse stage does not mark those tasks complete.
