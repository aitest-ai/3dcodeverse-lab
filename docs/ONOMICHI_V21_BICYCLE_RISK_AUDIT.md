# 瀨戶內騎行世界 V21｜OSM 自行車通行權與轉向風險預檢（非導航）

## 版本基底
- 繼承 V20 Draft PR #108，使用 `assets/setouchi/osm/onomichi-v20-20261102.osm` 真正 OSM 官方 XML（SHA256 `5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76`）。
- 不動原版 V06 人物、單車、渡船、場景、V15 Halows，原 `world.json`／`src/main.mjs`／`src/asset-loader.mjs` 和 6 份 GLB 與 V15 GLB 共 10 個受保護檔案逐 SHA256 與 V20 完全相符。
- 本輪不是新造寫實場景，也沒有替道路添加可通行碰撞。原 V06 `node --test tests/*.test.mjs` **21/21 通過**，原網站、main 與其他 Draft PR 均未改動。

## 從真實 OSM 標籤發現什麼？
- 最短候選 `483.06m`：2 個不同 OSM ways，包含國道 317 的 `trunk` way `167631309`（其中 408.70m）。該國道路段為 OSM `relation route=bicycle` ID `2236106` 的成員，**不等於整線合法或安全**。
- 避開 `trunk` 候選 `604.10m`：33 個 nodes、**9 個不同 OSM ways**（若以不連續的段落計算有 10 段），沒有 way 屬於這份快照的自行車路線 relation。
- 東側候選 `660.70m`：33 個 nodes、9 個不同 ways，也沒有 way 屬於該自行車 relation。
- 三個候選都經過 OSM way `388716484`，全長 74.36m。OSM 同時標記 `access=no`、`bicycle=yes`、`foot=yes`、`motor_vehicle=yes`。**OSM 標籤語法上**更精確的運具允許可覆蓋一般禁止，這不一定是矛盾；但是 2026 現場標示、道路所有權與可安全騎乘仍需獨立核對。
- 目前 bbox 中有 1 個 bicycle route relation、0 個 `type=restriction` relation。**沒有該 relation 不能當成所有路口都准轉彎**。兩個 service way 有 `oneway=yes`，另有一條 tertiary way 有 `access=private`；不應套用無向最短路到整個島上。這三個候選沒有直接逆向通過「有明示 oneway 的 segment」，仍不代表符合所有交通法規。
- 原 XML 包含 `node 3918269400` 的不確定性註記「maybe a tunnel or bridge here?」；此資訊屬需現場查核，不應擅自建隧道或橋。可供實際交通／地形證據支持後再進行物理建模。

## 本輪實際產物
- **私有完整工程**：`Onomichi_V21_Full_Original_Runtime_Plus_Risk_Audit.zip`，223627498 bytes，SHA256 `2cca82ed61b012043ed2e560a2b885572032f356373f6bdf2f66b7c2fea84bb3`，276 files；ZIP CRC PASS。
- **私有增量包**：`Onomichi_V21_Bicycle_Risk_Incremental_Patch.zip`，357319 bytes，SHA256 `69b5491dc45db2c4a51e1f68d81f69e06954eb2707067308ccc92b042c3c6f29`，8 files；ZIP CRC PASS。
- 私有工程包含 `scripts/v21_routing_risk.py`（從原始 XML 逐段核對 OSM 道路 ID、標籤及方向）、`scripts/v21_dashboard.py`（產生可攜離線 UI）、`review/onomichi-v21/V21_OSM_Tag_Audit.json`、`V21_Offline_Bicycle_Risk_Atlas.html` 及真正 Chromium 畫面。僅修改原 `index.html` 新增研究入口，保留所有舊版 UI 與原始 Runtime。
- 使用 Chromium `page.set_content` 執行三個候選按鈕與地圖切換：604.10/483.06/660.70m，路線個別不同 way 數 9/2/9，relation 命中數 0/1/0；無 JavaScript 錯誤。**這是離線 2D QA，不是 WebGL2 遊玩或 Android 實測**。
- GitHub 公開分支僅保存已授權的 OSM 研究程式、統計註冊、CI 與交接說明；私有大型 V06 Runtime、人物及 GLB 不公開上傳。GitHub CI 使用公開固定 XML 真正重算道路與標籤，但不會替私有完整遊戲做 3D 實玩。

## 下一輪 V22 不可跳過
1. 優先查實際 2026 住家小路 `388716484` 的自行車通行狀態、標誌、臨街圍欄、路緣坡口與交叉口；住宅區候選不能光靠避開 trunk 就叫「安全路線」。
2. 查 317／377 路口的號誌、轉向規則和腳踏車藍線證據；`route=bicycle` 只能作標註的路徑參考。
3. 自 GSI DEM5A 取得地面高程後，還要有橋面、道路路肩與實際路面標高及寬度；不能將坡線 GLB 當車輪可騎的 road mesh。
4. 真正使用 V06 人物與單車做完整路寬掃掠、上下船、鏡頭與 Android／WebGL2，確認後才能新增獨立可騎 Runtime 候選；目前禁止更新主站與合併 main。

## 來源與授權
- © OpenStreetMap contributors（ODbL），https://www.openstreetmap.org/copyright
- OSM Access 定義：https://wiki.openstreetmap.org/wiki/Key:access
- OSM 轉向限制：https://wiki.openstreetmap.org/wiki/Turn_restrictions
- 本四高速島波海道官方騎車注意事項：https://www.jb-honshi.co.jp/english/shimanamicycling/howto/index02.html
- Halows 向島店：https://www.halows.com/stores/detail/77 （僅供視覺／公開資料參考；官方汽車動線不轉成自行車導航）。
