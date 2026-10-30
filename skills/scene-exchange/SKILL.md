---
name: scene-exchange
description: Discover, validate, pull, stage and publish reusable 3D scene/map assets between AI agents using Git, per-scene manifests, and checksums.
---

# Scene Exchange — 3DCodeVerse Lab

When a task requires creating, reusing or sharing 3D maps, scenes, PLY, GLB, 3DGS or SPZ files:

1. Read repository `AGENTS.md` and [Scene Hub workflow](../../docs/SCENE_HUB.md) first.
2. Run `python3 scripts/scene_hub.py list` and inspect the entry, source, license, status.
3. For retrieval: `python3 scripts/scene_hub.py pull <scene-id> --output <target>`. Never overwrite existing targets. Hash success is not quality certification.
4. For a new scene: create a separate Git feature branch, run `stage` with source and license, then `verify --all`. Submit `push <scene-id> --confirm` only after the user has authorized repository publishing; create a PR and do not merge without review.
5. Keep triangles, point clouds and Gaussian splats distinct. Require Blender/Three.js/Spark visual acceptance and collision checks separately.
6. HY-World 2.0 bridge and mountain-river demonstration are in draft PR #20 until merged. The example is procedural and **not HY-World inference output**.
7. If this AI has no configured Git credentials, offer a patch, Fork or PR instead of claiming the repository was changed.

This SKILL.md is a discoverable repository instruction, not an automatically installed integration in any AI platform.
