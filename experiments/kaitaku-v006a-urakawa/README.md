# 北海道開拓之村 V006A — 17 舊浦河公會會堂擴建候選

**Date:** 2026-11-01. **Status:** first-pass exterior and runtime package, NOT visually accepted.

Parent: V005 A3H-B hedge experiment (GLB SHA-256 `09decb57caeb803cefd13bcd2ddf77bb0a2c31f80dc761458caafa778caa4a89`). The original V004/V005 and A3 remain independently preserved. No commits of large GLB binaries to this public repository.

## Added scene
- Fourth building **17 旧浦河公会会堂**, to the right of 16 旧渡辺商店.
- Procedural exterior: dark horizontal timber siding, steep gable, upper front sash, small pitched porch, closed front entrance, side windows, stone approach, two hedge beds.
- Extension roadway/ground from existing model x~19 to x~38.8, with 3 new route points.
- Scene walkable maxX now 38; new estimated external building/porch/hedge colliders. Interiors closed.
- The coordinate placement (center x 26.7, front z~-0.7) and scale are **UNSURVEYED ESTIMATES**. Building dimensions and exact relation to 16 must be checked against real site map/survey before claiming accurate placement.

## Sources
- Official 17 photograph: https://www.kaitaku.or.jp/assets/img/about/detailImg17.png
- Official traditional-Chinese building information: https://www.kaitaku.or.jp/ch_h/
- Official museum map: https://www.kaitaku.or.jp/assets/pdf/language/ch_h_areamap.pdf
- Listed as 1894 second Urakawa church congregation hall.

Do not redistribute the official photo as texture. The model uses original procedural flat wood/roof materials.

## Local generated candidate
- Environment merged GLB: `380,417,892` bytes, SHA-256 `697e053400df82457e947269c8c6c503d025f7910fb316b0e5b08b770b65b9c4`.
- New standalone 17 building/street overlay GLB: ~164 KB.
- Portable ZIP: 46 entries, CRC passed, manifest GLB bytes/SHA matched.
- Runtime schema updated with 4 buildings and 9 route points.
- Historical V005 frontend scene-ID guard and portable Python server guard have been changed in this **separate V006A distribution only** to accept `kaitaku-mainstreet-v006a`.
- `python3 scripts/serve.py --check` passed with extracted package files. No real WebGL2 play session, Android test, Cycles/native asset review or manual controller test this turn.

## Next gates
1. Compare official photo to model (porch proportions, roof pitch, rear/side elevations, sign and hedge density); **do not claim final quality from rough geometry**.
2. Real scene V006A WebGL2 loading, camera and 16→17 route traversal; new solid/hedge colliders and old 14/15/16 route regression.
3. Native Blender editable source and original-material same-camera renders, then touch Android.
4. Keep separate Draft PR; no merge or promotion until approved.

A separate local builder script and deliverable ZIP were generated in the conversation; future agents should obtain the user's delivered artifacts rather than assume binaries are in Git.
