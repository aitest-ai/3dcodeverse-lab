# Taiwan street NPC V15: source-geometry + Blender screenshot audit

Date: 2026-10-31 (Asia/Taipei). **Draft, ART REJECTED, 4/8 only. Never merge main or distribute as eight complete characters.**

## Reproducible verified run
- Actual Actions run: https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41088064071
- Run conclusion: SUCCESS on code commit `aaa3a813db3f6b045f511a5cc343762c4c92d5e2`.
- Workflow artifact: `taiwan-v15-real-waist-boundary-and-chest-diagnostics-PILOT`, artifact ID `12993151162`, about 25.5 MB. Its repository-artifact retention is 14 days.
- Outputs: 4 genuine GLBs (you, boss, uncle, jie), four neutral views and three facial-expression renders per person, plus 2 wardrobe closeup views each for boss and jie. Keep license provenance in reports.

## Real breakthrough: a shape-key Basis / source-mesh mismatch
- Before V15: V14 moved the global upper waistband vertices by numerical Z heuristic, but screenshot still exposed skin. A raw vertex-number measurement alone was not sufficient.
- V15 introduced actual wide boundary vertex components and 11 front x-axis waist samples, `waist_boundary_v15.py`, with strong no-success-on-gap CI checks.
- The **first V15 build** (run 41087893579) was deceptively green: `Mesh.vertices` positions showed front bare gap `0.02657 -> 0.00000 m`, 76 affected vertices, max intended rise 0.04457 m; **actual Blender image still showed bare skin**. It would be wrong to call that art passed.
- Root cause isolated: the fitted trousers have Blender Shape Keys. The original mesh vertices were moved, while underlying Basis/other key-block positions stayed old, so Blender's true rendered evaluated mesh retained the visible gap.
- Subsequent V15 commit translated **every original shape-key vertex position** by the same local delta, preserving morph differences. Independently rendered closeups from run 41088064071 now show the top of the trousers physically overlying the jersey hem with **no exposed skin in the neutral front near view**.
- Caveat: 11-strip geometry checks and a neutral still render do **not** prove walking/crouching/jawOpen clothing fit or all possible angles. Do not assign release approval.

## Remaining visual rejects confirmed by real Blender images
- **Boss**: fisherman sweater has two bright skin/color interruptions on upper chest; an exaggerated garment bust form; torn/misaligned dark spots along hem. New front/three-quarter chest closeups make this unmistakable. V15 measures genuine source-mesh chest depth (`front_depth_range_m=0.08598`), but does not invent an unreviewed corrective sculpt.
- Other characters: skin/eyes/hair remain overly synthetic, you and jie identity separation limited.
- Eight requested roles: still only **4/8**; no eight-GLB finished ZIP.
- No pose / rig animation / clothing-body interference animation testing completed.

## Next guarded work
1. Fix boss source sweater body-clipping and hem holes using the licensed original garment and verified neutral front/threequarter renders. Do not conceal holes with fake texture paint or claim a topology pass equals visual approval.
2. Re-check jie belt in threequarter, side and walking pose; if cloth moves during animation, all fitted Shape Keys and skin weights must remain coherent.
3. Improve skin/hair/face identity using separate CC0/provenance-checked assets, then add the remaining four Taiwanese roles.
4. Compare rendered previews **before/after** and obtain manual game-art acceptance before merging.

This audit is intentionally more conservative than successful CI labels. UI previews are real Blender renders, not AI redrawing.