# Copilot repository instructions — Shared Horse Asset Hub

Read `AGENTS.md`, `assets/horses/registry.json`, and `docs/HORSE_AI_COLLABORATION.md` before any horse/3D racing work. The canonical horse branch is `feat/racing-horse-cc0-pipeline` until PR #13 merges. Two real, CC0-based V2.3 GLB horses already exist (`horse-brown`, `horse-white`) and are distributed via the `horses-v2.3.0` GitHub Release. They retain 50 bones, 13 animation clips, and PBR UV/texture maps; they are stylized, not high-realism racehorses.

For private-repo authorized AI workflows:
```bash
python3 scripts/horses/horse_assets.py list
python3 scripts/horses/horse_assets.py pull horse-brown --dest ./public/models
```

Create new horse variant under a unique asset ID and semver on a new branch; ensure license, true Blender/GLB validation, and PR review before adding to registry and publishing a new versioned Release. Do not commit heavy binary GLBs to ordinary Git history, invent source licenses, claim physics are validated, or overwrite existing release assets.
