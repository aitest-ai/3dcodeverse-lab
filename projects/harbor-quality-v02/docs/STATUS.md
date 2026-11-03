# v02 驗收狀態

本版目標是把角色建模、動作量測與成熟引擎加入實際工作流。這是一個品質候選，尚未宣稱達到參考遊戲或商用品質。

## 已執行

- Blender 4.3.2 真實建模、蒙皮、動畫、GLB／FBX／可編輯母檔輸出。新版服裝、領口、袖口、襪鞋、髮束、肩帶與郵包；保留 CC0 人體／髮型／動作來源紀錄。
- 第一輪衣襬與布料邊界鋸齒、肩帶穿插已透過裁切、接合與權重修正；前後圖片留在 evidence/character_initial 與 evidence/character。
- 65 根骨、七段真動畫、兩個 facial morph 結構。批次合併配件降低 mesh 數量；仍需視覺審查表情與變形。
- 真正 evaluated skinned outsole 幾何逐整數影格量測，共 323 個影格；調整每段固定垂直偏移，修正舊 Turn 不完整姿態。這不是 Foot IK 或連續時間／全衣物穿模認證。
- 依取樣估算 Walk 約 0.986 m/s、Run 約 5.882 m/s 的局部 stance 速度，在 Godot AnimationTree TimeScale 中進行基本節奏校準；不宣稱達成 foot locking。
- Godot 4.6.3 實際匯入 GLB、讀取 Skeleton3D／AnimationPlayer，原生 CharacterBody3D、SpringArm3D、AnimationTree、BlendSpace、GUI、碰撞與 Web 匯出。
- 本地 Chromium 執行真 Web export；20 項真鍵鼠驗收全部通過，含完整交付、角色近景、表情、碰撞與 SpringArm 回縮。詳 evidence/godot-browser-qa.json。
- FBX 以 Blender 重匯入檢查骨架／動畫；UE-side 結果另列。

## Unreal 尚未執行

本環境沒有 UnrealEditor／UnrealEditor-Cmd，也沒有配置 Epic 存取憑證。交付 .uproject、骨架 FBX、Python import task 及 self-hosted runner 手動 workflow；這些是未經 Unreal 執行的交接候選，沒有 UE 畫面、遊戲建置或原作模型還原宣告。真實狀態在 evidence/unreal-status.json。

## 仍待改善

- 服裝目前是基於合法人體拓樸衍生的貼合幾何，仍需進一步衣料皺褶、鬆量與藝術造型；沒有布料模擬、完整重拓樸或全部關節姿態穿模量測。
- Blink 是幾何 morph 候選，沒有完整閉眼／口型系統；臉部表演尚待藝術審查。
- Turn 為完整 Idle 基礎的站姿轉體候選，沒有真正腳掌鎖定或 Foot IK。
- NPC 暫共用新版人物資產，尚未完成不同臉型、髮型與體型的獨立美術。
- 港口街區仍是小型程序化場景，材質與環境細節尚未達到參考遊戲的整體完成度。
- 網頁使用 Godot Compatibility renderer；本環境是 SwiftShader 軟體繪圖。桌機 GPU、手機實機、60／30 FPS、觸控控制未驗收。
- 僅有一個小任務及步調／限時獎勵選擇，沒有豐富分支敘事、存檔、NavMesh 或多場景串流。
- 不合併、不部署、不覆寫 Harbor Walk v0.1、既有資產或網站。

## 本輪執行結果

- Godot Web 完整任務：20 項 PASS；三枚印記、交付、晚到快遞結果 150 點、碰撞、攝影機、Idle/Walk/Run 與表情全部實測。60 秒內額外 50 點分支已實作，但本輪鍵鼠路線晚到，沒有宣稱及時交付 200 點已實測。
- 軟體繪圖 960×600 CSS 版面，省電模式關閉陰影並將 3D scale 設為 0.5，抽樣 FPS 中位數 8；GUI 保留原解析度。不能與 v01 不同設定的 3 FPS 當作嚴格 benchmark，也不能證明實機效能。
- 標準模式 1280×800 的角色全身、近景、臉部與微笑另外實際截圖，沒有以省電畫質截圖冒稱標準畫質。
- GitHub Actions 已實際成功執行 Godot 模型驗證、引擎匯入、場景重建與 Web 匯出： https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41578361400 。CI 不包含完整瀏覽器遊玩或美術驗收。Artifact ID 13204506978，保留到 2026-12-03，並非永久交付來源；本地交付包另有獨立雜湊。
- 第一輪乾淨 runner 缺少 web 輸出目錄，已修正並以乾淨副本及第二輪 GitHub job 成功重驗。舊失敗 run 41577610351 保留，不改寫為成功。
- 軟體渲染下的連續跑步自動導航曾因輸入／畫面延遲而追點過頭；測試改成真步行鍵脈衝及正常互動距離，不移除碰撞、不 teleport、不修改任務狀態。歷次失敗記錄保留 evidence/history。
- GitHub self-hosted runner 列表讀取被 integration 403 拒絕，不能聲稱已查明遠端沒有 Unreal runner。已知的是本工作環境沒有 Unreal，UE workflow 尚未執行。
