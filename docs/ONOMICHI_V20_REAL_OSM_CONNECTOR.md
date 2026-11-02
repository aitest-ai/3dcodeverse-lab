# 瀨戶內騎行世界 V20｜正式取得新 OSM XML，證明幾何路網已連通（不代表可騎）

## 本輪重大進展
- 利用獨立 GitHub Actions `41394293756`，2026/11/02 05:29:20 UTC 成功取得 OpenStreetMap 官方 API 的 bbox `133.1985,34.3964,133.2060,34.4005`，409700 bytes／SHA256 `5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76`。
- 原始 XML（1,436 節點、154 ways、70 條有 highway 標記道路）已在獨立分支的 `assets/setouchi/osm/onomichi-v20-20261102.osm` 永久保存、另留 `.source.json` 取得時間和授權。透過 Actions `41394692662` 從已驗證的 Artifact 鎖定原檔**不重新抓取後冒稱相同 bytes**。
- `scripts/research/onomichi_v20_route_topology.py` 從真實來源執行，以共同 OSM node IDs 確認 V17 377 終點 `1296327682` 與 Halows V09 路口 `1296327655` 的道路網絡連通；CI `41394899988` 綠燈。
- 只依 OSM 無向中心線長度：含 trunk 國道 317 的最短路徑 **483.06m**；排除 trunk 類道路的幾何候選 **604.10m**、33 nodes／9 ways；到 V09 東側服務道路接點 **660.70m**。先前 V19 的 441.24m 代表**兩份不完整舊快照的幾何距離**，現已找到共同節點連接，並非現場沒路。
- 特別要注意非 trunk 候選的第一個 way `388716484` 同時標示 `access=no` 與 `bicycle=yes`，且算法尚未檢驗任何現地路權、單行道、轉向限制與交叉口。不得直接用於旅行導航或遊戲自動騎乘。

## 私人 V20 交付
- 完整原 V19 + V20：`Onomichi_V20_Full_Original_Runtime_Plus_Real_OSM_Connection_QA.zip`，223591920 bytes，SHA256 `9c43c1e065a7154e4a2484e0c16fe62acf01830ec3ae4438ef69903e1af444ce`，269 files，ZIP CRC PASS。
- 增量：`Onomichi_V20_Real_OSM_Connection_Incremental_Patch.zip`，501281 bytes，SHA256 `00d08b0a82efa57d3955a45091e63e7abb1fa83a531575114593a6630d229fb9`，12 files，ZIP CRC PASS。
- 在新根目錄 `onomichi-cycling-v20/` 用 `python3 server.py --port 8765` 啟動，原步行／騎乘／渡船系統不變；操作說明新增 V20 QA 入口。
- `review/onomichi-v20/V20_Offline_Connected_Road_Atlas.html` 可離線觀看 70 條道路與 3 組候選，已經 Chromium `set_content` 實際測試四個按鈕切換、123 個 DEM 剖面點；有來源 XML、公開原始時間與明顯的非導航聲明。
- `V20_SourceDEM_Corridor_Visual_Only.glb` 是 3 幾何件的**靜態研究 GLB**，用真正 OSM 共用節點 + 原 V19 保存的兩片 SHA 鎖定的 GSI DEM5A 地面資料生成，非瀝青路面、0.32m 寬描線只供標示，不能當真實道路寬度、可騎路面或物理碰撞。
- 原 V19 10 個受保護檔案 SHA256 **全部一致**；原 Node 21/21 PASS。只有 V20 副本的 `index.html` 新增 QA 連結；`data/world.json`、`src/main.mjs`、人物／單車／渡船及六個核心 GLB 不變。
- V20 Three.js 研究頁能以原自帶本地 vendor 和上述 GLB 啟動，但目前測試環境 Chromium 的 localhost 回傳 `ERR_BLOCKED_BY_ADMINISTRATOR`，**未成功證明 WebGL2 真正動作或 GLB 載入**，也未測 Android。不能用離線 2D 切換測試冒稱 3D 實際遊玩通過。

## 仍需優先完成的 Gate
1. 真實 2026 自行車藍線、限制、住宅區 access/bicycle 特別標記、轉向／單行道、危險路口、Halows 店門、路緣坡口及路寬，不能靠 OSM 最短路徑替代。
2. 新的住宅區候選路面標高與 GSI DEM 地面一致性：本輪 123 個 DEM 點 min 1.64、max 7.49m 是**地面估計**，含可能與道路表面不符的高程變化，不能當作可騎坡度；V06 與 V15 完整 y 垂直基準仍不明。
3. 在來源與通行檢查完成後才建立可碰撞的獨立高品質 3D 道路，再對原 V06 真人物、單車、渡船使用完整掃掠／鏡頭／橋上下層與 Android 實測。**現階段零可騎路段加入正式 Runtime**。
4. 所有舊版、main 與原網站不更動，Draft PR 不自動合併。

授權：© OpenStreetMap contributors，ODbL https://www.openstreetmap.org/copyright；日本國土地理院地理院タイル（標高タイル）を加工して作成。Halows 官方汽車流線不應當自行車路線。完整私人 V19/V20 ZIP 不得自動公開上傳。
