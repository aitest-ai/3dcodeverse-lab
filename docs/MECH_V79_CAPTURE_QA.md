# 臺北機甲 v7.9：實際 PNG 的離線影像診斷參考版

此獨立分支接續 v7.8 PR #110 (commit 0985765)。它**不是**完整 Windows 遊戲，原有 v7.8 OSM 地圖、玩家 GLB、三型 Blender 敵機、三波防衛戰、煙霧和實際 RenderPipeline 攝影保持不變。

## 新增內容

- `examples/threejs/mech-image-diagnostics-v79.js`：對呼叫端提供的已解碼 RGBA 進行黑屏／白屏／透明像素／低細節／過曝及三時段亮度差的離線檢查。並不取得、產生或認證 WebGPU 畫面。
- `tests/mecha/v79-image-diagnostics.mjs`：用合成測試像素檢查异常與尺寸，**不是**臺北 101 遊戲截圖。
- `.github/workflows/mecha-v79-image-diagnostics.yml`：Node 22 執行 v7.8、v7.9 可攜式程式測試。
- **另行交付的** `v79_offline_capture_audit.html` 是可直接開啟的獨立離線驗收頁，使用者自選 PNG，於本機顯示、分析並匯出不含圖片或相機資料的 JSON。獨立 HTML 尚未集成完整 Windows 包。

## 真正玩法驗收與限制

本輪未取得使用者檔案庫完整 v7.8 ZIP 的可授權原始位元組，因此**沒有修改**正式 Windows `mech-addon.js`、`mech-capture-v78.js` 或 `patch_slop.py`，也沒有發布新的完整 Windows 遊戲包。

尚未測試：Windows WebGPU 三張實際臺北畫面、不同光線下的煙霧透明排序、真正 GPU FPS/VRAM、五分鐘三波任務、機甲穿模、手機運作。綠燈只表示影像啟發式檢查未發現疑點，不代表真實遊玩通過。

**Draft，不合併 main、不覆蓋舊 ZIP、不更動公開網站。**
