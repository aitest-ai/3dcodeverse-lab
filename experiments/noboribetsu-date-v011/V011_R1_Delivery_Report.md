# 登別伊達時代村 V011 R1｜街尾地形幾何補洞交付報告

## 已實作

從凍結 V010 Runtime（SHA-256 `fe3be61782ff688d67cb3f5f8d9faac13e01aa066c1e776edd3960dfa7391787`）讀取原始 B GLB。B GLB 重新解壓為 188,663,252 bytes，SHA-256 `3feac26ec59250494330974775bda07c089c0a4642eb4471dc18fd22b2ba6715`；原地形材質 `Original_grass` 有 79,704 個三角面，2 公尺格網應有 40,000 個面格，其中 **148 格完全沒有三角面，合計缺失 296 面**，另有 84 個格點缺少高程。缺口集中 X 116–174、Z 116–162 m，恰位於 V010 實際街尾視角左側的黑白破圖。

V011 使用原始周邊高度作四鄰點離散調和補值，新增 296 面 B 場景視覺補洞，不改舊 GLB。補洞共用原草地材質與 UV (`u=x/8`, `v=z/8+1`)，不改路線、高程來源檔、碰撞、建築、貼圖或人物；**補值為作者估計，不是官方實測高程**。

## 真 WebGL2 驗證

Xvfb + Chromium + ANGLE SwiftShader **真 WebGL2** 載入並繪出 1,432,282 個三角面／95 個幾何／47 張紋理（單次測試，非裝置效能保證）。V010/V011 同位置（231.566 m 街尾）、相同 960×600 相機的獨立實際渲染顯示黑白破洞消失；固定影像區域中 RGB max 小於 32 的深黑像素數由 1,270 → 0。A 首次載入並切回 B，全部相機視角差異為零；保留五棟灰量體共排除 100 面。

手機直式 Chromium 模擬下雙指搖桿與環顧同時有效，角色前進 **0.791 m**，放手位移 **0.000 m**；這不是 Android 真機測試。

## 可重建性

從乾淨 V010 ZIP 重新解壓，重跑 `build_v011_terrain_patch.py` 與 `integrate_v011.py`：**84／84 個 dist 輸出檔案 SHA256 逐檔完全一致**。V010 原本 98 份檔案中 94 個完全不變、4 個版本或介面程式改動，加 3 個檔案，V011 Runtime 共 101 個檔案。所有原始 GLB、碰撞與控制計算基礎完全保留。原始 V010 ZIP 也未覆寫。

V011 新增的補洞 JSON 使用真 `crypto.subtle.digest('SHA-256')` 驗證原始 bytes，資料長度／結構不符會拒絕載入。**實際 WebGL2 隔離測試**因環境阻擋 localhost/HTTPS top-level navigation，只能使用虛擬子資源與測試專用、預先 Python SHA256 核對的長度→雜湊 adapter；該 adapter 完全不在 Runtime。另附正常 localhost 伺服器供實際 WebCrypto/網站環境查核。

## 明確未驗收

1. 私人網站真正 CDN、登入、HTTPS 與部署：未測、不覆蓋。
2. Android 實體手機效能、GPU 記憶體與操作：未測。
3. Blender-native `.blend` / Cycles 同鏡位：未測。
4. 84 格高程補值是否與真實地形完全吻合：沒有現地測量資料。
5. SwiftShader FPS 不等於實體 GPU 的 FPS，不能據此宣稱效能提升。

## 交付內容

- `Noboribetsu_Date_V011_R1_Runtime.zip`：整份可執行 V011；解壓執行 `python start_v011_local.py`，瀏覽器開啟 `http://127.0.0.1:8765/index.html`。
- `Noboribetsu_Date_V011_R1_SourceQA.zip`：所有可重跑生成程式、資料契約、實測 QA JSON、兩版真實 WebGL2 截圖與比較證據。
- `Noboribetsu_Date_V011_R1_Review.html`：內嵌 V010/V011 同鏡位 PNG，可離線滑桿比較。
- `v011_terrain_gap_patch.json`：單獨的補洞模型資料；需使用本版 Runtime 的原草地材質，不是一份自給自足的 GLB。
- `Noboribetsu_Date_V011_R1_Validation.json`：整體驗證摘要。

**狀態：V011 R1 候選，待原生 Android／私人網站／Blender 驗收；勿自動合併或部署。**