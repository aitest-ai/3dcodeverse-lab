# 臺北機甲 v8.2｜真正留影的 2D 問題標註與跨 AI 修模線索

承接 v8.1 Draft PR #119；本次新增 **獨立離線的畫面標註工作台**，不改既有 Blender 機甲、三型敵機、臺北 101 三波戰鬥、OSM 幾何、傷害、側閃或 WebGPU 擷取。

## 核心

- `examples/threejs/mech-frame-annotations-v82.js`：與 Windows 差分 ZIP `runtime/mech-frame-annotations-v82.js` **byte-identical**，Git blob `9c8fce3cb664dab7b658cccbbaf71a5bc1b8bfb7`，SHA256 `91e85681dcd62b6a1d5c13e2cef2e68b0d5bcd3cb099cc78be7a986d0da3cc1a`。
- `tests/mecha/v82-visual-annotations.mjs`：Node 22 驗證 PNG/事件對應、有效動作、唯一編號、相對圖片座標、人工分類、禁止越界與 JSON 最小化。
- 完整安全差分 ZIP **另於使用者對話下載**，含 `UPGRADE_V82.py`／`ROLLBACK_V82.py`、前版重建參考、完整單檔 `qa/v82_visual_annotation_review.html`、Node/Python/Chromium 測試、Windows CMD、驗收紀錄及 README。**這個 GitHub 倉庫不是完整 Windows 遊戲**，不要拿本 PR 替代 64 MB 原始完整包。

## 交付驗收範圍

- 來源只接受真正由玩家提供的 v8.1 PNG 與事件 JSON，對照事件編號／類別／PNG 原檔名／byte size／尺寸。
- 圖片點擊座標用 0–1 的 **2D 畫面相對座標**；標記砲口、光束起點、爆炸視覺中心、手臂穿模、煙霧遮擋、街道碰撞、側閃姿勢；標註 JSON 不含圖片、世界座標、GPS、帳號或裝置資訊。
- ZIP SHA256 `a7bedcaa9d365db92a43766180ea59662beeaa49c04c88f895f2288ad65605ef`；14 個 ZIP 項目、13／13 檔案 SHA256 相符、CRC 正常。最終 ZIP 全新解壓後，**Node annotation contract、Python 合成原始碼錨點安裝／回退、隔離 Chromium 以合成測試 PNG 操作**三組通過。
- 所有瀏覽器測試 PNG 明確是合成**測試資料**，不是實際臺北場景。原 v8.1 既有戰鬥系統未實際在此環境的 Windows WebGPU 啟動，沒有真實 FPS、3D 穿模、五分鐘戰鬥或實拍成果。

**保持 Draft；Base = v8.1 分支。不要合併舊 PR／main、覆寫原 ZIP 或部署公開網站。**