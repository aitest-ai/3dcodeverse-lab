# 臺北機甲 v8.0｜真實擷取後的遊戲內影像驗收

此 Draft PR 接續 v7.9 #111，建立「把 v7.8 已擷取的真正 WebGPU PNG 交由 v7.9 像素診斷」的**可重用程式核心**。本工作室 GitHub **不是完整 Windows 遊戲**；v7.8 完整 Windows ZIP（包括真正原 Slop Taipei OSM 城市、15 骨架玩家機甲、三型 Blender 敵機、三波防衛戰）留存在獨立封裝，不應以此參考版冒充已更新完整遊戲。

## 本次完成

- `examples/threejs/mech-capture-review-v80.js`：只接受原有 v7.8 `getFiles()` 三張完整 PNG Blob，不產生假的場景圖片；用真正 PNG 解碼、RGBA 分析、三時段比對，拒絕重複／缺漏／不合理 PNG。
- `tests/mecha/v80-captured-png-review.mjs`：Node 22 合成測試驗證輸入、輸出、拒絕路徑、隱私欄位及解碼清理。此測試**不是**實際 GPU 渲染。
- `.github/workflows/mecha-v80-image-review.yml`：把既有 v7.8／v7.9 參考核心與 v8.0 新測試串成回歸。
- **v8.0 Windows 選用升級差分 ZIP** 在本次交付對話另附：內有真正 `UPGRADE_V80.py`、`ROLLBACK_V80.py`、`INSTALL_V80_WINDOWS.cmd`、兩個 runtime JS、離線 HTML、測試及完整安裝說明。安全升級器比對 v7.8 原 `mech-addon.js`、`patch_slop.py` 的唯一錨點與原玩家 GLB SHA，備份後只加新的遊戲內分析按鈕及模組。

## 界線

目前無法取得檔案庫 v7.8 Windows 完整 ZIP 的原始位元組，所以只完成**模擬原版文字錨點的差分安裝測試**，沒有在完整 Windows 3D 遊戲上直接升級，也不能宣稱已測試五分鐘關卡、WebGPU 實際截圖、煙霧透明排序、GPU FPS/VRAM 或人物／敵機穿模。新功能不改傷害、戰鬥邏輯、原始幾何、角色 GLB、貼圖、城市碰撞或光影。

## 版本安全

本 PR Base = v7.9 功能分支，而非 main；保持 Draft，不合併任何舊 PR、不更新公開網站、不覆寫舊版完整 Windows ZIP。真正完整整合需取回原 v7.8 ZIP 並在 Windows Chrome／Edge WebGPU 實機驗收。