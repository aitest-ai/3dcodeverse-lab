# 0.5.0 來源、授權與修改

此階段沿用 0.4.0 已逐檔核對的兩個 CC0 模型，沒有新下載未知授權模型、購買素材、取得付費模型權重或建立新憑證。原始檔及授權證據保持不變。

| 項目 | 作者與固定來源 | 本階段修改 |
|---|---|---|
| Vivi β2 | pixiv Inc. VRoid beta 範例；[madjin 公開鏡像固定提交 e16eb18](https://github.com/madjin/vrm-samples/tree/e16eb187100149a315ad92c3c9968f1d5baa6c7d/vroid/beta)，[官方 Vivi 條款](https://vroid.pixiv.help/hc/en-us/articles/360014900273)；原檔內嵌 licenseName=CC0，author/version 空欄仍保留 | 在原 VRM 二進位資料後附加根節點與 7 段動作；網格、蒙皮、材質、原解析度貼圖、表情及 VRM metadata 完整保留。沒有 .vroid 原始工程；提供修正後 Blender 工作副本。 |
| Shiba Inu | Quaternius，[Ultimate Animated Animals](https://quaternius.com/packs/ultimateanimatedanimals.html)，原作者 Drive 的 ShibaInu.blend/.gltf、License.txt 保留，CC0 | 原生骨架保留；統一模型單位，指定肩高約 0.40 m 的遊戲尺度；修改 Idle/Walk/Gallop 接地與根位移，保留其餘 9 段原生動畫。這是風格化犬隻，非生物力學精確模型。 |
| Vivi 軀幹動作參考 | 本專案 Harbor 0.3.0 母檔與 `gait_plan_v02.py`，源自已盤點的 PR #137／第 2、3 階段；原角色 Quaternius CC0，既有專案貢獻授權沿用 | 原生骨架語意與世界參考姿勢適配；手臂、腳掌接觸目標及裙骨為本專案編寫／烘焙。不是真人動捕，也不是自行訓練完成的 AI 模型。未引用 NVIDIA 合成實驗作正式動作。 |

`library-v05/*/0.1.0/adaptation.json` 記錄實際來源檔 SHA-256、適配規則、權重同步紀錄、尺度及腳掌頂點。`files.json` 鎖定 GLB、Blender 母檔、profile 等每個檔案。A 是適配／原生重烘焙初稿，不是已驗收成品；B 亦為待審候選。

Blender 工作副本的權重同步是為了精確符合原 GLB：Vivi 原 GLB 有同一頂點重複骨骼項目，匯入器原先覆蓋而未加總；柴犬原生 Blender 可有更多骨骼影響，原作者 GLB 已輸出為四個。原始母檔、原 GLB 權重位元組均不修改。犬隻原生 IK 母檔保留，新副本為烘焙 FK，以供瀏覽器重現。

CC0 僅描述上游素材；本專案新增腳本、動作與修改不藉此另作全面 CC0 宣告。Three.js r170 與 @pixiv/three-vrm 3.3.0 的 MIT 授權各保留在 `web/vendor/` 與 `web-v04/vendor/`；這些軟體授權不能取代模型權利。Blender、Chromium、Playwright 與 FFmpeg 是外部建置／驗證工具，未打包其程式。

更完整的既有來源在 [THIRD_PARTY_V04.md](THIRD_PARTY_V04.md) 與 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。台灣 V29–V31、V110/V111、彩虹橋的既有盤點缺口維持原記錄，沒有回退 V103 或把未取得素材替換成其他版本。
