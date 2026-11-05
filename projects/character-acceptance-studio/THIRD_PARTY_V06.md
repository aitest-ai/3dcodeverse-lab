# 0.6.0 來源、授權與修改

本階段不引入新素材，沿用已鎖定的 pixiv VRoid β2 Vivi。作者、[官方 CC0 條款](https://vroid.pixiv.help/hc/en-us/articles/360014900273)、[madjin 鏡像固定提交](https://github.com/madjin/vrm-samples/tree/e16eb187100149a315ad92c3c9968f1d5baa6c7d/vroid/beta)、原 VRM 內嵌授權與完整原檔均保留。原始 `Vivi.vrm` SHA-256 為 `eaf902e041a7a810f1423599ae75682f61184ab6ef0206da9a8ed9caa8ec3a9d`。原檔 author/version 空欄未虛構補寫，作者來源見官方條款。未取得 `.vroid` 工程，Blender 母檔是衍生可編輯工作副本。

直接基底為 `vroid-vivi-motion-review / 0.1.0`，來自 PR #150 的固定提交 `477cfb9135038af3dbc00309d0a8998aadbcef88`。A 使用該版修正後 model.glb，不使用更早的失敗 FK 初稿。B 是新的 `0.2.0`。每個版本自己的 Blender 母檔與雜湊都有提供。

本階段保留原網格、蒙皮權重、rest 骨架、材質、表情、VRM metadata、原解析度貼圖及整段 v0.1 GLB BIN 位元組；只附加指定動畫輸出並更新對應 sampler。修改包括原生手指彎曲、Run 前裙骨依大腿抬升作前向鬆量、TurnLeft/TurnRight 的上臂／大腿／小腿朝向扭轉與最後 15% 回到同朝向 Idle。轉身相關局部動畫通道有改動，不宣稱所有腿部通道不變。來源和改動通道逐筆記錄於 `adaptation.json`。

動作仍是前階段專案 Harbor／gait planner 衍生的專案編寫候選，加上本階段修正；不是真人動捕、NVIDIA 正式動作或自行訓練完成的模型。CC0 僅描述上游素材，新增腳本、動作與修正沿用專案貢獻授權，沒有代所有作者另作 CC0 宣告。

每手五個獨立指甲元件與其原生 Skin 嵌合保留；這些來源特性與手指 Skin 相互穿插分開記錄。裙片使用確定性骨骼烘焙，不是布料模擬。數值檢查沒有授予人工美術或遊戲整合核准。

Three.js r170 與 @pixiv/three-vrm 3.3.0 的 MIT 授權保留在各自 vendor 資料夾。詳細上游動作來源、既有資產與授權見 [THIRD_PARTY_V05.md](THIRD_PARTY_V05.md)、[THIRD_PARTY_V04.md](THIRD_PARTY_V04.md)、[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。原始貼圖另附於 Sources，無重採樣。Blender、Chromium、Playwright、FFmpeg 未打包。
