# 臺北機甲 v8.1｜按鍵後真正 RenderPipeline 戰鬥畫面留影

此 Draft PR 承接 v8.0 PR #115 的功能分支。完整 v7.8／v8.0 Windows 遊戲不在此 GitHub 倉庫；**這裡只存放可跨 AI 共用的來源程式、測試和交接規格**。完整 v8.1 差分安裝器與獨立 QA 網頁在本輪使用者下載 ZIP，不能把此 repo 當成包含 Slop Taipei 全城市和 Blender GLB 的完整遊戲。

## v8.1 可攜式核心

`examples/threejs/mech-combat-evidence-v81.js` 是從 v8.1 完整安全差分包中 **逐位元相同**的原始核心（SHA256 `ec659c8f9c44f983fc1401a1f728aed43fc4811ea5d7f824c68850be0439ff4a`）。

- 玩家**手動啟用**後，只觀察機甲模式裡鍵盤 F、Shift+F、G、V、Shift+V。這些都是**按鍵事件**，不聲稱實際開火或閃避成功。
- 每筆事件至少 3 個原遊戲 RenderPipeline 影格後，透過 v7.8 既有 `captureWebGPUCanvasV78(renderer.domElement, WebGPU device)` 取得真正的 PNG；被拒絕的畫布不得產生成功檔案。
- 鎖定其他日夜相機、離開機甲模式、取消、舊 Promise 遲到時丟棄該次擷取；最多五張，並自動停止，不更動戰鬥 HP、傷害、AI、碰撞或 GLB。
- 僅手動下載 PNG 與純事件 JSON。無自動網路傳送、定位、絕對時間、帳號識別或 localStorage。PNG 本身是原遊戲畫面，保留在本機記憶體直到下載或清除。

## 交付物與驗收

- GitHub 核心：`examples/threejs/mech-combat-evidence-v81.js`。
- Node 22 回歸：`tests/mecha/v81-combat-evidence.mjs`，驗證按鍵、節流、限制、取消、錯誤及報告欄位。
- Windows 差分 ZIP 另含：`UPGRADE_V81.py`、`ROLLBACK_V81.py`、`INSTALL_V81_WINDOWS.cmd`、`qa/v81_combat_evidence_review.html`、v8.0 來源核對參考和安裝／瀏覽器測試。**模擬安裝**通過，但並未直接取得並修改完整 v7.8 Windows ZIP。
- ZIP 最終 SHA256 `83f0cfb39f1ad6d8e2521c163d2c84d2f1911b8281149b2838636232dcd9bdf4`，CRC、逐檔雜湊和全新解壓後 3 組測試通過。瀏覽器測試圖片刻意以合成 PNG 作為測試材料，不是臺北真實場景。

未完成：Windows WebGPU 真正遊玩、五分鐘完整三波任務、真實截圖畫面、左右側閃手部及武器穿模人工驗收、GPU FPS/VRAM、Android。**不要合併 main，不要修改公開臺北網站或覆寫舊 ZIP。**
