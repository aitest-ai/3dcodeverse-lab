# 0.7.0 來源、授權與修改

本階段沿用已逐檔核對的 pixiv VRoid beta CC0 範例 Vivi、Vita，不引入未知權利的 VTuber／遊戲拆包素材。取得管道為 [madjin 固定鏡像提交 e16eb187](https://github.com/madjin/vrm-samples/tree/e16eb187100149a315ad92c3c9968f1d5baa6c7d/vroid/beta)，不是宣稱從官方取得原工程。作者依官方範例資料記為 pixiv Inc.；原檔 author/version 空欄保留。

| 來源 | 授權證據 | 原 VRM SHA-256 |
|---|---|---|
| Vivi β2 | [官方條款](https://vroid.pixiv.help/hc/en-us/articles/360014900273)，原檔 meta licenseName=CC0 | `eaf902e041a7a810f1423599ae75682f61184ab6ef0206da9a8ed9caa8ec3a9d` |
| Vita β3 | [官方條款](https://vroid.pixiv.help/hc/en-us/articles/360014900113)，原檔 meta licenseName=CC0 | `f2bf78f28a24e2f75f5ca0b6c3b646654c394e4b03592dfaa0d0633ef0972b4d` |

Vivi 直接基底為 PR #151 的 0.2.0，固定提交 `d58ec88446bde04fa79db1323ca4c4c340e0269f`。只替換 Run，六段其餘動畫 JSON 與所用 BIN 位元組精確保留。原幾何、蒙皮、材質、原解析度貼圖、表情與 VRM metadata 全部保留；B 新版週期不同，A/B 畫面按相位對齊。

Vita 原檔沒有動畫。此次 Idle／Walk／Run 是專案編寫候選，參考專案 Harbor 0.3 動作的世界方向與 gait planner，使用 Vita 自己的 rest pose、骨長、掌面與鞋底點，並烘焙原生骨架。A 是本階段低骨盆試作，明確未通過，不是原作者動畫；A/B 各有自己的 Blender 母檔及 SHA。Harbor 的既有來源／授權沿用 [THIRD_PARTY_V05.md](THIRD_PARTY_V05.md) 與隨附 licenses。

原始 GLB/VRM 權重位元組不變。Vita 新 Blender 工作副本針對原匯入器重複 joint 權重覆蓋問題，依原 GLB 加總同步；變動記錄於 adaptation.json。Vivi 沿用前階段已對齊的母檔。原始母檔不改；這不是跨角色直接貼局部旋轉或強迫統一骨架數。

`.vroid` 工程未取得，提供原 VRM 及衍生 Blender 工作副本。原始貼圖檔另附，不重採樣。裙片使用骨骼烘焙，不是布料模擬；手部原指甲／Skin 嵌合保留，不能把指定區域零交叉說成全身碰撞通過。沒有真人動捕、模型訓練、新付費工具、帳戶或憑證。

CC0 僅描述上游模型，新增腳本、動作和修改沿用專案貢獻授權，沒有替所有作者另作 CC0 宣告。Three.js r170、@pixiv/three-vrm 3.3.0 的 MIT 授權各保留在 vendor 資料夾；軟體授權不代替模型授權。完整前階段清單在 [THIRD_PARTY_V04.md](THIRD_PARTY_V04.md)、[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
