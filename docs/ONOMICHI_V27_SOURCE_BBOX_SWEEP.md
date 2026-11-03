# 瀨戶內騎行世界 V27｜真正 V06 單車外包矩形橫向投影 × GSI 地形條件試驗

## 承接 V26
- V27 以使用者私有 `Onomichi_V26_Full_Runtime_Field_Evidence_QA.zip` 為實際基底，**沒有重新製作簡化版**。原 V06 人物、自行車、渡船、四組環境 GLB、V15 Halows、V20 GSI GLB、原 `data/world.json`／`src/main.mjs`／asset loader 11 份受保護檔的 SHA256 全部相符；**只有副本首頁 index.html 新增一個 QA 連結**。
- 原有 Node 測試 21/21 PASS，V27 新增 5/5 PASS，合計 26/26 PASS。未修改 main、既有網站或遊戲的原可行走/騎乘路線。
- 真私人原始自行車 GLB SHA256 `7cb53e92247cf081354c1551b91ae812aab56be7c07748ed00764f0d2c844ece`，可見外包矩形約 **1.77699m 長 × 0.59478m 寬**。這不是人體坐姿、車輪動態、碰撞形狀或法定單車淨空。

## 實際新做的可操作內容
- `review/onomichi-v27/index.html`：**寬度 0.8–3.4m、偏轉 0–35°、假設側邊餘裕 0–0.5m、沿中心線位置 0–74.36m** 的可操作工程工具。原始 OSM 地理線與 9 個實際研究站點以 2D SVG 顯示，連動橫向包絡矩形，輸出單側假設餘裕與 JSON。
- 顯示的寬度一律是「假設通行帶」，不是現場道路。無論幾何是否符合假設條件，`riding_approved`、`collision_approved`、`runtime_changed` 永遠為 false。
- Python 真原始 GLB 包圍盒尺寸試驗：道路中心線 **74.3638m**，每 0.2m 取得 **371 個位置**；24 組 (0/10/20/30° × 假設 1/1.2/1.5/1.8/2.2/3m × 每側假設 0.15m)。橫向外包矩形的半投影 = `(|W cos θ|+|L sin θ|)/2`，0° 時約 **0.2974m**，20° 時約 **0.5833m**。這只能檢查本地每一條中心線截面的近似占用，沒有車頭掃掠連續實際轉向力學、騎姿、真實路緣或輪胎碰撞。
- `V27_Hypothetical_Width_Study_Only.glb`：來源鎖定 GSI 100×130m 地面與**1.8m 假設試驗帶**，9 個診斷球點。不是實際道路寬、路面高或導航碰撞。
- 另外 V27 雲端**真正執行官方 Blender 5.2.3**，GitHub Action `41554536189` SUCCESS、Artifact `13193624096`；包含可編輯 `V27_Editable_GSI_Hypothetical_Width.blend`、真正 GLB、兩張 Blender PNG 真渲染及來源與輸出 SHA256 報告。此真 Blender 物件清楚命名 `HYPOTHETICAL_WIDTH_1p8m_NOT_COLLIDER`，避免後續 AI 誤當可騎道路。Blender 場景僅包含公開 OSM/GSI，原私有人物/單車保留在交付 ZIP／瀏覽器原始 GLB 檢視中，**未上傳至公開 GitHub**。

## 實際測試及限制
- 真 V06 Runtime 21/21 + V27 新幾何 5/5 Node TEST PASS，原 11 保護檔 SHA PASS。
- Chromium **真正操作了自包含 DOM**：假設 1.8m／偏轉 20°／每側 0.15m，餘裕 +0.167m；縮成 1.0m／30°／0.20m 得 -0.402m，改到 3.4m 得 +0.798m，9 個站點皆顯示，始終沒有騎乘核准。此為 2D DOM 視圖與數值操作，不是 WebGL2 3D 成功證據。
- 這一環境 Chromium 用 `page.goto(http://127.0.0.1:8797/...)` 仍然 `ERR_BLOCKED_BY_ADMINISTRATOR`，**不能證明原人物、單車、地形 GLB 在真 WebGL2 互動畫面載入成功**；Android 沒有測試。
- 缺少 2026 這條 74m 路段**真實道路有效淨寬、路緣、欄杆、合法騎車路權、路面高度、共同 Y、高品質街屋的確切照片**。沒有這些資料不得增加具碰撞的真正可騎路面，不得部署主網站。未達成 Blender 寫實美術驗收，本輪僅工程驗證。

## 私人交付與驗收 SHA
- `Onomichi_V27_Full_Original_Runtime_Plus_Sweep_Lab.zip`，235449431 bytes／342 files，SHA256 `f9d7caaf516fb1f34bf6748fd487df629ee8123a54831172f958c2f326dee8ee`，ZIP CRC PASS。
- `Onomichi_V27_Conditional_Width_Incremental_Patch.zip`，3374098 bytes／18 files，SHA256 `7580727305185ebaa3fe4363663837798b8af857df952a1ee4342c59132e0cf8`，ZIP CRC PASS。**只能套用在 V26 的新副本**，參照內附 `V27_PATCH_README.md`。
- `Onomichi_V27_Standalone_Original_GLBS_Lab.zip`，18249672 bytes／26 files，SHA256 `caec36b683aa4a330dc07b670a46c462aa6f9ace519ceb16ec74edf6c68d58e2`，ZIP CRC PASS。內含原 V06 人物／自行車、V23 GSI 地形與 HTML + vendor Three.js，使用者私有檔案，**不公開 push**。
- 另附 Blender 母檔、兩張真渲染圖、道路假設研究結果圖、完整 SHA 與測試報告。來源 GSI DEM 衍生高度陣列 SHA `03726ce15167b760f6a738c1862097c258857299cae7a32353a84931c44cdbf1`，OSM XML SHA `5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76`。

## 下一輪 V28 不可跳過
1. 取得真實 2026 年兩端路口照片／合法騎車標誌及九個站點的道路淨寬、路緣坡口、欄杆和道路高程，不能拿試驗藍帶當實路面。
2. 以真 V06 騎姿和自行車骨架／車輪建立連續的時間軌跡與人車碰撞體；這輪的包圍矩形投影不能當物理碰撞驗收。
3. Blender 真實路面、側溝和周邊街屋精修需要真實影像和可追溯授權；不靠隨機方塊。
4. 最後在可執行 WebGL2 與 Android 的環境實玩，才考慮**獨立**新可騎路線候選；原網站不改、main 不自動合併。

授權：© OpenStreetMap contributors ODbL、國土地理院地理院タイル（標高タイル）を加工して作成。這個公開 PR 只保留衍生地理樣本、程式、CI、文件，沒有散布私人原 GLB。
