# 瀨戶內騎行世界 V18｜真實 GSI DEM5A 地面高程研究

本輪由 V17 Draft PR #97 繼續，而非再製作 Halows 方塊。真正 V06 Runtime、V15 GLB、OSM 2026-10-31 快照與 V09 site_lock 均按各自 SHA256 鎖定，且不修改原站、main、世界路線、單車、角色與渡船。

## 驗證成果
- OSM way `114435640`／向島循環線 377 已知 22 節點，WGS84/ECEF 平面中心線長 565.335m。
- 使用原 V06 隨包之 GSI DEM5A `15/28508/13045.png`（SHA256 `79dc9e009a448aec5726ee1c13906270fef196e92c36286075e5474310318e9c`），依地理院官方 RGB 標高編碼公式解碼：**22/22 節點有值**；沿路每段約 5m 對地面取樣，**113 點**；最低 1.73m，最高 2.81m。
- 377 起始 node `8255588823` 的 DEM 為 2.39m，與 V06 原有支線終點 world Y=2.39m 相同。此為單點比對，**不得**直接將 V15 Halows 估計平台（PAD 2.70m）當為已通過的 Y 平移。
- 已知 377 端點到 V09 道路快照最近節點仍相距 **441.235m 直線**，目前沒有共同節點，缺乏這段道路資料；V18 不創建道路 Mesh／Navmesh 或自動搬移玩家。

## 真正交付與復現
- 私有完整版：`Onomichi_V18_Full_Original_Runtime_Plus_Elevation_QA.zip`，223444614 bytes，SHA256 `4d49c74171cd778f0f4a50363ea1bcc90d0963331550202ca85694776a005fe9`，246 files，ZIP CRC PASS。
- 私有增量版：`Onomichi_V18_Elevation_Incremental_Patch.zip`，395304 bytes，SHA256 `ccd6fb183bc4bf3a2525ac4876f68c91034294ec47e2ae9bc140c53b11216b7a`，16 files，ZIP CRC PASS。
- V18 私有工程路徑：`review/onomichi-v18/V18_Offline_Elevation_Atlas.html`（完整路網研究圖與可互動的高程圖、22 節點表格）；`V18_Actual_GSI_Elevation_Profile.png`、`v18_profile_5m.csv`、`v18_elevation_report.json` 等均是由真正資料產生。
- `scripts/v18_dem_recheck.py` 需 Pillow；具有使用者自己的 V06 原始 PNG 時：
  `python scripts/v18_dem_recheck.py --tile data/geo/raw/gsi_dem5a_15_28508_13045.png --reference review/onomichi-v18/v18_source_nodes.json`。
- `scripts/v18_gap_osm_checker.py --fetch research/gap.osm` 可在**可連網的本機**向 OSM 公開 API 取得新的缺口區域快照；不覆寫檔案，僅以共享 OSM node IDs 分析拓樸，**不把任何路段認證為合法騎乘**。目前執行環境的對外 DNS 無法連線，不能把未取得的新道路稱作已完成。
- GitHub 公開分支只收錄 OSM/GSI 衍生研究資料、可重現檢查程式、CI 和此交接文件，**不公開上傳使用者的 211MB V06 主工程**。CI 不具備原始 GSI PNG 時只做資料結構檢查，不會假稱來源像素核對。
- 本地已實際取回原始 PNG 並重算 22/22；保留 10 個 V17 受保護檔 SHA，Node 原 21／21 測試 PASS；V18 獨立 HTML 以 Playwright 注入頁面文字方式驗證表格／切換可互動，但瀏覽器 file:// 直接開啟仍遭環境阻擋。**沒有完成原 3D 遊戲的 WebGL2、Android 或全幅碰撞遊玩測試**。

## 不可混淆的三種高度
1. PNG 表示精度 0.01m，並非保證高程測量精準至 1cm。
2. DEM 地面值不代表車道瀝青表面、路肩、橋面或無障礙通行坡度。
3. V06 原點海面參考與 V15 模型估計平台需要另做整體高程映射和碰撞檢查，不能用一個相符節點就宣稱全線已完成。

## 授權與來源
- GSI 官方 PNG 規格：https://maps.gsi.go.jp/development/demtile.html；出典：國土地理院地理院タイル（標高タイル）を加工して作成。
- 原 22 個地理節點 © OpenStreetMap contributors / ODbL：https://www.openstreetmap.org/copyright。
- 官方自行車藍線與渡船規則：https://www.jb-honshi.co.jp/shimanamicycling/howto/index02.html。
- Halows 官方歷史店面照片：https://www.halows.com/stores/detail/77（只作美術參考，非合法進場證明）。

後續 V19 應優先在可連網環境取得上述 441m 區域 OSM XML，查證來源、路口、路權，再生成獨立、不可通行的地形 QA；未經驗收不得接入 Runtime。
