# 交接點 0.5.0 · 2026-11-05（臺北時間）

工作分支 `feat/character-studio-v05-vivi-shiba-20261105`；基底為 PR #148 的 `7bd1e577d2867e3c4772f2655c8285cae5ac0700`。本階段只新增 v05 路徑、兩個新候選 ID 與獨立驗證 workflow；沒有改 main、既有母檔、前階段 GLB／ZIP 或其他專案網站。

交付入口：[README_V05.md](../README_V05.md)。原始 PR #50/#137/#39、V29–V31 及基隆河 V110/V111／彩虹橋盤點沿用前階段紀錄，不把 main 當成果全集。V111／彩虹橋最新可編輯成果缺口仍未補齊；沒有改拿 V103。來源鎖、原作者授權、各舊候選／失敗狀態保留。

## 本階段工程重點

- 原始 GLB/VRM 二進位區塊完整保留，動畫另附；新增共同根節點，沒有統一骨頭數或重塑身形。
- Vivi 使用原生 152 joints，明確 T-pose／世界軸適配、左右前彎膝／肘、前臂掌向、目標腿長與鞋底接地、裙骨響應；不複製不相容骨架局部旋轉。
- 柴犬保留 46 joints，原作者軀幹／尾巴動作，原生前腿 2 鏈與後腿 4 鏈 IK 做接地，再烘焙 FK。以原始幾何肩部測量換算指定 0.40 m 遊戲尺度，非生物學精度認證。
- 真正 bind pose 從 inverseBindMatrices 取得，不能把動畫預設 node pose 當 rest pose。原生柴犬 GLB 的兩者確實不同。
- 停用 VRM SpringBone 物理時，必須讓原生骨骼 matrixAutoUpdate 恢復；否則裙骨動畫旋轉已改、矩陣卻保持原姿勢。這是本階段實際瀏覽器比對發現並修正的問題。
- 新 Blender 工作副本權重對齊原 runtime GLB：Vivi 對重複骨骼影響加總，柴犬對齊原四影響輸出；原生 Blender 來源不動。修改頂點數與權重差異寫在 adaptation.json，不能描述成「完全沒改工作副本權重」。

## 實際環境

Blender 5.2.3 LTS（build e13b728c6880）、4 CPU quota、16 GiB RAM、無 NVIDIA GPU／/dev/dri。瀏覽器 Chromium + SwiftShader；未宣稱高階 GPU、真人動捕或自行訓練。沒有新增付費服務、帳戶、憑證或模型存取需求。原始貼圖不重採樣。

## 延續工作

先看 `evidence-v05/index.html` 與 `browser-contacts.json`，再開即時驗收場。接地通過不等於美術通過。手型、裙襬布料感、跨片段混合、完整碰撞、真機與第二引擎仍待完成。保留所有 `art_approved=false` 與 `game_ready=false`，直到有明確人工驗收紀錄。

每個後續角色建立新 ID／版本，沿用骨架語意與適配規則；不要把 Vivi 的全套通道直接貼到 KayKit，或把人體雙足相位套到犬／牛／馬。修改／重新匯出只寫新候選檔；勿覆寫本版 frozen model.glb 或發布為其他地圖的自動更新。
