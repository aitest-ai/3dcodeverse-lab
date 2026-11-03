# 瀨戶內騎行世界 V28｜原始 V06 自行車雙輪 GSI 接觸、原網格 373 位置掃掠

## 原始版本驗證與未修改界線
V28 確實從使用者真正私有 V27 完整 Runtime（342 個舊檔）建立新工作副本。11 個核心檔（含 world、main、asset loader、角色、自行車、渡船、四區場景、V15 Halows 與 V20 GSI）SHA256 全與 V27 相符。**唯一既有檔案修改**是 `index.html` 增加 V28 獨立 QA 入口；沒有改變 `data/world.json`、主遊戲、渡船、人物動作、模型或已部署網站，也沒有合併 `main`。

V28 本輪首次直接解析原 V06 私人自行車 GLB SHA `7cb53e92247cf081354c1551b91ae812aab56be7c07748ed00764f0d2c844ece` 的 **139 個原始可見網格**。原前後輪 hub 位於車局部座標 `[0, .35, +.54]`、`[0, .35, -.54]`，軸距 1.08m、輪半徑設定 0.35m（真輪胎外緣可見半徑約 0.3485m）。原人物 GLB SHA `4dab76c398f4c30c3aa62ef88e389b28974018c01fd271c08bf029d840d263d1` 真的具有 `Idle/Walk/Cycle` 動畫；沒有代替成簡化人車。

## 真正完成的分析與互動
- 公開來源 OSM way `388716484` 74.3638m、GSI DEM5A 衍生 2m 3366 地面樣本（SHA `03726ce15167b760f6a738c1862097c258857299cae7a32353a84931c44cdbf1`）。以 .2m 間隔分析 373 個位置；在 OSM 折線附近建立**試驗平滑軌跡**，與原中心線最大偏差約 **0.02387m**（不是實際已確認車道中心）。
- 使用**前後輪各自的 GSI 地面**、1.08m 真軸距及原輪胎圓半徑約束，計算輪心高度、車架傾斜與應轉輪數。模型最大俯仰約 **3.316°**、源軌跡模型理論轉向角最大約 **10.077°**。輪子的數學「接地」殘差 0 是方程式**設定**結果，**不是輪胎碰撞或實測車道路面正確**。
- 以原 **139 件真正 GLB 網格**轉換成 XY 世界平面的視覺凸包，再依 373 個位置與路向投影，取得約 **43.5145m² 的抽樣平面聯集**。這比 V27 長方形單點近似精細，但**不是完整 3D 連續碰撞掃掠體**：不包含人物姿勢、車頭真實轉動／側傾、欄杆、路緣與建築。假設通行寬度 1.0–3.0m 的投影外溢面積只供計算，不能當道路合法或安全。
- V28 私人 HTML `review/onomichi-v28/index.html` 引用**既有** `src/avatar.mjs` 的原版 `AvatarDriver`／`BicycleDriver`、原 `Cycle` 動畫、兩份 GLB 和 GSI 地形；提供播放／暫停、里程、速度、假設寬度、前後輪圖、原模型顯示切換與 JSON 匯出。載入原角色與車輛前使用 Web Crypto SHA256 核對。這是獨立研究頁，不是已新增到世界的騎行路段。
- VTK 9.6.2 用真原始自行車網格渲染 3 個不同位置及接地球，產出 PNG；非 AI 生圖、非已完成 WebGL 體驗影片。另有以真高程源資料生成的前後輪剖面、俯仰／理論轉向圖、真模型研究總覽。

## 本地驗收的確切範圍
- 私人 V28 完整專案原 Node 21 項，加上 V26/V27 延伸與 V28 六項，合計 `node --test ...` **37/37 PASS**；原 11 個受保護檔 SHA 相符。
- Chromium 透過 `page.set_content` 測過桌面 1380px 與手機 390px 的 2D 操作、圖表、滑桿與播放按鈕；但 `set_content` 不能載入本機 ES import map 的 Three.js 模組。以 Chromium 真正開啟本機網址得到 `ERR_BLOCKED_BY_ADMINISTRATOR`，**所以尚未通過真 WebGL2 人車動作、騎姿/手腳接觸、Android 或真碰撞測試**。不能稱所有部件動畫已被視覺驗收。
- 目前 **沒有**專屬 way 388716484 的 2026 現場標誌、道路實測淨寬／路緣／障礙物／瀝青高程與合法自行車路權證據。GSI 是地面高程而非正式道路表面。V06 世界與 V15 Halows 的共同垂直基準也還未完成核准。

## 私人交付（保留舊版，不能推到公開 GitHub）
- `Onomichi_V28_Full_Original_Runtime_Plus_Wheel_Contact_Lab.zip`，**235696298 bytes，362 entries**，SHA256 `2b83e637fca50f20eb4237b9ebc3ae52a4264079a686819b44d694c7978905d1`，ZIP CRC PASS。
- `Onomichi_V28_Incremental_Original_Bike_Motion_Patch.zip`，**1784638 bytes，21 entries**，SHA256 `2d80f450ed4d5ca386b233f90c4313a18d818efa1464a0daac6eb4be546d4e64`，ZIP CRC PASS。僅套用在 **V27 全包的獨立新副本**。
- `Onomichi_V28_Standalone_True_V06_Bike_Rider_Viewer.zip`，**16394366 bytes，30 entries**，SHA256 `a6290754d0ab90e0394c172587c1cd844d9293d829e7708420a5cce7076bdcf3`，ZIP CRC PASS；含原版人車、原 `avatar.mjs`、Three.js vendor、GSI 地形、可操作研究網頁。需在本機 `python3 server.py --port 8765` 啟動並驗證 WebGL2。

本 Public Draft PR **不包括**私人 V06 的 211 MB Runtime、原人車二進位或私人觀察資料。只上傳來源 GSI/OSM 再計算器、CI 及這份交接文件；GitHub CI PASS 只能證實公開衍生地面 373 點數學，不等於原私有模型或遊戲動畫在 GitHub 上通過。

## 下一階段 V29
先在可以進行 WebGL2 實際操作的電腦驗收 V28 原人物 Cycle 與原車輪、手抓車把、踏板及視角是否匹配。若發現騎姿漂浮或穿模，優先針對研究流程修正 **pose/contact 的證據**，不要擅自改已封存的人物 GLB。真道路還需要 2026 實測路寬、坡口、標誌與路面高度，之後才能進行獨立可碰撞騎行樣區、Android 實玩與美術升級；主網站、main 和全部舊版不得覆蓋。

來源授權：© OpenStreetMap contributors（ODbL）及日本國土地理院「地理院タイル（標高タイル）を加工して作成」。未採用未授權街景照片紋理或憑印象重建房屋。
