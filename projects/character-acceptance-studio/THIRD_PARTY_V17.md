# 0.17.0 來源與修改

上游角色、衣鞋、貼圖來自 pixiv Inc. 的 VRoid beta CC0 範例 Vivi β2 與 Vita β3；固定鏡像提交為 `e16eb187100149a315ad92c3c9968f1d5baa6c7d`：https://github.com/madjin/vrm-samples/tree/e16eb187100149a315ad92c3c9968f1d5baa6c7d/vroid/beta 。原 VRM、官方授權證據 HTML、原解析度貼圖一併交付。沒有取得原 `.vroid` 工程。

|角色|原 VRM SHA-256|官方授權證據|
|---|---|---|
|Vivi β2|`eaf902e041a7a810f1423599ae75682f61184ab6ef0206da9a8ed9caa8ec3a9d`|https://vroid.pixiv.help/hc/en-us/articles/360014900273|
|Vita β3|`f2bf78f28a24e2f75f5ca0b6c3b646654c394e4b03592dfaa0d0633ef0972b4d`|https://vroid.pixiv.help/hc/en-us/articles/360014900113|

直接來源為 [PR #165](https://github.com/aitest-ai/3dcodeverse-lab/pull/165) 的實際 CI 包，提交 `1afe2d74bd4551eae26c800d2d46590b830fc69a`、run `42178365826`、artifact `13484651685`。先核對外層 ZIP、內層逐檔索引，再抽取 Vivi 0.4.0／Vita 0.3.0。精確 GLB、母檔、profile 雜湊記在 `docs/INPUTS_V17.json` 與 bootstrap 腳本；沒有合併其他來源分支。

新增 Vivi 0.5.0、Vita 0.4.0：依原生上臂／前臂解剖軸修正 Run 的兩根前臂旋轉，另新增 Run 專用局部皮膚／衣料 morph。Vivi 最大皮膚位移約 7.5 mm，Vita 約 5.0 mm；全部局部修正最大約 12.7 mm。保留原網格拓樸、基礎座標、UV、權重、材質、貼圖位元組、其他骨骼曲線與其餘六段動畫。每次交付實際雜湊以該包 catalog、adaptation、profile 及 ZIP 索引為準；不同次 Blender 序列化的母檔不可互換。

新動作與擬合為專案程序化修改，非原作者動畫、真人動捕、布料模擬、自行訓練 AI 或 NVIDIA 推論。原有參考與授權沿革見 THIRD_PARTY_V16／V08／V07／V06／V05／V04。沒有新增外部模型、付費、帳戶或憑證。

CC0 描述上游素材；新程式與修改沿用專案貢獻授權。Three.js r170 與 @pixiv/three-vrm 3.3.0 的 MIT 授權保留於 vendor。全部維持候選，未取得人工美術與遊戲就緒批准。
