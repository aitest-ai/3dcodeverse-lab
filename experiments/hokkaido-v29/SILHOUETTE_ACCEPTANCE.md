# v29：真正的正／側輪廓約束 3D 木雕熊頭與鮭魚

**狀態：實驗候選、非正式遊戲模型，不覆蓋 `models/hokkaido-bear/latest`。**

## 工作方法已根本改變

- v28b 使用多組橢圓截面放樣，因頭部像玩具、魚身像木條被退件。
- v29 使用獨立繪製的兩組頭部輪廓（X-Z 側面、Y-Z 正面），以 signed distance intersection 建立 3D 立體，並將上下唇的輪廓當作 C 形空腔的真實幾何邊界。
- 鮭魚從 Y-Z 背腹輪廓與 X 軸厚度函數建立，包含魚頭、鰓區、厚腹、魚腰與尾柄，魚鰭在距離場中「融合」而非浮空貼片。
- 真正的魚鰓必須採表面位移雕刻：如果在 SDF 用封閉 V 字布林切割，會把鰓蓋切下來，已在第一次測試中被拓樸 QA 攔截。
- `silhouette_sdf.py` 以 SciPy/NumPy/skimage 建立 watertight 原生 PLY，`convert_blender.py` 以 Blender 5.2.2 輸出真的 GLB，`scripts/render_official_glb_bpy.py` 提供真正的 Cycles 四視角。

## 來自實物的視覺約束（不包含下載與再利用原始商家作品）

- 日本京都芸術大学木彫り熊研究：<https://www.kyoto-art.ac.jp/t/graduationworks/detail/21320/>，毛雕與面雕、八雲與旭川風格不可混淆。
- 手工木雕鮭熊實物側面形態：<https://shogunsgallery.com/products/vintage-japanese-ainu-hand-carved-bear-w-salmon-cedar-wood-6>；可觀察鼻樑、顎線、魚鰓蓋與魚尾柄。
- 木雕熊歷史訪談：<https://story.nakagawa-masashichi.jp/10635>；特定「咬鮭魚」形式發明者未能定論。
- 日本文化廳民族資料：<https://www.bunka.go.jp/seisaku/bunkazai/kokuyuzaisan/bunkazai/pdf/94267201_01.pdf>；部分手工毛雕熊工藝例，包含腳尖與毛紋細節。

所有參考僅用於**人工觀察形態**，沒有把商家圖片、照片貼圖或第三方模型複製成此模型，也不聲稱是完整還原的文化資產。

## 測試與發佈閘門

1. **拓樸**：熊頭與魚體都是各自單一連通、watertight、非平面圖像。掉出來的魚鰭、鰓蓋或耳朵直接拒絕，不允許自動刪除具有實質面積的組件。
2. **頭部輪廓**：側面額頭→鼻樑→上下唇的表面連續；正面眼睛、耳朵、顴骨不能過分卡通化。
3. **真實咬合**：正面和 45° 都應呈現下顎托住魚身、上唇壓住魚背且魚位於口中，不能只有最近距離接近，亦不能有不合理的貫穿。
4. **鮭魚解剖**：魚嘴、眼窩、鰓蓋、魚背腹、尾柄及尾鰭都要容易辨認，並注意頭尾比例。
5. **木雕質感**：目前不新增高密度毛雕，待輪廓驗收後，才整合 v25 的方向性雕刀模組。
6. **整合**：目前只製作頭部＋魚，不含熊的身體或四腳；只有頭魚原型人工驗收通過，再考慮整合。
7. 最終美術門檻：平均 ≥4/5，每項 ≥3/5，沒有 blocker/critical，且必須有真正渲染的四視角圖與可追溯 GLB。

凡不符合本門檻，`approved_for_game` 必須保持 false，任何 CI 成功都不等於美術合格。
