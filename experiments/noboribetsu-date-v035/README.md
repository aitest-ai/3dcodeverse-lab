# 登別伊達時代村 V035 R1｜白色橫帶兩面分離與三版本比較

**V035 是 Inspector-only、QA candidate。完整園區沿用 V031 Runtime，不修改、不部署、不合併、不覆蓋任何舊版。**

## 為何修正 V034 的面索引判斷

V034 已證明白色橫帶來自原 V004 的 `plaster_offwhite` (48 三角面)，但原先定位的 **20/21 號面**雖為水平面，在當前屋頂攝影機角度下並不是實際露出的橫帶。V035 透過真 WebGL2 著色隔離，確認可見的是 **8/9 號面**，來源 glTF index buffer 依序為 `[3,7,6]`、`[3,6,2]`。

- 原 V004 GLB SHA256：`132ee6c0add22fbfe4a9872d82cb5e6bed0e2e4f282533b6c61de6c156a7a5e3`
- `plaster_offwhite` 原本 48 triangles、32 vertices；實際分離 2、保留 46，其他建築 GLB 逐位元不變
- 8/9 面是 x 約 20.1475、z 約 11.7526 的原模型水平上表面，y 約 6.72852。這些數值都不是現地測繪
- A：只將兩面的灰白色轉成稍深的暖灰；B：只把其中一側在模型內下調 0.035，屬**可能產生新接縫的診斷候選**，不得直接當成修復成功

## 真正完成的交付與測試

使用未修改 V034 Inspector ZIP SHA256 `b631c6d0fbed245a493a087848dc6ceaf94373d9da6de4ada8349a3b97fa7040` 作基底；V034 41 個原有檔案中 39 個完全不變，只修改 `index.html`、`app.js`，新增獨立候選面 GLB、README 和驗證 JSON，V035 共 **44 檔**。新空白目錄重播 **44/44 SHA256 完全一致**。

真 Chromium + Xvfb + ANGLE SwiftShader **WebGL2 PASS**：10 份原始 GLB 載入、屋頂近景／簷口近景各三版本共 **六張真截圖**、模式切換和 V034 隱藏灰泥聯動通過、JavaScript page errors 0、console errors 0。430×932 Chromium 手機**模擬** WebGL2 模式切換通過，並非 Android 真機。

固定屋頂鏡位，A 與原版不同的像素（最大 RGB 單通道差 > 10）約 **39,510**；B 約 **7,572**。這只是圖像差異，**不等於歷史正確性或美學提升**。

**藝術審核：A/B 均未定稿，完整遊戲未更新。** 尚未有可靠同棟屋頂現地比例，無 Blender/bpy，所以沒有原生 `.blend` 或 Cycles；Android 真機、私人站 HTTPS/CDN/登入及完整遊戲均未驗收本版。

## 程式交接

GitHub 此分支包含小型可重用 `roofBandExtractor.js`（實際將 48 面分成 46+2，顏色或局部坡面可逆切換）及品質契約。完整可重建、可操作的 Inspector 及 Python/Playwright 測試在使用者交付的 **SourceQA ZIP**，不是只有 README。沒有上傳私有大型 3D GLB。

重建（需 Python numpy/trimesh）：`python source/build_v035.py V034_Inspector.zip NEW_EMPTY_DIR`

啟動：解壓 V035 Inspector.zip；執行 `python -m http.server 8765`，用 Chrome/Edge 開啟 `http://127.0.0.1:8765/`。也有完全離線的 HTML 滑桿比較頁。

## 版本封存 SHA256

- V031 完整遊戲 Runtime（未修改）：`57882e06ad6f9256c3150ff562656eb745b24331fe0c9893c777c351dde394f0`
- V035 Inspector.zip：`9aba85e945cc4a6cf7a465c867933aaee5570af34ef08453b3fdd0107beda7b1`
- V035 SourceQA.zip：`05b058a6ce797a5457fc6471bbd67d3f684f2e1d990d0a0d99196613df5489b8`
- 新 `v035_band_variants.glb`：`f34a75e9ea5dcd223b4831f174ff452deec9040ca4fe5bb21a1dbc170983bec2`

下一輪應尋找**同棟高等學問所**的完整屋頂照片，並在 Blender Native 原生環境確認屋面與側面是否連續，不能因一張 WebGL 改色成功就把白帶刪除。

**Keep Draft / NO MERGE / NO DEPLOY / NO CHANGE TO PRIVATE HOST.**
