# 臺北機甲 v7.7｜臺北城市日夜光色與煙霧遠近透明層次

此 Draft 延續 v7.6 PR #105，不覆蓋任何歷史 ZIP、不合併 `main`、不更新公開網站。完整 Windows 遊戲在另外交付的 `臺北機甲戰鬥_v7.7_日夜爆炸光影與煙霧遠近層次完整整合包.zip`，**不是本 GitHub 共用建模工作室內的單一 JS 範例**。

## 可重用核心與實際整合
- `examples/threejs/mech-scene-light-v77.js` 是 Windows 完整 ZIP `mech-scene-light-v77.js` **逐位元相同**的原始碼，Git blob SHA **665546de52fb468961859ad4e5e4c6d5db95afac**。
- 原城市 `main.js` 的 `selectTime(timeId)` 會對 `[data-time]` 時間按鈕新增 active，`lighting.js` 有 golden、midday、midnight 預設。完整版 `mech-addon.js` 直接讀取 `document.querySelector('[data-time].active')` 與原 `cameraSystem.camera.position`，交給 `mech-combat.js` / `mech-atmosphere-v77.js`。**不是依系統時鐘、GPS 或使用者地址猜測日夜**。
- 正午／黃金時刻／夜晚使用不同但有上限的短暫 `PointLight` 強度及淡出暖冷顏色，**不更改原城市照明 preset、曝光、陰影、地圖建築 PBR 或模型幾何**。
- 原本的兩張 64px 共用程序化煙紋、OSM 地形／建築薄牆掃掠、煙霧 36/22/9、局部光 3/1/0 及不增添陰影保留。新增近鏡頭 1.65–4.5m、遠景 48–94m 的 Sprite 透明漸變；仍使用 `SpriteMaterial.depthTest=true`、`depthWrite=false` 和 Three.js 自己的 transparent sorting。**不聲稱物理流體、GPU 深度淡出 Shader 或所有透明體都能精確排序**。
- `qa/v77_scene_lighting_lab.html` 是完全離線、單檔、可互動的 Canvas 2D 正午／黃金時刻／夜晚示意；沒有真實 Taipei OSM 道路或 3D WebGPU 畫面。使用隔離 Chromium page.set_content 完成桌面／手機排版、鏡頭距離滑桿、暫停／清空／爆炸互動。
- `patch_slop.py` 安裝前預檢 2 份 JS 與離線頁，缺檔時不修改原城市；使用 v7.7 獨立安裝資料夾。原 145 份 assets、v5.0 玩家 GLB（SHA-256 `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`）及 v6.3 三型敵機可編輯 Blender 來源完全不變。

## 證據與上限
- 完整 Windows source Node/Python/Three.js mock 回歸 **130／130 PASS**，分三個獨立 44+43+43 批次。新增的五項測試涵蓋新版光色、Sprite 生命周期、原 HP 真擊殺後觸發煙霧、Canvas 2D 頁、缺檔拒絕安裝與模型雜湊；原有測試未跳過。
- 最終 ZIP **64,378,505 bytes**，SHA-256 **c2bdefc2cdc65ad3a7223690b1659c2f26bd628d669523cb5520e2acb6a9d192**；**570 檔案項目、569／569 逐檔 SHA-256 相符、ZIP CRC 通過**，原 145 份 assets 逐位元一致。
- 從**最終 ZIP 全新解壓**後，另外 **12／12 關鍵測試 PASS**，涵蓋正式 combat、v7.7 日夜 Sprite、v7.6 材質、原 v6.0 三波、完整安全安裝。JSON：`QA_v77_final_release.json`（另交付）。
- GitHub Node 22 共用核心測試 https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41395118644 已成功。

## 重要未驗收
**Windows Chrome/Edge 真正 WebGPU 臺北 101 五分鐘遊玩、現場建築遮擋/透明排序、夜間 GPU 照明效果、FPS／VRAM、Android 實機**仍未驗收。這一輪只提供真實遊戲整合程式與可重現的回歸證據，不能把 2D Canvas 截圖當成正式遊戲畫面。請保持 Draft，不合併任何歷史 PR，也不部署網站。
