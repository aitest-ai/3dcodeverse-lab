# 交接點 0.7.0 · 2026-11-05（臺北時間）

目標：改善上一版 Vivi 跑步偏蹲，讓較長腿的 Vita 用自己原生衣鞋、骨架驗證可共用規則。獨立分支 `feat/character-studio-v07-run-posture-20261105`，基底 Draft PR #151 的 `d58ec88446bde04fa79db1323ca4c4c340e0269f`。只新增 v07 檔案，前版、main、既有母檔與其他網站保持不變，不自動合併。入口：[README_V07.md](../README_V07.md)。

## 已完成

- Vivi `vroid-vivi-motion-review / 0.3.0`：只改 Run，其他六段 GLB 動畫精確保留。原骨盆高度約腿長 84% 導致蹲姿；新曲線按支撐／騰空相位在 93–95% 間變化，以原生腿長及鞋底點重解 IK，未拉長腿或鎖直膝蓋。週期 0.7 s，根速度約 1.489 m/s。
- Vita `vroid-vita-motion-review / 0.1.0`：原生 155 joints、腿長約 0.804 m（Vivi 152 joints、約 0.632 m），新增 Idle／Walk／Run。Run 共用相位與原生長度求解工具；Walk 另用支撐期較高、換腳期較低的骨盆曲線。步幅、站距、鞋底與衣片鬆量為自己的設定，沒有直接貼 Vivi 局部旋轉。Run 約 1.895 m/s。
- Vita A 為 `vroid-vita-motion-experiment / 0.1.0` 低骨盆試作，不是原作者動畫；A/B 都有自己的母檔／profile／SHA。原 VRM 沒有動畫。
- 原始 GLB/VRM BIN、網格、權重、材質、貼圖與 metadata 保留。Vita 衍生 Blender 副本權重依原 GLB 同步，原始母檔不動，原因與數量記錄在 adaptation.json。
- 裙骨求解必須先重設整條原生鏈，再加當前腿姿修正。直接在舊烘焙姿勢疊加角度會造成衣襬過度翹起；失敗試作另列 `evidence-v07/rejected-trials.json`，不列為成品。
- 網頁 A/B 按相位比較，以 B 的原生秒數為時鐘。A 舊週期可能加速，不得稱同秒數／各自原速比較。單看 B 就是其原生速度。Vita 未製作的連續動作按鈕停用。

## 驗證與交付

`evidence-v07/acceptance-summary.json` 彙整程式、冷開 Blender、實際瀏覽器、真機與人工美術的不同狀態。Vivi Run、Vita Idle/Walk/Run 每比較變體共 632 個 120 Hz 樣本，含實際變形網格、腳底、分接觸段漂移、膝彎曲、軀幹角度、指定裙片／腿部與手部 Skin 交叉，以及全網格循環接縫。141 張實際瀏覽器連續畫面與兩段 WebM 保留；CPU 編碼可能掉格，以 ffprobe 時長為準。

原生動作／蒙皮 Blender helper 沿用前階段並保留來源。inverseBindMatrices 的 rest 與 VRM 骨骼 matrixAutoUpdate 修正不可退回；根位移循環仍在獨立父節點累積，不改 AnimationMixer 擁有的根通道。Runtime 含兩位角色，兩個角色 Sources 包各含本階段重建所需直接輸入、原 VRM／貼圖／母檔。較早版本完整製作鏈留在前版固定套件。

實際環境：Blender 5.2.3 LTS e13b728c6880、4 CPU quota、16 GiB、無 GPU；Chromium + SwiftShader。沒有新帳戶、憑證、付費工具、真人動捕或訓練完成的 AI。

## 限制與下一步

人工美術、手機真機、Godot／地圖內、任意速度混合、地形接地、全身／衣物自碰撞仍未驗；所有候選 `art_approved=false`、`game_ready=false`。先人工檢視兩種身形的走跑、手臂與衣襬風格，再補 Vita 起停／轉身；動物沿用已存在的柴犬與馬庫擴充，不能將人體雙足相位直接搬到四足。

舊 PR #50/#137/#39、台灣 V29–V31 與基隆河 V110/V111／彩虹橋盤點沿用前階段，缺口仍明列，沒有回退 V103。既有 20 個候選與原始動物成果未被本版替換。
