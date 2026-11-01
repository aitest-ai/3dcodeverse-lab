# 臺北機甲 v6.4｜真實事件驅動的戰鬥回饋

## 版本與原則

v6.4 依據 v6.3 Draft PR #69 延續，**不修改原本真實臺北 OSM 地理、玩家 GLB、三型 v6.3 敵機 Blender／GLB 母檔、主分支 `main` 或公開網站**。避免未經實機確認便大幅擴充地圖。這版新增小而實用的回饋功能，讓 101 三波防衛戰中的操作有清楚視覺確認。

## 真正的遊戲內改良（完整 Windows ZIP）

- `mech-combat.js` 在**真正生命值降低**時發布 `enemy_hit / player_hit / relay_hit`，在真正敵機死亡時發布 `enemy_down`，在可破壞立面受擊時發布 `building_hit`，在爆破彈實際引爆時才發布 `rocket_impact`，從三波真任務狀態發布 `wave_start / heavy_arrival / victory / defeat`。不以關鍵字或畫面文字猜測命中。
- `mech-battle-feedback-v64.js` 有優先序與節流，讓重裝機登場／中繼站告急不被大量低優先的光束命中訊息淹沒。最多保留有限類型與彙總值，不在歷史中記錄世界座標、玩家身分或 GPS。
- 畫面中央新增短暫命中與戰況文字，可以在原機甲控制面板按「命中提示：關」停用；沒有強烈全螢幕閃白。尊重系統 `prefers-reduced-motion`，鏡頭震動隨之停用。
- 以原生 Web Audio 產生原創簡單警示短音：真命中、擊毀、中繼站警報、重裝機、勝／敗。沿用原本 **音效預設關閉** 的使用者設定，不取得第三方音檔、不使用付費服務。玩家同意音效前不發聲。
- 舊有 v6.3 原主炮、Shift+F、G、V/Shift+V、三波中繼站、敵機定點預警、真實碰撞和原有動畫保持不變；這層不更改真實傷害、無敵時間或行動速度。

## 可重用工具鏈（本 Draft PR）

- `examples/threejs/mech-feedback-kernel-v64.js`：無 DOM 的精簡純邏輯移植參考，事件優先序／資料最小化／時間界限與 Windows 模組相同；**並非完整 Windows HUD 的逐位元副本**。
- `tests/mecha/v64-feedback-kernel.mjs` 和 `.github/workflows/mecha-v64-feedback.yml`：GitHub Node 22 QA。
- Windows 完整事件來源、HUD 樣式及音效播放在獨立 ZIP：`mech-battle-feedback-v64.js`、`mech-addon.js`、`mech-combat.js`，也有 `qa/v64_feedback_offline_demo.html`（完全離線，使用內嵌的相同事件判斷核心，**純 2D 示意頁，非真實臺北地圖**）。

## 實際測試證據及限制

- 完整 Windows 疊加包：既有 63 項 + 4 項新增（事件／完整戰鬥／離線 DOM 模擬／重複安裝），全部 **67／67 Python／Node 回歸測試通過**。含真敵機 HP、9 架敵機、第三波重裝登場、第一波至勝利、資產原始雜湊。
- GitHub 公用純邏輯核心已通過 CI：https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41302034895
- Playwright Chromium 在此環境開本機檔案回應 `ERR_BLOCKED_BY_ADMINISTRATOR`；**離線測試頁的程式／DOM mock 通過不等於真正瀏覽器渲染通過**。
- Windows WebGPU 的臺北 101 五分鐘遊玩、實際 GPU FPS、反射光影、主炮／重裝型完整美術驗收**仍未實測**。不得用 Node 模擬結果宣稱實機通過。

## 交接給下一位 AI 的規則

先讀 `AGENTS.md`、`docs/MECH_V63_MOTION_CONTACT_REVIEW.md`。下一輪請優先以使用者提供的完整 v6.4 ZIP 直接查看 `mech-combat.js` 和 `mech-addon.js`，**不要拿 GitHub 獨立核心當作完整臺北遊戲**。保留 15 骨架／六動畫、真實建物遮擋、v6.3 精修 GLB。PR 依賴 v6.3 #69，勿提前合併整串 Draft。
