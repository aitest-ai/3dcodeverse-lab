# v0.11 來源、授權與修改

原作者 Quaternius，Ultimate Animated Animals： https://quaternius.com/packs/ultimateanimatedanimals.html ，原動物素材 CC0-1.0。既有 Horse Library 2.3.0 的 UV／PBR 程序貼圖與鬃毛派生作者為 aitest-ai。正式來源：https://github.com/aitest-ai/3dcodeverse-lab/releases/tag/horses-v2.3.0 。原包 LICENSE_AND_SOURCE.md、registry、SHA256SUMS、GLB、Blender 與 1024px 貼圖完整保留；未降低解析度。延續 v10 接地候選，來源動作仍是既有原生骨架動畫，沒有真人捕捉或自訓模型的宣稱。

本輪 aitest-ai 專案的 AI 協作流程新增 `horse-brown-walk-world-review`、`horse-white-walk-world-review`，版本 0.1.0。保留 v10 全部 13 段動作及原有 50 根骨、幾何、材質、貼圖，新增 WalkWorld 與獨立位移包覆節點。原始 BIN、節點、骨架、權重精確保留。候選在明示顯示尺度下以 0.8 m/s 前進，每週期 0.933333 m；原生身體姿勢下修 20 mm，原腿長不變，四蹄依預定支撐相位鎖定世界位置，擺動區間平滑銜接。可編輯的 TRS 文字曲線用於跨機器穩定輸出；每次仍執行求解並比對曲線。

`*-walk-translation-trial` 是本輪新製作的 A 比較試驗：v10 Walk 加上同速根位移，仍滑蹄。不是上一版已正式提供的移動動畫。A 的來源母檔是 v10 13 段動作母檔，位移包覆由本輪程式產生；B 有完整 14 段骨架動作與 WalkWorld_Root 的母檔。

所有來源與輸出雜湊見 adaptation.json、skeleton-profile.json、config-v11/horses.lock.json；整包每檔 SHA 見兩個 ZIP 內清單。Blender 儲存序列化可能因建置機器產生不同母檔 SHA，以該包清單為準；GLB 須符合固定雜湊。棕、白馬是同一解剖身形的兩種材質／鬃毛變體，不代表第二種身形通過。

Three.js、three-vrm 等依賴沿用原 vendor 授權，見 THIRD_PARTY_V04.md、THIRD_PARTY_NOTICES.md；v10 修改見 THIRD_PARTY_V10.md。素材 CC0 不代表所有工具或程式均採 CC0。本輪沒有付費服務、額外帳戶、模型權重或訓練工作。

僅 Draft PR 驗收候選：art_approved=false，game_ready=false。正式 Release、registry、main 與地圖網站不更新。
