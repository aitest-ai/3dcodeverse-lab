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
