# 登別伊達時代村｜V008 R1 實際交付與驗收報告

日期：2026-11-01（Asia/Taipei）

## 這輪真正做了什麼

從完整 V007 Runtime ZIP 衍生 V008。依照登別伊達時代村官方網站既存的草鞋屋舊照，替草鞋屋追加上層窗格背襯、簷下木構端頭與前方石基座。**因草鞋屋 2025-04-01 改裝重新開幕，這只是一份「歷史圖片導向的結構候選」，不是已查證的 2026 實景模型。** 沒有把官方照片作為模型貼圖。

本輪新增 4 組網格、2,120 三角面。由 V007 的 14,888 增加到 17,008，原始 17 組幾何網格全部原樣保持，暖簾不再變更。變裝攝影館本輪只產出「未修改同鏡位」對照，沒有假裝修好其實景比例。

## 確實通過的驗證

- V008 GLB 已由 trimesh 真正輸出、回讀，並逐個對照原始 17 組 mesh 的頂點、面數、面索引：最大頂點差異 **0**。
- V007 Runtime ZIP 原有 **69** 個檔案中 **65** 個逐位元相同；僅 `dist/app.js`、`dist/index.html`、`dist/qa.json`、`dist/scene_view.json` 變動，原模型、路線、碰撞、Three.js 皆保持不變。
- Node 模擬實際程式中 V008 model loader SHA 驗證、被竄改 manifest 拒絕載入、隱藏舊模型跳過下載及 A/B 切換姿態零漂移：PASS。
- A/B 共 944 個導航路線檢查點、全程去回步行：PASS（靜態模擬，不是遊玩測試）。
- Chromium 無 WebGL2 情況可正常顯示錯誤，HTML 比較頁三張真 GLB 的同鏡位圖片載入：PASS（DOM/資源模擬）。
- 從凍結 V007 ZIP 在新資料夾重新建出 GLB、JavaScript、manifest、HTML 等 7 個輸出，SHA-256 全部相同。
- VTK 同鏡位 V007/V008 生成 3 張比較圖片，確認新增窗格材質及簷下結構可見，變裝攝影館外觀與 V007 相同；VTK 不等同 Three.js、Blender Cycles。
- 初次進場少載入兩份不可見的舊 GLB，減少網路傳輸 **1,027,648 bytes**，不宣稱真實載入時間或 FPS。

## 明確未通過

1. 實際 Three.js WebGL2 三維播放（本機 Chromium 144 嘗試多組 SwiftShader/EGL 設定，均無 context）。
2. Android 實體手機，私人網站 CDN、登入與網路載入。
3. Blender 5.2.3 `.blend` 原生回寫及 Cycles 同視角正式渲染。
4. 2025 改裝後草鞋屋的當代實景照片／門窗比例與顏色核對，變裝攝影館實景外觀核對。

## 完整性與版本

- 基礎：V007 Runtime 原封存 ZIP，保存、未覆寫。
- V008 新 GLB SHA-256：`ff6725b1ecb22b455203c69dd4dd194f68c2b356ce17364ad89e09941d4ca4ea`。
- 新 GLB：674,648 bytes；21 meshes、17,008 triangles。
- 原 V007 外觀 GLB SHA-256：`077e900be4a0591909625b7e1c7b2d8eaa441eb855717da0b9c6b87b7d90b34e`。
- 路線長：231.56641497226084 m；472 個節點；A/B 944 個靜態檢查點通過。

## 交付邊界

這是可以下載至 WebGL2 裝置本機試玩的候選包與真正可重建的來源包，不是已驗收完成或上線的新網站。保留 V003–V007 舊分支及全部既有版本，預覽網站不修改。

官方資訊：
- https://edo-trip.jp/facility/waraji-ya/
- https://edo-trip.jp/2025/03/15/warajiya-renewal/
- https://edo-trip.jp/facility/utsuroi-kan/
- 舊官方照片參考：https://edo-trip.jp/wp/wp-content/uploads/2018/04/f0272006b776b4fd294606a2d4a80622-800x600.jpg

## 新增的離線成果檢查

- `Noboribetsu_Date_V008_R1_Review.html` 是所有圖片內嵌的離線比較頁，Chromium 於 1280×800 與 430×932 分別確認 6 張圖載入、3 組滑桿可操作。這不等於 WebGL 三維場景通過。
- 保留 V007 的 `start_server.py` 原檔，額外新增 `start_v008_local.py`（預設 `127.0.0.1:8768`）和 `START_HERE_V008.md`，不對外部署。
- 由全新解壓 V007 ZIP 的目錄再次重建，7 份主要輸出 SHA-256 完全一致；診斷 PNG 在重播時沿用已生成的相同圖片，未假裝重渲染。