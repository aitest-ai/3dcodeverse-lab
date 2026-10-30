# Third-party asset sources (CC0 only)

The realistic pilot (`scripts/blender5/aviator_human.py`) needs two free CC0 packs by Quaternius. They are NOT stored in this repo.
Put them in a folder and pass it as `ASSET_SRC`:

```
assets_src/
  ubc/                      <- unzip of "Universal Base Characters[Standard]" (rename the folder to ubc)
  ual1.glb                  <- Universal Animation Library[Standard]/Unreal-Godot/UAL1_Standard.glb
```

| Pack | Page | License |
|---|---|---|
| Universal Base Characters [Standard] | https://quaternius.itch.io/universal-base-characters | CC0 1.0 |
| Universal Animation Library [Standard] | https://quaternius.itch.io/universal-animation-library | CC0 1.0 |

Both packs share the UE-mannequin skeleton (65 bones), so clips transfer by bone name. Local run:

```
ASSET_SRC=assets_src ASSET_OUT_DIR=outputs blender -b --factory-startup --python scripts/blender5/aviator_human.py
CHAR=female ...   # other body
```

GitHub Actions: the packs are not fetched automatically (itch.io downloads need a scripted session); add them as a
release asset or an Actions cache/secret-free artifact before running the workflow. Not yet automated.

## Modular Character Outfits - Fantasy [Standard] (added 2026-10-30)
- Source: https://quaternius.itch.io/modular-character-outfits-fantasy (Standard/free zip)
- License: CC0 1.0 (Quaternius). Used: Peasant and Ranger outfits (male + female) with the alternate colour textures T_Peasant_2 and T_Ranger_3. Ranger hood not used.
- Same 65-bone UE skeleton as Universal Base Characters; meshes are re-bound to our rig in `scripts/blender5/aviator_human.py`. Only the head/neck of the base body is kept.
- Replaces the earlier procedural "offset shell" clothing, which looked puffy/inflated in review.
