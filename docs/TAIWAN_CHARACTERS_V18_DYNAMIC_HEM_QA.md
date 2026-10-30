# 臺灣街頭角色 V18｜真實骨架動態與毛衣下襬精修實測（2026-10-31）

**此版為 Pilot；美術仍拒收，不得合併 main，也不能稱為八人正式交付。**

## 來源基線與變更範圍

V17 完整來源 MPFB 四人建置在 Actions [41138623403](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41138623403) 成功：you/boss/uncle/jie 各有一份實際 GLB，13380 原始人體頂點、53 game_engine bones、10 組真實 Faceunits 表情；這只證明來源模型結構，非美術合格。

V18 不覆寫 V17，也不直接改 main。以 **V17 來源四角色 GLB** 為輸入，分成兩個獨立實測工作流：

### 1. 53 骨架的真正動態壓力測試

Actions [41140731630](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41140731630) **SUCCESS**，Artifact 名稱 `taiwan-v18-real-armature-2roles-motion-stress-PILOT`。

- 老闆娘 boss 和外送員 jie，皆以 Blender 5.2.3 真正匯入 GLB、操作原有 53 骨、打關鍵影格，建立 neutral、arms_raise、torso_bend、step、reset，真正輸出帶 1 組 animation、159 channels 的 GLB。人體主網格在重新輸出的 GLB 裡仍保有 10 個官方風格 morph targets；這不是重新畫出來的姿勢。
- 初次版本手臂軸向指定錯誤，雙手反而向前下方移動。已加入骨架 FK 實際旋轉軸偵測，依真實手腕高度自動選出左右兩側旋轉：老闆娘左/右手腕各上升 **0.38524m**，外送員各上升 **0.45616m**。正式 V18 僅採用已驗證升高的第二輪輸出。
- 動態偵測採固定正前方 37×35 個 BVH 射線；此數字只是診斷，**手臂、皮膚自然遮住衣服也會被記錄，不可以直接叫作布料穿模**。

| 人物 | 姿勢 | body-first 射線 | 褲子壓到上衣前方的射線 |
|---|---|---:|---:|
| boss | neutral | 0 | 0 |
| boss | arms_raise | 0 | 0 |
| boss | torso_bend | 5 | 0 |
| boss | step | 0 | 3 |
| jie | neutral | 22 | 6 |
| jie | arms_raise | 24 | 6 |
| jie | torso_bend | 72 | 23 |
| jie | step | 22 | 6 |

**結論：** 老闆娘抬手時前視中央網格沒有新增錯層，但跨步出現 3 個衣褲錯層取樣。外送員彎腰有明顯新增的錯層取樣（6→23），應優先針對腰部做角度與 3D 深度精查；尚不能宣稱通過動態穿模驗收。這些是 4 個動作關鍵姿態，不是 walk/run locomotion cycle，也沒有布料模擬。

### 2. 真正的 CC0 毛衣下襬平順化實驗

Actions [41140919867](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41140919867) **SUCCESS**，Artifact `taiwan-v18-boss-real-knit-hem-comparison-DEBUG-NOT-RELEASE`。

- 同一份 V17 boss GLB，由 Blender 匯入後找真實網格 boundary edges，選最下方的寬 hem，對原本毛衣輪廓進行局部受限平順化，不增刪面，不做純貼圖遮蔽，所有原本的 Shape Keys 同步位移。
- glTF 重新匯入後因 UV / 法線拆點，偵測到 **52 個下襬 boundary 頂點**；不同於 V17 來源 MPFB 在 Blender 網格上的 36 點，不可將 52 和 36 誤認為同一套索引。
- 52 點都有小幅位移；最大位移約 **6.878mm**，下襬局部 Z 高度與兩鄰點平均的偏差均值由 **1.520mm → 0.476mm**（只代表幾何邊緣更平順，不代表布料自然）。
- 同一相機燈光下渲染 before / after，右側黑色三角缺口明顯減少；但仍可見下襬有不自然折邊、鋸齒和細小陰影，**仍不可通過美術驗收**。僅處理中性姿態，也尚未驗證彎腰時是否變差。
- 這個毛衣試驗 GLB 需與真實 MPFB 來源 V17 差分合併驗證，現在只是獨立的候選修改，不能直接替換正式四人。

## 下一個技術瓶頸

1. 外送員彎腰時的腰部：需要擴充 3D 側面／背面射線，避免把手臂遮擋當作穿模，同時縮小真正腰部穿模。
2. 老闆娘下襬剩餘的細小陰影與不自然厚邊，需要源網格細修並以四姿態全角度監工，不能僅依數值通過。
3. 真正走路循環、腳底接地、動作連續播放與表情搭配尚未完成。
4. 4/8 人，另外四位角色尚未建立；目前所有 V18 ZIP 都是 QA/Pilot。

**狀態：V18 技術實測成功，仍 ART REJECTED，保留 Draft。**
