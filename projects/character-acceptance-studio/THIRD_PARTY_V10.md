# v0.10 來源、授權與修改

原作者 Quaternius，Ultimate Animated Animals：
https://quaternius.com/packs/ultimateanimatedanimals.html
原動物素材 CC0-1.0。既有 Horse Library 2.3.0 的 UV／PBR 程序貼圖與鬃毛派生作者為 aitest-ai；保留原包 `LICENSE_AND_SOURCE.md`、registry、SHA256SUMS、GLB、Blender 與 1024px 原始貼圖。來源正式版本：https://github.com/aitest-ai/3dcodeverse-lab/releases/tag/horses-v2.3.0 。未把素材尺寸縮成 512px，未重新製作幾何或服裝。

本輪由 aitest-ai 專案的 AI 協作流程，新增獨立候選 ID `horse-brown-grounded-review`／`horse-white-grounded-review`，版本 0.1.0；僅改 Walk／Gallop 的循環與蹄部接地動作。可編輯工作副本權重同步至既有 GLB 的四影響權重，原始母檔不變；GLB 幾何／權重／材質／貼圖的舊二進位內容精確保留。各候選來源與輸出 SHA 見 adaptation.json、config-v10/horses.lock.json；整包每檔 SHA 見 ZIP 內清單。

原生骨架的參考姿勢、骨名父子、軸、尺度與骨長記錄由 v09 horse profile 延續，各模型分別匯出。棕／白馬材質分區與鬃毛資料各自保留，沒有把白馬當成不同解剖身形的驗證。

Three.js、three-vrm 等瀏覽器依賴保留既有 vendor 授權，詳 THIRD_PARTY_V04.md 與 THIRD_PARTY_NOTICES.md。原資產 CC0 不代表所有外部工具或專案程式一律 CC0。本輪未使用額外付費模型、帳戶、動作生成服務或自訓模型。

發佈狀態：僅 Draft PR 的驗收候選，art_approved=false / game_ready=false；原版 2.3.0 Release 與正式 registry 不更新。
