# 登別伊達時代村 V040 R1｜F+G 降低屋面後的原始柱頂外露稽核

**獨立可操作 Inspector／QA，不是新版完整園區 Runtime；繼承 V039 Draft PR #160。保持 Draft，勿合併、勿部署、勿改原有權限。**

## 本輪具體成果
沿用 V039 Inspector（SHA256 `e3858af7ed6000002ac5d240586e10165f5beaa92222f82eebe62c3457a650da`），封存的 **17 份原始 GLB 逐位元不變**（其中 16 份供 WebGL2 載入）。
新建可操作 V040 3D 檢視器：以 V039 G 經過驗證的端牆方向修正為基準，在**記憶體內複製模型**調整 `plaster_offwhite` 四個共用角點的高度；滑桿 0–0.225 模型單位。原先模型仍完整保留。亦可切換封存的 F+G，顯示 4 處木柱頂部診斷橘框，點選場景查詢 Mesh／三角面。

## 已查證的根因
- G 基準灰泥上表面 Y = `6.728520393`，原模型 `wood_dark` 四組柱頂頂面 Y ≈ `6.678520679`，原本高差 = −0.0500 模型單位（木柱頂面藏在灰泥下方）。
- F+G 降低灰泥面 −0.225，屋面 Y ≈ `6.503520489`，四組原有木柱頂面因此高出灰泥約 **+0.1750 模型單位**。木柱頂面原始三角面索引配對：`20/21`, `32/33`, `44/45`, `56/57`。
- V039 封存畫面出現棕色小塊，以真正 Chromium WebGL2 Raycaster 反查，命中原始 `wood_dark` face 56。這不是新產生的漂浮物，而是既有柱體頂部因 F 降低灰泥屋面而外露。
- 若下降量大於約 **0.050 模型單位**，柱頂在高度上開始超出灰泥平面；但某個鏡位是否可見仍受瓦片與其他構件遮蔽影響。這些都是作者模型內部位置，不是現場測量值。

## 真正 WebGL2 與完整來源驗收
- V039 原 Inspector 62 個檔案中 **59 檔逐位元不變**；只有 `app.js`、`index.html`、`style.css` 修改，新增 README、ZIP manifest、工程契約、Windows 啟動器，V040 **66 檔**。從未改的 V039 ZIP 在全新目錄重建，**66/66 SHA256 一致**。
- Xvfb + Chromium + ANGLE SwiftShader **真正 WebGL2 16/16 GLB** 成功載入，桌機 7 張真截圖與 Chromium 430×932 手機**模擬** 1 張，無 JavaScript 或 console error。
- 動態滑桿下降 0.225 與封存 F+G：全部 V004 灰泥頂點最大差 **0**，同鏡位畫面差 **0 像素**。非灰泥四角的原始網格頂點沒有改動。橘框 4 個柱頂模型檢查通過。
- G 和下降 0.100 的畫面約 12,416 像素最大 RGB 通道差 >10；G 和下降 0.225 約 27,623 像素。這是可見差異，不是美術提升或效能加速證明。

## 工程決策
**保留 V039 G 為最新的完整園區隔離 QA 候選；不要把 F+G 的高程調整升級。** G 的右側端牆面朝向修正有獨立工程原因、已通過 V039 完整 B 場景操作驗收。F+G 雖能縮減寬白帶，但也會露出原先被遮蔽的木柱，缺少同棟建築照片／Blender 原生環境的接合驗收。

Blender `.blend`／Cycles、Android 實機、私人 HTTPS/CDN/登入、現地尺寸與長時間 FPS **未驗**。V040 沒有產生或修改完整遊戲 Runtime；原有 V039／V031 網站與碰撞保留。

## 交付及重建
- `Noboribetsu_Date_V040_R1_Inspector.zip`：66 檔，SHA256 `800439290b4415deaf691d4e9e369b34a091573a8277be27a6051bd860fbc168`。
- `Noboribetsu_Date_V040_R1_SourceQA.zip`：21 檔，SHA256 `b60a5384c9c5f9312de71c8402b6c5d8a41dce9ece53bd98b98e18a5f69c5b73`。
- 另有 WebGL2 四格 PNG、完全離線可拖曳 Review.html、Delivery_Report.md、Validation.json。
完整 Python 建置、GLB 來源 QA、Chromium WebGL2 QA、二次重播及八張證據圖均在 SourceQA ZIP。GitHub 本 PR 保存來源定位、數學與幾何 QA 契約及可公開的小程式，不上傳私有 GLB。

使用 V039 原封 ZIP 重建：
```bash
python source/build_v040.py Noboribetsu_Date_V039_R1_Inspector.zip NEW_EMPTY_V040_INSPECTOR
python source/qa_v040_integrity.py Noboribetsu_Date_V039_R1_Inspector.zip NEW_EMPTY_V040_INSPECTOR
python source/qa_v040_geometry.py NEW_EMPTY_V040_INSPECTOR V040_geometry_QA.json
xvfb-run -a python source/qa_v040_webgl.py NEW_EMPTY_V040_INSPECTOR EVIDENCE_DIR
```
Windows 啟動獨立檢視器可使用 `START_V040_Windows.bat`；或在檢視器資料夾執行 `python -m http.server 8765`，以 Chrome/Edge 開啟 `http://localhost:8765/`。

官方園區建築背景：https://edo-trip.jp/tw/about/（無該棟屋頂精確尺寸；不得混用「學問所寺子屋」照片）。

**DRAFT ONLY. NO MERGE, DEPLOYMENT OR SITE OVERWRITE.**
