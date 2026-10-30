# Character pipeline (Blender 5.2 + GitHub Actions + three.js)

General rules for any AI or human adding a **rigged, animated character** to this lab. Built from the `aviator_kid`
asset (Q-style child pilot). Read `AGENTS.md` and `docs/AI_ASSET_PIPELINE.md` first; this page only adds the
character-specific conventions that those two do not cover.

## 1. Files per character
| File | Purpose |
|---|---|
| `scripts/blender5/<asset_id>.py` | the only source of truth: geometry, materials, rig, clips, export, measurements |
| `outputs/<asset_id>.blend` / `.glb` | editable source / runtime model (CI artifact) |
| `outputs/asset_manifest.json` | clip list, speeds, size, customization hooks |
| `outputs/report.json` | **measured** numbers (see section 4) |
| `outputs/preview/*.png` | review images from `render_preview.py` |
| `docs/ci/blender5-character.yml.proposed` | independent workflow proposal (install to `.github/workflows/` with a `workflow`-scope token) |

Run locally: `blender -b --factory-startup --python scripts/blender5/aviator_kid.py` (env `ASSET_OUT_DIR` optional).
Until the proposed workflow is installed, run the existing one with `scene_script = scripts/blender5/aviator_kid.py`
(its script selector accepts any reviewed file in `scripts/blender5/`).

## 2. Skeleton and naming standard
* Units meters, Blender Z-up, character faces **-Y** in Blender (= **+Z** in glTF after export). Origin on the ground between the feet.
* Bones: `root > hips > spine > neck > head`; `thigh/shin/foot.{L,R}` from `hips`; `upper_arm/forearm/hand.{L,R}` from `spine`.
  Character left = +X in Blender.
* Clip names (exact, case-sensitive): `Idle Walk Run Wave Salute Cheer Sit`. Locomotion clips are **in-place** loops; speed is
  declared in `manifest.clip_info[clip].speed_mps` so the engine can set `timeScale = actualSpeed / speed_mps`.
* Style choice for stylised characters: each part is weighted 100% to one bone (rigid toy joints). For realistic skinning,
  add weight painting but keep the same bone names so clips stay compatible.

## 3. Customization conventions
* One material per colour role, named by role (`jacket`, `scarf`, `skin` ...). Engines recolor by **material name**.
* Optional parts are separate nodes prefixed `acc_` (cap, goggles, scarf, pack). Hide/show them by node name.

## 4. Gates the script measures (evaluated on the deformed mesh, never from bone data alone)
| Gate | Threshold (assert) |
|---|---|
| stance-foot slip (ground-frame drift of the planted foot) | Walk <= 0.02 m, Run <= 0.03 m |
| lowest sole point | >= -0.012 m on Idle/Walk/Run/Cheer |
| knee flexion | <= 140 deg |
| hand-to-torso clearance | > -0.02 (ellipsoid test) on Walk/Run |
| loop closure error | reported (0.0 for Idle/Walk/Run/Cheer) |
| all required clips and exactly one skin in the exported GLB | hard assert |

Joint limit table used as design budget: knee 0-140, elbow 0-150, thigh swing -35..100, shoulder swing -60..180,
spine lean -20..35, head nod +-40 (degrees).

## 5. Foot grounding method
Per frame, 2-bone sagittal IK places each ankle on a generated foot path; the **stance foot moves backward at exactly
the clip speed** so it does not slide when the engine moves the character at `speed_mps`. Heel/toe pitch is keyed and
returns to 0 at stance contact. No runtime IK is needed in the engine.

## 6. Review (two independent steps)
1. `validate_glb.py` = structure only (skin, clips, file integrity). It cannot see foot slip or a bad pose.
2. Visual acceptance = `outputs/preview/*.png` plus an in-engine check. Record who/what reviewed in the PR. The build
   script never claims visual approval.

## 7. three.js integration notes (r128 compatible)
* `GLTFLoader` -> `AnimationMixer`; state machine Idle -> Walk -> Run with hysteresis and 0.18 s cross-fade.
* Set `frustumCulled = false` on skinned meshes; clone materials before recoloring.
* Match movement speed to the clip: `timeScale = speed / clip_speed`, clamp to about 0.5..1.9.
* Hosts that cannot serve `.glb` (e.g. artifact previews) can embed it as base64 in a `.js` file and use `GLTFLoader.parse`.

## 8. Known limits of this pipeline
* GitHub MCP/text tools cannot commit binaries; the GLB/BLEND travel as Actions artifacts or a Release.
* No facial animation, cloth or secondary motion; Salute hand-to-brim error is about 0.11 m (see manifest).

## aviator_human: outfit and customization conventions (2026-10-30, rev 2)
- Nodes `o1_*`..`o4_*` = four outfits (show exactly one set): 1 卡其飛行服, 2 機師制服, 3 皮夾克飛行員, 4 農夫襯衫. Nodes `acc_goggle*`, `acc_cap*`, `acc_scarf*` = optional accessories (goggles sit on the cap).
- Pilot looks are the CC0 Quaternius Peasant/Ranger meshes with **re-coloured atlases**: `dump_outfit_uv.py` (Blender) exports UV triangles per part, `make_outfit_recolor.py` (PIL+numpy) colourizes the UV islands of shirt/pants/boots (keeps the painted shading) into `outfits/recolor/<Male|Female>_<kind>_<variant>.png`, which `aviator_human.py` then swaps in. Ranger pauldron/bracers/belts/hood are dropped.
- Engine recolours by material name (suffix `.001` stripped): `cap`, `scarf`, `MI_Hair_*` (hair texture is neutral grey, multiply colour), `MI_Superhero_*` / `MI_Regular_*` (skin tint). Clothes are texture based and are switched, not recoloured.
- Three bodies selectable in the wardrobe: `aviator_kid.glb` (Q-style, rev 2 uses tapered lathe tubes instead of ellipsoid "balloon" limbs; colour roles jacket/pants/boot/scarf/cap/hair/skin), `aviator_human_m.glb`, `aviator_human_f.glb` (`CHAR=female`, short hair so the cap does not clip). Each is loaded lazily on demand (~5 MB for humans).
- Known limits: outfits were authored for a "Regular" body while the retained head is Superhero; walk heel-roll slip up to ~5 cm; only visual review by the author (AI), no real-GPU test; GitHub Actions never run (no permission). Outfits are fantasy-themed meshes recoloured toward a pilot look; a real flight-jacket asset would still need an artist/GPT texture or new modelling.
