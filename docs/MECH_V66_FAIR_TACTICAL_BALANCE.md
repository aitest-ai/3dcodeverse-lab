# 臺北機甲 v6.6 — 戰鬥節奏與有限次防卡點

本 Draft 分支承接 v6.5 PR #73。三波防衛、玩家高品質 v5.0 GLB、三款 v6.3 Blender 敵機、原本真實臺北 OSM 城市不修改。完整 Windows v6.6 Overlay 另用 ZIP 交付（不是整份放在本 GitHub 建模參考庫）；不覆寫任何舊版或正式網站。

## GitHub 與 Windows 完全一致的可移植模組

- `mech-combat-pacing-v66.js` Git blob `903bcbdc1454c112f87295a86e9926be75b7ae1e`；第一波最多 1 個、二／三波最多 2 個同時開啟的預警，間隔 0.28/0.48/0.62 秒，波次開場緩衝 0.65/1.05/1.45 秒。重裝第二階段增加 0.85 秒新的瞄準準備；**已開啟的預警不能被這層提前取消**。
- `mech-unstuck-v66.js` Git blob `01bcfb1445d2edc62a8504b17aa94f5d06ae59b1`；觀察卡角約 0.45–0.92 秒，最多 3 次有限間隔的 A* 路徑重啟，長期無路則休息／降低計算頻率。此核心 **不直接移動敵人**、不穿牆、不改碰撞；真世界每一步仍受原 OSM 障礙物／水域／車流／高程回呼控制。
- `mech-enemy-ai-v59.js` Git blob `ca1cdb7cf36d4a12089dc7f5126a7d6fb56cb4fb`；新增可選 `allowWindup`、`preferNavigation` 參數，已開啟的射擊預警會鎖住原準備時間，即使 Boss 此時降半血也不會突然縮短鎖定倒數。原射線／HP 不改。
- `mech-mission-v60.js` Git blob `5a28983bd74e644148aba582017d4e9aa3cefa06`；新增可選 `intermissions:[3.4,4.4]`，預設舊 4 秒行為完全保留。
- `tests/mecha/v66-tactics.mjs` 和 `.github/workflows/mecha-v66-tactics.yml` 在 GitHub Actions 測試上述純核心，不假裝包含全部遊戲。

## Windows 完整遊戲 ZIP（獨立發佈）

完整包還包括 `mech-combat.js` 連接上述四個核心與原本玩家光束、真實射線、三波任務、中繼站及地形；`mech-addon.js` HUD 顯示重新尋路數、敵人預警上限與倒數；`patch_slop.py` 先檢查新模組後安全複製；`START_WINDOWS.cmd`、`launch.ps1` 固定本版目錄下載原城市，不修改旁邊其他版。模組的原生程式碼比 GitHub 提供更多宿主整合，GitHub 僅提供可重用核心。

Windows 全整合包的 Python/Node **78／78 項測試通過**，包含原有 73 項、v6.6 計時／防卡點／真正戰鬥／安裝安全／離線 2D 畫布示意（新增 5 項），相關隔離回歸輸出位於 ZIP 的 `QA_v66_parallel.json`。舊兩項硬編 v6.5 版號的測試改為驗證 v6.6 顯示，**未跳過原功能測試**。

## 尚未完成的必要驗收

真實 Windows WebGPU、臺北 101 原始街景中的敵機繞角、真正同時開火體感、遊戲 FPS／VRAM、五分鐘完整任務以及玩家難度調查都未實測。**秒數與上限是程式候選參數，不是經過玩家實驗證明的最佳難度**。2D 實驗室是矩形障礙示意，不是臺北真實街圖；嚴禁用它聲稱已完成實機測試。

請保留前序全部 .blend／GLB／ZIP 和 Draft PR，不要自動合併、更新公開網站或覆蓋 main。
