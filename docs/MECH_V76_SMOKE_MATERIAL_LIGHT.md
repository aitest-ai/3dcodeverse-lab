# 臺北機甲 v7.6｜煙霧材質透明層次與爆炸暖冷光影

本 Draft PR 接續 v7.5 PR #101，保留原始 Slop Taipei 城市、原 v5.0 玩家 GLB、三款 v6.3 精修敵機 GLB、共 145 份原始 Blender 母檔及貼圖資產；不更新公開網站，不修改 main，也不覆蓋以前 ZIP。**完整 Windows v7.6 疊加包是獨立交付的 ZIP，不是本 GitHub 跨 AI 資產庫。**

## 這輪實際完成的內容

- **程序化不規則煙霧紋理：**使用確定性雜訊，在本機產生兩張 64×64 RGBA、無第三方授權疑慮的煙霧紋理，像素總計 32 KiB；共用兩張 Three.js `DataTexture`，每顆煙霧仍然只有一個 `Sprite`，沒有因層次增加而把粒子數乘二。使用低透明度、破碎邊緣和顏色隨時間改變，改善 v7.5 煙霧重疊時整片亮灰、形狀太一致的問題。
- **煙霧動畫：**初期受到爆炸暖色光調影響，隨上升、擴散逐漸轉成冷灰色。每顆 Sprite 材質不透明度上限 **0.31**，且仍會乘上紋理 alpha。這只是視覺代理，不是精確體積散射、流體模擬或物理煙霧。
- **局部爆炸光源：**仍沿用 v7.5 的數量和生成節流（完整 3／平衡 1／精簡 0），`PointLight.castShadow=false`；隨動畫讓偏暖的爆炸亮光迅速變弱／變色，適度接近原臺北城景的 PBR 明暗氛圍，但**不重新設定全城燈光或材質**。
- **真實城市視覺約束：**沿用 v7.5 `mech-smoke-city-v75.js`，繼續以既有 OSM 的地形與建築完整線段碰撞控制煙霧；查詢預算仍然是 16／10／6 次牆面、12／8／5 次地形取樣，不因材質更新增加。
- **資源生命週期：**重置時清除所有煙霧 Sprite、SpriteMaterial 與 PointLight；完全卸載才釋放兩張共享 DataTexture。詳細統計可看到 textureVariants 與 textureBytes。正式遊戲 `mech-combat.js` 真正改為使用 `mech-atmosphere-v76.js`，保留 v7.4／v7.5 舊特效程式作為回退資料。
- **離線材質對照頁：**`qa/v76_smoke_material_lab.html` 是可直接開啟的單一 HTML、沒有 CDN／外部圖片／上傳／追蹤。畫面分別演示 v7.5 單一圓形紋理和 v7.6 兩種漸層紋理，具有觸發、暫停、清除控制。此頁明確標為 **Canvas 2D 材質示意，不是實際 Windows WebGPU 遊戲畫面**。

## GitHub 可供其他 AI 重用

- `examples/threejs/mech-atmosphere-material-v76.js` **與 Windows 完整 ZIP 的 `mech-atmosphere-material-v76.js` 逐位元相同**，Git blob `82c2fb2dc0f802d232194e64ee6ea0ff8f8aecc1`。
- `tests/mecha/v76-smoke-material.mjs` 及 `.github/workflows/mecha-v76-smoke-material.yml` 測試兩張透明紋理互異、透明度上限和局部光源動畫。
- 完整 WebGPU 整合 `mech-atmosphere-v76.js`、原始 `mech-combat.js`、`patch_slop.py`、正式臺北三波任務、GLB、BLEND 等都在用戶獨立完整 ZIP。**不可拿單一 GitHub 數學模組冒充完整遊戲。**

## 真正執行過的自動化驗證

- 工作目錄的 Node.js／Python **125／125 PASS（42＋42＋41，三批互不重複，0 fail／skip）**：保留歷史戰鬥、3 型 Blender 資產與原始 GLB 雜湊、Three.js 模擬載入、OSM 碰撞與安裝器、更新後煙霧材質生命週期、獨立 HTML 互動測試。
- 最終完整 Windows ZIP：**552 個檔案項目／551 個 SHA-256 全部吻合，ZIP CRC 通過**。ZIP SHA-256 `6ccbf380e694e3615b4e7e087fd0ae8ee89d543829683af0e91f0b01b7e3d620`，64,104,831 bytes。與前版相比，145 份 assets 逐位元相同，玩家 v5.0 GLB SHA-256 仍是 `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`。
- **最終 ZIP 全新解壓後**，在獨立測試專用的 Three.js mock 下再次跑 **12／12 關鍵測試 PASS**，並完成 551 檔雜湊複驗、CRC。
- 使用 Chromium `page.set_content` 真正渲染桌面、手機 2D 材質比較網頁，觸發爆炸、清空、畫布更新與分組正常。**這不是從 Windows 原始網站 `file://` 或真正 WebGPU 渲染的證據。**

## 未完成且不能聲稱通過

真正 Windows Chrome／Edge WebGPU 在臺北 101 附近的煙霧透明排序、原始 PBR 反射、PointLight 的 GPU 耗時、GPU FPS／VRAM、手機／Android 3D、五分鐘完整遊玩均**尚未實測**。Node／隔離 HTML 測試無法替代 GPU 真實驗收，請按照完整版 `qa/V76_MANUAL_ACCEPTANCE.md` 逐項測試。

保持 Draft，不自動合併 PR 或部署網站。