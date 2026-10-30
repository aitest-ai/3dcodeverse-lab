# 台灣街頭遊戲 8 人｜臉部美術監工：REJECTED

日期：2026-10-30。此文件是**人工審查實際 Blender Cycles 輸出**，不是生成成功宣告。

## 證據
- 第一版 Actions：https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41019232065
- MPFB 真實宏觀型態變形 v2（目前結構成功但美術失敗）Actions：https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41021688476
- 原始 CC0 素材參考基底：Actions 40991317263
- 審查了八位角色各自的 `*_face.png`、`*_front.png`。注意正式成品不得用 AI 生圖假裝 3D 渲染。

## 審查結果：八位臉部全部 REJECTED
| 人物 | 明顯不合格處 |
| --- | --- |
| you | 額頭與髮線比例不自然；眼睛閉鎖，嘴巴方形凹洞 |
| boss | 原圍裙與人體比例重疊，臉部被遮蔽，頭飾分離 |
| uncle | 老年肌膚與鼻口不自然；黑色嘴巴方洞、眼鏡比例失準 |
| jie | 安全帽、口罩錯位；眼睛閉鎖、表情僵硬 |
| oldman | 眼鏡/帽子漂浮、眼睛錯位、嘴部方洞 |
| cop | 警察帽顏色可辨，但五官比例/眼睛缺陷顯著 |
| shui | 眼鏡尺寸與位置過大，嘴部方洞，花襯衫簡化 |
| bro | 鼻口變形，牙齒/口腔黑洞，項鍊不自然 |

## 根本原因
1. v1 以同一 MakeHuman 中性人體反覆換色、拉寬，沒有真正區分 8 張臉。
2. v2 雖使用 MPFB 官方 `macro_detail_dict` 計算不同性別、年齡、體型的幾何，但**將新基底頂點移植到舊 BLEND 的眼睛、牙齒、服裝、骨架**。這些外部資產仍沿用中性基底，重新貼合不足，故出現嚴重穿模、口腔與眼睛錯位。
3. 使用固定世界座標製作帽子、眼鏡和臉部表情，比例差異大時更容易失準。
4. glTF 結構/頂點數/8個 targetNames 通過 ≠ 真實人臉美術通過。

## 阻擋上線（Release blocked）
- 不接受 v1、v2 ZIP 為正式遊戲角色，不能合併 main。
- 不得將 `STRUCTURE_PASS` 描述成 `ART_APPROVED`。
- 下一輪必須**同一個 MPFB 實例**先生成年齡/性別/體型/臉部 target，再於此身體新增眼睛、眉毛、牙齒、頭髮、服裝與骨架。不可再用舊中性人體的外部資產硬拼。
- 先驗收 `you` + `boss` 臉部、正側面，核准後才延伸其他 6 人。
- 每人要能看出不同的下顎、眼距、鼻形、顴骨、年齡；表情 0 時嘴巴閉合自然、眼睛張開合理；任何頭飾/眼鏡/牙齒穿模都不准發佈。
- 最後還要驗證動畫骨架、衣物變形、32 個方向攝影角度與授權，不可只看 3 張圖片。

## 狀態
`REJECTED_HUMAN_VISUAL_QA`。技術結構測試曾成功，**美術驗收尚未通過**。


## 2026-10-30｜真正同源 MPFB 臉部重建 v3，兩位先導結果

- **執行證據**：https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41024748080 （工作成功；artifact `taiwan-face-v3-PILOT-NOT-APPROVED`）。
- 兩名試作角色：`you`、`boss`；每人三張真實 Blender Cycles PNG 正面、側面、全身，以及 JSON 診斷。
- 已在**同一個真實 MPFB 宏觀變形人體**上裝配正式系統 eyes/eyebrow/eyelashes/teeth/tongue、官方 CC0 髮型、服裝和 53 骨 game_engine rig。保留 13,380 真正身體頂點，實際刪除 helper。
- 具體素材：`you`：short01.mhclo、male_casualsuit01.mhclo；`boss`：short03.mhclo、female_elegantsuit01.mhclo，boss 頭髮材質已深色化。
- 比 v1/v2 的顯著改善：眼睛確實張開且位於正確眼眶；沒有方形黑洞嘴；側面鼻唇比合理；髮型、衣物使用系統原生 MHCLO fitting，不再懸浮球體。
- **人工審查仍不接受發佈**：`boss` 厚瀏海遮一眼；女性老闆娘雖年齡變形已套用，臉部仍過平滑、缺乏真實 50+ 歲肌膚和不對稱特徵；`you` 臉部過白偏蠟像；`boss` 上衣胸前與肩有貼圖/穿模異常；兩位皆無鞋，僅供頭部與衣物原型測試。
- 8 ARKit morphs 此兩人先導尚未重新建立；更**沒有正式驗證表情、可動性或 8 人 34 檔案最終 ZIP**。
- 最新人工狀態：`FACE_TOPOLOGY_AND_EYE_ALIGNMENT_PASS`，但 `ART_APPROVAL=BLOCKED`。下一步優先解決髮際線遮眼、皮膚反射粗糙度/年齡細節、胸前布料瑕疵，兩人合格才升級到全八人表情動畫。


## 2026-10-30｜v4 → v5：臉部、年齡貼圖、髮型、穿模與真實 GLB

- **v4 人工 QA**：Actions 41047071687。每位角色 4 視角，測試老闆娘 short02、short04、bob01；眉眼遮擋改善但發現程式以字母順序誤選 \`middleage_african_female.mhmat\`，且衣服破碎色塊是 **身體穿出衣服** 而非只有布料材質問題。v4 **REJECTED**。
- **v5 人工 QA**：Actions 41047917200。改正使用 \`young_asian_male.mhmat\`（you）與 \`middleage_asian_female.mhmat\`（boss），老闆娘對照 ponytail01/short04/long01，偏好 \`ponytail01\`，不再遮眼。
- 服裝校正是以真實 13,380 頂點身體 BVH 最近表面與法線作穿模修補，修正 you 4,905 個服裝頂點、boss 1,992 個；其中估算原始 signed distance 為負的分別是 108、78。換上不帶破碎印刷的雙色布料材質，並裝配官方 CC0 鞋子。
- **真 GLB 導出**：Actions 41048710339；兩人各 1 GLB，1 skin、53 joints、9 3D meshes、8 image maps，來源身體確實保留 13,380 頂點。未優化 GLB：you 11,710,208 bytes、boss 13,128,664 bytes。
- **驗證過的 GLB 紋理優化**：用 Pillow 改寫 GLB 內真正的 PNG bufferView，8 張貼圖最多 512×512；原始骨架 nodes、meshes、accessors 與每個非圖像 bufferView 位元組都保持完全一致。you 3,794,088 bytes；boss 3,471,744 bytes。對應實作 \`scripts/taiwan_characters/optimize_embedded_glb.py\`。v6 曾嘗試直接在 Blender 內縮圖失敗（貼圖未先載入，處理張數 0），已改採可靠的 GLB 後處理。
- **依然不准正式發布**：兩個 GLB 的 morph targets 數量仍為 0（原要求 8 個表情尚未做）；動態與服裝穿模測試未通過；角色風格仍偏普通 NPC，沒有達到高品質遊戲近景角色的皮膚與衣物細節；其餘六位尚未製作同一套真正的來源人體與原生 fitted assets。
- v5 結果只可描述為 \`TWO_CHARACTER_STRUCTURAL_PILOT\`，**不是 8 人完整資產，也不是 ART_APPROVED**。


### 正式可重跑的兩人 6 MB 體積檢查（Success）

- GitHub Actions：**41050118969**，成功，artifact 名稱 \`taiwan-two-optimized-MPFB-GLB-PILOT-NOT-FINAL\`。
- 從合法實際 Blender 匯出的 2 個 GLB 出發，在獨立 Python 程式 \`optimize_embedded_glb.py\` 對貼圖的 GLB bufferView 進行 PNG 縮圖及 4-byte 對齊重建；不重新建模、不修改骨骼與 mesh buffers。
- 主角 \`you_v5_main.glb\`：11,710,208 → **3,794,088 bytes**；老闆娘 \`boss_v5_ponytail01.glb\`：13,128,664 → **3,471,744 bytes**。
- Actions 自動斷言每張嵌入貼圖 <=512px、GLB <6MB、每位至少有 1 skin、多個 mesh、4 張實際 Blender 角度圖、真正 13,380 身體源頂點與合法 report。
- 目前 GitHub Actions 只交付 **兩人先導測試**，沒有默默恢復不合格的八人批次，PR 繼續 Draft。
