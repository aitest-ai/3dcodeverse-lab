# 登別伊達時代村 V034 R1 — 原始 V004 屋頂白帶網格來源隔離

> **本輪為 QA／Inspector-only，不修改 V031 正式候選 Runtime，不改 GLB，不刪除任何白帶幾何。** 基底為 V033 Draft PR #138。所有舊版、私人網站及分享設定保持不變。

## 本輪真正找到的來源

在 V004 原始 `v004_merchant_facades.glb` 的 17 個網格中，`plaster_offwhite` 負責寬大的白色橫帶；`ridge_tile` 是另一個獨立屋脊構件。

已在真正 Chromium + Xvfb + ANGLE SwiftShader WebGL2 的同一視角做三種隔離：
- 全部原始網格：白色寬橫帶明顯。
- 隱藏整個 `plaster_offwhite`：寬白帶消失。
- 僅隱藏 `ridge_tile`：細線改變，寬白帶仍在。

這是**原模型視覺來源證明**，不是白帶是否與真實建築不符的證明。不可直接把 `plaster_offwhite` 整個刪除，因為它也包含其他白牆構件。

使用 trimesh 讀取 V004 GLB，在 `plaster_offwhite` 48 個三角面中找到兩個接近屋面的大型水平面（trimesh indices 20/21）：模型 bounds x=1.8208966..22.0183983，y=6.1935205，z=56.7219162..57.3419151；x 向跨度約 20.1975 **模型單位**。尚未分離或移除該兩個三角面；在真正 glTF index buffer 上手術前必須再核對，不能直接假定 Python 的面編號就是 glTF 面編號。這不是實地測量。

## 實際新增：可操作 3D 檢視器

從原封 `Noboribetsu_Date_V033_R1_Inspector.zip`（SHA256
`b1a430f27f390bc284ba5febbdcd07b5ea45c1e281c5b2308d16c5fb38356339`）乾淨重建。
- 10 份舊 GLB **逐位元不變**（包含 17 Mesh 的 V004 原始建築及 V033 A/B）。
- 新增原始網格切換：完整／隱藏灰泥／隱藏屋脊／隱藏瓦片／只看灰泥／只看屋脊；維持 V033 所有舊功能。
- 原 V033 38 個檔案中 **36 個完全不變**，只改 `app.js`、`index.html`，另加 README、contract、integrity，V034 共 **41 個檔案**。
- 空白資料夾重播 **41/41 SHA256 一致**。
- 真實 Chromium WebGL2 載入 10/10 GLB、V004 17 個 Mesh，六種來源隔離狀態均已取得截圖，0 JavaScript page errors、0 console errors。
- 測試不是正式網站、Android 真機或 Blender .blend/Cycles 驗收；本輪沒有手機模擬驗收，也沒有完整 B 遊戲更新。

## 交付與保護

檢視器 ZIP SHA256：
`b631c6d0fbed245a493a087848dc6ceaf94373d9da6de4ada8349a3b97fa7040`

SourceQA ZIP SHA256：
`7dd54c65609ead87503c512c4565bf987b60422d73509a73dcd56a3c2a61f834`

SourceQA 包含真實 WebGL2 六張截圖、對照報告、原始 GLB 幾何稽核、`build_v034.py`、`qa_v034_browser.py`、`audit_v034_source.py` 與打包來源。GitHub 保存版本來源、實際通過的結果及安全界線；原本私人 GLB 只保存在獨立交付 ZIP。

啟動：先解壓 Inspector.zip，在該資料夾執行 `python -m http.server 8765`，再以 Chrome/Edge 開啟 `http://127.0.0.1:8765/`。不得直接雙擊 `file://` 頁面。

## 下一版 V035 的正確方向

先在 V004 原始 `plaster_offwhite` 對應區域**局部分離 2 個來源面**，試做保留原牆面的可逆材質／形狀比較；但要先找同棟高等学問所的可靠照片確認白帶是否為真實構件，切勿把「学問所寺子屋」視為同棟。

**維持 Draft，不合併、不部署、不覆蓋任何舊版。**
