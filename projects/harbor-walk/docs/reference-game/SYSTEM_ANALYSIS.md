# 原作遊戲流程與獨立重建

| 系統 | 原作可驗證證據 | 未確認項目 | 本版原創實作 |
|---|---|---|---|
| Rendering | cooked SM5/SM6 shader library 路徑、材質貼圖名稱、影片陰影 | 實際渲染選項、toon 算法、後製參數 | Three.js PBR、ACES、色彩管理、陰影、海面與薄霧 |
| Character | `ThirdPerson/Blueprints/BP_ThirdPersonPlayerController.uasset`、影片移動 | 移速、加減速、狀態條件 | 相機相對 WASD、加減速、面向、Shift 跑步 |
| Animation | `ABP_Unarmed_*`、`BS_Idle_Walk_Run` 名稱 | 藍圖圖表、root motion、IK | 真 GLB 骨架動畫與 crossfade |
| Physics | `*_PhysicsAsset.uasset` 名稱 | 原作 collision primitives、solver 設定 | Rapier capsule / KCC、重力、靜態碰撞 |
| NPC / AI | `xSeries/xBP/BP_GirlBase.uasset`、`INT_Girl.uasset`、影片居民 | 行為樹、感知參數、導航細節 | 路點巡邏、等待、接近轉向 |
| Interaction | `xSeries/xUI/WBP_AimIcon.uasset`、影片粉紅目標圈 | 原 target selection 算法、視線規則 | 距離 + 靜態遮擋 + E 鍵對話 |
| Gameplay | `xSeries/xBP/BP_GameManager.uasset`、影片計分倒數 | 原分數公式、任務規則 | 收集三枚印記，交付手帖，防重複計分 |
| UI / HUD | `UI_Menu.uasset`、`UI_Fishing.uasset`、`UI_FinalResult.uasset` | UI 內部事件與動畫 | 原創 DOM 面板、提示、地圖、對話、結果 |
| Camera | 影片第三人稱跟隨、近距離視角 | SpringArm 實際參數、避障 solver | 平滑追蹤、拖曳 yaw/pitch、raycast 回縮 |
| Assets / scene | `.pak/.utoc/.ucas`、SchoolRoom 路徑、打包 manifests | streaming／載入時序與資產依賴圖 | 一個原創街區、GLB 載入進度與失敗重試 |

本表的名稱證據只是原作能力的線索，不是 Blueprint decompilation。`BP_GameManager` 等壓縮 chunk 解碼受限，原控制流程和事件圖尚未恢復。

觀察到的原作循環是：移動 → 鄰近目標 → UI 選擇 → 動作／效果 → 分數與倒數回饋。新作品採獨立設計：探索海風里 → 向阿澄接委託 → 收集三枚街區印記 → 交給阿青 → 慶祝與 150 點結果 → 繼續散策。沒有複製原作的角色、對白、地圖、選單圖像或互動主題。

原創模組架構與圖表見 `../architecture/ENGINE_DECISION.md`。後續深入原作研究需要可合法使用、支援此版本 Oodle 與 cooked UE5.6 格式的解析鏈，才有條件解析 skeletal mesh、animation sequence、Blueprint bytecode 與材質參數。此版沒有金鑰破解、記憶體注入或動態掛鉤。
