# 第一個實際高品質人物流程｜MPFB 2.0.18 × Blender 5.2

2026-10-30 實際驗證：正式 MakeHuman 人體基底透過 Blender 5.2.3 雲端執行成功；約 19,158 頂點、53 根骨、身高 1.6946m，GLB 含蒙皮與 PBR 測試材質。第一輪中性人體 GLB 與四視角圖已經交付在 [Actions #6](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/40990388439)。

## 第二輪：CC0 著裝與寫實材質實驗

在第一輪已通過的人體拓樸上加入 MakeHuman 官方 `makehuman_system_assets_cc0.zip`：

- 肌膚貼圖：`young_caucasian_female.mhmat`
- 眼睛、眉毛、睫毛、牙齒、舌頭
- `long01.mhclo` 髮型、`female_casualsuit01.mhclo` 服裝、`shoes01.mhclo` 鞋

來源：https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html （官方標示 CC0；各第三方素材如另行加入需逐件查核）。

下載／解壓只發生在 GitHub Actions 的臨時執行環境。**不將 267MB 素材包或第三方外掛原始碼複製進這個 GitHub 儲存庫**。確認演算法穩定後，成品由 Actions Artifacts 保存 14 天，避免無限累積。

## 執行方式

GitHub → Actions → **Blender 5 MPFB Human — Real Basemesh and Rig** → Run workflow。

- 分支 `feat/mpfb5-human-production-smoke`；暫不合併 `main`。
- 建模：`scripts/characters/create_mpfb_human.py`。
- 獨立驗證：`scripts/characters/verify_mpfb_human.py`。
- 預覽合成：`scripts/characters/contact_sheet.py`。

輸出 `human_mpfb_blender5.blend`、`human_mpfb_blender5.glb`、`preview_front.png`、`preview_side.png`、`preview_back.png`、`preview_isometric.png`、`preview_contact_sheet.png`、`asset_manifest.json`、`report.json`、`validation.json`。

## 驗收與誠實標示

- 結構檢查：正確人類身高、足量頂點、遊戲骨架、JOINTS/WEIGHTS、帶材質 GLB。
- 有 CC0 素材包時新增：含 7 件以上可獨立視覺確認的角色部件、圖片貼圖與多材質。
- 人工驗收：髮型貼合、衣物穿模、手指、臉部／眼睛、膝與肩變形；若不通過只能稱為基底或原型。
- **不代表已通過寫實人類肖像、皮膚細節、表情、4K 材質或 UE5 高規格角色驗收**。
- 第三方模型／貼圖授權與版權必須隨成品記錄，不能從單一腳本授權推論所有模型商用許可。

若後續要人物講話、跑步或換衣服，可將 GLB 放入 Three.js，和現有 `examples/threejs/load-animated-glb.js` 合併；必須實際驗證骨架動作與模型相容，不得假設已有完成動畫。
