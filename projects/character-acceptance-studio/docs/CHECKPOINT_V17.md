# V17 continuation checkpoint

Goal: variable native Run elbows and bounded local skin/sleeve correction on Vivi and Vita. Branch `feat/character-studio-v17-run-arms-20261106`, based on immutable V16 commit `1afe2d74bd4551eae26c800d2d46590b830fc69a`. No main edits, merges, releases or map/site changes.

Candidates: Vivi 0.5.0 (68–92 degrees), Vita 0.4.0 (68–80). Two forearm rotation tracks and one Run-only local corrective morph. Upper-arm skirt-clearance, hands, lower body/root and six other clips retained. Shared semantics/phase formula, per-body native axes and separate amplitudes. Do not promote failed larger-flexion or garment-only trials.

Immutable source inputs are in `inputs-v17/library-v16`; output models/mothers/profiles in `library-v17`. Build starts from pinned *actual CI* V16 mothers, not a locally generated substitute. Evidence and delivery packages are regenerated in `evidence-v17` and `deliveries-v17`, excluded from Git. See README_V17 for startup, exact export commands and artifact-expiry fallback.

Local checks: cold Blender 5.2.3; preserved native base geometry/UV/weights/actions; morph reexport; guarded editable export; actual Chromium/SwiftShader 120 Hz motion/surface checks. Two candidates' six other clip surfaces are unchanged after Run. Forearm angle varies without moving feet/root. Browser shoulder/elbow cameras and diagnostic corrective switch are included; switch restoration has its own regression test.

Visual limitation: Vivi has a dark triangular shoulder/armpit fold, more exposed in some new poses, and angular sleeve cuffs. No visual art pass is claimed.

Known failure: original source arm skin self crossings remain (maximum 9 Vivi / 3 Vita in bounded 120 Hz Run samples). New arm skin pairs, sleeve/skin pairs, sleeve self pairs, hand self and hand/skirt pairs are zero in the checked samples. This is not solid containment, cloth thickness, full-body, all-motion or artistic approval. Larger Vita angle and excessive skin-displacement trials were rejected. Original .vroid files unavailable.

Verification categories and measured data: `evidence-v17/acceptance-summary.json`, `browser-crossings.json`, `corrective-toggle.json`, `export-guard.json`, `blender-cold.json`, `delivery-smoke.json`. View actual frames/video via `evidence-v17/index.html`. All `art_approved=false`, `game_ready=false`; phone hardware, human art, Godot and maps untested this version.

Environment: 4 CPU quota, 16 GiB memory, no GPU, Blender 5.2.3 LTS, Playwright 1.57 + Chromium CPU rendering. No model training or paid inference. An environment interruption was recovered without overwriting sources.

Next dependency during delivery: finish current local capture/ZIP verification, run branch CI, download and verify that exact remote artifact before updating Draft PR. After delivery, next art task is shoulder/armpit source folds and broader clothing silhouette review across views; keep current version fixed while exploring new candidates.
