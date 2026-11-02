# 臺北機甲 v7.8｜真實 WebGPU 三時段同鏡位截圖與離線畫面驗收

本 Draft PR 接續 v7.7 PR #106。**完整 Windows v7.8 ZIP 才包含正式臺北 WebGPU、三型 Blender 敵機、原始 OSM 地圖安裝器與真正的 3D 畫面擷取程式。** 此 repo 是跨 AI 共用程式與 Blender 模型工作室，不是完整 Windows 遊戲；本 PR 只放可重用的精簡示範調度器和測試文件。

## 真正的 Windows 功能（獨立完整 ZIP）

- 原 `mech-addon.js` 透過原 Slop Taipei `cameraSystem.camera` 的 position/quaternion 鎖住相同鏡位，仍保留原玩家、敵機及全部城市內容。
- 原 `patch_slop.py` 在真正的 `renderPipeline.render()` **後方**新增一次且只有一次 `mechAddon.postRenderFrame()` 掛鉤，原本後相機更新 `postCameraUpdate()` 也保留。
- 擷取順序 midday 正午、golden 黃金時刻、midnight 夜晚。**使用原城市按鈕**切換預設，不私自設定燈光，也不依系統時間/GPS 猜日夜。每次留足數個原始 RenderPipeline 影格，等待 GPU 工作完成後才要求真實 `renderer.domElement.toBlob('image/png')`。
- `mech-capture-v78.js` 會驗證 PNG 檔案格式、大小、尺寸及 32×18 像素色彩變化；黑畫面／透明畫布、無 WebGPU canvas、GPU 無法回傳時，明確標為錯誤，不能生成偽裝的遊戲截圖。三張有效才提供手動下載，以及包含虛擬城市相機位置／方位的本機 JSON；恢復原本日夜設定。
- `qa/v78_scene_capture_review.html` 是完全離線、無 CDN／外部網路的三欄比較頁。**預設沒有任何圖片**，使用者自行選取真正截圖及相同鏡位 JSON 才顯示，核對格式、大小與像素尺寸。畫面中不存在虛假的 3D 臺北背景。
- **限制：** 僅鎖定攝影機，不凍結真實車流、敵機與煙霧模擬；同鏡位不代表每個遊戲物體逐像素一致。部分 WebGPU 驅動可能拒絕或返回空白 canvas 截圖，將如實告知失敗。玩家仍可以用 OS 手動截圖，但沒有 v7.8 自動中繼證據。截圖時間不能當 GPU FPS。JSON 相機座標只由玩家主動下載到自己的電腦，沒有傳輸、儲存、GPS 或帳號識別。

## GitHub 本分支的可重用參考

- `examples/threejs/mech-real-capture-reference-v78.js`：**小型參考核心，並非完整 Windows `mech-capture-v78.js` 的逐位元副本**，示範真正繪圖完成後觸發三時段 PNG、錯誤拒絕、恢復原始 preset。
- `tests/mecha/v78-real-capture-reference.mjs`、`.github/workflows/mecha-v78-capture.yml`：Node 22 流程驗證。這些測試只提供程式狀態機證據，不自稱實際 Windows 3D 截圖成功。
- 本 repo 不附第三方 Slop Taipei 完整城市；完整 ZIP 的下載器固定上游提交 `1d70708fc92a088b779c8c0e22677adb64966a1b`。

## v7.8 獨立 Windows ZIP 完成的驗證

- **134／134 項** Node/Python 模擬、原始 GLB 雜湊、完整武器/三波關卡、城市安裝器、WebGPU 截圖調度測試，分成 45＋45＋44 三個互不重複批次通過。
- **145 份 assets 與 v7.7 完全相同**，原玩家 `mecha_v50.glb` SHA-256：`296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`。
- 最終 ZIP：**583 項，582／582 SHA-256 相符，CRC 通過；SHA256 `1abc2bc769fe4ce553a6dd740878635ab114780145c5c4754a372bbb7a675285`，64,439,878 bytes。** 最終 ZIP 全新解壓後 **12／12 關鍵測試通過**。
- 隔離 Chromium 桌面＋手機實際測試：離線比較頁預設不顯示假圖、手動匯入三張**測試專用合成 PNG**和 JSON、核對、清除。測試 PNG 沒有作為臺北實機畫面交付。
- **未測／不能宣稱成功：** Windows WebGPU 真正三張 3D 擷取、指定 GPU 的 PNG 回讀、臺北 101 五分鐘實戰、GPU FPS/VRAM、實際煙霧／光影透明排序。需要 Windows 上實際開啟 `START_WINDOWS.cmd`，依 `qa/V78_MANUAL_ACCEPTANCE.md` 完成人工驗收。

保持 Draft；不要合併舊 PR、覆蓋舊版、或直接更新公開網站。