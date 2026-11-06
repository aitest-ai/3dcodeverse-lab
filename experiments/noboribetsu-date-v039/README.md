# 登別伊達時代村 V039 R1｜右側三角端牆法線修正

**本 PR 為 Draft。從 V038 Draft PR #153 延伸，但可操作完整遊戲候選由未更動的 V031 Runtime 獨立產生。沒有合併、部署或修改正式網站。**

## 釐清 V038 仍存在的黑色三角缺口

V004 的 `v004_merchant_facades.glb` 中 `plaster_lower` 右側三角端牆 face 13 的法線為 -X，與左側 face 12 相同。右端牆應對 +X 外側觀察方向，卻因單面材質背面剔除而消失，露出後方深色區。

- 原始左側 face 12 indices [8,9,10]，法線 -X，完全保留。
- 原始右側 face 13 indices [11,12,13]，法線 -X；正確候選為 [11,13,12]，法線 +X。
- G 候選 GLB：原 17 個 Mesh、所有頂點與材質不變，只交換 2 個原始索引整數的方向；GLB 只改了 2 個實際位元組，長度不變。新 SHA256 `bced01973a6a4c1909427092175ee924e73a1daed01b0f66608c60c0a91ffc03`。
- F+G 候選：保留 V038 F 的灰泥面下降研究，再修正右側 gable winding；SHA256 `5583d3d9c54eb19ac4396f4a9803e57fe337daeaf70e446c249a5337758d5985`，只在獨立檢視器呈現，尚未美術與現場比例驗收。

## 實際 Chromium WebGL2 的因果驗證

在隔離 Xvfb + Chromium ANGLE SwiftShader 建立真 WebGL2，16 份 GLB 全數載入；屋頂側面、右側缺口近景、右側端牆正視 3 個鏡位，各測原版／原版 DoubleSide 診斷／G／F+G，合計 12 張，加 F-only 一張及 430×932 手機 Chrome 模擬一張，共 14 張 PNG。沒有 JavaScript/console errors。

屋頂側緣鏡位的 DoubleSide 與 G 逐像素完全一致；右側缺口近景差 >10 RGB 的僅 13 個像素，支持問題是背面剔除。G 在不使用雙面材質、不新增覆蓋面、不移動模型的情況下修正缺口。這是現有作者模型內部 bug 修正，不是現地尺寸或古建築認證。

## 首次推出可操作完整園區 V039 Candidate

原封 V031 Runtime.zip SHA256 `57882e06ad6f9256c3150ff562656eb745b24331fe0c9893c777c351dde394f0`，共有 146 檔。全新 Runtime 148 檔，**143 份舊檔逐位元不變**，僅修改 app.js/index.html/qa.json，再增加 README/contract；所有原始 GLB、V031 局部瓦、路線、碰撞、A/B、控制模組均未修改。V039 修正是原始 GLB 經原生 WebCrypto SHA256 與舊 manifest 契約載入後，才於 Three.js 記憶體 clone 幾何，改對一個右端面索引，提供開→關→開按鈕。完整 Runtime 不包含 F 灰泥高程變動。

**真 WebGL2 完整遊戲隔離 QA**：B 精修場景載入 PASS，G 開→關→開切換 PASS，[11,13,12]→[11,12,13]→[11,13,12]；原 V031 瓦片仍可見，W 鍵前進 1.26816 模型單位，沒有 JS error。舊 V031 路線與碰撞仍保留。

乾淨重播：獨立檢視器 62／62 檔案 SHA 一致，完整 Runtime 148／148 檔案 SHA 一致。各 ZIP CRC 測試通過。

## 信任界線和待驗

隔離全園區瀏覽器 QA 需在 about:blank 使用**測試專用 SHA adapter**，該 adapter 的 SHA 對照值已由 Python 對原始真實文件預先驗證，不存在任何 Runtime。自動化瀏覽器直接存取 localhost 遭管理限制 `ERR_BLOCKED_BY_ADMINISTRATOR`，因此**尚未在正式 HTTPS/CDN 執行 native WebCrypto 端對端驗收**。

沒有 Blender/bpy，故沒有 `.blend`、Cycles；Android 真機、私人站、長時間 FPS、第三人稱、同棟建築測量皆未驗。F／F+G 灰泥高度調整不能因 G 的法線修正通過就升級為實景定稿。

## 來源、可重建工程與檔案 SHA

- 原封 V038 Inspector SHA256 `2078d61d53a9f52fcf76064b5abfc05fc7117753be4565d383884f5e40727f38`。
- 原始 V004 GLB SHA256 `132ee6c0add22fbfe4a9872d82cb5e6bed0e2e4f282533b6c61de6c156a7a5e3`。
- V039 Inspector.zip SHA256 `e3858af7ed6000002ac5d240586e10165f5beaa92222f82eebe62c3457a650da`（62 檔）。
- V039 Runtime.zip SHA256 `9f38174114a9661a7e77b14874d21b5eb09237476ad0966bc7b601528a7638d5`（148 檔）。
- V039 SourceQA.zip SHA256 `1af456c27f5bdba30795854e5666a3660304e6bb3ddf1f9f5411b92af1f38c00`（26 檔）。

SourceQA.zip 保存完整 build_v039.py、build_v039_runtime.py、validate_v039_source.py、qa_v039_webgl.py、qa_v039_full_runtime.py、14 張 Chromium 實際截圖、JSON 報告與交付說明。GitHub 本 PR 只保存小型可公開程式、版本合約、執行指引；不推送私人 81MB Runtime 大型場景。

下一階段應檢查原始屋瓦端部與修正端牆的光影接合，並在真正 Blender/正式 HTTPS/Android 環境完成剩餘驗收。與「學問所寺子屋」照片不可混充高等學問所實地測繪。

**DRAFT ONLY; NO MERGE; NO DEPLOY; NO HOST OR PERMISSION CHANGES.**