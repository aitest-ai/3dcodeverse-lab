# 0.9.0 來源、授權與修改

本階段固定基底為 Draft PR #154 的 `454be2fcf9a18ece5a8077351a4a5d9b3cf79489`；所有舊模型、母檔、貼圖及已發行馬匹原檔保留。

| 角色 | 作者／授權 | 本輪用途 |
|---|---|---|
| ShibaInu | Quaternius，Ultimate Animated Animals，CC0 | 沿用前版接地候選，新增行走中左右 90° 弧線轉向 |
| horse-brown／horse-white 2.3.0 | Quaternius 原模型；aitest-ai 的 UV、PBR 材質與鬃尾衍生工作；既有來源授權隨附 | 原 GLB 13 段動畫逐位元組不改，只新增檢視設定與診斷 |

[Quaternius 官方來源](https://quaternius.com/packs/ultimateanimatedanimals.html)；馬來源與修改記錄位於 `sources-v04/horses/<id>/LICENSE_AND_SOURCE.md`、既有 [Horse Library v2.3.0](https://github.com/aitest-ai/3dcodeverse-lab/releases/tag/horses-v2.3.0)。本輪沒有發布新馬、修改馬匹正式 registry 或 Release。

柴犬直接基底為 `quaternius-shibainu-grounded-review / 0.1.0`，GLB SHA-256 `52561dc53ad291ded9b9cc726253b9b72344469acdd24a5d68a815c7380b3329`；母檔與原生輸入 SHA 均在新版 `adaptation.json`。前版來源、原始權重同步原因見 [THIRD_PARTY_V05.md](THIRD_PARTY_V05.md)。新 `0.2.0` 保留全部 12 段舊動畫、原網格／蒙皮／材質與原 BIN，僅附加 `WalkTurnLeft`／`WalkTurnRight`。

A `quaternius-shibainu-arc-experiment / 0.1.0` 是本輪將前版直走姿勢轉到弧線的失敗對照，不是原作者動作，也不是已發行的轉向成品。B 依四足原生相位固定世界接觸位置，支撐期保持原 Idle 足掌方向，擺動期平滑恢復原生足姿；沿用前腿二鏈、後腿四鏈 IK，烘焙 60 Hz FK。A／B 各有自己的可編輯母檔與 SHA。只鎖中心的中間試作因足掌邊緣仍滑約 7 mm 而淘汰，記錄於 `evidence-v09/rejected-trials.json`，未列入成品。

兩匹馬保留既有 50 joints、原解析度貼圖與原 13 段動畫。診斷程式只在記憶體工作副本同步 GLB 權重，沒有另存或覆寫馬母檔。檢視採明確等比例縮放和固定 rest-floor offset，參考的是肩頸截面，不宣稱真正鬐甲高度或生物尺寸準確。馬的原地動畫沒有校準的移動速度；本輪沒有把原地足端位移直接判成腳滑。

全部是風格化模型與專案動作候選，不是寫實解剖、真人動捕、AI 訓練或完整物理驗收。CC0 描述上游；新腳本與動作沿用專案貢獻授權，未代其他作者新增 CC0 宣告。Three.js r170 與 @pixiv/three-vrm 3.3.0 的既有 MIT 授權保留；本輪動物不依賴 VRM 表情或物理。前階段完整來源見 [THIRD_PARTY_V04.md](THIRD_PARTY_V04.md)、[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
