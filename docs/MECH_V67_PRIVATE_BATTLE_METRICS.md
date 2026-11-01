# 臺北機甲 v6.7｜本機戰鬥統計與三檔難度

## 系統定位與版本

本 Draft 接續 v6.6 PR #76，不直接改動 `main`、Slop Taipei 公開網站、原始臺北 OSM 城市、玩家 v5.0 GLB 或三款 v6.3 Blender 敵機。完整 Windows v6.7 遊戲程式／貼圖／模型／啟動器提供在**另外交付的 ZIP**；GitHub 共用工具鏈只保存可在其他引擎重用的純核心與測試。

## 和完整 ZIP 逐位元一致的 JS 核心

- `examples/threejs/mech-battle-metrics-v67.js`，Git blob `6eab9d70b05d90c1d3eec1f277282ebd7a0e31c3`：僅保留單次遊戲的記憶體聚合計數，沒有外部網路、儲存、裝置識別碼、地理座標或原始操作軌跡。玩家主動匯出 JSON 才會寫檔；可以關閉量測或清空。
- `examples/threejs/mech-difficulty-v67.js`，Git blob `ed8b1ed7179479ef14195519e0fba1d2669aeb44`：練習／標準／挑戰。**標準等於 v6.6 原本敵機傷害**；練習敵機對玩家 ×0.70、對中繼站 ×0.75；挑戰 ×1.25／×1.20。僅調整真正被 OSM 射線命中的傷害，不更動 AI、真實碰撞、玩家武器或原建模。
- `tests/mecha/v67-metrics-difficulty.mjs` 與 `.github/workflows/mecha-v67-metrics.yml`：純核心 Node 22 模擬驗證與隱私資料結構檢查。

## 完整 Windows v6.7 的新功能（不在此 GitHub 純核心內）

- 原本 `mech-combat.js` 新增真正玩家／敵機發射、真正命中與 HP 損失事件；擊毀、任務波次、側閃實際移動與阻擋、敵機真正重新尋路都透過現有遊戲系統導入記錄，不看畫面文字猜測結果。
- `mech-addon.js` 新增「難度」、「量測開關」、「匯出戰鬥統計」、「清除紀錄」。任務中不能改難度；量測留在 RAM，不透過 Google、OpenAI 或第三方伺服器上傳。
- `qa/v67_battle_metrics_dashboard.html` 是無外部 CDN 的靜態離線分析頁，可直接選取玩家手動匯出的 JSON。內建範例已明確標示為**合成資料，不是真實遊玩紀錄**。每波長條圖、側閃／損傷／尋路計數均來自讀入檔案。
- 專門的 `qa/V67_PLAYTEST_PROTOCOL.md` 為 Windows WebGPU 人工驗收與難度實驗的待辦，不會假裝實機已通過。

## 自動化測試證據

完整 Windows ZIP 已在**乾淨目錄重新解壓縮**後完成：
- ZIP CRC PASS，402 個檔案項目、401 份 SHA-256 檔案核對一致。
- 145 份舊版正式 `assets/` 資產**逐位元不變**。玩家 `mecha_v50.glb` SHA-256：`296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`。
- **83／83 Node/Python 測試 PASS，0 失敗，0 逾時**：包含以前 v6.6 的戰鬥測試以及新增的真的敵機射線造成 12／16／20 點 HP 損失、只量測允許事件、JSON 不輸出座標、離線 UI DOM 模擬與安裝器重複安裝／缺檔拒絕。
- 既有測試中硬編舊版 HUD／啟動器文字的斷言更新為 v6.7，**沒有略過原有測試**。正式 `mech-battle-metrics-v67.js` / `mech-difficulty-v67.js` 在 ZIP 與本 PR 同一個 Git blob。

## 誠實的限制與下一階段

- Chromium 測試本機頁在這個執行環境遭 `ERR_BLOCKED_BY_ADMINISTRATOR` 阻擋，所以離線儀表板只做了 JS／DOM VM 測試，**不是** Chrome 實際視覺驗收。
- 尚未完成 Windows WebGPU 真實臺北 101 五分鐘遊玩、實際 FPS／VRAM、三款敵機碰撞視覺、真實玩家勝率或確切難度平衡。練習／挑戰傷害倍率仍是供測試的候選值，不是實驗得出的最佳設定。
- 不要直接拿此 GitHub 純核心覆蓋整份遊戲。應使用另外交付的 v6.7 完整 ZIP，並保留原版和全部 Draft PR 直到驗收。
