# 登別伊達時代村｜V007 R1 商家街近景精修交付

日期：2026-11-01（Asia/Taipei）。**V007 R1 是可供本機測試的工程候選版；並非已在 WebGL、Android 或 Blender 原生環境驗收完成的正式版本。**

## 既有工程與本輪範圍

- **凍結基礎**：V006 R1 Runtime.zip（63 個既有檔），前段大手門／遊戯館／商家街與 231.5664 公尺路線全部沿用。
- **新模型**：`dist/assets/v007_east_facades.glb`，由 V005 兩棟外觀模型 `v005_east_facades.glb`（來源 SHA-256 `f2f579f398334473a5c93a55109e87fae6d175c1be5756c484a368ee07b20afb`）衍生。原始模型仍附在新執行包中，**沒有改寫**。
- 兩棟既有店：草鞋屋 `way/283905573`（日本官方資訊確認是餐飲店，2025-04-01 改裝重新營業）；變裝攝影館 `way/283905580`（官方提供時代裝扮、攝影與服裝租借）。店名／建物底面沿用 V002 凍結 OSM；**外觀並非攝影測量還原**。
- **材質**：修正 9 組原始 PBR Base Color／Roughness 參數，新增 4 張自行生成之低對比木紋材質及 3 張低對比灰泥材質（無付費、無第三方照片貼圖）。
- **暖簾**：只調整 B 場景草鞋屋布面頂點，下緣增加克制垂墜與皺褶，最大頂點位移 `0.01407` m；上緣不動。
- **避免重疊**：先將原 V005 外觀切換為隱藏，再顯示 V007 外觀；V004/V005 原始建物排除契約與 V006 遮罩不變，實際瀏覽器遮罩畫面仍待驗。
- **無新建物、無道路擴建、無室內、無第三人稱**；路徑、碰撞、A/B 切換與來源高品質 B 模型均不更動。

## 實體驗證

1. `v007_east_facades.glb` 已由 `trimesh` 輸出、真正回讀；17 個 mesh、14,888 面，16 個非暖簾 mesh 幾何坐標與 V005 一致。SHA-256 `077e900be4a0591909625b7e1c7b2d8eaa441eb855717da0b9c6b87b7d90b34e`，檔案大小 `632,080` bytes。
2. 原 V006 ZIP 的 63 個既有檔案：**59 個完全相同**；改動僅 `dist/app.js`、`dist/index.html`、`dist/qa.json`、`dist/scene_view.json`。V006/V005 GLB、地形、碰撞、控制與 Three.js 依賴逐位元保留。
3. 原路線 **472 點、231.566414972 m**；A/B 共 **944 個**路線查核及全線雙向步行通過；A/B 相機姿態零漂移（Node 靜態/動作邏輯測試，**不是**瀏覽器 3D 互動實測）。
4. V007 模型 SHA 描述、版本契約、A/B 隱藏／顯示切換與故意竄改 manifest 拒絕載入均通過 Node 測試；未執行完整 GPU 渲染。
5. Chromium 模擬頁面（`page.set_content` + 自訂子資源回應）驗證：**缺少 WebGL 2 時明確顯示錯誤**，沒有開始下載 B 大型模型；離線診斷頁三張 GLB 同鏡位圖可開啟。**本環境的 Chromium 對本機網址 top-level navigation 回傳 `ERR_BLOCKED_BY_ADMINISTRATOR`，故此項不能宣稱真實 HTTP 頁面導覽通過。**
6. 本機無 Blender 執行環境，尚未產生 V007 原生 `.blend`，也無 Cycles 正式同光源畫面、Android 真機測試或私人預覽 CDN／登入驗收。

## 開啟與重建

- 只想在支援 WebGL2 的裝置試用：解壓 `Noboribetsu_Date_V007_R1_Runtime.zip`，在最外層執行 `python start_server.py`，瀏覽 `http://127.0.0.1:8766/`。登入、網路與手機操作尚未宣稱驗收；請自行檢查。
- 不支援 WebGL2：預覽會提示錯誤並連至 `review_v007.html`。也可獨立開啟 `Noboribetsu_Date_V007_R1_Review.html` 看三組同鏡位比較（VTK 診斷，非 WebGL）。
- 其他 AI：讀 `SourceQA.zip` 內的 `README.md`。使用現有封存 V006 Runtime、V005 原始 GLB 及原始腳本重跑，不要拿 V003 或 V004 重新生成。`refine_v007_facade.py`、`integrate_v007.py` 保留 SHA guard，遇來源不符就停。

## 來源與授權

- 園區官方：`https://edo-trip.jp/map/`
- 草鞋屋：`https://edo-trip.jp/facility/waraji-ya/`
- 變裝攝影館：`https://edo-trip.jp/facility/utsuroi-kan/`
- 路線／建物底面：© OpenStreetMap contributors (ODbL)，沿用 V002 凍結快照。
- V002 GSI DEM 衍生高程資料、原先交付來源歸屬與授權保留。
- **不將第三方商家照片或官方圖片打包成場景貼圖**；新增影像材質均以 Python/Numpy/Pillow 程序生成。

## 尚需改善（下一輪真正的驗收項目）

- 以實際草鞋屋／變裝攝影館立面照片逐項核對屋頂、門窗、招牌、柱廊比例；尚未確認不能宣告「實景還原完成」。
- 在可用 GPU 的 WebGL2 瀏覽器測試整段來回、兩棟新舊切換與灰色量體殘留、30/180 frame FPS、手機觸控及錯誤恢復。
- 於 Blender 5.2.3 把 V007 改良正式回寫可編輯母檔、附同光源對照；在此前維持 source-ready candidate，不合併 PR、不變更既有私人網站。