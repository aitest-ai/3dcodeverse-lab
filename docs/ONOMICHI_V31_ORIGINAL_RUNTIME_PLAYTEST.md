# 瀨戶內騎行世界 V31｜真 V28 原版騎行遊戲本機驗收工作臺

本輪針對 V30 的最大缺口：V30 只播放原版 glTF 的 Cycle 片段，但**沒有操作真正的 V06 遊戲主程式**。V31 不再新建一套假單車控制器；改為讓使用者的**完整原始 V28 Runtime**在本機獨立副本中執行，透過附加的 V31 被動面板記錄真正按鍵／操控嘗試，並人工勾選步行、騎乘、轉彎、鏡頭、渡船、手腳接觸的實際表現。

**重要限制**：本輪無法在雲端工作環境取出使用者 235MB 的私人 V28 Runtime ZIP，因此本公開分支只有驗證器、面板、程式與測試，不含原角色／自行車／街景／渡船二進位。GitHub CI 的 Chromium 操作測試使用**明確標示為合成的空白遊戲**，不代表原版遊戲已通過操作。

## 原始來源與不可更改內容

唯一接受的完整 V28 ZIP：
- 檔名：Onomichi_V28_Full_Original_Runtime_Plus_Wheel_Contact_Lab.zip
- 大小：235,696,298 bytes
- SHA256：2b83e637fca50f20eb4237b9ebc3ae52a4264079a686819b44d694c7978905d1
- 原紀錄 362 個項目；實際 ZIP 內的唯一程式根路徑由工具自行判讀。

使用 V26–V28 跨版本不變的 11 核心檔逐位元 SHA，以及 src/avatar.mjs 原始 SHA，共**12 項來源驗證**。包括 data/world.json、src/main.mjs、src/asset-loader.mjs、src/avatar.mjs、原人物 GLB、原單車 GLB、四區場景 GLB、Halows V15 GLB 及 GSI 研究 GLB。檢查程式會嚴格拒絕不同 SHA，不能選不相干的 V27、V30 獨立檢視器 ZIP 代替真 V28。原始檔永遠只讀；輸出若已存在則直接拒絕覆蓋。

從 ZIP 解出的獨立工作副本中：
- 所有原始 src/、assets/、data/ 保留；
- 只有副本的 index.html 在結尾**新增一行**觀察器載入標記；
- 只新增 review/onomichi-v31/observer.mjs、observer_ui.html、index.html、audit.json；
- **不變更** original src/main.mjs、src/avatar.mjs、data/world.json、任何 GLB 或 navmesh；
- 不改 public main、不合併舊 Draft、不更新已部署的網站。

## 實際使用（Windows）

先從本輪 GitHub Actions Artifact 下載 V31 工具包並完整解壓，確認頂層同時有 scripts/ 與 apps/ 資料夾。原本的 V28 完整 ZIP 請保留於你電腦其他位置，不要解開覆蓋既有瀨戶內資料夾。

在工具包根目錄開啟終端機，以自己的實際路徑替換以下示意路徑：

    py -3 scripts\research\onomichi_v31_local_runtime_gate.py --zip "D:\瀨戶內\Onomichi_V28_Full_Original_Runtime_Plus_Wheel_Contact_Lab.zip" --out "D:\瀨戶內\Onomichi_V31_Original_Playtest" --serve

接著在同一台電腦開啟：

- 本機驗收入口：http://127.0.0.1:8767/review/onomichi-v31/
- 真正原遊戲副本：http://127.0.0.1:8767/

原遊戲頁面的右下角會出現 V31 記錄器。按「開始記錄」後，按原遊戲既有的鍵盤／滑鼠／觸控方式操作；依畫面親自勾選通過的項目，按「停止」並下載 JSON。請另外截取問題畫面，例如手沒有抓住車把、腳沒踩踏板、鏡頭進牆或渡船無法操作。**本工具不會用自動路線替代操作，也不會把事件計數當成成功騎行證據。**

本機伺服器只監聽 127.0.0.1，其他電腦／手機不能直接連入。需要 Android 真機驗收時應另規劃安全的預覽通道，不能把本機測試等同實機完成。

## 系統如何保存證據

- 只記錄 W/A/S/D、方向鍵及少數遊戲操控按鍵的代碼與時間，不記輸入框內容；
- 記錄按鈕 ID、指標種類（滑鼠／觸控／筆），不記滑鼠位置或 GPS；
- 記錄 Canvas 數量、視窗尺寸、觀察器自身 RAF 頻率、JavaScript／資產錯誤類別；
- 逐項人工確認步行、進出單車、轉向、鏡頭、渡船、騎姿；
- 每次最多保留 5,000 筆操作事件；達上限後只計丟棄筆數；
- 產出本機 JSON，不上傳到網路；
- 明確標記 observer FPS 並非 Three.js 遊戲 FPS，操作事件不是輪胎碰撞或真路權證據。

## GitHub CI 驗證內容

1. Python zip 路徑穿越／重複大小寫／惡意 symlink／檔案過大／覆蓋拒絕與來源 hash gate。
2. Python 架設**合成、非原遊戲**的 ZIP，確認原來源不更動、副本可新增觀察器，且審核紀錄只標示 SYNTHETIC_FIXTURE_NOT_REAL_GAME。
3. GitHub Actions 真 Chromium 打開合成頁面，按 WASD、點騎車按鈕，檢查觀察器記錄與 JSON 下載、桌機及手機大小版面。這不是實際 V28 角色、渡船或街景實測。

## V31 完成／未完成

已完成：原 ZIP 來源鎖定、12 檔 SHA 保全、獨立原遊戲副本建立器、被動操作／異常記錄器、人工驗收清單、JSON 匯出、合成操作自動測試。

**尚未完成**：在此工作環境以真 V28 ZIP 執行遊戲，量測 original AvatarDriver/BicycleDriver 的內部狀態、車輪與踏板物理更新、真 WebGL2 騎姿接觸、原三條路線、渡船與 Android 完整實玩。現地 2026 自行車路權、道路寬度／地面坡口／路緣／碰撞也未核准。因此沒有新可騎 Halows 連接路，也沒有主網站部署。

**V32 的明確接點**：等 V31 真原遊戲本機副本的畫面及原 src/avatar.mjs／src/main.mjs 合約回讀後，針對真實 AvatarDriver／BicycleDriver 內部狀態建立安全的唯讀 hook，取得人物手腳與車把踏板的真模型世界座標。接著解決騎姿問題，才談可騎場景擴張。這比猜想控制器 API、重造簡化人物更能保住已有品質。
