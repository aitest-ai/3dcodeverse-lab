# v5.2 runtime inertia and guarded ground sampling

This is the next **Three.js-only** runtime upgrade following [v5.1 CCD IK](https://github.com/aitest-ai/3dcodeverse-lab/pull/17). It does NOT create a new Blender GLB. The existing validated `mecha_v50.glb` is reused unchanged (SHA-256 `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`).

## Runtime integration

- After `AnimationMixer.update(dt)`, feed `createMechMotion().update({dt, position:controller.position, heading:controller.heading, speed:controller.speed})` and **add** `pitch`/`roll` to *spine bone rotations only*. This is inertial visual acting, not a changed movement controller or an altered cannon/weapon ray.
- For opt-in terrain contact, call `createMechGroundSampler({THREE,scene,getReferenceHeight:()=>controller.position.y})` once and supply its `sample(x,z)` as `createMechFootIK(..., groundHeightAt:(x,z)=>sampler.sample(x,z))`.
- Evaluate IK **after** mixer and chassis visual inertia; then update dynamic hydraulics. The existing six-clip animation and 15-bone skeleton still apply.
- T toggles walkable-mesh sampler; I toggles IK; B toggles procedural/GLB skin; original F/Shift+F/G weapons and city-destruction logic unchanged. UI displays detected mesh count and actual hit counts.

## Terrain honesty / safety boundary

OSM road polylines are **not** elevation meshes. Sample only explicit walkable meshes or allowlisted road/street/sidewalk/ground/terrain mesh names and categories; reject buildings, roofs and water, slopes >~44°, and heights >.55m from authoritative pedestrian controller. When no safe real scene geometry is available, sampler returns `NaN`, so existing CCD uses the controller ground plane. There is **no claim of a verified city-wide Taiwan terrain DEM**; a runtime scene mapping and Windows WebGPU visual test are required before promoting this to real-height support.

## Verified candidate package

- Separate 34.4 MB Windows candidate ZIP `臺北機甲戰鬥_v5.2_加速煞停慣性與安全地形取樣測試包.zip` generated; includes source, real v5.0 Blender GLB, fallback models and test suite.
- **26 local Node/Python tests pass**, including acceleration/turn/braking, teleport reset, real scene normal/height rejection, opt-out, CCD, weapons, building damage, install and model fallback.
- ZIP CRC integrity and unchanged v5.0 GLB SHA-256 confirmed.
- Tests are unit/mock tests, **NOT** full gameplay verification or a real terrain-data proof. No new Blender render has been claimed.

## Known limitations

No ground reaction force; no slope-aware sole orientation, IK joint-angle clamps, per-road terrain availability guarantee or actual Windows WebGPU FPS test. Conservative fallbacks are intentional.
