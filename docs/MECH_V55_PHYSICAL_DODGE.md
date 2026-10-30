# Taipei Mecha v5.5 — Physical sidestep candidate (not yet integrated into Windows production)

## Motivation

v5.4 V / Shift+V was a visual-only side sway (no game movement). This candidate makes directional sidesteps move the authoritative game controller *only through a collision resolver*, without altering any v5.0 GLB or Taipei OSM assets.

## Files

- `examples/threejs/mech-dodge-v55.js` — pure, dependency-free movement kernel; also includes flat-AABB test-only swept collision reference
- `tests/mecha/v55-physical-dodge.mjs` — deterministic tests, safety and frame-rate checks
- Standalone offline interactive test-range candidate is delivered separately, because this repo is an asset & verification lab rather than the original Taipei game repo.

## Usage in the existing Taipei game

1. After controller input is known but **before** visual animation / foot IK, create a `createMechDodgeV55()` instance.
2. On V / Shift+V, call `begin(1/-1)`. If true, also call existing `createMechCombatMotion().dodge(side)` to preserve the v5.4 torso tilt.
3. Each frame, call `update(dt, { position:{x:controller.x,z:controller.z}, right:{x:worldRight.x,z:worldRight.z}, resolveMovement })` and copy its output position into the authoritative controller **before** camera and foot IK update. Right must be unit-length in world coordinates.
4. `resolveMovement(from,to,{radius,mode})` must return the highest valid collision-safe point on the original segment. Use the real OSM physics world / bounds. Flat AABB demo resolver is not production-grade, not slope-aware, and not suitable for multilevel geometry.
5. The host still owns enemy attacks, weapon damage and position persistence. This module never grants invincibility or modifies damage, never overrides collision, and never moves if the collision resolver is missing.
6. Do not double-apply displacement through old v5.4 cosmetic V behavior.

## QA

- Run `node tests/mecha/v55-physical-dodge.mjs`. Tests cover 30/60/120 FPS equivalent displacement, wall obstruction, world bounds, stamina, cooldown, malicious resolver, no silent i-frames, and large-frame clamp.
- Still required: obtain latest Windows v5.4 ZIP and integrate at authoritative movement layer; run real Taipei OSM geometry and GLB leg contact checks; then Windows GPU/FPS manual review.
- No Blender output or new GLB was generated. Visual test range is schematic and should **not** be confused with genuine Taipei OSM city.

## Dependency

This candidate is branched from v5.4 PR #21 and should be merged only after its base lineage is ready.
