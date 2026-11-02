# 瀨戶內騎行世界 V19｜雙 OSM 保存快照的道路斷點與通行證據調查

## 本輪不是新造 441m 道路
延續 V18 Draft PR #100 的**真正 V06 Runtime 與 V15 Halows GLB**。這次直接重新讀取 V06 2026/10/31 原始 XML 快照（SHA256 `c972cd5db85ea729f969c0d3db390ad42f4513ccb98a505574a907bf131b3bab`）及 Halows V09 原始 `site_lock.json`（SHA256 `71873821d96c937465fd6cbd3f05d0f6a66c564f4f3cbcd6f6e968b462f2ccf9`），比較**完整道路折線**（不是只比較道路末端）。

已確實比對：
- V06: 3,906 個原始 OSM nodes，737 個 OSM ways，其中 183 個有 `highway` 標記的道路 way，共 857 個道路 nodes。V17 377 路段 frontier `1296327682` 所屬連通道路分量為 86 nodes。
- V09 Halows: 4 條道路、39 個道路 nodes。V06 與 V09 兩份來源 **0 個共用 OSM node ID**。
- 最近道路折線距離約 **441.24m**，由 V06 way `114435640`「向島循環線」（`secondary`）至 V09 way `1384242539` 國道 317（`trunk`）的兩份幾何得出。V06 接近點約 34.3996339,133.2048095，V09 約 34.39696591,133.20125049。
- 請勿把任意 OSM 節點當道路：最靠近 Halows 的 V06 原始「任意節點」約 232.74m，node `6609328051` **不是道路節點**，不能以它宣稱道路缺口縮小或已連通。

**441m 的真正意義**：這是兩份歷史快照內、已保存道路中心線之間的最近幾何距離；不是現地真的沒有道路。V06 原始查詢 bbox 南緣是緯度 34.4028，V09 在 34.397 附近。OSM API 會把原始查詢框內道路的完整 way 引入框外，因此 V06 有部分道路節點在 34.4028 以南，但**不表示框外所有道路都已下載**。要補這段，須拿到同時覆蓋雙方的完整 OSM XML，並與真實自行車路權、藍線、路口、人車分流和高程相互校驗。

## 私人可執行交付
- `Onomichi_V19_Full_Original_Runtime_Plus_Gap_Audit.zip`：223094053 bytes，SHA256 `ef1e9ebe7fc8feee09fa48ee187c9bc00cfeb6dec0097d42129ca41052f647fa`。
- `Onomichi_V19_Connectedness_Incremental_Patch.zip`：397138 bytes，SHA256 `e3ceb24d97d7226e8d93c11ae92650cd4730cb310e4dee48d1b2bd97e4e56a67`。
- 兩 ZIP 均 CRC PASS；從真正 V18 源包用 hardlink 建立**獨立新副本**，僅修改 `index.html` 加入獨立 QA 入口，新增 `README-V19.md`、`scripts/v19_gap_audit.py`、`review/onomichi-v19/`。
- 在 `onomichi-cycling-v19/` 執行 `python scripts/v19_gap_audit.py --v06 data/geo/raw/osm_pilot_bbox.osm --v09 review/halows-v16/site_lock.json --out review/onomichi-v19/manual_audit.json`，需 `pyproj`、`shapely`。原始來源 hash 不合則停止。
- 地圖：`review/onomichi-v19/V19_Offline_Connectedness_Atlas.html`，可單獨開啟；提供 5 層切換、全景／缺口放大、18 筆道路候選及完整 JSON。Chromium `set_content` 模式真實操作切換／表格皆 PASS，`file://` URL 直接開啟被管理員阻擋，**不能稱作原 3D 遊戲已成功實玩**。
- 真實地圖 `V19_Road_Snapshot_Gap.svg` / PNG；紅線為尚未連通之資料間距，不是穿越建築的新道路。
- 保護 V18 的 10 個核心檔案 SHA 全相符；原 Node 測試 21/21 PASS；沒有改世界路線、人物／單車／渡船或 GLB。
- 新 OSM 下載工具有 `--fetch-new`，必須在有網路的環境以另一路徑保存、不可覆寫。當前模型容器 DNS 無法連到 OSM API，經本輪測試仍無新 OSM XML；沒有自行假裝新資料已取得。

## GitHub 公開部分與界線
此公開分支保存 derived registry、安全 CI 與交接文件；**不擅自公開上傳使用者 211 MB V06 ZIP 或私有原始 GLB**。後續 AI 必須向使用者私人交付取得完整包，不應從 GitHub 的這個 registry 假設擁有完整 Runtime。

未通過：2026 路口現況、自行車藍線、國道 317 可騎合法性、完整補洞 OSM、共同垂直 Y 基準、真實 3D 可碰撞道路、WebGL2 動態騎乘、Android、站點部署。保持 Draft PR，不合併 main、不更動原網站與其他 AI 正在製作的版本。

## 後續 V20 Gate
1. 在可連網環境取得 `bbox=133.1985,34.3964,133.2060,34.4005` 的完整新 OSM XML，逐檔保存 SHA256 與取得時間。
2. 先檢查原 V17 的 377 frontier 與 V09 Halows 局部道路是否在同一張最新 OSM XML 的拓樸中**共享真實 node ID**；不能用幾何最近或跨線交叉當連通。
3. 對每段的自行車通行權限、轉彎、路緣、道路坡度、行人／自行車分流及真實照片另外驗證。不能沿用 Halows 官方汽車進出箭頭推定自行車路線。
4. 全部完成後，才能建立獨立可碰撞 3D candidate；整個 V06 Runtime 未驗收不得直接更新網站。

資料與授權：© OpenStreetMap contributors、ODbL https://www.openstreetmap.org/copyright；日本國土地理院 DEM 原始來源鏈保留於 V18。
