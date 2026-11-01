# 登別伊達時代村 V009 R1｜變裝攝影館側牆與模型載入精修

日期：2026-11-01（Asia/Taipei）
狀態：**候選版（source and GLB verified；WebGL2 GPU / Android / Blender-native / private CDN 未驗收）**。

## 版本與保護

- 基礎：完整封存 `Noboribetsu_Date_V008_R1_Runtime.zip`（未修改或覆蓋）。
- 新建候選：`V009-utsuroi-candidate-r1`；原 V003～V008 資產仍保留。
- **231.566414972 m / 472 點路線完全不變**；碰撞、A 骨架、原高品質 B 模型、輸入控制、Three.js 及所有舊版 GLB 均不改。
- V008 執行包 72 個 `dist` 檔案中，68 個逐位元相同；只有 `app.js`、`index.html`、`qa.json`、`scene_view.json` 調整載入及版本資訊。新增 11 個候選版資源。

## 本輪實際建模

- 位置：OSM `way/283905580`，官方確定用途是變裝紀念攝影及服裝租借。官方介紹：https://edo-trip.jp/facility/utsuroi-kan/
- 只修正原 V005/V008 模型中變裝攝影館的「側牆木格柵過密與高度規律」：從一個原始共用 wood_structure 網格中**精確排除 20 組指定木條（240 面）**，新增四組獨立候選幾何（336 面），包括較疏的支柱、低矮木板與木檻。
- 原模型 21 mesh / 17,008 triangles；V009 **25 mesh / 17,104 triangles**。
- **其餘 20 組原始幾何網格保持原頂點、面索引不變**。草鞋屋 V008 二樓窗格、簷下木構、石基座原樣保留。
- 未新造屋頂、門窗、室內、角色；材質及建築側牆的尺寸與形式是作者推估，**並無已驗證的 2026 年立面照片支持精確還原**。外部照片沒有收進模型或 ZIP。

## 真正完成的測試

1. 重新輸出並回讀 GLB，檢查 20 組舊木條精準排除、其餘原始 mesh 保留、全部新增幾何未越出本建築指定局部側牆範圍。新版 GLB 670,128 bytes，SHA-256：`e724542806e99cbd634ccd98eee219a3a69e41f8e26f0bf6bc99c3f683d92620`。
2. 從原始 V008 Runtime ZIP 乾淨解壓重新建模，兩份新版 GLB **SHA-256 完全相同**。
3. Node 對執行碼真實函數進行 SHA/model manifest 檢查、刻意竄改契約拒載、A/B 可見性切換及姿態不變測試，通過；只載入 V009 外觀，不載入封存的 V005/V007/V008 外觀，初始少傳輸 **1,702,296 bytes（1.62 MiB）**。這是明確減少的位元組，不是 FPS／秒數實測。
4. A/B **944 個路線點檢查**、全路線往返與碰撞模擬通過，無卡住、無視角漂移（**Node 靜態模擬，不是 GPU 遊戲**）。
5. 以 VTK 真正重讀 V008、V009 兩份 GLB，固定鏡頭與燈光產生四組側牆、屋簷、行走視角與草鞋屋控制對照；**不是** WebGL2 遊戲畫面、也不是 Blender Cycles。
6. Chromium 144 的桌面及手機尺寸 `page.set_content` 比較頁測試：8 張真渲染圖片載入、4 個滑桿可操作（DOM 測試）。
7. 本機 Python HTTP 伺服器的 12 個資源請求均回應 200，檔案內容與執行包完全相同。
8. Chromium 四種 WebGL2／SwiftShader 設定均無法建立 WebGL2 context；未冒充成真實 3D 遊玩測試。

## 還不能宣稱完成

- V009 **真正 Three.js WebGL2 3D 遊玩**、Android 真機、私人部署 CDN/登入、記憶體與 FPS、WebGL 丟失後恢復。
- Blender 5.2.3 原生 `.blend`、Cycles 同視角回讀及完整園區 Blender 母檔。`blender_v009_extension_import.py` 是可重跑腳本，**本輪未執行 Blender**。
- 變裝攝影館 2026 年現況立面比例／門窗分布的照片查核；現有模型是美術假設。

## 交付

- `Noboribetsu_Date_V009_R1_Runtime.zip`：完整 V008 高品質執行場景 + V009 外觀與新契約 + HTTP 啟動器、比較頁。
- `Noboribetsu_Date_V009_R1_SourceQA.zip`：可重播的程式、單獨 GLB、幾何及路線 QA、四組同鏡位來源圖與交接 README。
- `Noboribetsu_Date_V009_R1_Review.html`：完全離線內嵌圖片的四組可拖曳對照。
- `v009_utsuroi_facade.glb`：獨立外觀模型，只包含商家街兩棟外觀，不是整個園區或原 B 場景。
- `Noboribetsu_Date_V009_R1_SHA256.json`：交付品雜湊。

以 V008 為來源建立獨立 GitHub Draft PR，未合併、不部署、不覆寫任何舊版。