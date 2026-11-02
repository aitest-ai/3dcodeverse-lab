# 臺北機甲 v7.1｜真實 OSM 地形約束的 GLB 殘骸、斜坡碎片與查詢預算

## 版本關係

此 Draft PR 從 v7.0 PR #89 獨立延續，沒有修改 main、Slop Taipei 原始公開網站或任何 v7.0 ZIP，也沒有更新玩家 15-bone 機甲／三款 v6.3 Blender 敵機。原有 145 份 assets 及所有 .blend/.glb 素材均逐位元相同。

## 可重用程式

- `examples/threejs/mech-wreck-ground-v71.js` 是完整 Windows ZIP 中 `mech-wreck-ground-v71.js` **逐位元相同的原始碼**：Git blob `c44878fa70089eff6bbc0910e0f4c51b95bbb4b6`、SHA256 `4ed9e41b03ad00eb093c82abbb5f08ccbfd485a860230d62748dfbad88965b4e`。
- `tests/mecha/v71-wreck-ground.mjs` 和 `.github/workflows/mecha-v71-ground.yml` 用 Node 22 測試這份原始碼。
- 完整 Windows ZIP 額外有 `mech-cinematic-v71.js`（修改 v7.0 實際 THREE 鏡頭畫面用殘骸／碎片）、`mech-combat.js` 真正遊戲接入、`patch_slop.py` 安裝器、實際 Blender GLB，不能誤稱這個單一 GitHub 幾何核心已經代表整套遊戲。

## 修正內容

- v7.0 對死亡 GLB 固定沉入地底 0.18m，v7.1 改用「身體下緣八個代表接觸點」估算傾倒高度，然後從真正 `controllerManager.getGroundHeight` 取得腳邊與傾倒方向附近的臺北街道地形。沒有讀到可用高度時回退上次視覺高度，不杜撰地面。
- 高度突變大於 0.70m（已知不一定同一層高架）不納入殘骸接地；碎片落點突變大於 0.60m 不直接吸附。**這只是安全代理幾何與連續性閥值，不是精確 OSM 建物物理碰撞**。
- 碎片不再永遠使用爆破原點的高度，而是在落地附近重新取樣移動後的 x/z；單一更新最多取樣 24 顆碎片。殘骸每 0.12 秒重取地形，模擬同時五架重裝敵機時測得最高 **44 次地形呼叫／影格**。
- 保留 v7.0 舊模組作版本回退，新版 `mech-cinematic-v71.js` 另檔新增，安裝器預檢新檔案，缺任一個就拒絕更動城市。沒有強制切換原版的攝影機，原有簡短鏡頭微震動仍遵守「減少動態效果」。

## 測試與不可誇大的範圍

完整 Windows ZIP 在工作目錄的 **102／102 項 Node/Python 測試**以三個互不重複的 34-test shards 通過（不是同一次不中斷執行）。從最終 ZIP 全新解壓縮後，**10／10 項重點測試通過**，含原始光束造成真實 HP 死亡、v7.1 地形代理、高架／無效數值回退、查詢上限、安裝器缺檔不改原城市、重複安裝等。正式 ZIP **467 檔案項目、466/466 SHA256 通過，CRC 通過**。

v7.1 完整 ZIP SHA256：`9dec9fd77cb15c3e9a641f10d21233e6fd13dc1d71fdae600a63a49f41c8eb2c`（63,569,891 bytes）。

**尚未完成：** 真正 Windows WebGPU 5 分鐘遊玩、臺北 101 真實街道上的傾倒接觸、盾牌與牆角穿模、GPU FPS/VRAM、手機及 Android 實際 3D。Node 模擬測得的接地代理清空與取樣上限不可視為高品質美術人工驗收完成。請使用完整包內 `qa/V71_MANUAL_ACCEPTANCE.md` 執行實機測試。

保持 PR Draft，不合併上游 PR，也不更新公開網站。下一階段如取得使用者真實遊玩截圖／影片，再調整實際模型支撐點、物理碰撞與鏡頭。
