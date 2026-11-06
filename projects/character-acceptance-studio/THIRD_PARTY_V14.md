# v0.14 來源、授權與修改紀錄

2026-11-06（Asia/Taipei）。原作 **Quaternius** Horse 為 CC0，既有 UV／PBR／鬃毛修改由 aitest-ai Horse Library v2.3.0 管線產生。來源、原始授權及作者證據保留於 `THIRD_PARTY_V04.md`、`THIRD_PARTY_NOTICES.md`、`sources-v04/horses/`；貼圖原始解析度與位元保留。Three.js 與 three-vrm 的 MIT 授權隨 vendor 交付。

直接輸入是 [v13 Draft PR #159](https://github.com/aitest-ai/3dcodeverse-lab/pull/159)，commit `fac4b1c99de06a0d6a75617a231ecb8626e6dcf5`：

| ID／版本 | GLB SHA-256 |
| --- | --- |
| horse-brown-walk-transition-review@0.1.0 | 882fc780b7f0ed00c85dfa98afc6a4615fdeda5c6ae0cb53469b8f5e27880b2d |
| horse-white-walk-transition-review@0.1.0 | f07734fe54e91cff8c996a81f36cbca68e77de01d553fee96a3abe0654fdddca |

A 沿用上述兩項精確版本，不重新修改或發行。B 新 ID 為 `horse-{brown,white}-walk-smooth-review@0.1.0`，只改 `WalkWorld`、`StartWalk`、`StopWalk` 的身體曲線：原生 Walk 首尾各 1.5% 局部 Hermite 過渡與原接縫姿勢約束、既有接地 IK，再以 240 Hz／局部 2400 Hz 烘焙。其餘 15 動作、所有根位移與來源場景／貼圖資料精確保留。

未引入新模型、外部動捕、付費服務、帳戶或生成模型權重；程序修改不等於自行訓練模型。新 GLB SHA 見 `config-v14/horses.lock.json`；來源與輸出母檔、profile、修改紀錄和完整雜湊在各資產目錄及 catalog。兩個 ZIP 各附每檔 SHA 索引；文字 TRS 的雜湊由 `scripts/v14/curve_recipe.py` 鎖定。

全部仍是 review candidate；接地與程式通過不等於人工美術／遊戲完成。前輪未鎖蹄失敗試驗與本輪未採用的平順試驗均不列入 v14 成品取用清單。
