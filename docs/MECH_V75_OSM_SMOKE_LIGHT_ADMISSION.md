# 臺北機甲 v7.5｜煙霧與原始街廓遮擋及局部爆炸照明節流

## 真正承接的工作版

從完整 v7.4「動態煙霧與局部爆炸光影」Windows ZIP 複製成獨立 v7.5 工作資料夾，再直接更新原本 `mech-combat.js` 真正整合，而不是只做示意畫面。原始玩家機甲 15-bone GLB、三種 v6.3 高品質 Blender 敵機、145 份正式 assets 及真實 Slop Taipei OSM 城市/建築/水域判定不變。完整 Windows ZIP **不是**整份提交這個資產實驗室 repo；不修改 main 或公開網站、不合併先前 Draft PR。

## 原始可重用模組

- `examples/threejs/mech-smoke-city-v75.js` **逐位元相同**於完整 Windows ZIP 根目錄的 `mech-smoke-city-v75.js`；Git blob SHA **5099822ab476e0c6a1601d2f0f62f778c8533490**、SHA-256 **246fc0ec56fff9e2741c41dd879a602d88df0dbef6cbba11d0d1983b47b4065a**。
- `tests/mecha/v75-smoke-city.mjs` 與 `.github/workflows/mecha-v75-smoke.yml`：Node 22 檢查薄牆從起點到終點的掃掠、不同橋層高度拒絕、OSM 查詢失敗保守停止、每影格查詢預算。
- 完整 Windows ZIP 有獨立 `mech-atmosphere-v75.js`，沿用 v7.4 原創煙霧 DataTexture / Three.js Sprite、不取消 PBR 模型，並依真實遊戲 `ColliderGrid`、`pointInBuilding`、`rayBuilding` 和 `getGroundHeight` 檢查煙霧位移。原版 v7.4 模組仍保留供比對及回退，GitHub 的精簡核心**並不是整份真實 Three.js 遊戲**。

## 改善與安全界線

- 煙霧每次移動從上次已確認的位置掃過完整線段（包含薄牆）；碰牆、無效地面、不可信另一層高架或查詢額度用盡時**保留最後安全位置**。降低錯誤穿過實際臺北大樓的機率，卻不會自稱真正流體模擬，也不會改物理碰撞、牆面材質、射線或敵機 HP。
- 完整／平衡／精簡的每影格地形取樣上限 **12／8／5**、牆面查詢上限 **16／10／6**；低檔降低查詢頻率時保持上次確認煙霧位置，不能在跳過查詢影格盲目穿牆。保留 v7.4 原有煙霧／光源物件數 36／22／9、3／1／0 和完整品質預設。
- 同時觸發多個爆炸時不反覆殺掉既有 PointLight 騰出空位，而是**有生成間隔的額度控制**；滿額的額外閃光忽略，不會增傷或影響遊戲，重置／結束時清除全部煙霧、共享貼圖、短命光源。
- 效能介面新增煙霧被牆拒絕次數及多次爆炸被略過的局部光源數。這些是**CPU/事件計數，不等於 GPU FPS 或 VRAM**。
- 安裝器 `patch_slop.py` 在觸碰原始城市檔案之前確認新增兩份模組存在，安裝兩次不重複掛載，使用獨立 v7.5 的本地城市資料夾。

## 實際可重現測試

- **120／120 個 Python/Node 回歸測試通過**，三組互不重複各 40 項。包含既有三波防衛、真實遊戲程式的光束造成 HP 歸零、原始模型資產雜湊、OSM 模擬安裝、薄牆煙霧、8 次連續爆炸成本與元件回收。測試使用 Three.js 模擬載入器，不能宣稱真實 Windows GPU 通過。
- ZIP `臺北機甲戰鬥_v7.5_煙霧街廓遮擋與局部光源節流完整整合包.zip` **64,032,515 bytes**、SHA-256 **1c57bd5a0a1239237e3bc1f06901cfab29341e3fe5409080cdc3cf84eb478d05**、**535 檔案項目／534 份 SHA-256 逐檔相符、CRC 通過**。原 145 份 assets 逐位元完全相同、玩家 GLB SHA-256 **296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c**。
- 從最終 ZIP **全新解壓**後，另外 12 項與 v7.5 烟霧、局部照明、v7.4 光影、v7.2 真實擊殺模擬、臺北三波、城市安裝的關鍵測試全部通過。詳情在交付驗收報告 JSON。
- GitHub Actions Node 22 核心 QA：<https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41381986445> 已成功。

## 未完成（請明確保留）

真正 Windows Chrome/Edge WebGPU 臺北 101 街景中煙霧是否完全不穿模、橋面高度、爆炸光影、GPU FPS/VRAM、實際手機/Android 3D 及 5 分鐘防衛戰**仍未實測**。此版本使用保守代理碰撞／路線查詢，並非完整流體或透明體積遮擋。下一輪先取得真實場景錄影及實測 GPU 資料，再決定是否升級材質、複雜度與鏡頭。保留全部 Draft PR、不自行更新網站。