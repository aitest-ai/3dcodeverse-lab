# 登別伊達時代村 V020 R1｜柱廊近距離導引

此版本從 V019 Draft PR #102 的 `feat/noboribetsu-date-v019-porch-guide-r1` 分支接續；**保持 Draft、不合併、不部署、不覆蓋任何舊站與私有模型**。

## 已在獨立 Runtime 實作
- B 場景的 13 個 V019 柱廊導引環保留，僅顯示距玩家前方 15m、後方 3m 的提示；不在路段附近時全部隱藏。
- 玩家位於 s=84.5–105m 時保留側向 -0.45m 模型警語，新增 s=85–103m 的低負擔進度條。
- A 場景、手動關閉、遠離柱廊，提示點與進度條隱藏。改善 V019 診斷下載檔名殘留 V014 的問題。
- **純視覺改良**：原本 GLB、貼圖、座標、路徑與真正的 CollisionWorld 一律保留。現場尺寸、無障礙與逃生安全未得到驗證。

## 來源與重播
完整私有候選包為 `Noboribetsu_Date_V020_R1_Runtime.zip` 與 `Noboribetsu_Date_V020_R1_SourceQA.zip`。其中有整合過的 `dist/app.js`、可重播修補 `source/patch_v020.py`、Node 測試、隔離 WebGL2 測試程式與影像。此 GitHub PR **只存可公開的核心邏輯與來源說明，不上傳大型私有場景包**。

從原始 V019 ZIP（SHA-256: `bb7e93bb5639b8f45461b968ab0fce25432199d8594ed4c3c264b90164ded8ea`）進行純函式版本升級；完整差分修補腳本位於私有 SourceQA 包內。把本目錄的 `porch-guidance.js` 複製到 `dist/` 與 `navigation.js` 同層，並依 SourceQA `patch_v020.py` 的指令整合 `app.js`、`index.html`、`style.css`、`qa.json`。

## 測試證據
- V019 原 118 檔中 114 份 SHA-256 完全相同，修改 4 個介面/程式檔、加一個獨立函式模組；V020 Runtime 共 119 檔。
- 119/119 從封存 V019 重新建置後 SHA-256 一致；兩份交付 ZIP CRC 通過。
- Node 使用實際 CollisionWorld 檢驗 13/13 V019 中心線提示點可走；遠近、A/B、關閉、左右偏移與進度端點測試通過。
- 隔離 Chromium / Xvfb / SwiftShader **真 WebGL2** 渲染通過。s≈90.5m 有 11 個近距離點、進度 30%；入口及離開柱廊時為 0；同鏡位已存開/關 PNG。
- WebGL2 環境僅在**測試程式**採用預先查核模型 SHA 的 adapter 與相機定位 hook；正式 Runtime 不含，不能據此推定私人網站與 HTTPS 完成驗收。

## 不得宣稱完成
Android 實體裝置、私人 CDN/登入、原生 WebCrypto 整站流程、Blender-native .blend/Cycles 與現場柱廊尺寸都尚未驗證。V015 的 4 個埋沒取樣／V016 兩條石基座並沒有被這次的視覺提示修復。

**不合併、不得改公開網站。**
