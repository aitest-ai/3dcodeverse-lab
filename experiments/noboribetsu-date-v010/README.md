# 登別伊達時代村 V010 R1｜真正 WebGL2 驗收與低幀率控制修正

**版本：V010-controls-candidate-r1**；世界模型仍使用 V009，不重做任何建築、路線、材質或碰撞。V002～V009 及其 GitHub PR 原封保存。

## 本輪新增可驗證成果

- 在獨立 Xvfb 顯示環境使用 Chromium + ANGLE SwiftShader 建立**真 WebGL 2.0**，並真正解析 V003 高品質 B 模型、顯示 231.5664 m 場景；首幀渲染器資訊為 1,431,986 個三角面、94 geometries、47 textures（桌面測試）。
- 由 Python 針對 B 的 23 個 gzip 分片解壓重算完整 SHA-256，並核對 A 與 8 個擴建/外觀 GLB，全部與原 manifest 符合。
- 真 DOM / Chromium 事件測試：進場、入口／街尾按鈕、A 首次延後載入、A/B 切換零姿態漂移。
- V009 舊程式在軟體繪圖慢幀率環境下，按住 W 約 0.85s 測得 0m；V010 同條件下實際前進約 1.03m、放手漂移 0m。
- 手機直式 **Chromium emulation（非 Android 真機）**：雙指左搖桿 + 右拖曳環顧，測得約 0.83m 移動、放手漂移 0m，環顧約 7.02°。
- 舊 Runtime 96 份檔案只有 `dist/app.js`、`dist/input-events.js`、`dist/index.html`、`dist/qa.json` 修改，另新增 `start_v010_local.py`；其餘 92 個檔案包含完整模型均 SHA-256 完全相同。

- 從原始 V009 ZIP 全新解壓、套用 V010 補丁重新建置，與交付版 98/98 份檔案的 SHA-256 完全一致。

## 非常重要的測試界線

1. 此管理環境不允許 top-level localhost 或 HTTPS 導覽，採用 `page.set_content` + 子資源攔截。此 `about:blank` 頁面不是 secure context，因此**測試程式使用限測試用 SHA adapter**：按已獨立驗證的完整 GLB 位元組長度回傳該 GLB 預先核對的 SHA。它不會在 Chromium 內對該 buffer 再算一次 SHA。因此「模型獨立 SHA 檢查」和「WebGL2 遊戲整合」均通過，但**真實網站 HTTPS/WebCrypto 端到端未驗**。
2. 這個 adapter 只存在 `scripts/isolated_webgl2_test.py` 的隔離測試中，**絕對不可複製到正式程式或部署**。正式 Runtime 的 `model-codec.js` 原封保留，真正使用 `crypto.subtle.digest()`。
3. SwiftShader 是軟體繪圖，不代表使用者電腦/Android 的 FPS、GPU 記憶體或熱負載。軟體幀率非常低，雖然 V010 操控修正有效，仍不能聲稱正式高流暢度驗收通過。
4. 私人網站 CDN、登入、Android 真機、Blender 原生 `.blend` / Cycles 尚未驗收。三維商家外觀仍是作者估計，不是官方立面測量。
5. **視覺已知缺陷**：231.6m 街尾真實 WebGL 畫面有左側鋸齒狀黑白地形接縫，未修正，不應隱藏或合併為正式版。

## 開啟與重建

把 `Noboribetsu_Date_V010_R1_Runtime.zip` 解壓到**新資料夾**；使用 Python：

```bash
python start_v010_local.py 8770
```

在同一台電腦打開 `http://127.0.0.1:8770/`。Chromium 將 localhost 視為安全來源，正式 WebCrypto 應可工作；此流程尚需由有完整 GPU/一般瀏覽器的裝置實測。

用 `scripts/native_local_origin.py` 對一般環境的真 localhost 執行端到端測試（**不使用 SHA adapter**）：

```bash
python scripts/native_local_origin.py /path/to/unpacked/V010_runtime --out /path/to/results
```

若所在管理環境禁止 browser top-level navigation，該測試會**失敗並明確記錄**，不能改報 PASS。

受管理容器的隔離 WebGL2 驗證（需安裝 Playwright、Chromium、Xvfb）：

```bash
DATE_DIST_ROOT=/absolute/path/V010_runtime/dist \
DATE_QA_DIR=/absolute/path/results \
xvfb-run -a -s '-screen 0 1280x800x24' python scripts/isolated_webgl2_test.py
```

只在**從 V009 新複製、尚未修改**的 V009 完整 Runtime 根目錄應用補丁，不直接對 V009 母版執行：

```bash
python scripts/patch_v010.py /path/to/copy_of_V009_Runtime
```

檢查新舊差異：

```bash
python scripts/verify_v010_delta.py /path/to/V009_runtime /path/to/V010_runtime
```

## 建議下一輪（V011）

先對 V006 尾段道路與 DEM 接縫做 Blender/幾何及真 WebGL 同位置比較，修掉黑白鋸齒；再進行 Android 真機與有正常 HTTPS origin 的完整驗收。人物第三人稱仍不得提前整合。