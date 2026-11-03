# 登別伊達時代村 V030 R1｜局部瓦片厚度與灰階美術候選

**此分支直接疊加 V029 Draft PR #128。請保持 Draft，不合併、不部署、不修改任何舊版或私人網站。**

## 實際完成
- 讀取**原封 V029 Runtime.zip SHA256**：`a21beba4ba44ea03ed1f517eeea27e100a45917c6c10dcfd496bac892d9396bd`。
- 精確沿用 V004 已建立的屋瓦三角面，對上層屋面擬合 y(x,z) 平面，來源模型平面 RMS 殘差約 **6.17 mm**。**這是作者模型幾何內的擬合，不是現場測量。**
- 在現有模型表面上製作約 12m × 1m 局部灰瓦候選：**180 片弧形、帶薄端緣的瓦片，3 Mesh、7200 triangles**。3 種偏克制的灰階、9 張原創程序化 PBR BaseColor／Roughness／Normal 紋理。新增 GLB **783,976 bytes**，SHA256 `0a3203c26b263bd6aa111939f4c2439b0a2950ca8d032bb1b261079ccb9c9b6f`。
- 候選只在 **B 精修場景**顯示、可開／關；V029 屋簷木作、V026 窗框維持正常。A 骨架不新增瓦片。
- 不修改 V004–V029 原 GLB、建築底面、原屋頂骨架、472 路線點、導航／碰撞或玩家控制。候選非實地仿真，不提供安全、排水或文資工程尺寸證書。

## 來源與真正測試
- 原 V029 Runtime 共 **140 個檔案**，其中 **136 個 SHA256 完全不變**；只更新 `dist/app.js`、`dist/index.html`、`dist/qa.json`、`dist/scene_view.json` 四個接線／說明檔，新增獨立 GLB、SHA JSON 契約與 README，V030 合計 **143 檔**。從未改的 V029 ZIP 在全新目錄重建，**143/143 SHA256 一致**。
- 原 V029 3D Inspector ZIP SHA256 `df8cfef094b74311825f12fd874bc32282f6c4e5d1af8c6350478a24d44fcdc6`，新檢視器保留六份舊 GLB，新增 V030 1 份，從原封 ZIP 重播 **27/27 檔案 SHA256 相同**。
- Chromium + Xvfb + ANGLE SwiftShader **真正 WebGL2**：檢視器 **7 份 GLB** 載入，屋瓦近景／屋簷／街道 3 鏡位 ON/OFF 共 **6 張 PNG** 通過，0 筆 JavaScript 例外。
- Chromium 手機 emulation **430×932** 的 WebGL2 與屋瓦開關通過；**不是 Android 真機**。
- 隔離 **完整 B 遊戲**實際載入，V030 開→關→開、V026 窗框保持、W 鍵實測 **1.2684m**，JS errors 0。測試用 SHA adapter 與觀測 hook 僅在隔離測試中使用，不存在正式 Runtime；正式 JSON/GLB 均使用 **原生 WebCrypto SHA256 fail-closed**。
- **Blender/bpy 目前不可用**，本輪並未產生 .blend 或 Cycles PNG；獨立 SourceQA 內的 `blender_native_v030.py` 只是一份可執行的待驗腳本。Android 實機、正式私人站 HTTPS/CDN/登入、長時間 FPS 未驗。

## 交付／版本保護
各 ZIP 的 SHA256：
- Runtime: `0f6dc2124eac569301cffaca86e803ade253a160acaa2fe32212b3de6a273172`
- Inspector: `32e9cfee0d7b83c83fbb6282494c33dafd44a3fd8231bbd32f6b7e1c38add985`
- SourceQA: `b38b11009e5dcaac223e831d739eaba86d5dc25d1b3e27424b1fee122b8654c3`

可重播的完整 `source/build_v030_roof.py`、`source/integrate_v030_runtime.py`、`source/replay_v030.py`、`source/replay_v030_inspector.py`、`source/qa_v030_source.py`、Chromium 桌機／手機／完整園區腳本、Blender native gate、貼圖與真截圖都已放在獨立 **SourceQA.zip**。GitHub 不提交私人完整 GLB 場景或 ZIP；本 PR 僅保留來源定位與品質契約。

使用者可解壓 Inspector.zip 並啟動本機 Python HTTP 服務，於 Chrome/Edge 切換屋瓦前後版本。完整園區仍是候選 Runtime，不自動發布。

參考：官方介紹 https://edo-trip.jp/tw/about/ 只確認仙台藩相關街景背景，**無法證明高等学問所同棟屋瓦精確尺寸**；不能混用学問所寺子屋的照片。

**保持 Draft；不要合併或部署。**
