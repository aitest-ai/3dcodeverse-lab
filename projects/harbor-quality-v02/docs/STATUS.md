# v02 驗收狀態

本版目標是把角色建模、動作量測與成熟引擎加入實際工作流。這是一個品質候選，尚未宣稱達到參考遊戲或商用品質。

## 已執行

- Blender 4.3.2 真實建模、蒙皮、動畫、GLB／FBX／可編輯母檔輸出。新版服裝、領口、袖口、襪鞋、髮束、肩帶與郵包；保留 CC0 人體／髮型／動作來源紀錄。
- 第一輪衣襬與布料邊界鋸齒、肩帶穿插已透過裁切、接合與權重修正；前後圖片留在 evidence/character_initial 與 evidence/character。
- 65 根骨、七段真動畫、兩個 facial morph 結構。批次合併配件降低 mesh 數量；仍需視覺審查表情與變形。
- 真正 evaluated skinned outsole 幾何逐整數影格量測，共 323 個影格；調整每段固定垂直偏移，修正舊 Turn 不完整姿態。這不是 Foot IK 或連續時間／全衣物穿模認證。
- 依取樣估算 Walk 約 0.986 m/s、Run 約 5.882 m/s 的局部 stance 速度，在 Godot AnimationTree TimeScale 中進行基本節奏校準；不宣稱達成 foot locking。
- Godot 4.6.3 實際匯入 GLB、讀取 Skeleton3D／AnimationPlayer，原生 CharacterBody3D、SpringArm3D、AnimationTree、BlendSpace、GUI、碰撞與 Web 匯出。
- 本地 Chromium 執行真 Web export；真鍵鼠驗收正在完成，結果以 evidence/godot-browser-qa.json 為準。
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
