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
