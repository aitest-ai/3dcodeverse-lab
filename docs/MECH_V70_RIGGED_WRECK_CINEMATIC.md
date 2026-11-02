# 臺北機甲 v7.0｜真實 GLB 敵機擊毀、有限殘骸與戰鬥收尾

## 來源及版本約束

此獨立 Draft 接續 v6.9 PR #85，沒有自動合併至 `main`、沒有更改公開臺北網站，也不覆寫以前的 v6.3 Blender 母檔、GLB 和 v6.9 ZIP。實際完整 Windows 7.0 整合包獨立交付，並保留既有 Slop Taipei 的真實 OSM 街道、建築遮擋、玩家光束、G 爆破、M 三波防衛及本機統計。

## 在完整 Windows v7.0 ZIP 的真正功能

- `mech-cinematic-v70.js`：真正透過既有 HP／raycast `explodeEnemy` 進入死亡流程。敵機已標記 `dead=true`，也已計入波次，但原本 15 骨架、6 動畫的 **Blender Skinned GLB 暫留可見約 2.25 秒（Heavy 約 3.1 秒）**，加上有限傾斜／沉降，而非瞬間抽換成低品質立方體。到期呼叫原 `clearEnemy` 正式卸載 AnimationMixer 和 GLB。
- 共用幾何／材質的金屬碎片上限：每個普通敵機 11、重裝型 19，所有存活碎片最多 110、同時殘骸最多 5、能量環最多 8。只有**真正 3 波擊殺勝利**才從中繼站釋放勝利擴散環；重裝敵機**成功生成**才出現入場環。
- 尊重系統 prefers-reduced-motion，降低碎片數與傾倒程度；全部由有限的遊戲 dt 更新，並在 `reset()` 和 `dispose()` 清理。不會改原本傷害值、移動碰撞、敵機 AI 或真實城市。
- `mech-cinematic-timing-v70.js` 是此 GitHub 分支 `examples/threejs/mech-cinematic-timing-v70.js` 的**完全相同來源內容**，Git blob SHA `a8698d3b76a0d0de52e836f964cf0753fe9bc373`。純數值模組由 Windows 完整 Three.js 效果真正 import。**完整 Windows `mech-cinematic-v70.js` 與 `mech-combat.js` 在 ZIP 裡，沒有不實地宣稱 GitHub 參考核心就是整套遊戲。**

## 測試可重現性與限制

- 96 個 Python／Node 測試採 **三組互不重複、各 32 項**執行，96 PASS、0 FAIL、0 TIMEOUT。分組紀錄在 ZIP `qa/QA_v70_shard_0.json`、`_1.json`、`_2.json`，彙總在 `qa/QA_v70_complete.json`；`tests/run_shard.py` 在本地臨時建立 Three.js mock 後會自動清除。
- 全新解壓最終 ZIP 後，另測 8 項重要測試，全數通過（真實光束擊毀與僅一次計分、原 GLB 暫留、重裝型第二階段、OSM 關卡、缺檔拒絕安裝、v6.9 結算）。
- 最終 ZIP **449 個檔案項目、448 SHA-256 檢查全相符，CRC 完整性通過**。全部 145 份舊版 assets 完全不變，玩家 `mecha_v50.glb` SHA-256 仍是 `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`。
- ZIP SHA-256：`4a030f817a13c64da0b8ebb578ae197df6173ba0c85f07140384f5b68c270763`（63,501,908 bytes）。
- GitHub Node 22 pure core workflow：<https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41371356412>，SUCCESS。
- **未完成：** Windows Chrome／Edge WebGPU 內的 3D 擊毀演出實際視覺審查、地形碰撞下的殘骸自然性、FPS／VRAM、臺北 101 五分鐘真實遊玩。Node mock 與數學測試不能代替真正 Windows GPU；沒有捏造實機截圖。需要實測時，請按照完整 ZIP `qa/V70_MANUAL_ACCEPTANCE.md`。

## 安全交接給其他 AI

1. 以 **v7.0 完整 Windows ZIP** 為最新工作版，勿改寫 v6.9 的 zip 或使用過時 v5.0 外觀替代 v6.3 敵機。
2. 保留可編輯 Blender 母檔、每個 GLB 貼圖與 OSM 授權來源。第三方 Slop Taipei 固定 revision `1d70708fc92a088b779c8c0e22677adb64966a1b`，預設 ZIP 不內含第三方城市。
3. 若需畫面提升，**先完成真正 Windows WebGPU 影片與 FPS**；再以真實截圖決定殘骸落地、鏡頭收尾和特效品質。不要自動合併 Draft 或部署公開站。
