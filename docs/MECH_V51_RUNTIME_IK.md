# Taipei Mech v5.1 — planted-foot CCD in Three.js

This branch demonstrates the **runtime animation follow-up** to [v5.0](https://github.com/aitest-ai/3dcodeverse-lab/pull/16). The Blender GLB geometry itself remains v5.0; no new v5.1 geometry or four-view render has been falsely claimed.

## Runtime flow
1. Keep the validated v5.0 15-bone, 6-clip hard-surface mech GLB and `weapon_socket.R`.
2. Update `AnimationMixer` normally with `Run` / `Idle`.
3. Use world-coordinate stance targets; alternate left and right stance per run phase.
4. Run bounded three-pass CCD on thigh/shin joints (quaternion deltas translated through each parent world transform), then counter-rotate the ankle to preserve foot orientation.
5. Use terrain sample function `groundHeightAt(x,z)` when available; otherwise fall back to player/controller ground plane.
6. Only after IK, refresh mechanical hydraulics. Combat, city collision and projectile origin remain authoritative and unaffected.

## Scope and validation
The Windows v5.1 test bundle includes production `mech-foot-ik.js`, modified `mech-glb-bridge.js`, `mech-addon.js` (I to toggle IK, B for old model), installer, actual validated v5.0 Blender assets, and tests. The adjacent `examples/threejs/planted-foot-ccd-v51.js` is a **minimal reusable reference module**, not an exact byte-for-byte copy of the Windows UI-enabled version.

Local tests: **23 Node/Python suites passed**, including a three-dimensional transform test that moves the rig, checks that leg joints really rotate and world-space foot drift decreases; enables/disables, teleports and disposes cleanly. This does **not** constitute Windows WebGPU visual/performance validation.

## Limitations
This is two-link post-animation CCD and world-space stance locking, **not full-body inverse-dynamics physics** or guaranteed planted foot contact on steps. Without a real height sampler it uses a single controller ground plane. Contact targets can release when a move exceeds the leg's reach; knee hyperextension needs a future explicit biomechanical joint-angle constraint. The original v5.0 288-frame Blender root-height QA remains valid but is separate from this browser runtime IK.

Do not automatically merge into main or infer AAA artistic acceptance. Prior PR dependency is v5.0 (#16).
