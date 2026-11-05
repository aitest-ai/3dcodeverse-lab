# v0.12 來源、授權與修改

3D 原作者 Quaternius，Ultimate Animated Animals：https://quaternius.com/packs/ultimateanimatedanimals.html ，原動物素材 CC0-1.0。既有 Horse Library 2.3.0 的 UV／PBR 程序貼圖與鬃毛派生作者為 aitest-ai。來源正式版本：https://github.com/aitest-ai/3dcodeverse-lab/releases/tag/horses-v2.3.0 。保留 LICENSE_AND_SOURCE.md、registry、SHA256SUMS、GLB、Blender 與原始 1024px 貼圖；沒有重採樣或降低貼圖解析度。

本輪直接來源是 v11 `horse-brown-walk-world-review@0.1.0` 與 `horse-white-walk-world-review@0.1.0`。來源 SHA 分別為 `b5036b2f646bd7026d66aacf41249509ec1d44f0957124bf9c271c6d4125ddc9`、`8a95e2c2398a005e91d5b755fb80571b1ac415c3eb69ddec64841cb54dbea99d`。A 完整使用這兩個已鎖定版本及其完整母檔，不重製比較動畫。

aitest-ai 專案 AI 協作流程新增 `horse-brown-walk-support-review`、`horse-white-walk-support-review`，各版本 0.1.0。B 只替換 WalkWorld，落蹄相位 LH .19 / LF .44 / RH .69 / RF .94，支撐比例均為 15/28。原生 50 骨、骨長、rest、所有節點、根位移、其他 13 段動作、幾何、權重、材質與貼圖保留；v11 的 20mm 身體姿勢下修保留。沒有重新訓練模型、套用其他骨架的動作或宣稱取得真人／真馬動作捕捉資料。

步態研究僅作時序與驗收指標參考，不是模型或動畫素材：Alan Vincelette (2023), The Characteristics, Distribution, Function, and Origin of Alternative Lateral Horse Gaits, Animals 13(16):2557, https://doi.org/10.3390/ani13162557 ，CC BY 4.0；Hilary M. Clayton and Sarah Jane Hobbs (2019), A Review of Biomechanical Gait Classification with Reference to Collected Trot, Passage and Piaffe in Dressage Horses, Animals 9(10):763, https://doi.org/10.3390/ani9100763 。本輪未複製文章圖片、影片或動作資料，只附來源與少量事實摘要，詳 config-v12/references.json。

GLB、Blender、骨架設定與來源雜湊見 adaptation.json、skeleton-profile.json、config-v12/horses.lock.json。ZIP 各檔雜湊列於封裝清單。Blender 序列化可能因建置環境產生不同母檔 SHA，以實際包內清單為準；GLB 必須符合固定 SHA。可編輯 TRS 文字曲線用來穩定跨機器輸出，每次仍重新求解並比對，不會掩蓋失敗。

Three.js、three-vrm 等沿用既有 vendor 授權，詳 THIRD_PARTY_V04.md、THIRD_PARTY_NOTICES.md；前期修改見 THIRD_PARTY_V10.md、THIRD_PARTY_V11.md。素材 CC0 不代表所有工具或程式均採 CC0。沒有付費工具、額外帳戶、模型權重或網站部署。

候選 art_approved=false / game_ready=false。白馬與棕馬是同一解剖身形的材質／鬃毛變體；不代表第二種身形通過。正式 Release、registry、main 與地圖網站不更新。
