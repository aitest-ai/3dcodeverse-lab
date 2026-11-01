# V005 A2 郵局樹籬自然化實驗

狀態：**EXPERIMENTAL / NOT PROMOTED**。

這一層必須套在已驗證的 FinalPolish A runtime GLB 上，不能直接套 baseline V005，也不能取代 A。

## 目的

FinalPolish A 的郵局兩叢樹籬在遊戲畫面中仍略像方盒。A2 只對以下 12 個 leaf/twig POSITION accessors 做輕微輪廓塑形：

- 14 Left entrance hedge branching twigs + leaves x5
- 14 Right postal hedge branching twigs + leaves x5

不移動郵筒、不改土壤底座、不改郵局通路、不改石緣、不改草地、不改建築、窗戶、屋頂、階梯或任何 node transform。

## 固定雜湊

- Parent FinalPolish A: `752887763308bf71342b0d9ac292fc0f30ffa2e30d0ec6639e7373bb03cd5a55`
- A2 output: `45d9beb938e876e55c37b93237b6344b88db202f832e39d5641f2d8a4ffb0265`

本地重跑已得到 byte-identical A2。

## 幾何幅度

- 左樹籬最大垂直位移約 8.7 cm、深度位移約 1.8 cm。
- 右樹籬最大垂直位移約 9.6 cm、深度位移約 2.0 cm。
- 端部略降、中段保留高度，加入非常小的非週期起伏。

結構差分檢查確認只有 12 個預期 POSITION accessors 的 binary range 有變；materials、node graph/transforms、mesh primitive definitions 都不變。

## 視覺驗收界線

輕量「真實三角面」幾何審查顯示端部比 A 更不方盒，方向可保留。但完整 V005 場景在目前 SwiftShader 環境中雖曾成功到 `ready`、環境與 visitor SHA 皆匹配，之後拍攝時發生 `CONTEXT_LOST_WEBGL`。因此：

- **A 仍是目前正式 runtime 候選。**
- **A2 只是可重現實驗層，不得升格。**
- 等 Blender native render 或穩定 GPU browser 再做最終郵局同鏡位驗收。

這個實驗不新增第四棟。
