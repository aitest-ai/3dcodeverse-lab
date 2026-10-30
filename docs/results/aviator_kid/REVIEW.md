# aviator_kid - build and review log

| Item | Status |
|---|---|
| Script runs in Blender 5.2.3 headless | PASS (local run, same version, SHA256 verified) |
| Same script run in GitHub Actions | NOT RUN by the authoring environment (no Actions permission). Run `blender5-cloud.yml` with `scene_script=scripts/blender5/aviator_kid.py` |
| `validate_glb.py` (structure) | STRUCTURE_PASS: 47 meshes, 1 skin, 7 clips, 414,708 bytes |
| Measured foot slip | Walk 0.0071 m, Run 0.0066 m |
| Measured sole penetration | none (min z about -5e-8 m) |
| Visual review | contact sheets of Idle/Walk/Run/Salute/Wave/Cheer/Sit reviewed by the authoring AI only; **a human review is still required** |
| In-engine (three.js r128) | model visible, 47 skinned meshes, Idle/Walk/Run state machine, 0 console errors in a software-GL test |

Known issues: Salute hand-to-brim error 0.11 m; Wave arc is low; no face or secondary animation; no real-GPU frame-rate test.
