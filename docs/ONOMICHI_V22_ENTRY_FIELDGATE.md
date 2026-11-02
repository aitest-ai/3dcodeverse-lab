# 瀨戶內騎行世界｜V22 377 號道路－國道 317 號共享入口現地證據門檻

## 延續原始 V21，不重做人物與 Halows
- 從已驗收的 V21 來源再往下做。私有完整 V21 包：`Onomichi_V21_Full_Original_Runtime_Plus_Risk_Audit.zip`，SHA256 `2cca82ed61b012043ed2e560a2b885572032f356373f6bdf2f66b7c2fea84bb3`。
- V22 使用完整的 V06 Runtime、V15 Halows、V20 固定 XML，以及 V21 通行標籤審計。這次**完全不修改**遊戲 `data/world.json`、`src/main.mjs`、`src/asset-loader.mjs` 或六份場景／角色／單車／渡船 GLB。原受保護 10 份檔案 SHA256 全部與 V21 相同。
- 只有 V22 工作副本的 `index.html` 新增獨立 QA 入口，不修改主網站、main 或任何舊版 Draft PR。

## 經過實際來源資料確認
- 固定 OpenStreetMap XML（2026-11-02 取得）：`assets/setouchi/osm/onomichi-v20-20261102.osm`，SHA256 `5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76`。
- 住宅道路 way **388716484**，連續節點依序 `1296327682 → 3918810183 → 3918810175 → 3918269426`。三段長約 33.659m／16.483m／24.222m，合計 **74.36m**（道路中心線幾何）。
- 第一端 node 1296327682 連到 `114435640`（secondary/ref 377 向島循環線）；最後 node 3918269426 連到 `167631309`（trunk/ref 317 國道）與 `388652159`（residential）。真實路口的號誌、轉彎、道路寬度、路緣與安全性仍未實測。
- 固定 OSM way 標籤 `access=no`、`bicycle=yes`、`foot=yes`、`motor_vehicle=yes`。**OSM 運具特定規則可能覆蓋一般禁止，但現場法律與交通標誌仍未知**；不能用 OSM `bicycle=yes` 宣稱已確認現場可騎。
- 四個節點用原始 GSI DEM5A `gsi_dem5a_15_28508_13045.png`（SHA256 `79dc9e009a448aec5726ee1c13906270fef196e92c36286075e5474310318e9c`）得地面標高 **2.81、2.70、2.80、2.48m**。DEM 值不是實際瀝青表面或車輪碰撞高度。掃過的 XML 在此路段四個節點附近 40m 沒發現標記的 barrier／號誌節點，但**沒有標註不等於現場沒有障礙或號誌**。

## 本輪真實交付
- 完整 V22：`Onomichi_V22_Full_Runtime_Entry_Evidence_QA.zip`，224111283 bytes、SHA256 `9af06efb794620e2056359e9ad1404a13468a4cb6feb0ac9f60bf4994a632f97`，285 entries，ZIP CRC PASS。
- 增量 V22：`Onomichi_V22_Shared_Entry_Incremental_Patch.zip`，168506 bytes、SHA256 `f1146846560fcb0765cb66c250d5b1b6ba920e29bcdc243a6fb7da0eae2cf771`，10 entries，CRC PASS。
- 新增 `review/onomichi-v22/V22_Offline_Shared_Entry_Inspector.html`：**單頁可離線、原 OSM SVG 地理線段，不需要網路與字型**。含風險／純來源圖切換、377 端與 317 端檢視、四點高程、來源標籤與現場待查項目。另有 `V22_Shared_Entry_Audit.json`、`V22_Entry_Node_Review.csv`、`V22_Field_Evidence_Checklist.md`、`V22_Source_Geometry_Overview.png`。
- 源碼：`scripts/v22_build_entry_qa.py` 可從原始 V20 XML 與 GSI DEM5A 複製來源重建圖面及 JSON，嚴格核對原始 XML SHA／Way／四節點位置，需 Pillow。GitHub 公開同源簡化驗證：`scripts/research/onomichi_v22_shared_entry.py` 與 GitHub Actions。
- Node 原遊戲測試 PASS；來源 PNG 自行生成並檢視；新 HTML 的 JavaScript 由 `node --check` 驗證通過。此執行環境 Chromium 對本機檔案與 `set_content` 操作受阻，**未通過真正的瀏覽器 UI／WebGL2／Android 互動**，故上述 PNG 是根據同一 SVG 產生的靜態研究圖，**不是網頁畫面實際截圖**。

## 下一階段 Gate：禁止拿沒有證據的路段接入遊戲
1. 取得 2026 現場照片：377 與 317／住宅路端的兩組交通標誌、號誌、標線、自行車藍線及道路轉角。需記錄照片來源／日期與授權，參考照片不能未授權作 3D 貼圖。
2. 核對真實自行車合法通行權、路面淨寬、路緣坡口、現地欄杆與標高。可能須採先牽車後騎車的分流，但**未有依據前不得擅自設定**。
3. 建立來源與高程一致、全寬連續掃掠可通的 Blender/GLB 試作，保留原 V06 車與人物，實測來回轉向、騎姿、鏡頭和物件碰撞。
4. 使用真實 Chrome WebGL2 與 Android 實玩後，才能提議把候選路段加入可騎 Runtime；原網站不自行覆寫，Draft PR 不自動合併。

授權與資料：© OpenStreetMap contributors（ODbL）；日本國土地理院「地理院タイル（標高タイル）を加工して作成」。OSM access 語義：https://wiki.openstreetmap.org/wiki/Key:access；官方島波海道路段：https://www.jb-honshi.co.jp/shimanamicycling/howto/index02.html。
