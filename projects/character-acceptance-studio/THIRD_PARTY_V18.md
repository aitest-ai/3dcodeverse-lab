# 0.18.0 來源與修改

角色、衣鞋、原貼圖作者：pixiv Inc.。VRoid beta CC0 範例 Vivi β2、Vita β3，固定鏡像：https://github.com/madjin/vrm-samples/tree/e16eb187100149a315ad92c3c9968f1d5baa6c7d/vroid/beta 。原 VRM、官方授權證據 HTML、原圖片／原始導入 Blender 資料保留於 Sources；原 `.vroid` 工程未取得。

|來源|SHA-256|官方證據|
|---|---|---|
|Vivi.vrm|eaf902e041a7a810f1423599ae75682f61184ab6ef0206da9a8ed9caa8ec3a9d|https://vroid.pixiv.help/hc/en-us/articles/360014900273|
|Vita.vrm|f2bf78f28a24e2f75f5ca0b6c3b646654c394e4b03592dfaa0d0633ef0972b4d|https://vroid.pixiv.help/hc/en-us/articles/360014900113|

直接來源為 [Draft PR #166](https://github.com/aitest-ai/3dcodeverse-lab/pull/166)，提交 `8e5e3bb7a64d353bb4b3e7440474b93b0204ad73`，CI run `42187889048`、artifact `13488354383`。驗證實際下載外層 ZIP、內層索引後，取用 Vivi 0.5.0／Vita 0.4.0 的固定 GLB、母檔、profile；沒有混合整條其他來源分支。版本雜湊見 `docs/INPUTS_V18.json`。

V18 新增 Vivi 0.6.0／Vita 0.5.0。新增 2048px 局部 MToon 描邊寬度遮罩，減少反面描邊從肩腋摺疊穿出；全部幾何、拓樸、權重、動畫、原色彩貼圖與解析度保留。遮罩不修復幾何碰撞。袖口細分試作因新增交叉被拒收，演算法與數值失敗紀錄保留，沒有列入候選資產。

新增程式／素材修改為本專案程序化修正，沿用專案貢獻授權；CC0 指上游角色。沒有真人動捕、AI 訓練或 NVIDIA 模型推論，沒有新外部付費素材／憑證。Three.js r170、@pixiv/three-vrm 3.3.0 的 MIT 授權在 vendor；既有沿革見 THIRD_PARTY_V17／V16／V08／V07／V06／V05／V04。所有新版本保持候選，未批准正式地圖取用。
