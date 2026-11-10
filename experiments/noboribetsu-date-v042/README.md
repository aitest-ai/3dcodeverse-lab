# 登別伊達時代村 V042 R1｜四根木柱與獨立木樑的跨網格接合稽核

V042 **是能操作的輕量獨立 Three.js WebGL2 診斷工具，不是新建築 GLB 或完整園區 Runtime**。本分支從 V041 Draft PR #169 接續。保留全部原始資產與主網站，絕不自動合併或部署。

## 來源鎖定
- 原始 V041 Inspector.zip SHA256 `9561dcbdcb9fab6b173425eb2b0d809744a44882e41bd9018a8fedbb32417b87`。
- 擷取原始 G GLB SHA256 `bced01973a6a4c1909427092175ee924e73a1daed01b0f66608c60c0a91ffc03`、F+G GLB SHA256 `5583d3d9c54eb19ac4396f4a9803e57fe337daeaf70e446c249a5337758d5985`、H GLB SHA256 `9d6ec28e7844c3b522b6b1453426334f36da580808ad78bd4bc3e7c5969463f4`。**三份位元組完全不變**，原 V041 其他十四份 GLB 仍在封存包，不刪除、不覆寫。
- 精簡成 3 份必要 GLB（而非一次載入 17 份），避免本次環境大型 SwiftShader WebGL2 載入逾時。完整 V041 檢視器的那次逾時不算通過。

## 本輪實際的三角面計算結果
直接使用 `wood_dark` 四個柱頂面組 `[20,21]`、`[32,33]`、`[44,45]`、`[56,57]` 確定柱頂中心；依真實模型的三角面，計算垂直向上與 `plaster_offwhite`、`wood_lintel`、`wood_timber` 的投影交會、到木構件表面的 **3D 最短距離**（`trimesh.triangles.closest_point`）。

| 柱頂 | 模型 X,Z | 到灰泥淨距 | 最近木樑 `wood_lintel` | 最近木構件 `wood_timber` | 木樑中心垂直投影 |
|---|---|---:|---:|---:|---|
| P1 | 2.296,45.699 | 0.050 | 0.7074 | 0.5600 | 未命中 |
| P2 | 21.543,45.699 | 0.050 | 0.7074 | 0.5600 | 未命中 |
| P3 | 2.296,56.452 | 0.050 | 0.7074 | 0.8334 | 未命中 |
| P4 | 21.543,56.452 | 0.050 | 0.7074 | 0.8334 | 未命中 |

數值均為既有作者模型單位。**只證明中心垂直射線沒有和上述兩類木構件三角面直接交會**；不代表柱頂周邊沒有其他接合，更不能推定現地木構架沒有承重支撐。最近距離不是結構安全分析。

## 真正實作與測試
- 獨立 Three.js 網頁：G／F+G／H 模型切換、四根柱頂各自放大、顯示全部、診斷彩色量測線、暫藏瓦片、滑鼠與觸控旋轉縮放、JSON/CSV 下載。彩色線與球是只讀標記，**不是新建築構件**。
- SourceQA 包保存完整可重建 `replay_v042.py`、真正計算來源三角面的 `audit_v042.py`、`qa_v042_lean.py`、完整可編輯 `site_source/`、六張實際 Chromium WebGL2 PNG 與結果 JSON。
- 原封 V041 ZIP 以兩個全新空資料夾乾淨重播，**17/17 網站檔案 SHA256 完全一致**；Node JS 語法、Zip CRC、三個 GLB 真實 SHA 核對通過。
- Chromium + Xvfb + ANGLE SwiftShader **真 WebGL2：3/3 GLB 成功載入**，G、F+G、H 切換、四柱、遮瓦、隱藏診斷線與 G 還原皆通過。桌機 5 張、430×932 Chrome 手機**模擬** 1 張，共 6 張真正 WebGL2 截圖，0 JavaScript/console errors。
- **Blender/bpy 未執行**，沒有 `.blend` 或 Cycles；Android 真機、正式私人網站 HTTPS/CDN／原生 WebCrypto 端到端、長期 FPS、實地建築尺寸均未測。

## 交付檔案
- `Noboribetsu_Date_V042_R1_Inspector.zip`：17 檔，SHA256 `d6949e140f0763df1f2608ed5da6c48938192852878e52d18e121d69ac51d139`。
- `Noboribetsu_Date_V042_R1_SourceQA.zip`：44 檔，SHA256 `eedba81e1efd37e47fbdd34e9842be58ce9de0aa7dd2b984d752ad89da353810`。
- 另外有 Comparison.png、完全離線可拖曳 Review.html、完整 Delivery_Report.md、Validation.json。

重建指令（需 numpy 和 trimesh）：
```bash
python replay_v042.py /private/Noboribetsu_Date_V041_R1_Inspector.zip /new/EMPTY_V042
python -m http.server 8765 --directory /new/EMPTY_V042
```
以 Chrome/Edge 開啟 `http://127.0.0.1:8765/`。不支援雙擊 `file://`。完整私有原始資產只存在使用者的舊版 V041 封存包，本 PR 不上傳大型私有 GLB。

**下一步 V043：** 使用 Blender native 驗證木柱與其他獨立橫樑間的可能搭接，需同棟可查證建築資料後再決定是否新增或調整橫樑。保留 V039 G 為完整園區穩定基準，H 不升級。

KEEP DRAFT · NO MERGE · NO DEPLOY · NO SITE OVERWRITE.