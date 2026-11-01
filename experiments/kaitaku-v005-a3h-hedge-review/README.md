# 北海道開拓之村 V005 A3H-B — 郵局綠籬獨立實驗

**狀態：EXPERIMENTAL / NOT PROMOTED。** 此分支疊在 Draft PR #53 的 A3 基礎上；**不修改原始 V005、A3 或 main，也不增加第四棟**。

## 承接資料

- V005 original BLEND SHA-256: `7ead93b961f243c3521244a509e53546c73e27af4539a89a303a2e28c632ddbc`
- V005 environment GLB SHA-256: `32ddd3721e75b95f54ade22304e4d383930e4411507b0858f7d957f7171462d4`
- A rollback: `752887763308bf71342b0d9ac292fc0f30ffa2e30d0ec6639e7373bb03cd5a55`
- A3 parent (verified, required input): `8df3ada77443c390556e71c873d43dd65fe67996716e08ecfaff4e5faf60e27f`
- A3H-B experimental output SHA-256: `09decb57caeb803cefd13bcd2ddf77bb0a2c31f80dc761458caafa778caa4a89`
- Output size: **380,250,200 bytes**.

A3H-B is based on the separately tested A2-style profile shaping method, **applied to A3**, *not* an A2 promotion. Entrance-side hedge is rounded more than postbox-side hedge. It is a photo-informed, unsurveyed silhouette adjustment, not a claim about historical exact dimensions.

## What changed

Only `POSITION` data for the **12 named leaf/twig accessors** of:
- `14 Left entrance hedge`
- `14 Right postal hedge`

Maximum observed absolute vertex height change: **0.140759 m**. Both hedges' soil/planting beds are preserved. A3 glass, doorways, asphalt, barber slant patch, postbox, passage, kerbs, stairs, roofs, grass and character assets remain unchanged.

Independently read-back checks in the working environment:
- 592/592 mesh node identities intact.
- GLB JSON keys other than the 12 allowed accessor min/max values are exactly equal to A3.
- Binary geometry **outside those 12 POSITION spans is byte-identical** to A3.
- Same mesh count, unchanged indices, materials, textures and image references.
- A3H-B output digest exactly as pinned above.

## Reproduce

```bash
python3 experiments/kaitaku-v005-a3h-hedge-review/apply_a3h_b_hedge.py \
  --source kaitaku-v005-finalpolish-a3.glb \
  --output kaitaku-v005-finalpolish-a3h-b.glb
sha256sum kaitaku-v005-finalpolish-a3h-b.glb
```

**Do not** overwrite `mainstreet-v005.blend`, native A3 candidate or A3 runtime GLB.

## Visual status and reference

- Simplified-material offscreen VTK **geometry-only** matched-camera comparison completed for the entrance and postbox hedges (A3 vs A3H-B).
- Reference: [Sapporo Tourism Photo Library — 北海道開拓の村](https://www.sapporo.travel/sightseeing.photolibrary/area/area07/2571/) (a post office image showing an irregular rounded entrance-side hedge and a more upright postbox-side hedge).
- Geometry-only preview **is not** Blender/Cycles native original-material review.
- Full-scene WebGL, native Blender five-view re-review, Android and user controls for A3H-B: **not tested**.
- Do not promote A3H-B to A3 or merge until it passes original-material same-camera review and runtime regression without side effects.

A3 remains the preferred operational runtime candidate, A remains rollback, A2 remains experimental separately, A3H-B is an independent hedge-only draft.
