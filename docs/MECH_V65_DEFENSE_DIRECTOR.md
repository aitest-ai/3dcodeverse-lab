# 臺北機甲 v6.5｜臺北 101 三波防衛戰導演系統

## 版本與交接

本分支從 v6.4 Draft PR #71 接續；保留獨立完整 Windows 遊戲包與前序分支，不合併 main、也不更新原本公開臺北街景。請先讀 AGENTS.md、docs/AI_ASSET_PIPELINE.md，再讀 v6.4 戰鬥回饋文件。

本 GitHub 分支提供與完整 Windows ZIP **逐位元相同** 的可移植無 Three.js 核心：
- `examples/threejs/mech-mission-director-v65.js`（blob SHA `ce17da109bc82b69528577f94282c8351ee0f6c7`）。
- `examples/threejs/mech-enemy-ai-v59.js`（v6.5 重裝階段整合後 blob SHA `86c81cc8021fa51ba97b5f6b7628f170fa21d9ff`）。
- `tests/mecha/v65-defense-director.mjs` + CI `.github/workflows/mecha-v65-director.yml`。

本倉庫仍是跨 AI 的 3D 建模與程式參考庫，**不是 Slop Taipei 的完整遊戲程式**。真正 Windows v6.5 整合套件另外包含完整 `mech-combat.js`、`mech-addon.js`、`mech-mission-director-hud-v65.js`、安裝程式、測試、所有 v6.3 模型與原始玩家 GLB。

## 關卡設計與實作規格

- 第一波東／西兩翼兩架突擊機，第二波北／南／東三個方向（兩突擊、一遠距），第三波西／東／北／南四個方向（兩突擊、一遠距、一重裝）。方向是**真實世界座標的候選進場方位**：1m = 1 單位，+X 向東，+Z 向南，不是假設已有一條名叫「北街口」的道路。
- 真正生成仍由原 Taipei OSM 的路面高程、建築多邊形、破洞碰撞、水域、車流與其他敵機間距決定；**不安全則拒絕部署、不補一架幽靈敵機、不用空波次贏得勝利**。
- 第三波重裝敵機只有在真實 HP > 0 且 <= 90/180，才進入第二階段；移動速度 *1.18、預警時間 *0.82（原始 1.1 秒縮至約 0.9 秒）、冷卻 *0.74、真實命中傷害 *1.25（16 → 20）。其他敵機、自由模式、原玩家光束傷害都維持原數值。
- 在導演 HUD 顯示**真正生成後確認的方向**，非抽象規劃方向。開場、三波、守護站 <= 30%、Boss 半血、勝利／失敗都有單次提示與優先級，不依賴任意畫面文字判斷。
- 重裝第二階段和中繼站危急沿用 v6.4 的 Web Audio 原創短音，只有使用者手動開音效才播放；系統減少動態設定會停用 v6.4 震動，關卡導演不強制控制原城市鏡頭。
- 既有三種高品質 v6.3 敵機 GLB、原 v5.0 玩家 GLB（SHA256 `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`）、可編輯母檔、武器、腳掌 IK 都保留。

## 驗收紀錄與限制

完整獨立 Windows v6.5 ZIP 的 Node/Python **73／73 項測試已於工作目錄通過**，包含真 HP 降低後的第二階段、重裝攻擊真正增加 16→20、中繼站危急、波次方向、安全生成、Android／桌面通用 HUD 介面 DOM 模擬、舊版安裝升級／重複安裝及缺模組拒絕安裝。GitHub CI 只驗證可移植核心，不等同完整 Windows 遊戲的實機畫面。

環境限制：Chromium 嘗試開啟本機離線頁回覆 `ERR_BLOCKED_BY_ADMINISTRATOR`，因此 2D 示範頁只作 JavaScript VM／Canvas mock 驗證；**Windows WebGPU、臺北 101 真實街角敵機進場與繞行、GPU FPS／VRAM、五分鐘戰鬥實測和真實畫面截圖仍待驗證**。不能聲稱這些項目已通過。

## 如何安全接手

先取得完整 v6.5 ZIP，**在原 v6.4 ZIP 的副本上**操作；不要把本純核心當成完整遊戲。將 `patch_slop.py` 的修改限制在它已備份的原城市檔案，保留原始 OSM、全部舊版 GLB 和可編輯 .blend。確認實機紀錄後再考慮開下一個 Draft PR，勿提前合併此 PR 與先前尚未合併的機甲分支。


### v6.5 解壓縮驗收補記
在 2026-11-01 完整 ZIP 重新解壓縮後再跑 Python/Node 回歸檢查：73／73 PASS，退出碼 0。新增 Windows 啟動器隔離測試，確認只使用 v6.5 自己的 `slop-taipei-source`，不覆寫鄰近 v6.4 舊版安裝。ZIP 共 374 個項目、373 份檔案 SHA-256 核對一致，145 份既有正式資產保持相同。仍未完成 Windows WebGPU 真正遊玩。
