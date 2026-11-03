# Taipei Mecha v8.4: author the real Blender V50 cannon tip, without touching original gameplay

Base: v8.3 Draft PR #125. Existing 15-bone Blender v5.0 player, v6.3 enemies, OSM city, weapons, rubble and 101 defense mission are **not modified**.

## Confirmed V50 source facts

The original `scripts/blender5/mecha_v50.py` defines `weapon_socket.R` (a bone pivot), `PrimaryCannon_energy_bore` (actual exposed glowing bore) and `PrimaryCannon_outer_barrel` as separate, skinned geometric components. The bore projects along local negative Blender Y in its rest pose. Bone pivot != gun barrel exit. Do not infer a tip position from 2D PNG.

## Deliverable

- `scripts/blender5/muzzle_geometry_v84.py`: estimates the true tube end-ring centers using current **actual mesh vertex data** and validates bore/outer-barrel alignment, axis, radius, barrel length and a conservative 8 mm extension. No Blender dependency for math unit tests.
- `scripts/blender5/author_muzzle_anchor_v84.py`: Blender 5 script, starts with an existing authentic `mecha_v50.blend` and writes a **separate new candidate** `mecha_v84_muzzle_anchor.blend` and `mecha_v84_muzzle_anchor.glb`. It adds one `MuzzleTip_R` non-deforming Empty parented to existing `weapon_socket.R`, keeps 15 bones and original meshes, captures original Blender SHA, and checks GLB export rather than claiming success if the node disappears.
- `scripts/blender5/verify_glb_v84.py`: validates unique marker, ancestor being original weapon socket, original cannon meshes, a skin with exactly 15 joints, and at least six animation clips.
- `examples/threejs/mech-muzzle-anchor-v84.js`: reads **actually exported** GLB node after animation/mixer update. Safe preview gate rejects >0.3 meter origin gap and >18° angle. It does **not** alter the `combat.fire` ray or damage.
- `tests/mecha/v84-*.{mjs,py}` and `.github/workflows/mecha-v84-muzzle.yml`: independent synthetic geometry, node ancestry and JS transform tests.

## Current verification / limits

Blender executable and the original `.blend` are not available in this execution environment. **No real edited GLB was rendered, exported or visually approved.** GitHub CI only verifies source syntax and Blender-free geometry, GLB mock structure and runtime logic. The full 3D game/WebGPU, real weapon alignment, six authored clips inside a new asset, human pose checks and FPS are still pending. The original Windows ZIP does not get overwritten.

A separate downloadable v8.4 authoring kit in the conversation contains a Windows candidate build command, full source scripts and offline verification report. Keep this PR **Draft**, base on the v8.3 branch (not `main`), do not deploy the live public website or merge older PRs.