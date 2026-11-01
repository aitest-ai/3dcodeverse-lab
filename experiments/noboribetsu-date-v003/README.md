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
