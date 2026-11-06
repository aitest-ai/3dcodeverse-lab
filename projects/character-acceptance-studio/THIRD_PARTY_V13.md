# v0.13 來源、授權與修改紀錄

2026-11-06（Asia/Taipei）。角色原作 **Quaternius**，Horse 動物資產為 CC0，可修改與隨專案交付；既有來源證據、原始材質與授權文件見 `THIRD_PARTY_V04.md`、`THIRD_PARTY_NOTICES.md`、`sources-v04/horses/`。UV、PBR 與鬃毛由 aitest-ai 的既有 Horse Library v2.3.0 管線產生。原始貼圖位元與解析度保留，沒有全部縮成 512px。

直接輸入來自 v12 Draft PR #158，commit `a6240e57f3154a0fa3060916d41edac1ddd74d0d`：

| ID／版本 | GLB SHA-256 |
| --- | --- |
| horse-brown-walk-support-review@0.1.0 | 1904546061754251a43b85d555046a200e821410e8ebb1a4e88cb177f7853978 |
| horse-white-walk-support-review@0.1.0 | 6db040ebc75cce158d350cd142b17fa7446e18bdd04bdf7edd00db425c2084f3 |

本輪由 aitest-ai 專案新增 `StandReady`、`StartWalk`、`StopWalk`、`StandStopped`，以原生骨架 Idle／Walk 參考姿勢、解析加減速路徑與固定世界落點解算後烘焙。它不是外部動捕、AI 動作模型或自訓模型。未下載額外權重、使用付費服務或新增帳戶。

B 新 ID 為 `horse-{brown,white}-walk-transition-review@0.1.0`；A 為 `horse-{brown,white}-transition-baseline@0.1.0`。A 僅供未修正比較，具有已知腳滑／穿地／跳接，不能當正式成品。所有原有 14 動作、節點、rest、網格、權重、材質、貼圖與原始 BIN 前綴都保留。

各 GLB 的新 SHA 在 `config-v13/horses.lock.json`；母檔、source GLB／母檔、骨架設定、修改紀錄及版本在各資產 `adaptation.json`、`skeleton-profile.json`、catalog。兩個 ZIP 各附完整 SHA-256 檔案索引。文字 TRS 曲線 `motion-v13/horse-transition-curves.json` 的 SHA 為 `309bd0651022084a7e5690671346e4dbbbd12647e86208f5a03a4214151a12fe`。

Three.js MIT 與 three-vrm MIT 的授權隨原本 `web/vendor/`、`web-v04/vendor/` 提供。v12 步態文獻保留於來源文件，僅供運動學參考；本輪沒有複製論文圖片、數據或擷取外部動畫。
