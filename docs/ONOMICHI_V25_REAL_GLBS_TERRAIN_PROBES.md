# 瀨戶內騎行世界 V25｜真正 V06 人物／單車與可調式 GSI 地形探針

## 版本來源（不可退回粗糙占位）
- 基準為 V24 Draft PR #121，搭配使用者的真正 **V24 完整 Runtime** ZIP SHA `04d20b6e12958fe692a649275a54aac459b4e82c50ace44fcbeccdc5ab0088d8`。保留舊 ZIP 與獨立工作副本。
- 原 V24 `V24_MANIFEST.json` 的 11 個受保護原檔 SHA256 全部一致，包括 `data/world.json`、`src/main.mjs`、`src/asset-loader.mjs`、原角色／自行車／渡船、四個環境 GLB、V15 Halows 及 V20 GSI GLB。原遊戲 Node **21／21 PASS**。唯一舊檔更動為 **V25 副本首頁 `index.html`** 新增 QA 連結。
- 原版 V06 人物 GLB SHA `4dab76c398f4c30c3aa62ef88e389b28974018c01fd271c08bf029d840d263d1`，高度 1.754m；原版自行車 SHA `7cb53e92247cf081354c1551b91ae812aab56be7c07748ed00764f0d2c844ece`，長 1.777m、包圍盒寬 0.595m；V23 GSI 真地形 GLB SHA `a45dc26ca6f4e3d28787148493e4014db6df2f06c709899ccb5cb7a55c2a484a`。**本 GitHub 分支不公開上傳以上私人二進位模型。**

## 這輪真的實作了什麼？
- `review/onomichi-v25/index.html`：獨立 Three.js 檢視器可直接載入私有 V06 人物、單車與 V23 GSI 地形，每一 GLB 由 Web Crypto SHA256 冷驗後才顯示；鳥瞰／377 端／317 端／人車比例四種鏡位與分別顯示切換。
- 直接由 V23 公開的 GSI 衍生格網（100×130m，2m 間距、3366 高度值）SHA `03726ce15167b760f6a738c1862097c258857299cae7a32353a84931c44cdbf1`，依 OSM way `388716484` 真實四節點產生 74.3638m、**77 個中心線取樣點**，提供左右探針距離 **±0.5、0.75、1.0、1.25、1.5、2.0、2.5m**。左右高度差 max 在 ±1.5m 為 **0.2062m**、±2.5m 為 **0.2349m**。每個距離同步變更 3D 細線與 HTML/SVG 剖面。**探針不是路肩、道路邊界、路寬或安全淨空標準**。
- V25 真來源計算圖：`V25_Actual_GSI_Probe_3D.png` 與 `V25_Probe_Comparison_Profile.png`，都是高程研究圖（非 WebGL 截圖／照片）。
- 兩端路口的可編輯現地紀錄：觀察日期、原照片／公文來源 URL、真實量測淨寬（可留 null）、自行車標示、備註，以按鈕匯出 **本機 JSON**。即使輸入寬度，只能算單車外包尺寸的靜態數值，無論多寬都不會自動批准道路。**不下載、上傳或重新散布任何官方照片**。
- 本地可復現與保護：`scripts/v25_probe_source.py` 檢查 GSI SHA、77 點、7 種探針與 11 原檔 SHA。公開同類程式 `scripts/research/onomichi_v25_probe_preflight.py`、CI、來源／私人檔案雜湊 registry。GitHub CI 沒有私人 GLB，僅重算公開衍生資料。

## 實際測試
- V24 真正 11 個原檔逐 SHA256：11/11 PASS；Node tests：21/21 PASS。
- HTML ES module Node22 `--check`：PASS。本機 HTTP GET 頁面：200。
- Playwright Chromium 對本機 `http://127.0.0.1:8765` 回覆 `ERR_BLOCKED_BY_ADMINISTRATOR`：**完整 Three.js 原始 GLB 即時畫面與原遊戲 WebGL2 遊玩未通過實測**。Android 仍未測。
- 另用 Playwright `page.set_content` 在**移除 WebGL 模型載入的獨立 DOM 測試**中成功操作探針滑桿、SVG 及 JSON 匯出，絕非完整 3D 操作證據。

## V25 完整私人交付（GitHub 只有來源與測試，不包含私有 V06 GLBs）
- `Onomichi_V25_Full_Original_Runtime_Plus_Probe_QA.zip` 230515065 bytes／316 entries／SHA256 `9a20f109c0a28cc135655a6fed6853220b2f9b58ac81462b2048bcbba6faeae3`／CRC PASS。
- `Onomichi_V25_GSI_Probe_Incremental_Patch.zip` 476999 bytes／9 entries／SHA256 `07f3a1cbf424c699f16d0c4ffb5d8b0b3042201021c86bbc3b5033988594cbd7`／CRC PASS；只能在 **V24 新副本**套用。
- `Onomichi_V25_Standalone_Original_GLBS_Probe_Viewer.zip` 15116354 bytes／20 entries／SHA256 `7ec083ef58d8ac18a94b2f11418201d0d9390a6348243533a5f7b6cb1392d588`／CRC PASS，內含私有真正 GLB 和 vendored Three.js，不能隨 public GitHub 發布。

## 尚待 V26 的 Gate
1. 取得**這個 74m 路段的 2026 現場照片及路口交通標誌、路緣坡口、障礙物和道路淨寬**，記錄來源時間；其他路口照片不能冒充。
2. 與 GSI 地面高度比對的真正瀝青路面及 V06 世界共同 Y 基準；不可將 ± 探針視為路面橫坡。
3. 真實人物騎姿／單車輪胎全寬掃掠、轉彎與退回、WebGL2／Android 互動測試後，方可建立**獨立**可騎候選。
4. 舊網站、main 與所有既有 V06–V24 不更動；不得自行合併或部署。

## 來源
- OSM 原始 XML SHA256 `5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76`、© OpenStreetMap contributors / ODbL https://www.openstreetmap.org/copyright 。
- 日本國土地理院「地理院タイル（標高タイル）を加工して作成」，https://maps.gsi.go.jp/development/demtile.html 。
- 尾道市交通道路改善規劃：https://www.city.onomichi.hiroshima.jp/uploaded/attachment/58670.pdf （只是區域性資訊，不是 388716484 個別路段的現地證據）。
