# 北海道木雕熊 v21｜造型優先驗收

狀態：**CANDIDATE / UNREVIEWED**。此檔是待驗收規範，不是美術通過紀錄。

## Source
- Blender model: `tasks/hokkaido-bear/model.py`
- Source commit: `ed4c1d52ef452925913da3742382becb422f9053`
- Actual official Harness build and Cycles rendering: https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/40836206685
- Review JSON will be prepared only after inspecting actual generated GLB render and recording exact hashes.
- Run previews are quarantined at `experiments/hokkaido-bear/runs/<run-id>/`.

## What changed and must be confirmed visually
1. Bear nose is a **triangular bevelled mesh**, not a flattened oval sphere. Muzzle is shorter and ear masses are embedded.
2. Removed pasted brow / cheek / lip lines; check whether genuine upper and lower jaw geometry still communicates a bite. This cannot be validated by X/Z distance assertions alone.
3. Salmon head is fuller, posterior half tapers more gradually, gill engraving is displaced within mesh instead of separate round badges, and belly has a different natural-wood color.
4. Removed uniform sculpt stamp function and replaced it with sparse, variable-length negative knife cuts. Check **all angles**, especially shoulder and flanks.
5. Paws remain an unresolved potential issue: fused three-toe pads may still read as boots. Do not call this fixed without new evidence.

## Visual quality bar
- Compare *front*, *front-right-high*, *rear-left-high* and *top* actual GLB renders.
- Mandatory gates: readable bear body shape, visually obvious fish held inside mouth, natural fish head/fin/tail, carved directional fur, no floating details or floor clipping.
- A genuine GLB build does not mean the sculpt is approved.
- Store actual `model_sha256`, `hero_sha256`, `side_sha256`, `sheet_sha256`; reject until hash-matched review scores reach mean >= 4 and each >= 3 with no blocking/critical issue.

## Craft references (for shape grammar, do not copy model files)
- [Traditional wood-carving study, Kyoto University of the Arts](https://www.kyoto-art.ac.jp/t/graduationworks/detail/21320/) — distinction between hair carving and plane carving.
- [KAI Hokkaido, Yakumo wood-carving shapes](https://kai-hokkaido.com/archives/town_vol33_woodenfigure/) — radial shoulder fur cuts.
- [Wood carving shop technical comparison](https://masamaru320.com/viewpoint-of-wood-carving-bear-1-salmon-eating-bear-made-from-japanese-linden/) — analyze salmon shape and gill fin treatment.
