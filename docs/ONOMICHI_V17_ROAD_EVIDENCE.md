# 瀨戶內騎行世界 V17｜向島 377 道路中心線來源與斷點驗證

## 這次是什麼進度？
本輪不再反覆修 Halows 建築外牆；以 **V16 私人真正 V06 Runtime** 為基底，對 2026-10-31 保存的 OSM 原始快照做確切路網拓樸研究。能從既有支線終點 node `8255588823` 接上 OSM way `114435640`「向島循環線／縣道 377 號」的**22 個真實節點，21 條路段，累計 565.335 m**（WGS84/ECEF 轉 V06 東-南平面測量）。這段路在 OSM 標記 `secondary`、`lanes=1`、`maxspeed=40`、`asphalt`，但**不能**推定自行車合法、藍線、實際有效路寬、現在是否施工或安全過街。

道路最南研究端點 `1296327682` 與 Halows V09 道路快照的 `1296327655` 最近距離 **441.235 m（直線）**；兩份快照沒有確認可共用的道路節點。該缺口可能有現存道路但當前兩個快照沒保留完整資料，不代表道路實際中斷。**不得用直線補出路面、連接 navmesh 或替人物自動尋路。**

## 成品及驗收
- 保留 V06 原版車、人物、渡船與主程式。V16 修復的兩筆 `world.json` 資產 SHA 索引不改。 V17 僅增加 `review/onomichi-v17/index.html` SVG 離線地圖、`scripts/v17_route_evidence.py`、JSON 來源與地理圖，再在 V16 已修改的 `index.html` 加一個 QA 入口。
- V17 完整私有 ZIP：`Onomichi_V17_Full_Original_Runtime_Plus_Road_Atlas.zip`，221910191 bytes，SHA256 `2ce3c1414046349558fadefd77f2b6ca5dd44902f5f418f468fc5c1d936541b8`；ZIP CRC PASS。
- V17 增量 ZIP：`Onomichi_V17_Road_Evidence_Patch.zip`，42609 bytes，SHA256 `e25439de26ec24c965b2b62865a3cbe720279f65172a33fa7cba4b5bb1845b5a`；ZIP CRC PASS。
- 真實 V06 Node 測試 `21/21 PASS`；10 個受保護原始 V16 檔（world、main、loader、六個核心 GLB 及 V15 Halows）SHA 全部不變。檢視頁的 SVG/HTML 和按鈕已作靜態結構及 JS 語法檢查；本環境 Chromium 讀 `file://` 時回傳 `ERR_BLOCKED_BY_ADMINISTRATOR`，因此**沒有**真瀏覽器互動／WebGL2／Android 實測通過證據。
- 原始完整 V06 ZIP (211MB) 是使用者私人 ChatGPT 交付，**不公開上傳 GitHub**。此 Public PR 只包含 22 個 ODbL 衍生節點、來源鎖定、CI 及交接說明。CI 僅核對精簡來源拓樸／距離與未批准門檻，不代表已重新讀取使用者私人 211MB 原始檔。完整離線 Python 工具在私人 V17 ZIP 中。

## 下輪不得跳過的項目
1. 取得覆蓋剩餘 441m 的新鮮可追溯道路資料及一致路口 node，並與 V09 site lock 確認轉彎、無路緣阻隔或建築穿越。
2. 官方藍線以現地標記／最新可靠照片查證。Halows 汽車進出示意圖**不等於**自行車進店或合法駐輪動線。
3. V06 海面／道路 `y` 與 V15 店區平台 +2.70m **尚未對齊**；新增研究路段 22 節點 `height_m=null`，不允許生成可通行 3D 道路。
4. 使用真正 V06 人物與自行車，以全寬掃掠、橋上橋下、渡船上下船／鏡頭／碰撞和 Android/WebGL2 分別驗證。不得以 Blender/Node CI 當成實玩通過。
5. 遵守原網站由獨立工作流處理、不改 main、不自動合併 PR、不覆蓋任何舊版。

## 來源與授權
- OSM 2026/10/31 保存快照 SHA `c972cd5db85ea729f969c0d3db390ad42f4513ccb98a505574a907bf131b3bab`，© OpenStreetMap contributors、ODbL：https://www.openstreetmap.org/copyright
- 日本本四高速藍線與尾道—向島渡船：https://www.jb-honshi.co.jp/shimanamicycling/howto/index02.html
- 尾道市兩條渡船：https://www.city.onomichi.hiroshima.jp/soshiki/32/65681.html
- Halows 官方外觀與車道示意（車流箭頭不是單車路線）：https://www.halows.com/stores/detail/77
