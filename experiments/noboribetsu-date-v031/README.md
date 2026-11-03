# 登別伊達時代村 V031 R1｜局部屋瓦接縫過渡（可回退候選）

本分支堆疊 **V030 Draft PR #131**，不合併、不部署、不覆寫原始 Runtime、模型或私人網站。

## 實際建模
- 以 V030 原本在 V004 高等學問所上層屋面覆蓋的 180 片局部瓦片為來源，維持相同的 x/z 面積、3 個 Mesh、7,200 個三角面。
- V031 新 GLB `assets/v031_v004_roof_transition.glb`：**571,784 bytes**，SHA256 `3971f06b4bbba86432db3df09e486295e57d272f0ba4b187dbc0d4bdc7b1e763`。
- 依原屋面作者幾何擬合平面，在接縫附近漸少瓦片弧度、壓低下緣端面厚度及色調對比，減少整齊深色條紋。自製 3 組 PBR 材質共 9 張程序化紋理。
- **V030 原 GLB 完整保留且與 V031 互斥顯示**：V031 預設開啟，關閉時顯示 V030；舊 V026 窗框、V029 屋簷木作保持正常；A 骨架不新增瓦片。未改任何原屋瓦、屋頂大輪廓、CollisionWorld、472 點路線、導引或玩家控制。
- 只宣稱作者模型內局部美術修正，**不宣稱實測比例、屋脊重製、古建築工程或整棟實景還原**。

## 來源、重播與實測
- 唯一原始基底 V030 Runtime ZIP SHA256：`0f6dc2124eac569301cffaca86e803ade253a160acaa2fe32212b3de6a273172`。
- 143 個舊 Runtime 檔案中 **139 個逐位元不變**，只更新 `dist/app.js`、`dist/index.html`、`dist/qa.json`、`dist/scene_view.json`；另新增 README、V031 GLB、V031 契約 JSON。新版 **146 檔**。獨立空白資料夾重播，**146/146 SHA256 一致**。
- 網頁仍在 Runtime 用原生 `crypto.subtle.digest('SHA-256')` 對新 JSON 與 GLB 做 fail-closed 驗證。隔離測試時預先對真實檔案計算雜湊後所使用的 digest adapter 與觀察 hook **不在 Runtime**。
- 真 Chromium/Xvfb/ANGLE SwiftShader **WebGL2 獨立檢視器**載入 V004/V021/V022/V024/V026/V029/V030/V031 共 8 份 GLB；屋瓦、屋簷、街道三鏡位新／舊各一張共六張 PNG；UI 新→舊→新及原屋頂開關通過、JavaScript 例外 0。Chrome 430×932 直式手機**模擬**通過。
- **完整 B 遊戲**真 WebGL2 載入及 V031 新→V030 舊→V031 新切換通過；原 V026 窗框保持可見，W 鍵實際前進約 **1.26756m**，頁面錯誤 0。
- 近景 PNG 差異較大，遠景很小，不以像素差異等同品質改善或 FPS 加速。

## 外部門檻仍待驗
- Blender/bpy 不在本次環境中，因此**沒有實際生成 `.blend` 或 Cycles PNG**；SourceQA 包的 `src/blender_native_v031.py` 是未執行的 source-ready 腳本。
- Android 實體裝置、正式私人站 HTTPS/CDN/登入、長時效能及同棟現地屋頂尺寸仍待測試。
- 官方園區資料只能提供江戶風格背景；**「高等学問所」不是「学問所寺子屋」**，不能把後者照片當前者的尺寸證據。

## 私人交付
- `Noboribetsu_Date_V031_R1_Runtime.zip` SHA256 `57882e06ad6f9256c3150ff562656eb745b24331fe0c9893c777c351dde394f0`（146 檔）。
- `Noboribetsu_Date_V031_R1_Inspector.zip` SHA256 `661eb6a6d18d4f430ccd0ed1a0b2805548793dd4fe6b662542212dc4e64730e5`（32 檔）。
- `Noboribetsu_Date_V031_R1_SourceQA.zip` SHA256 `465cef192382e919effa98dc0c3aa28230b808fe4e76cab7f1bca2df03c9f571`（33 檔，包括真 WebGL2 PNG、程序化建模/整合/重播/驗收/Blender 未執行腳本）。
- 另有 `Comparison.png`、`Review.html`、`Validation.json`、`Delivery_Report.md`。

重播：將 SourceQA.zip 解壓到工作目錄，執行 `python src/replay_v031.py /path/to/Noboribetsu_Date_V030_R1_Runtime.zip /path/to/NEW_EMPTY_WORKSPACE`；必須使用雜湊符合的原版 V030 封存包，拒絕覆寫現存工作目錄。
檢視器重建需另提供 V030 Inspector.zip，解壓於 `prev_inspector` 後執行 `src/patch_inspector.py`；本版 SourceQA 不重複上傳 V030 的既有大型 GLB。

維持 Draft，勿合併、部署或修改網站分享設定。
