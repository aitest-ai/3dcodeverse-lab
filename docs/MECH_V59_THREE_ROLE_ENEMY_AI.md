# 臺北機甲 v5.9｜三種戰術型 AI 與攻擊預警

## 本分支性質
此獨立 Draft PR 以 `feat/mecha-v58-ground-qa-20261101` 為基礎；**不更改 main、不合併舊分支、不更新公開網站**。GitHub 放的是與完整 Windows 包位元內容一致的純 JavaScript **敵機決策核心**，不是 Slop Taipei 完整原始碼。完整 Windows v5.9 整合包另以 ChatGPT ZIP 交付，保留舊版 v5.8 和 Blender 母檔。

## 核心規則
- `assault`（突擊）：100 HP、3.25m/s、近距離、0.43 秒預警、7 點傷害
- `ranger`（遠距）：80 HP、2.4m/s、遠距離、0.75 秒預警、9 點傷害
- `heavy`（重裝）：180 HP、1.52m/s、較強攻擊、1.10 秒預警、16 點傷害
- 分階段：approach/search → flank/retreat → telegraph → recover；實際角色 HP、敵機射線和損傷由原遊戲系統管理。
- 預警開始時鎖定玩家座標，射擊時不重新追蹤；玩家能在射擊前側閃。真正 LOS 必須由 OSM 建築 raycast 決定，已被牆擋住時不能傷害玩家。
- 地形、建築、水域、其他敵機及交通障礙由宿主 `canOccupy` 和 `sampleGround` 拒絕；演算法不繞過碰撞，也不給敵機無敵。
- 分頁停頓的 dt 被限於 0.05 秒，不讓 AI 瞬間跳移。

## 交付與驗證
GitHub 本分支含 `examples/threejs/mech-enemy-ai-v59.js` 與 `tests/mecha/v59-enemy-tactics.mjs`、自動化工作流程。
完整 Windows ZIP 另含 `mech-combat.js` 整合三類敵機、OSM 碰撞、長預警視覺環、真正敵方 HP/傷害、HUD、固定原機甲 v5.0 GLB。其完整 46 項 Node/Python 自動化測試在交付工作目錄通過。自動化**不能**證明 Windows WebGPU 畫面正常。

## 未完成
- 真正 Windows／Chrome／Edge WebGPU 的 5 分鐘臺北 101 街道遊玩
- 敵機在實際 OSM 繞路的多角度 QA、河岸／高架／車流及足部視覺、GPU FPS
- 高品質 Blender 敵機模型（現有遊戲中的新角色外形為區分角色用途的程序化暫用模型）
- v6.0 有目標保護、分波與過場的「臺北 101 防衛戰」

這些項目不可用 GitHub Actions 的核心測試或簡化 2D 戰術頁代替。

## 版本依賴
v5.9 Draft → v5.8 Draft PR #57 → v5.7 Draft PR #54 → v5.5 Draft PR #23 → 早期機甲 PR 鏈。請依序審查，而不是直接合併整串歷史分支。
