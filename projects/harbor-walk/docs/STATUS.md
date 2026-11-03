# 驗收與交付狀態 · v0.1.0

日期：2026-11-03（Asia/Taipei）。這是可玩垂直切片候選，沒有把高品質商業遊戲的全部標準標為完成。

## 已完成並有執行證據

| 項目 | 結果 | 證據 |
|---|---|---|
| REA 安裝與 Codex 註冊 | 6.8.0 setup ready，registration / skill aligned | `evidence/rea-setup-result.json`、`rea-doctor.json` |
| REA 真正呼叫 | ZIP artifact / desktop application / PE imports 成功，含 Evidence ID 與 digest | `docs/REA_SETUP.md`、`evidence/rea-*.json` |
| ZIP 安全與檔案研究 | 402 成員；路徑、大小、壓縮比、CRC 檢查完成 | `zip-inventory.json` |
| 引擎判定 | Unreal 5.6.1 字串、UE5.6 build marker、PE AMD64、IoStore header 與 REA marker 一致 | `reference-facts.json`、`retoc-info.txt` |
| 原作資產索引 | 812 packages / 2441 chunks，骨架／動畫／材質／NPC／UI 路徑已列出 | `retoc-paths.txt`、研究報告 |
| 原創場景與玩法 | 自製港口街區、WASD、跑步、加減速、第三人稱視角、Rapier 重力／碰撞 | `src/`、真瀏覽器錄影 |
| NPC 與完整任務 | 兩位 NPC 巡邏／等待／轉向／對話；三印記收集、交付、150 點結果 | `browser-qa.json`、`quest-complete.png` |
| 骨架與母檔 | Blender 4.3.2 真 `.blend` / GLB；65 joints、1 skin、7 nonconstant clips、1 morph | `assets/`、`asset-deep-validation.json` |
| 視覺證據 | 真 Blender 前／側／背／臉部渲染、真遊戲截圖與完整操作錄影 | `evidence/character/`、`gameplay.mp4` |
| 建置與測試 | TypeScript、Vite build、4 個有實質斷言的單元／物理測試通過；15 項真瀏覽器遊戲驗收通過 | `build.log`、`unit-tests.log`、`browser-qa.json` |
| 預建版本／工房／重試 | PASS，11 項檢查 | `review-qa.json` |

主遊戲的 15 項瀏覽器測試用真鍵鼠及 DOM 操作，觀察介面沒有位置或任務修改能力。包括 Idle 骨變化、Walk 切換、停止回 Idle、滑鼠旋轉、兩 NPC 實際位移、接任務、三印記、交付、碰撞、camera 回縮與零 JavaScript error。完整任務在 Vite 開發伺服器驗證；預建 `dist/` 另外檢查載入、動畫工房、失敗重試與 responsive layout。沒有將它們混稱為正式網站已部署或實機已通過。

## 尚未完成／品質未通過

1. **本對話 REA MCP live connection**：host 無熱載入／重啟工具；採官方 CLI 真實執行。native decompiler providers 未配置。
2. **原作壓縮模型與 Blueprint 完整解碼**：IoStore 的 Oodle 依賴不可用，選擇性轉換部分失敗。沒有量測原作骨數、拓樸、蒙皮、Foot IK、root motion、shader 演算法或完整事件圖；沒有破解加密或下載專有 codec。
3. **高品質角色美術**：目前是合法 CC0 人體／髮型／衣物／動作的改作，加上原創配件與造型；不是全數自行建模。需改善肩部服裝接縫、領巾／肩帶厚重感、手臂配色與 NPC 輪廓差異。未做全動畫逐格穿模與足底滑動量測；`art_approved=false`。
4. **動作完善**：無 Foot IK、turn-in-place 角度校準、stride matching 或 root motion；Turn 是新製作的骨架候選片段。走跑速度與動畫節奏只有基本縮放，未做動捕級校正。
5. **硬體效能未達標驗收**：本次 Chromium ANGLE SwiftShader 軟體繪圖，960×600、省電畫質、最後 300 個 frame 平均 **3.01 FPS**，p95 frame **550 ms**。這是雲端軟體渲染結果，不能證明桌機 GPU 60 FPS 或手機 30 FPS。低 FPS 時因固定步長追趕上限而放慢遊戲時間；待硬體測試與進一步最佳化。
6. **手機與平台**：只有 430px Chromium emulation 排版檢查；沒有觸控移動、Android／iOS 實機、Windows 安裝或手機效能測試。
7. **擴充功能**：無存檔、多場景串流、NavMesh、LOD、KTX2、音效／配樂或自動動態解析度。NPC 與其他 kinematic 不互相實體阻擋；環境碰撞已測。
8. **GitHub 私人 repo 建立**：integration 的 createRepository 權限拒絕，改用既有庫獨立分支與獨立 `projects/harbor-walk/` 子專案的 Draft PR。沒有合併、部署或覆寫既有網站。實際交付連結另記 `DELIVERY.md`。

## 修正與失敗紀錄

- 初版 Euler／Quaternion 混用造成 T-pose，已修正為 Quaternion keyframes；GLB channel 與真瀏覽器骨變化已確認。
- 初版 GLB 約 44 MB，貼圖最大降至 1024，最終 **11,547,472 bytes**。仍可進一步去重與壓縮。
- 場景依材質合批，首輪鏡位 draw calls 約 643 降到 113；完整驗收結束鏡位為 71 calls、62,048 triangles。鏡位不同，不能當作嚴格同場景效能 benchmark。
- 第一輪 QA 路線穿過真樹幹，被碰撞阻擋；保留 `evidence/history/browser-qa-tree-collision.json`。第二輪改走東側通道，完整任務與後續碰撞／攝影機檢查全部通過，沒有移除障礙物或使用 teleport。
- 多入口 build config 少一個 brace，經 build 發現並修正，失敗 log 保留 history；以最終成功 build 為交付版本。
- 初次角色預覽啟用不可用的 denoiser，改為 CPU Cycles 16 samples 並關閉 denoising 後真實輸出四個視角。圖像有取樣雜訊，沒有用後製圖冒稱渲染通過。

## 下一個可驗收里程碑

先在桌機 GPU 與一台中階手機實測，再針對實際瓶頸做 rendering/texture 最佳化；接著完善服裝接縫與 NPC 差異，對 Walk/Run/Turn 做逐格足底與穿模量測。原作深入模型研究需另有可合法使用的 Oodle／UE5.6 解析鏈。保留現有可玩核心與證據，避免每次從頭重做。
