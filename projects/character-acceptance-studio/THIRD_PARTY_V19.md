# V19 sources, author, license and changes

No newly acquired external model or motion source. V19 uses exact V18 CI output (PR #171, commit `380f1aacc14498bc96ebb4102ce137cb832bf422`, run `43117873306`, artifact `13899702463`). See `docs/INPUTS_V19.json` and the per-file archive SHA indexes. Original images retain original bytes and dimensions; source VRMs, imported editable Blender masters, textures and license evidence are in Sources.

Vivi β2 / Vita β3 by **pixiv Inc.**, VRoid beta sample models, **CC0**. Mirror revision `e16eb187100149a315ad92c3c9968f1d5baa6c7d`; source URLs, original VRM hashes and earlier modifications in `THIRD_PARTY_V18.md`, `THIRD_PARTY_V17.md` and `THIRD_PARTY_V04.md`. Upstream `.vroid` files are unavailable. Existing seven clips are project-authored native-rig motion overlays, not captured human motion or a newly trained motion model.

V19 project modifications: alpha-supported triangle-intersection diagnostic; explicit local cuff subdivision with interpolated weights and normals, preserved UV seams and original attribute prefixes; quarantined experiments on each body; browser failure bookmarks, triangle overlays and paired playback. Both geometry experiments are **rejected**, never reusable catalog entries. Numerical skinning-compensation/SVD study was not baked or promoted. No new texture resampling, retargeting, body proportion edit or global rig normalization.

Runtime vendors retain upstream licenses from previous packages: Three.js, three-vrm and supporting loader modules. Included source modules v05/v06/v17/v18 remain versioned project code; their notices are supplied. Generated diagnostic JSON, scripts and viewer changes belong to this repository under its existing terms. No claim of new upstream rights is made.
