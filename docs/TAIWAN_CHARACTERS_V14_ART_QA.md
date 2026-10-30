# V14 臺灣街頭 NPC 四人：真實臉部配件形變驗收（草稿）

日期：2026-10-30。狀態：**MPFB/GLB 結構檢查通過；高品質遊戲美術驗收未通過**。

## 實際產出與證據

- GitHub Actions [41072947135](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41072947135)：先讓主角與老闆娘的牙齒、舌頭、睫毛完成 MPFB 原生表情插值。
- GitHub Actions [41073651911](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41073651911)：四人版本已成功，原始 Artifact 名稱為 `taiwan-v14-4-roles-10-shape-face-accessory-PILOT`。
- 4 位真正不同的 MPFB 人體：you（主角）、boss（老闆娘）、uncle（阿伯）、jie（外送員）。
- 4 GLB 大小（實際檔案）：you 4,139,356 B；boss 4,040,452 B；uncle 3,689,592 B；jie 3,927,272 B。皆小於每角色 6 MB。
- 每人具有 53 根 game_engine 骨骼、只留 13,380 個真正人體網格頂點（已物理刪除 helper）、開源 CC0 獨立上衣與長褲。
- 人體具有 10 個 **真正** MPFB ARKit-style morph targets：mouthOpen（jawOpen 別名）、jawLeft、jawRight、mouthSmileLeft/Right、eyeBlinkLeft/Right、browInnerUp、mouthFrownLeft/Right。
- 原生 `teeth_base`、`tongue01` 皆具有 **非零 mouthOpen 頂點位移**，`eyelashes01` 有非零眼皮 blink 位移。已檢查 GLB 內 POSITION accessor 位移，並非僅改名字。
- 28 張真正 Blender Cycles 渲染照片：四人各正面近景、45 度、側面、全身，以及 3 種表情（微笑、張嘴、眨眼）。

## 本輪發現的真正故障與修正

**第一輪失敗**（Actions 41072368698）：MPFB 官方 FaceService 找不到我們額外解壓的 MHCLO 配件來源。因此牙齒舌頭沒有插值，即便人體有口部表情。

**第二輪修正**：保留 MPFB 官方 `FaceService.interpolate_targets()` 幾何演算法，針對非標準資料夾中的外部 CC0 原始 MHCLO，從配件上原有的 `asset_source` 欄位解析實際來源路徑。這個對應在 Blender 執行時是唯一且可驗證的，執行完立即還原原本的 resolver，不變更 MPFB 本體。

**結果**：牙齒、舌頭、睫毛現在會隨表情動。V13 的張嘴黑洞改善為可看到同步移動的牙齒；仍沒有達到真實口腔解剖或 AAA 遊戲外觀。

## 仍須拒收的地方（實際從 V14 四人視圖看見）

1. **外送員 jie：T 恤和褲子中間仍有一條明顯露腰皮膚。** 即便目前腰褲前處理將最高點提升約 7cm，仍不能證明衣緣在正面所有位置完全相交；全身 Blender 圖證實仍留空隙。
2. **老闆娘 boss：針織衣物胸前存在過度凸起的造型感**，需要修衣服的幾何輪廓與布料法線。
3. **人臉精緻度**：嘴唇開合較僵硬、牙齒排列偏粗略、鼻翼與眼周細節不足，臉部材質塑膠感明顯。主角與外送員仍存在相似感。
4. **髮型**：幾個素材髮束像塑膠殼，缺少分層及高精度材質。
5. **尚無動畫 QA**：53 根骨骼存在，不等於走路、碰撞、換裝會成功；角色 8 人完整包目前只有 4 人，禁止冒稱完成。

## 下一輪優先級

- 優先以 **正面腹部實際頂點間隙** 計算衣褲遮蔽，不再用全模型最高／最低 Z 值猜測前腰高度。針對腰部跑真實幾何 QA，再出全身 Blender 圖。
- 改善臉部：臉型辨識度、真實眼周、牙齒/舌頭尺寸與下顎表情比例。
- 再導入另外 4 位人物與更豐富的原生 CC0 髮型及服裝，全部需檢查個別授權。
- 骨架動作與服裝穿模測試通過後才考慮正式八人發行。
