# Sources, rights and attribution

## Game and character design

Harbor Walk environment, interface, quest, character styling, satchel, scarf and pocket accessories are newly authored for this project. They do not reproduce KochiGame characters, setting, story, UI, music, or code. Character anatomy, hair, base clothing and locomotion are adapted from **Quaternius CC0 1.0** Standard packs, rather than wholly original topology or motion capture.

- https://quaternius.itch.io/universal-base-characters
- https://quaternius.itch.io/universal-animation-library
- https://quaternius.itch.io/modular-character-outfits-fantasy

Original pack license texts are retained in `assets/licenses/`; source download archive sizes and SHA-256 are in `assets/source-lock.json`. Only the free Standard files were downloaded using the publisher's normal download flow. No Source/Premium content was acquired. CC0 permits adaptation and redistribution. The `.blend` is our editable imported/adapted production master; it is not the publisher's paid source `.blend`.

## User's existing pipeline

https://github.com/aitest-ai/3dcodeverse-lab, especially `docs/AI_ASSET_PIPELINE.md`, `examples/threejs/load-animated-glb.js`, and `scripts/blender5/aviator_human.py` at commit `172efe078e5791c181b701f9c96f99b68051a9c7`, informed the named-animation, rebind and validation workflow. `scripts/validate_glb.py` is the user's existing validator reused with the user's authorization; no upstream license is invented. No existing character/model files were overwritten or imported from an unreviewed branch.

## Runtime dependencies

Three.js (MIT), Rapier / @dimforge/rapier3d-compat (Apache-2.0), Vite (MIT), TypeScript (Apache-2.0), tsx (MIT). Exact resolved versions are in package-lock.json. Their package license files are distributed by npm when dependencies are installed. Default typography uses locally installed system fonts; there are no external image, font or telemetry requests at runtime.

## Analysis tools

REA 6.8.0: https://github.com/morluto/rea (MIT; third-party components retain their licenses). retoc v0.1.5: https://github.com/trumank/retoc (MIT). Neither tool is bundled into the game. The retoc Linux release archive was SHA-256 checked against GitHub's release asset digest (`3c309a4aea0c6d0a5c6ee31b1d1b32768eb86ac67e3a1890d677eabe6ce26b36`). No Oodle proprietary library was downloaded, run or redistributed. Failed compressed-chunk extraction is documented.

The reference game's original assets and executable remain local analysis inputs and are excluded from deliverables and GitHub.
