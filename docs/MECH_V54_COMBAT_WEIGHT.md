# Taipei Mech v5.4 — combat recoil and visual hit reaction

The original v5.0 **square hard-surface mech** remains byte-identical. No new Blender render or 3D model is claimed. The independently delivered **Windows v5.4 candidate ZIP** contains the full integrated production addon, original authentic Slop Taipei city overlay installer and backward-compatible GLB assets.

## Production integration (inside the ZIP)

- New `mech-combat-motion.js` creates bounded, critically damped visual impulses for `light`, `charged`, `heavy`, and `hit`. These have visibly different torso and right-arm recoil strengths.
- `mech-glb-bridge.js`: after `AnimationMixer.update()`, combine combat offsets with existing v5.2 locomotion momentum on spine/head/right arm; then run v5.3 foot IK and hydraulic updates.
- `mech-addon.js`: fire event calls `react(charged ? 'charged' : heavy ? 'heavy' : 'light')` only after a successful weapon event. Hit reaction is based on **HP decreasing**, not a status string which can repeat across hits.
- `V` for right / `Shift+V` for left lateral pose. **ONLY COSMETIC**: no displacement, invulnerability, speed advantage or damage reduction. Cooldown/interrupt protection, UI status and counts.
- Original real OSM Taipei scenery, actual combat raycast, building damage, GLB fallback, F/Shift+F/G, v5.1 CCD foot IK and v5.3 footstep impacts remain unchanged.

## Verification

**33 local Node/Python integration and asset suites passed**, including a mock glTF scene where torso and right forearm bones are genuinely rotated after firing, target-direction visual dodge and repeat-dodge cooldown, original installer idempotence and GLB hashes. ZIP passes CRC checks, 194 entries, 34,419,068 bytes (SHA256 `1335430013b81af480e16b5019275b2e82e1b6e702cb4348783b92b7b8d1b330`).

This repository's `examples/threejs/mech-combat-v54.js` is the portable tested core matching the Windows ZIP's production implementation. The fully integrated addon and asset package are in the delivered ZIP, **not duplicated as a standalone Slop Taipei repository here**.

## Limits

Windows WebGPU actual visual playback, frame time/FPS, recoil animation foot clipping and genuine hardware controller input have **not** been manually accepted. The V move does not dodge real attacks. No new 3D asset was generated; all old Blender evidence applies to the unchanged model.
