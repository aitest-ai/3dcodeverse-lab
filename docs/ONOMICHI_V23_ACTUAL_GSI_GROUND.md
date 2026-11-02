# 瀨戶內騎行世界 V23｜377／317 共享入口「真正高程 3D 樣區」交接

## 從 V22 安全繼承
V23 獨立分支 `feat/onomichi-v23-ground-visual-qa` 派生 V22 Draft PR #114。並使用使用者私人 V22 完整 Runtime 建立 V23 副本。只在本地 `index.html` 新增一個獨立 QA 入口；原 `data/world.json`、`src/main.mjs`、`src/asset-loader.mjs`、原 V06 人物、單車、渡船、四區場景、V15 Halows GLB、V20 地形研究 GLB 共 **11 個重要檔案 SHA256 全相同**。原 21 項 Node logic tests 全部 PASS。**未**合併 main、未更新原網頁／路線，不修改其他 AI 的版本。

## 真正 Blender 5.2.3 實際完成的內容
- 來源為 GSI DEM5A `15/28508/13045.png` 原始瓦片 SHA256 `79dc9e009a448aec5726ee1c13906270fef196e92c36286075e5474310318e9c`，依地理院 RGB 公式解碼後，在原地理座標 34.399288575,133.204908475 周圍，取樣 **100×130m、2m 間距、3366 個地面高度值**。這是對原生圖磚*再取樣*，不是較高精度的新地形測繪。數值約 1.48–11.61m，較高部分位於研究畫面西側，非道路高度。
- 原始取樣資料可重現 `assets/setouchi/onomichi-v23-gsi-ground-sample.json`，壓縮高度資料 SHA256 `03726ce15167b760f6a738c1862097c258857299cae7a32353a84931c44cdbf1`，沒有任何道路寬度／路緣估計。
- 固定 OSM 官方 XML（`5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76`）的 way `388716484` 四節點在正確的 ENU 平面位置，以**半徑 9 公分的純可視化標記線**呈現，而不是鋪成瀝青道路或宣稱單車淨寬。四個標示球體只供確認節點，沒有真實柱位意義。
- **Blender 5.2.3 實際成功**：GitHub Actions `41406671236`，官方 Blender 下載 SHA256 核對、來源高度資料驗算、獨立可編輯 `.blend`、GLB、四張 Blender Eevee 真渲染及 SHA256 檢查全部 PASS。Artifact `13124245810`。渲染角度：aerial、route_end、junction_end、terrain_oblique。
- 本地另有直接從原 GSI 網格產生的技術 GLB 和真來源剖面圖；不以第三方照片或 AI 假想街景冒充實景。
- 視覺美術驗收：**目前僅作地理／高程結構預覽，不是寫實街景 ACCEPTED**。沒有真實街屋、道路淨寬、標誌與路緣的已查證資料，不會憑印象生成方塊城鎮。整地精度／平滑處理仍可提升。

## 私人實際交付
- `Onomichi_V23_Full_Original_Runtime_Plus_GSI_Blender_QA.zip`：229,952,461 bytes、299 files、ZIP CRC PASS。
- `Onomichi_V23_GSI_3D_Incremental_Patch.zip`：5,844,829 bytes、15 files、ZIP CRC PASS。
- 兩包包含 `onomichi-cycling-v23/review/onomichi-v23/` 的獨立真正 Blender GLB、四張真 render、來源圖、資料及 `index.html` Three.js 互動檢視入口。完整包另保留原 V22 Runtime 全部檔案；母檔與 Blender 腳本及重現報告保存。若已有 V22，增量包解壓到**新工作副本**，避免覆蓋主網站。
- 新 HTML 的原始 JavaScript 已完成 Node 語法檢查，localhost 的 Python HTTP 200 有回應；**Chromium Playwright 到 localhost 受到 `ERR_BLOCKED_BY_ADMINISTRATOR`，所以不能宣稱 WebGL2／Android 已通過真實操作驗收**。
- 新圖與 GLB 不加入原 V06 `world.json`／任何可騎路段，沒有新增可碰撞 Navmesh。

## 待完成
1. 補到**這段道路專屬**的 2026 道路照片及現行自行車標誌。公開可見的其他國道 317／縣道 377 報導照片可以幫助理解地區，但不是 way 388716484 的確切現地證據；不得作路面及標誌位置的模型重建依據。
2. 對兩端路口核對實際自行車路權、交通指示／單行、路面淨寬、排水溝、欄杆、路緣坡口；OSM `access=no`／`bicycle=yes` 僅能理解為特定運具例外的**資料標籤語義**，不等於現場合法或安全。
3. 取得真正**道路表面高度**與 V06／V15 共用垂直基準；高程 PNG 地面高不等於車輪接觸點／橋面。
4. 完成上述來源、全寬連續碰撞、V06 原真人物／自行車來回、鏡頭及桌面 WebGL2/Android 測試後，才能製作獨立可騎遊戲候選，仍不自動更新網站。

## 授權與查證
© OpenStreetMap contributors（ODbL），https://www.openstreetmap.org/copyright；國土地理院 `GSI DEM5A`：地理院タイル（標高タイル）を加工して作成，https://maps.gsi.go.jp/development/demtile.html。Blender 母檔沒有打包或使用任何官方街景照片像素／字型檔。外部對照可參考尾道大橋區域與島波海道通行限制，但只作背景，不推定這段小路的車道結構。
