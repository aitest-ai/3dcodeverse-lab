# 0.8.0 來源、授權與修改

本階段固定於 PR #152 的提交 `36547a2349caebd6ae1d04e13ebbb5055479572f`。沿用 pixiv Inc. 的 VRoid beta CC0 範例 Vita β3、Vivi β2；原始作者／版本空欄保持原值。來源網址、原 VRM SHA-256、鏡像固定提交與條款證據見 [THIRD_PARTY_V07.md](THIRD_PARTY_V07.md)。本輪沒有新增外部模型、付費工具或憑證。

Vita 0.2.0 以 0.1.0 的 GLB `c2b0a9522177b2f4ccda29fd886c503b3f58ff503076f65496050a109a559157` 為固定基底，只附加 Start／Stop／TurnLeft／TurnRight；舊 Idle／Walk／Run 的動畫 JSON 與全部舊 BIN 位元組精確保留。Vivi 0.3.0 與其 0.2.0 比較檔完全沿用前版，不重做模型或動作。

Vita 新動作由專案編寫，參考 Harbor 0.3 世界方向與步態規則，再依 Vita 原生 rest pose、155 joints、腿長、鞋底、衣片與手掌方向求解。起停骨盆混合接到已凍結 Walk 曲線，轉身修正世界朝向造成的軸向扭轉，結尾回到完整 Idle。不是原作者動畫、真人動捕、模型訓練或四足動物動作。Harbor 來源／授權見 [THIRD_PARTY_V05.md](THIRD_PARTY_V05.md) 及 Sources 包的 licenses。

原網格、蒙皮、材質、原解析度貼圖、表情、骨長和 VRM metadata 保留。原始 `.vroid` 未取得，提供原 VRM、衍生 Blender 工作副本、原始貼圖與可重現腳本。原衣鞋版型未重做；衣片為烘焙骨骼動作，沒有布料模擬、衣物厚度或全身碰撞核准。

CC0 描述上游模型；新腳本與動作沿用專案貢獻授權，沒有代替其他作者追加 CC0 宣告。Three.js r170、@pixiv/three-vrm 3.3.0 保留 MIT 授權。全部新候選維持 `art_approved=false`、`game_ready=false`。
