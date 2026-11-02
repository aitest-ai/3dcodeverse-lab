# 瀨戶內騎行世界 V24｜真正 V06 人物單車比例與 DEM 接觸驗證

## 源版／母檔
- V24 從 V23 Draft PR #118、**使用者私人完整 V23 Runtime** 的所有 299 個檔案衍生。並非用簡化方塊、替身人物或自行生成的自行車。
- 私人 V23 ZIP 的 11 個受保護檔案逐 byte 保留（world、main.mjs、loader、V06 角色／自行車／渡船和四個環境 GLB、V15 Halows、V20 地形研究 GLB）。只有 `index.html` 新增 V24 獨立檢視入口，正式騎乘路線完全不動。Node 21/21 PASS。
- 真正原 V06 人物 `jie-v110-arm-v02.glb` SHA `4dab76c398f4c30c3aa62ef88e389b28974018c01fd271c08bf029d840d263d1`，模型高度 **1.754m**（10 meshes）；V06 自行車 SHA `7cb53e92247cf081354c1551b91ae812aab56be7c07748ed00764f0d2c844ece`，尺寸約 **1.777m 長、0.595m 寬、1.104m 高**（139 meshes）。V23 地形 GLB SHA `a45dc26ca6f4e3d28787148493e4014db6df2f06c709899ccb5cb7a55c2a484a`（11 meshes）。
- 這些是**原始可見模型的包圍盒尺寸**；未做人物動作、騎姿或車輪動態接地／碰撞驗收。以 VTK 9.6.2 真正回讀上述 GLB 並將三套幾何放在同一場景出圖，並清楚標註其僅為「人車比例擺放」而非遊戲 spawn、可騎道路或真正瀏覽器畫面。

## 來源可靠、不可誤解的高程資訊
- OSM way `388716484` 的道路中心線長約 **74.364m**；GSI DEM5A 原始來源 PNG SHA `79dc9e009a448aec5726ee1c13906270fef196e92c36286075e5474310318e9c`，V23 衍生 2m 格網 3366 個樣本 SHA `03726ce15167b760f6a738c1862097c258857299cae7a32353a84931c44cdbf1`。
- 本輪沿道路中心線逐約 1m 採 **77 個診斷位置**：2m 網格內插地面高約 **2.47–2.95m**；原 PNG 四節點高程 2.81、2.70、2.80、2.48m；2m 衍生網格在四節點的內插值和原 PNG 差 **+0.0273、+0.0095、+0.0057、+0.0036m**。這不是測量誤差，只是不同取樣／內插方法的數值差。
- 在中心線兩側各 **1.5m** 的純技術探針位置，對側地面高差最大 **0.2062m**。這並不代表真正車道寬 3m、路面橫坡或自行車要跨越 20cm 障礙；**是 DEM 地形橫向檢查位置**，道路實際寬度／路緣／路面標高全都未知。
- 官方島波海道指引建議沿自行車藍線並注意尾道往向島使用渡船，但不是針對 OSM way 388716484 的現地實測。公開的國道317或縣道377照片不確定是否為指定路口，**沒有冒用它們來建造路緣／房屋或交通標誌**。

## 真實私有交付
- 完整工程 `Onomichi_V24_Full_Original_Runtime_Plus_Real_Scale_QA.zip` （308 files，ZIP CRC PASS）；私有增量 `Onomichi_V24_Incremental_Real_Asset_QA_Patch.zip` （10 files，ZIP CRC PASS）。實際 SHA/bytes 見 `assets/setouchi/onomichi-v24-scale-registry.json`。
- 完整版中的 `review/onomichi-v24/index.html` 使用原始 Three.js vendor GLTFLoader 直接從原 V06 的原始資產路徑載入角色、單車及 V23 地形，切換「人物／單車」及三個相機鏡位；沒有對原始 GLB 進行網格修改。單車和人物擺放位置由 QA 人員人工指定，只比較大小，不作碰撞判定。
- `scripts/v24_scale_seam_audit.py` 可用原始 V23 2m 高程衍生 JSON 與真實三個 GLB 重算中心線採樣、橫向差、尺寸及來源 SHA；`review/onomichi-v24/V24_Scale_Seam_Report.json` 保存 77 個診斷點；另附真正 GSI 三維地形圖、剖面圖與**原實際 VTK GLB 人車接合圖片**。
- 原始 Node **21/21 PASS**。HTML ES Module 已用 Node `--check` 確認語法。嘗試 Chromium Playwright `http://127.0.0.1` 得 `ERR_BLOCKED_BY_ADMINISTRATOR`，**未驗證 WebGL2 圖形載入或 3D 遊戲**；不把 VTK 渲染圖片偽稱網頁截圖。
- 私人完整包可在獨立工作副本執行 `python3 server.py --port 8765`，再開首頁「操作說明」中的 V24 QA 連結。增量包根目錄是 `onomichi-cycling-v23/`，僅在 V23 的**新副本**覆蓋套用，保留舊版。

## GitHub 公開範圍與下一階段
GitHub 只保存衍生 GSI/OSM 診斷演算法、註冊、CI、交接文檔，**不公開推送使用者私人 V06 人物/單車、V23 230MB 專案**。公開 CI 可重跑 3366 格 DEM 與 77 點數值差，不可能對私人 GLB 作實際回讀測試。

下一輪應以真實、可追溯的**現場道路證據**核查兩端路口、車道淨寬、欄杆、路緣、交通標示、坡面、共用 y 基準，之後才考慮建立全寬掃掠碰撞的可騎候選。沒有通過道路驗收前，不更改 V06 `world.json`、沒有新 navmesh、不合併 main、不部署原網站。

來源與授權：© OpenStreetMap contributors (ODbL)，https://www.openstreetmap.org/copyright；地理院タイル（標高タイル）を加工して作成 https://maps.gsi.go.jp/development/demtile.html 。
