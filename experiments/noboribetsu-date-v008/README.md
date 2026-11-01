# 登別伊達時代村 V008 R1｜草鞋屋歷史照片導向建築精修

## 基礎版本

- 唯一可信來源：`Noboribetsu_Date_V007_R1_Runtime.zip`（不覆蓋）
- 固定 V007 立面模型 `dist/assets/v007_east_facades.glb` SHA-256：`077e900be4a0591909625b7e1c7b2d8eaa441eb855717da0b9c6b87b7d90b34e`
- V007 `231.56641497226084 m` 步行路線及全部碰撞、A 骨架和 B 模型均凍結

## 已完成的 V008 變更

- 官方舊照片：`https://edo-trip.jp/wp/wp-content/uploads/2018/04/f0272006b776b4fd294606a2d4a80622-800x600.jpg`。該照片出現在官方網站，但網址 /2018/04/ 並非現在外觀時間的證明。2025-04-01 草鞋屋重新開幕，**新模型不聲稱 2026 現況還原**。
- 在 V007 原 17 個網格、14,888 三角面、幾何逐位元近似保留（實際頂點最大差異 0）上追加：二樓窗格背襯（10 片窗格背襯）、20 個簷下木構端頭、22 顆不規則的低矮石基座；合計 4 個新 mesh／2,120 三角面，新 GLB 共 17,008 三角面。
- 不更動 V007 屋頂、木樑、暖簾，沒有更動變裝攝影館、任何道路與碰撞，也不做室內和第三人稱。
- V008 冷啟動不再下載隱藏的 V005（395,568 bytes）與 V007（632,080 bytes）完整立面 GLB；兩份完整資產**仍保留在 ZIP 中**供回溯，實際節省首次網路傳輸 1,027,648 bytes（0.980 MiB），不宣稱固定加速秒數。

## 重建

1. 在新空資料夾解壓 **完整** V007 Runtime.zip。
2. `python build_v008.py <V007>/dist/assets/v007_east_facades.glb <V007>/dist/scene_view.json <work>/outputs`。
3. 用 `render_v008_compare.py` 從實際 GLB 產生同鏡位圖片（需 VTK）。
4. `python integrate_v008.py <V007> <work>`，將 `dist/` 中的候選程式與新 GLB 更新為 V008。**不要在原 V007 位置執行**。
5. `node --check <V008>/dist/app.js`、`node test_v008_contract.mjs`、`DATE_V006_ROOT=<V008> node test_v008_navigation.mjs`、`python test_v008_browser_fallback.py`、`python verify_v008.py`。
6. 若有 Blender 5.2.x，可執行 `blender_v008_facade_master.py` 以新路徑建立獨立可編輯的外觀 `.blend`；本輪未有 Blender，因此目前此步尚未執行。

## 使用與邊界

- `Runtime.zip` 解壓後，執行 `python start_server.py`，於 WebGL2 可用的瀏覽器開啟 `http://127.0.0.1:8766/`；**真實 WebGL2 遊玩與 Android 尚未驗收**。
- 若瀏覽器沒有 WebGL2，會顯示錯誤及 `review_v008.html` 比較頁，未開始下載高品質大模型；此 DOM fallback 已用 Chromium 模擬通過，不等於最終網站 CDN/登入驗收。
- 來源圖片僅以網址列示，沒有放進模型、貼圖、Runtime 或 SourceQA ZIP；新幾何及貼圖來自本專案自行製作。
- GitHub 只放原始程式、結構來源契約及 QA，不上傳私有高品質 GLB；完整二份 ZIP 存私人 ChatGPT 檔案庫。
- 請勿把 `source-ready` 當成 Blender `.blend` 已生成，也不要覆蓋 V007 原正式或候選版。