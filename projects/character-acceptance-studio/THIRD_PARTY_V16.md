# 0.16.0 來源、授權與修改

沿用 pixiv Inc. VRoid beta CC0 範例 Vivi β2、Vita β3。固定鏡像提交 `e16eb187100149a315ad92c3c9968f1d5baa6c7d`：https://github.com/madjin/vrm-samples/tree/e16eb187100149a315ad92c3c9968f1d5baa6c7d/vroid/beta 。原檔作者／版本空欄維持原值，沒有宣稱取得原 `.vroid` 專案。

|來源|原 VRM SHA-256|官方授權證據|
|---|---|---|
|Vivi β2|`eaf902e041a7a810f1423599ae75682f61184ab6ef0206da9a8ed9caa8ec3a9d`|https://vroid.pixiv.help/hc/en-us/articles/360014900273|
|Vita β3|`f2bf78f28a24e2f75f5ca0b6c3b646654c394e4b03592dfaa0d0633ef0972b4d`|https://vroid.pixiv.help/hc/en-us/articles/360014900113|

本輪直接固定來源為 Vivi 0.3.0 GLB `1efdd916d4f14b59b27c9baf71bb52fd334fa64d88c67c1484e11a6f4d4814a0`、母檔 `08829fc3da823c10b6228249f05d8ce4de864ba6c562fdbabe4d0ca6674cc5a3`；Vita 0.2.0 GLB `73810ed0414c723da46dd74dfe227b4c1aec83e4321a6cd0eda0a7ec5f7e7194`、母檔 `97889b9e27a4a40c3d40b718b2c5f40da8e805a3d0b22223e64e1c3e1fa7c699`。這些檔案已存在於本輪起點提交 `36b2299db1c4f80fdb86f83fab615bdec7014c62`，沒有合併來源分支。

新增 Vivi 0.4.0、Vita 0.3.0：依各自掌面及指骨 rest frame 修正 Run 手型，另依裙片輪廓採用不同的上臂外展曲線。保留全部舊 BIN、網格、UV、權重、材質、貼圖、表情及 VRM metadata，保留其餘六段動畫 JSON、全部非目標骨骼曲線與原生動作。每包自己的實際 SHA-256 見 catalog、adaptation、骨架 profile 與 ZIP 索引；母檔內容雜湊因 Blender 序列化而不同，不能以不同次輸出母檔互換。

動作延續專案的程序化步態與原生骨架適配，不是原作者動畫、真人動捕、自行訓練 AI 或 NVIDIA 推論。歷史 Harbor 動作參考的來源說明保留於 THIRD_PARTY_V05／V07／V08。此輪沒有新增外部素材、帳戶、費用或憑證。

CC0 僅描述上游模型；新腳本、修改與動作沿用專案貢獻授權。Three.js r170 與 @pixiv/three-vrm 3.3.0 的 MIT 授權保留於 vendor。人工美術與遊戲就緒狀態均未核准。
