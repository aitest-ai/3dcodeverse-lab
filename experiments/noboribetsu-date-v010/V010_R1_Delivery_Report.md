# 登別伊達時代村 3D 漫遊｜V010 R1 交付報告

**2026-11-01｜範圍：實際 Chromium WebGL2 整合驗收 + 低幀率操控修正。**

這一輪首次在本次工程環境成功以 Xvfb + ANGLE SwiftShader 建立 WebGL2，載入原版 V009 完整高品質 B 世界，實際呈現大手門、草鞋屋、變裝攝影館及 231.6 m 路線。新的 V010 **沒有重做、降低或壓縮 GLB 幾何和貼圖**。

## 本輪實際驗收（精確界線）

| 項目 | 結果 |
|---|---|
| 真實 Chromium WebGL 2.0 context | 通過，ANGLE SwiftShader（軟體繪圖） |
| GLTFLoader 完整 B 場景解析 + 第一次渲染 | 通過，第一畫面繪圖資料約 1,431,986 triangles / 94 geometries / 47 textures |
| 五棟舊 OSM 灰色建物替換 | 真 WebGL 內確認排除 100 triangles |
| V009 低幀率鍵盤移動比較 | 0 m；V010 同一操作前進 1.029 m |
| 放開鍵盤後漂移 | 0.000 m |
| 入口／231.6m 街尾往返 | 真 Chromium DOM + 場景狀態通過 |
| A 第一次延後載入／切回 B | 真 Chromium 中通過，相機差 0 |
| 手機直式雙指搖桿／右手環顧 | Chromium mobile emulation 通過，移動 0.833 m、環顧約 7.02°、放手漂移 0.000 m |
| 全模型獨立 SHA-256 | Python 解 gzip 並核對 10 份模型，全部通過 |
| 231.5664 m Node 靜態步行及返程 | 通過，未修改碰撞 |

**嚴格限制：** 管理環境會阻擋本機網址 top-level navigation，因此在 `about:blank` 的隔離資源攔截流程中，測試程式採用依模型長度回傳預先獨立核對 SHA 的介面。這**不是瀏覽器內真正的 WebCrypto 整條驗收**。正式 `model-codec.js` 完全未改；實際 HTTPS、登入及 CDN 仍待驗。此整合測試已真正使用 GPU API WebGL2，但軟體渲染 FPS 不代表使用者硬體效能。

## V009 → V010 僅變動事項

只修改 4 份既有檔案：`dist/app.js`、`dist/input-events.js`、`dist/index.html`、`dist/qa.json`，另新增 `start_v010_local.py` 與 `README_V010.md`。原有 96 份檔案中有 **92 份逐位元不變**；所有 B 分片、A、V004～V009 模型、道路、碰撞、場景座標及 Three.js 依賴均保留。

技術修正：用每次輸入變化前的 `advanceMotionTo(performance.now())` 結算尚未計算的位移，將這段時間分為每步最多 0.1s 的碰撞更新；畫面繪圖與角色移動解耦一部分。設有最多 2 秒補步上限，避免分頁長時間停滯後不合理跳躍。相同設計支援鍵盤與搖桿放手。這不會提升 GPU 的渲染幀率，也不能代替真機流暢度測試。

## 乾淨重播驗證

重新從保存的原始 V009 Runtime ZIP 全新解壓，執行 `sourceqa/scripts/patch_v010.py` 並附上 V010 的原創啟動器與說明，再逐檔與本次 V010 交付對照，**98／98 份檔案的 SHA-256 完全一致**。這是確實已重播的來源工程，不是未經執行的接手腳本。

## 已知仍須修正

1. **街尾 231.6m 的真 WebGL2 畫面有黑色鋸齒與白色斷裂的地形／道路交界**，截圖已保存，不宣稱已消除。
2. 軟體繪圖幀率低，即使 V010 行走時間正確，畫面仍會卡頓；需在有實際 GPU 的電腦／Android 確認。
3. 真正私人網址、HTTPS WebCrypto、CDN/登入及 Android **實體**手機未驗。
4. V009 建築是作者估計外觀，草鞋屋改裝後現況、變裝館精確立面仍缺資料；Blender-native `.blend` / Cycles 也未驗。

## 檔案與下一步

- `Noboribetsu_Date_V010_R1_Runtime.zip`：與 V009 相同高品質場景，V010 低幀率操作修正，本機 HTTP 啟動器。
- `Noboribetsu_Date_V010_R1_SourceQA.zip`：可重建補丁、真 WebGL2 與移動 QA、真 localhost 無測試替身的另用測試腳本、同鏡位實際截圖。
- `Noboribetsu_Date_V010_R1_Review.html`：桌面、手機、街尾與兩間店的真 WebGL2 畫面（商家截圖採 V009 同一套模型）。
- `Noboribetsu_Date_V010_R1_Validation.json`：通過與未測狀態分開列出。

**建議 V011：優先修復街尾可見地形接縫，並在真正 HTTPS + 實體 Android 裝置完成驗收；V010 保持候選，不覆蓋 V009 或網站。**