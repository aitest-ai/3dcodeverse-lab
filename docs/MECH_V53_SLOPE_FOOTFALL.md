# Mecha v5.3 — slope-aware ankle, stance-impact FX and launch/settle

The **working Windows candidate ZIP** contains the complete integrated runtime files: `mech-addon.js`, `mech-foot-ik.js`, `mech-ground-sampler.js`, `mech-footstep-fx.js`, `mech-motion.js`, `mech-glb-bridge.js`, tests, installer and the unchanged verified `mecha_v50.glb`. The repository's `examples/threejs/mech-contact-v53.js` is a pure **reference/acceptance kernel**, not a replacement for the integrated Three.js bridge.

User preference: retain the square hard-surface armor; no need for increasingly rounded armor.

### Integration order (Windows package)
- The allowlisted road sampler returns **both height and world-space normal** and safely rejects roofs, steep faces and distant heights. A v5.2 bug that excluded `street` as `tree` has been corrected.
- The existing v5.1 CCD solver keeps stance feet world-locked, and then rotates the **foot bone** toward a valid surface normal, capped at 0.24 rad. If the ground normal is unverified it leaves the animated ankle orientation intact.
- Moving foot transitions from swing→stance generate **debounced step events**; the first idle stance is suppressed. A capped pool of real Three.js torus rings expands at ground contact points, fades and cleans up. Sound is opt-in; a low-strength camera impulse only happens when enabled.
- v5.2 real-position inertia now adds visible **launch and settle** upper-body motion envelopes. The actual original person controller movement, collisions, weapon ray and destruction remain untouched.
- User controls: `B` GLB skin, `I` foot IK, `T` verified road raycaster, **`H` footfall FX**, F/Shift+F/G original weapons.

### Verification and honesty
- Local Windows integration candidate: **30 Node/Python tests passed** including v5.3 actual CCD slope/step event, safe ground normal, bounded shock rings, launch/settle, installer and prior F/G/destruction regression.
- The underlying v5.0 Blender model is unchanged, SHA-256 `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`. **There is no new Blender model or preview for v5.3.**
- The reference kernel gets its own separate GitHub Actions Node 22 acceptance check.
- **No actual Windows WebGPU playthrough, FPS, sound playback or Taipei-wide terrain mesh coverage verified.** Without a real certified road mesh, the model falls back to a flat controller ground plane. This is a visual postprocess, not a full dynamic physics solver.

Follow previous PR #18 before merging v5.3 into main.
