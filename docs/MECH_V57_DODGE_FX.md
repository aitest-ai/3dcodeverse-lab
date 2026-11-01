# Taipei Mech v5.7 — Dodge gait, IK release and layered weapon FX

## Current lineage

This **Draft PR** starts from `feat/mecha-v55-physical-dodge-20261030` and does not merge other open branches into `main`. The actual complete Windows integrated v5.7 overlay is delivered separately as a new ZIP and is **not** a source checkout or standalone copy of the Slop Taipei project. The portable deterministic function `examples/threejs/mech-fx-v57.js` matches the overlay's FX timing functions.

## Changes in the separately delivered Windows ZIP

1. The **unchanged** v5.0 square hard-surface 15-bone / 6-clip GLB supplies its authored `Mecha_Dodge` clip. Remove `root.position`, `root.quaternion` and `root.scale` tracks only from the playing Dodge clip to avoid double-applying displacement. Keep actual lower limb rotations. Evaluate one action over 0.36 seconds, with easing matching the v5.5 physical sidestep. The real OSM controller, not AnimationMixer, owns movement.
2. On a real (non-blocked) dash begin, release planted feet by resetting CCD IK; do not apply stance locking during the authored sidestep. After its completion, reset and delay relocking by 0.12 seconds to let the feet settle. Blocked dash must not play moving feet in place.
3. Original v5.4 torso recoil, real hit reactions, v5.5 stamina/dodge timing, v5.6 OSM wall/traffic/water/deck collision and real destructive facades remain unchanged.
4. `F` bright laser: 3 animated perpendicular energy fronts, with continuously fading core. `Shift+F` uses 5 fronts and stronger core. `G` keeps a travelling projectile with damage only on impact and adds two upright pressure rings alongside existing ground shockwaves, ember particles and smoke. Cap beam groups to 14 and pulse groups to 64. Dispose geometries/materials on reset/expiration.
5. Overlay installer preflights modules/GLB files before modifying any Slop Taipei files. Newly downloaded base-city source is pinned to `shwang1979/slop-taipei` revision `1d70708fc92a088b779c8c0e22677adb64966a1b` (2026-10-24); previous complete local city installs are preserved.

## Verification

- In the separate actual Windows overlay ZIP, `python tests/run_all.py`: **38 PASS**, including new tests for GLB root-motion masking and IK state, beam-ring progression, blast shell cleanup, repeat overlay installation, and unchanged original GLB SHA-256 `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`.
- GitHub Actions here checks the **portable pure FX kernel only**; it cannot be treated as Windows rendering or Slop Taipei integration acceptance.
- **Not tested in production**: Windows WebGPU/browser manual gameplay, side-step near actual Taipei OSM buildings, feet/arms penetration visual, rendered quality of blast/beam, FPS and GPU memory.
- No new Blender model was generated. The v5.0 file is unchanged; do not replace it with a simpler block model.

## Handoff

Other AIs should first read `AGENTS.md`, `docs/AI_ASSET_PIPELINE.md`, plus `docs/MECH_V55_PHYSICAL_DODGE.md` before editing. Treat this as a **reference and QA source**: the full game overlay remains an independently versioned ZIP and must be read and patched directly for actual integration. Do not auto-merge these branches, overwrite old assets, change a public URL, or claim browser validation from headless Node tests.
