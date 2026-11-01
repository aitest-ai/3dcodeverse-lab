# 登別伊達時代村 V003｜Blender Source-Ready

這個目錄只保存 **V003 的可重跑 Blender 回寫邏輯與驗證契約**。它不包含 V002 私有完整母檔，也不宣稱 GitHub Actions 已經產出正式 V003 Blender 母檔。

## 範圍

- 場址：北海道登別市中登別町53-1「登別伊達時代村」
- 核心：大手門 → 遊戯館，沿用 V002 的約 82.877 m 步行導引與既有碰撞
- 不擴園、不開放室內、不加入第三人稱
- 不重做 V002 已完成的瓦片與柱腳
- V003 只處理：
  1. 遊戯館暖簾的細微垂墜
  2. 已存在木／牆材質的克制 PBR 校正
  3. 既有道路邊緣的渲染層土／苔色過渡

道路邊緣過渡 **不是排水溝、路緣測量或新地理資料**；碰撞、DEM 與步行頂面保持不變。

## 已驗證的 Runtime Candidate

目前可重建的 V003 R2 GLB SHA-256：

`3feac26ec59250494330974775bda07c089c0a4642eb4471dc18fd22b2ba6715`

瀏覽器整合測試已在 Chromium + Three.js + GLTFLoader + WebGL2 中跑過完整高品質 B 模型；Android 實體手機與私人網站 CDN／登入網路仍未測。

## Blender-native 回寫

需要：

- Blender 5.2.3 LTS
- 凍結的 V002 母檔 `authoring/date_v002_master.blend`
- V002 母檔 SHA-256：
  `1d7637c7dd98642ffbfa03074fa6f3af50339a5e965afc2feb47e1ed86567ee1`
- V002 專案中的 `data/scene_geometry.json`

執行方式：

```bash
blender -b authoring/date_v002_master.blend \
  --python experiments/noboribetsu-date-v003/promote_master_v003.py
```

輸出必須另存，不得覆寫 V002：

- `authoring/date_v003_master.blend`
- `models/scene_B_native_v003.glb`
- `evidence/v003_native/*_A.png`
- `evidence/v003_native/*_B.png`
- `qa/v003_native_blender_replay.json`

## 真實性界線

Blender-native 重新輸出的 GLB **不要求與 GLB 後處理 Candidate 逐位元相同**；但場景位置、A 骨架、路線、碰撞、鏡頭與未修改貼圖必須保持既有契約。若產生超出暖簾、指定材質因子與道路邊緣過渡以外的幾何／材質變更，必須停下檢查。

目前此分支是 source-ready。因 V002 私有母檔未放入公開 repo，GitHub 雲端 Blender 尚未執行，不能把「腳本提交」描述成「正式 V003 母檔已完成」。


## 2026-11-01 Source QA2（仍為 source-ready，未升格）
這一輪已從使用者保存的 **V002 Complete ZIP 實體檔案**執行唯讀檢查：
- 5 個凍結來源：V002 Blender 母檔、scene_geometry、collision、A GLB、B GLB，SHA-256 全部符合既有契約。
- 路面拓樸：504 vertices、668 triangles、338 boundary edges、0 nonmanifold edges。
- B 模型中 V003 要修改的 6 種材質名稱全部存在；R3 Runtime ZIP 也已依保存的 SHA-256 重新核對，ZIP CRC 無損。
- 對應的獨立唯讀 preflight 程式與 8 個 Python 單元測試另存為 `Noboribetsu_Date_V003_SourceQA2.zip`；**此 ZIP 不含私人 V002 母檔**。

GitHub 此分支修正了四個回寫風險：
1. 無連線 Roughness 輸入要保留 V002 原值再乘因子，不得直接把 0.98 等倍率當成絕對值。
2. 暖簾形變只可操作 `B_SITE_REFINEMENT`；依材料標記重複套用，單頂點位移上限 0.05 m，避免改到 `A_DATA_SKELETON`。
3. 道路過渡不得產生零面數空幾何，或重複插入同名物件。
4. `promote_master_v003.py` 強制核對五個 V002 來源 SHA、Blender 5.2.x、輸出路徑不覆寫，並檢查六張 PNG 與 GLB／BLEND 的實體檔案和簽章。

請以完整 V002 解壓專案、明確 `NOBORIBETSU_PROJECT_ROOT`、Blender **5.2.3 LTS** 執行；若任何 SHA 不符，直接停止，不重新製造 V002 代替。Blender 官方在 2026-10-22 發布 5.2.3 LTS。

**狀態嚴格分開：** 此處已通過的是真實來源/格式/拓樸與純 Python 測試，**不是** Blender 5.2.3 實際回寫、Cycles 正式 A/B、Android 真機、或私人預覽 CDN/登入驗收。這些都仍未通過。切勿因此合併 Draft PR、覆寫 V002 或更新私人網站。
