# 瀨戶內騎行世界 V16：真正 V06 主 Runtime 復原與 V15 Halows 同場檢視

## 已完成且有原始檔證據
- 已從**使用者私人 ChatGPT 檔案庫**取回真正的 `Onomichi_V06_Runtime.zip`：211MB（210,838,257 bytes）、197 ZIP entries、SHA256 `d9b29904db113a82ab348e4dfed026e05941ae5bdedd5448afda83891efce375`。不是 V05 或本 GitHub 影子生成器。
- 在獨立的新工作副本 `onomichi-cycling-v16/` 完整解壓；原 V06 的 `main.mjs`、人物/單車與 `harbour/onomichi/mukaishima/ferry` 四個 GLB 均逐 SHA256 原封不動。V16 副本 `world.json` 只修正兩筆過期 GLB 資產索引，原 ZIP 的 world 完全保留且修正可逆。原版 Node 測試 **21/21 PASS**。
- 既有世界含土堂－兼吉的渡船模型、三條原路線 `onomichi-approach`、`mukaishima-approach`、`mukaishima-halows-01`；其中 Halows 支線 3 個來源點，長約 55.5m，仍只到 OSM node `8255588823`。此節點距 Halows V09 建築參考原點的球面直線距離 **859.104m**；不是已建道路或自行車導航。
- 完整 V16 候選包（private artifact）在**上述 V06 Runtime 所有原本檔案**上只修改 `index.html` 的 QA 連結與 `data/world.json` 的兩筆 GLB SHA，其他原內容與腳本保持不變。新增 `review/halows-v16/` 獨立展示頁及 `scripts/v16_bridge_gate.py` 逐檔檢查。
- 同頁顯示真正 V15 原始 GLB（SHA `317106f7edaabd87df6d5ff8aef314c00a8a6905ba9b0b6478ee4a60afc765b0`）、真正 V06 人物 GLB 與自行車 GLB，供相對比例、鏡頭與地形 QA；按鈕可選擇開關人物、單車與四條 V09 OSM 中心線。V15 BLEND 母檔、七張 Blender 真 render 與原版 site lock 仍同包。
- 原始真 GLB 離線 VTK 幾何檢視可讀取 V15 314 mesh 和 V06 人物 10 meshes、自行車 139 個 VTK actor；人物的 VTK 材質是近似檢查用色，不是正式美術驗收。該離線圖片不可充當網站已可玩的證據。

## 交付與必要檔案
- 大型完整工程 ZIP：`Onomichi_V16_Full_Original_Runtime_Plus_Halows.zip`（223,010,122 bytes，SHA `5643ce4bb378584ebfe958bef43a35ef32feb54abae5f06cf76dcd617f197b91`）。
- 小型差異／來源 QA ZIP：`Onomichi_V16_Incremental_Bridge_Patch.zip`（12,482,305 bytes，SHA `3ad71423e85988b348565387611ba783aeb7d8cd92d58124862c34813e7d5163`）。
- 兩個 ZIP CRC 全通過；這是**使用者的 ChatGPT 交付檔**，未公開上傳到 GitHub，本公開 GitHub 分支只存來源註冊、審計、驗收規範；其他 AI 不應假設可以從本 repo 直接下載大型私人 ZIP。
- 本地啟動：`cd onomichi-cycling-v16 && python3 server.py --port 8765`。首頁原版 V06；右上角說明連結跳到 `/review/halows-v16/index.html`；後者是**獨立模型 QA**，不是將 Halows 接入可騎行世界。比例檢查的人物／車輛在場景中只是展示位置，不應提交為已認證出生點。

## 仍然 BLOCKED（嚴禁替代說法）
1. **未**將 V15 模型加入 V06 世界 route 或 navmesh，世界路線未改動（僅兩筆資產 SHA 索引修正），也未創建 859m 虛構路線。
2. **未**驗證共同 Y 垂直高程基準；V15 的 2.70m 平台是估計值，不能盲目加在 V06 世界 Y 上。
3. **未**驗證渡船到 Halows 間的實際自行車藍線、東西橋、穿越國道 317 的安全性、停車場入口與人車分流。不得直接推定路權。
4. **未**完成 V16 即時 WebGL2 或 Android 遊玩。原主機內的 Chromium 嘗試連接 `localhost` 回傳 `ERR_BLOCKED_BY_ADMINISTRATOR`。原版 Node 21 項邏輯測試成功與 VTK 圖像，只能代表各自測試範圍。
5. **未**產生新的整體 V06 原生 Blender 環境母檔；V15 `.blend` 是超市候選，並非整個島波海道／V06 母檔。V06 仍保有原版本的 Blender 修補腳本與母檔來源記錄。
6. **未**更新既有網頁、權限或公開分享；main、V06 原版及 V07–V15 均保留。

## 下一步優先方向
- 從真實 V06 `data/world.json` 的 ferry/route endpoints 與 V15 WGS84 origin 入手，建立可核對的向島道路**來源資料採集清單**，而不是從 OSM 幾何距離臆造合法騎行線。
- 取得精確、來源可追溯的路口／藍線／店門照片及地形 Y 對位；完成連續掃掠通行與 V06 角色／自行車碰撞後，才能嘗試獨立延伸路線。
- 使用 WebGL2 真瀏覽器與 Android 實際測試原有碼頭上下船、鏡頭、人物動畫與整體效能；將不同設備的證據分開。

## 來源與授權
- © OpenStreetMap contributors（ODbL）；GSI DEM5A 沿用 V06/V09 的鎖定快照。
- 日本本四高速島波海道騎行規範：https://www.jb-honshi.co.jp/shimanamicycling/howto/index02.html （尾道到向島建議渡船，既有藍線作一般道路指引）。
- Halows 向島店官方歷史照片：https://www.halows.com/stores/detail/77 ，未包含任何官方照片貼圖。

**來源註冊 JSON：** `assets/setouchi/onomichi-v16-source-registry.json`，本分支保留 Draft PR，不自動合併、更新原站或假稱 V16 騎行接通。

## V16 新增可執行的載入完整性修復（實際 QA 發現）

V06 官方交付 ZIP 本身的兩份 GLB（二進位 bytes）沒有損壞，但 `data/world.json` 中 `assets.harbour.sha256` 與 `assets.mukaishima.sha256` 保留 V05 舊版雜湊。 `src/asset-loader.mjs` 會在載入時用 Web Crypto 驗證，必然拒絕這兩份 SHA 不符的資產。

這輪 V16 **只在獨立副本** 將兩筆雜湊修正為 ZIP 內真實 GLB 的雜湊（同 V06 Release Index），不動任何 GLB、route、ferry、main.mjs，原始 V06 ZIP 保留。修正後 6 組主 GLB 與 `world.json` 的 SHA 全部相符，39/39 內嵌圖片解碼通過，21/21 Node 測試通過。

V16 副本 world SHA：`ec06865c6cb69f34c833b981e93df7a511c05e252afb2be278fc4f730e003fd5`。檢查/可逆重現：`scripts/v16_runtime_hash_fix.py`、`scripts/v16_release_gate.py`、`docs/V16_RUNTIME_HASH_REPAIR.json`。

另增 `review/halows-v16/route-gap.html` 與來源鎖定的 `scripts/v16_route_gap.py`：從原本 V06 3 個支線節點實際量得 55.496m，至 Halows 中心仍缺 859.104m **直線距離**，紅虛線不是騎乘道路。已核對官方兩條渡船航路，但 V06 原模型只含土堂／兼吉；檢視頁與獨立 `ferry_registry.json` 不會自行創造第二條可玩航線。

**仍無瀏覽器 WebGL2 或 Android 實際操控通過證據。** 本次只證模型與程式資產索引完整性、Source SHA 與資料幾何 QA。下載 ZIP 需在本對話取得；GitHub PR 不公開散布使用者的原始 211MB 模型。
