# 登別伊達時代村 V018 R1｜V004 柱廊真實碰撞程式與 Chromium 操作驗收

## 目的與範圍
這是一輪**驗證版，而非建築修改版**。延續 V017 的 231.5664 公尺完整高品質漫遊；實測 V004 高等學問所附近的柱廊，確認既有玩家半徑 0.26 公尺、既有障礙物及滑動/停止行為。沒有自行縮小碰撞、移動建築、變更道路、重畫貼圖或擴建。

## 已實際驗證
- 直接從 V017 Runtime ZIP 解壓並匯入真正的 `navigation.js`、`controls.js`、`walk-session.js`，合併 `collision.json`、`extension_collision.json`、`v005_collision.json`、`v006_collision.json`。Node 22 的 **10/10 項碰撞/移動回歸全部通過**。
- 最窄中心線淨餘距約 **0.23073 公尺**，與 V017 的 0.23203 公尺吻合，僅取樣間距略有不同。
- 靠近高等學問所柱子時，碰撞 solver 計出 **35 次受阻子步**，未發生穿柱；貼柱側移 0.99 公尺保持有效位置；放開輸入漂移零；A/B 切換位姿零漂移。
- 237 個縱向測站 × 7 條橫向軌跡（1,659 次 `world.check`）：中心線零受阻；向左偏 0.5m/1.0m/1.5m 分別有 10/38/29 個受阻取樣點。說明**中心線可走，不代表柱廊側向全面可走**。
- 真正的 Chromium DOM 事件環境匯入 V017 原本 `input-events.js`：**6/6 項輸入回歸通過**。包含 W 按放、合成雙指 PointerEvent 移動+轉頭、放手停下、視窗 blur 清除輸入。第一次 QA 腳本誤把 `lookPointer` 物件與數字比較，已修正 QA 本身，非遊戲缺陷。
- 圖片是實際 2D 位置與碰撞取樣圖，**不是**真 WebGL2 的 3D 截圖。這輪未重新執行完整 B 高品質 GPU 場景，也未宣稱 Android 真機已過。

## 可重現方法
1. 將**原封未修改** `Noboribetsu_Date_V017_R1_Runtime.zip` 放在這份 QA 原始碼根目錄。SHA-256 必須是 `eb6ceb13d51b813b8111070cd13eadf36b13fb9ff246964519e6118892458866`。
2. `python prepare_v018.py` → 只允許解壓至空的 `base/`；SHA 或 CRC 不合就停止。
3. `node test_v018_motion.mjs` → 原生程式碰撞，產生 `outputs/V018_motion_qa.json`。
4. `python test_v018_browser.py` → Chromium 及 Playwright 的 DOM/合成 PointerEvent 測試（須具備 Playwright 與 Chromium），產出 `outputs/V018_browser_input_qa.json`。
5. `python make_v018_review.py` → 自原場景資料和兩個 QA JSON 產生 PNG 與 HTML 比較報告（需 matplotlib、numpy）。

### 保護原始檔
- V018 Runtime ZIP：完整保留 **V017 115 個原有檔案的內容與 SHA**，僅在 ZIP 根目錄增加 `README_V018_QA.md` 與 `V018_QA_summary.json`；`dist/` 內 **沒有任何更動**。網站本身仍顯示 V017 版本，這是預期且正確的狀態。
- V018 來源工程獨立；所有修改只在 QA 程式與報告，不覆寫 V017、V016 或 GitHub main。
- GitHub 上獨立 Draft PR，保留舊版供多 AI 接續。

## 未完成／不能宣稱
真實商店門檻測量、建築現況還原、Android 實體手機、私有 HTTPS/CDN/登入、Blender Native 母檔，以及**本輪真實 WebGL2 第三人稱/第一人稱近景錄影**都尚未驗證。請勿從目前模型模擬結果推論真實建築消防、無障礙或行人通行規範合格。