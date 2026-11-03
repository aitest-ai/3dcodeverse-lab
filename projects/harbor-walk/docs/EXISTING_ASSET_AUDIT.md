# 既有資產庫保護與查核

已先閱讀 `3dcodeverse-lab/AGENTS.md`、`docs/AI_ASSET_PIPELINE.md`、`examples/threejs/load-animated-glb.js` 與 GLB validator，查詢遠端分支、開啟 PR 與 Release。原有工作目錄的正式檔案沒有被改動；只 fetch 參考分支供讀取。

已確認的角色方向包括：

- `feat/aviator-kid-character`，head `172efe078e5791c181b701f9c96f99b68051a9c7`：具有 `aviator_human.py`，使用 Quaternius CC0 同 UE skeleton 的 body/outfit/animation rebind，輸出報告描述 Idle/Walk/Run 等。該分支查得的近期 CI run 為 failure，不能據此說「角色不存在」，也不能把舊報告當成本輪已成功建模。
- `feat/diverse-character-studio`，head `abb756d8cd9f92c5d559c048747ce15a0ebba35e`：delivery index、原創差異化參數工房與 source lock，標示 `art_approved=false`、`game_ready=false`。其中登錄灰模缺動畫，本版沒有將它們直接當成 locomotion-ready 角色。
- `feat/mpfb5-human-production-smoke`，head `d50aa581ccae8049848fa9e3a8df238acb1962bf`。
- `fix/taiwan-character-face-anatomy`，head `3905c0cee3658a913d43f15a1c59bee56571882c`。
- 開啟 PR 列表存在多條未合併角色／場景分支；沒有合併它們或覆寫其資產。
- Release 列表確認 `horses-v2.3.0` 的 brown / white GLB 與母檔包。馬匹已存在；本版不需要馬，因此沒有重造或下載它們。

採納既有技術：具名動畫介面、共用 UE-style skeleton 的 rebind 思路、母檔／GLB／manifest／report 交付契約、結構與視覺分開驗收。新專案用獨立腳本重建合法 CC0 輸入及原創配件，不修改上述任何分支或資產。

既有庫指定其 Blender5 工作流程只能以 Actions 背景模式執行。本次**未在該庫執行其生成流程**，改於獨立新專案，以本環境實際具備的 Blender 4.3.2 背景模式製作；版本差異已明示。沒有冒稱 Blender5.2.3、桌面 GUI、Animatica 或既有分支的 CI 成果。
