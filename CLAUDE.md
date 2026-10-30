# Claude project instructions — 3DCodeVerse Lab

Read [`AGENTS.md`](AGENTS.md) before every 3D task. For sharing/reusing scene maps with other AI, follow [`docs/SCENE_HUB.md`](docs/SCENE_HUB.md) and [`skills/scene-exchange/SKILL.md`](skills/scene-exchange/SKILL.md).

Use `python3 scripts/scene_hub.py list`, `inspect`, `verify`, `pull`, `stage` and (after explicit approval on a feature branch) `push`. Never claim repository writes, GPU inference or Blender/WebGL validations that were not actually executed. Do not put weights, secrets or unlicensed assets in Git. The HY-World 2.0 bridge is currently PR #20 until merged into main.