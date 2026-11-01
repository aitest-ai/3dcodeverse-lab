# 登別伊達時代村 V011｜B 場景地形缺口修復（可重建）

**基礎版本**：V010 Runtime ZIP（凍結 SHA-256：`fe3be61782ff688d67cb3f5f8d9faac13e01aa066c1e776edd3960dfa7391787`）。V011 的所有輸出都建基於此版本，且新分支由 V010 的 Draft PR #77 分支接續。不改原版、不合併、不部署。

## 根本原因（不是貼圖）

原 B GLB SHA-256 `3feac26ec59250494330974775bda07c089c0a4642eb4471dc18fd22b2ba6715`；其中草地 primitive 為 201×201 個 2m 格點，原本 40,000 個格網應有 80,000 個三角面，實際只有 79,704 面；局部 X 116～174、Z 116～162 公尺的 **148 格 / 296 面缺失**，且 84 個格點缺少高程。街尾黑白鋸齒狀缺口正由此造成。

## 真正的修補

使用 `build_v011_terrain_patch.py` 從凍結、已核對 SHA 的原始 B GLB 讀取已存在的草地幾何，以 4 邊離散調和補值建立缺失格點，生成 `v011_terrain_gap_patch.json`。新版只附加 296 面，與舊 B 的 `Original_grass` 材質及 UV 完整共用。**不改原 GLB、碰撞、道路、貼圖或路線，補值不代表現地測量。**

程式中的資料完整性閘門要求 patch JSON 原始長度及 SHA-256 完全符合契約，才會建立三角面。修補只在 B 精修場景顯示，切 A 後隱藏。

## 從頭重建

```bash
# 1. 將 V010 ZIP 解壓成一個獨立資料夾，取得 dist/
python build_v011_terrain_patch.py /your/frozen/V010/dist ./v011_terrain_gap_patch.json ./terrain_qa.json

# 2. 在新的資料夾生成 V011 dist，不覆寫原 V010
python integrate_v011.py /your/frozen/V010/dist ./new_v011_dist ./v011_terrain_gap_patch.json ./delta_qa.json

# 3. 若已取得 V011 Runtime，檢查所有 84 個 dist 檔案能從 V010 ZIP 逐位元重建
python clean_replay_v011.py V010_Runtime.zip V011_Runtime_Unzipped/ replay_qa.json
```

需 Python 3 與 numpy；實際 WebGL2 browser QA 需 Playwright + Chromium + Xvfb；視覺 ROI 測試需 Pillow。完整 QA 腳本參見同目錄；Runtime 請使用 `start_v011_local.py` 從 localhost 開啟，讓原生 WebCrypto 生效。

## 驗證結果

- V010 與 V011 街尾相同 Chromium WebGL2 相機：黑白尖角消失；固定 ROI 深黑像素 1,270 → 0。
- 修補新增 296 三角面；真實 B 場景渲染 1,432,282 面、95 geometry、47 textures。
- A／B 首次切換及返回，視角零漂移；手機直式瀏覽器模擬雙指操控，移動約 0.79m、放手 0m 漂移。
- 原 V010 Runtime 的 98 個檔案中 94 個逐位元相同、4 個程式／版本檔更動；新 Runtime 共 101 個檔案。從原 V010 ZIP 重建後 **84／84 個 dist 輸出一致**。
- 真實 Xvfb SwiftShader WebGL2 的隔離測試使用預先經 Python 驗證來源 SHA 的測試專用 digest adapter；**正式應用不含該 adapter**，真實 HTTPS/localhost WebCrypto 仍待一般瀏覽器環境驗收。

## 尚未完成

私人網站 CDN／登入／HTTPS、Android 實體手機、Blender 原生 `.blend` 與 Cycles、推算高程現地查核。這些不能拿本機軟體繪圖測試冒充完成。

**請維持 Draft，勿自動合併，勿覆寫任何舊模型及原有網站。**