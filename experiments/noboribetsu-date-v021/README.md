# 登別伊達時代村 V021 R1｜商家柱腳與木柱精修（候選）

此版本接續 V020 Draft PR #103，不更動 V020 已建立的 231.5664m／472 點路線、13 個柱廊導引點、原始 GLB、角色控制、碰撞與道路。**勿自動合併、勿部署或覆蓋原有私人網站。**

## 已實際製作
- 從 V020 原始 Runtime 封存包 SHA256 `fa380a356d3365bae441aa664e3ee5e7b3e62a70159c1e48a7896fe485d65e23` 重建。
- B 模型可開關的**視覺表皮**：原 V015 8 處懸空柱腳支撐外層細緻石材斜角，以及高等學問所 8 根木柱細微磨損筆觸。
- 新增獨立 43,988 bytes 的 GLB（2 個 Mesh，合計 704 triangles）與 SHA256 驗證 JSON，維持原生 WebCrypto 驗證；不更動碰撞、路線或任何舊建築 GLB。
- UI「柱腳與木柱細節」可關閉；關閉 V015 原接地支撐時，新的附加表皮也一併隱藏。
- 特別釐清：V016 的 4 個「埋入」數值是兩條連續 0.55m 石基座的 4 個坡地取樣點，**不是 4 根待修壞柱**。本版不抬高建物。

## 驗證界線
- V020 原 119 個檔案中 115 個 SHA-256 完全相同，另外 4 個是 app.js、index.html、qa.json、scene_view.json；新增 1 份 GLB、1 份 JSON、README，總計 122 檔。
- 從未改動 V020 ZIP 清潔重建，122/122 個 Runtime 內容雜湊相同。
- Chromium + Xvfb + ANGLE SwiftShader 確實建立 WebGL2 並載入 B 模型。新增的 2 個 mesh、8+8 對應、開→關→開、V015/V021 聯動均已驗證；QA 僅用隔離 about:blank 虛擬資源與**測試專用** SHA adapter（先由 Python 逐檔驗證真實雜湊）。測試專用程式未寫入 Runtime。
- 同鏡位「細節開／關」WebGL2 PNG 已另行保存；因軟體渲染速度慢，對照截圖的測試行程未正常收尾，與後續完成的開關互動測試應分別看待。
- Android 真機、私人網站 HTTPS/CDN/登入、Blender Native .blend/Cycles、實地柱腳尺寸與材質尚未驗收。新模型是根據既有作者推估幾何的**美術候選**，不是現地數位孿生或安全通行認證。

## 交接與重建
完整 Runtime、SourceQA（含 `build_v021.py`、`patch_v021.py`、`replay_v021.py`、`qa_v021_source.py`、`qa_v021_webgl.py`）、兩張實際 WebGL2 同鏡位圖以及驗證報告，另以獨立交付 ZIP 提供，不將私人大型場景 GLB 放到 GitHub。

本 GitHub Draft 保存契約、版本定位與驗收證據索引，不代表已上線、已合併或 Blender 原生驗收通過。