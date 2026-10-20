---
name: hokkaido-3d-pbr
description: Upgrade official 3DCodeVerse GLB wooden bear with real Blender PBR color/normal/roughness/AO maps, UV QA and tested glTF export.
---
# 3DCodeVerse → Blender 5.2 → UV/PBR → GLB

Use this skill when the user requests higher-quality wood/stone/organic material textures for an existing 3DCodeVerse generated GLB. **This is code-and-mesh processing, not image generation.**

## Installed reference skills (MIT)
- [EL4CTEO PBR](../vendor/EL4CTEO/blender-pbr-materials/SKILL.md)
- [EL4CTEO UV](../vendor/EL4CTEO/blender-retopology-uv/SKILL.md)
- [EL4CTEO Texture Baking](../vendor/EL4CTEO/blender-texture-baking/SKILL.md)
- [RobLe3 UV Texturing](../vendor/RobLe3/blender-uv-texturing/SKILL.md)

These are vendored **reference documents**, not full installation of external Blender add-ons. Their vendor scripts may have independent dependencies; do not execute them without review.

## Repeatable workflow
1. Read `models/hokkaido-bear/latest/hokkaido_bear_official_harness.glb`, which was built with official 3DCodeVerse Harness.
2. Audit active UV layer, 0–1 coordinate coverage, object names, separate fish parts, and current glTF materials.
3. Generate 2048px surface maps with `scripts/pbr_refine_bear.py`:
   - `wood_basecolor.png`, sRGB albedo.
   - `wood_normal.png`, tangent OpenGL normal, Non-Color.
   - `wood_orm.png`, R=AO, G=roughness, B=metalness, Non-Color.
4. Apply each map through exporter-recognized Blender Principled BSDF inputs, export new GLB, *keep original geometry*.
5. Validate GLB embedded PNGs and JSON material links (baseColorTexture, normalTexture, metallicRoughnessTexture, occlusionTexture).
6. Render actual 3D artifact from different angles. If appearance is still wrong, identify whether bottleneck is UV seams, material scale, or actual geometric anatomy; DO NOT hide mistakes with a generated picture.

## Execute
Use [Hokkaido bear PBR material lab](../../.github/workflows/pbr-refine-bear.yml) via GitHub Actions.
Or with Blender 5.2.2:
```bash
blender -b -t 4 --python scripts/pbr_refine_bear.py -- \
  --source models/hokkaido-bear/latest/hokkaido_bear_official_harness.glb \
  --output output --res 2048
```

Outputs are published under `models/hokkaido-bear/pbr-latest`; preserve the original `latest` version. Report all failures, never label a workflow as successful before checking the artifact and the GitHub run.

## Caveats
A normal map simulates *light and shadow*, not silhouette or real cuts. A low-stretch UV layout is necessary before progressing to 4K. The pilot UV check covers valid UV coordinates, **not full texel-density uniformity or overlap**; a more sophisticated UV unwrap/bake still needs separate validation. The PBR texture is intentionally synthetic and may remain less convincing than a carefully scanned physical wooden sculpture. This does not activate official 3DCodeVerse AI agent generation.
