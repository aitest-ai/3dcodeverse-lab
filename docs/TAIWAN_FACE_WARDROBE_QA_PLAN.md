# 台灣街頭 NPC：不同臉型與原生開源服裝驗收

日期：2026-10-30。狀態：四位角色的 Blender 實拍測試中，非正式美術驗收合格。

## 開源服裝

使用 MPFB 官方 MHCLO，從個別人的 MakeHuman 人體擬合真正不同的上衣、褲子，不再把舊連身服裝切開變色。

|角色|造型特徵|CC0 上衣|CC0 下著|原生皮膚|

|---|---|---|---|---|

|主角 you|窄頭、寬下顎、窄鼻翼|namuhekam_male_polo_shirt|cortu_cargo_pants|young_asian_male|

|老闆娘 boss|圓臉、短下巴、頰肉|toigo_fisherman_sweater|toigo_wool_pants|middleage_asian_female|

|阿伯 uncle|寬臉、大下巴、較寬鼻翼|namuhekam_male_polo_shirt|toigo_wool_pants|old_asian_male|

|外送員 jie|長窄臉、細下巴|elvs_crude_t-shirt_male|cortu_cargo_pants|young_asian_male|

服裝原始來源：https://www.makehumancommunity.org/assets/assetpacks/shirts01.html 和 https://www.makehumancommunity.org/assets/assetpacks/pants01.html

## 更多可用候選（尚未實測導入）

臉頰 https://www.makehumancommunity.org/assets/assetpacks/cheek01.html

鼻子 https://www.makehumancommunity.org/assets/assetpacks/nose01.html

表情 https://static.makehumancommunity.org/assets/assetpacks/faceunits01.html

女性膚質 https://www.makehumancommunity.org/assets/assetpacks/skins01.html

男性膚質 https://www.makehumancommunity.org/assets/assetpacks/skins02.html

髮型 https://www.makehumancommunity.org/assets/assetpacks/hair01.html

## 品質門檻

每一人必須先獨立建立 MPFB 宏觀身形與微觀臉型，再配戴同一人體原生擬合五官、衣服、頭髮，驗收正面/側面/四十五度/全身實際 Blender 圖。

至少比對下巴、鼻子、眼距、顴骨、頭髮、皮膚年齡紋路、穿模與衣緣。4 人擁有不同臉部參數不等於視覺上真的能辨認出不同人物。

對所有引入的單項素材核對授權，僅憑 pack 名稱不可推論每一檔都一定是 CC0。

每角色 <6MB 為低負擔版需求；若要近景高品質，應另做可選的高解析度版本，不能自動放寬原有規格。

這次的 4 人 GLB 尚未驗證 8 個 ARKit morphs，未完成動態骨架與衣物測試，禁止當成正式 8 人包。

開發分支 feat/taiwan-4-role-cc0-wardrobe-qa，PR #26，暫時 Draft。
## 2026-10-30：V10 → V12 真實 Blender 美術監工結果

- **V9 原型**：4 人 GLB 及四視角真實 Cycles 圖均完成，但主角與外送員外觀相似；外送員衣襬黑色破口，老闆娘年齡感弱。
- **V10 監工**：改外送員髮型 short03，結果厚瀏海遮一眼；雖換 toigo_basic_tucked_t-shirt，但在腰部露出明顯皮膚。因此 V10 外送員美術拒收。
- **V11 監工**：改 short02 不遮眼，嘗試向下延長實際 T-shirt 網格 7.8 cm，出現鋸齒狀衣緣，拒收此衣襬變形演算法。原生 UV、骨架權重保留並不能彌補幾何缺陷。
- **V12 監工**：還原完整原始 T-shirt 幾何；改沿身體法線重新擬合貨物長褲腰部，確實修改 74 個頂點，將原貨物褲腰高度從 1.00417m 提到 1.07376m（增加 6.96cm），遮掩腰部露出的皮膚。實際 Cycles 全身圖已經改善，但仍留有深色接縫。**V12 只列測試候選，不得標示最終美術核准。**
- **V12 Actions 成功**：https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41060425286。四 GLB（boss 3,731,996 B；jie 3,610,768 B；uncle 3,377,824 B；you 3,830,988 B）加 16 Blender PNG 和 4 報告，均有 53 bones、單人物確實有 13,380 原始身體頂點、2 件原生 CC0 上下身服裝、內嵌貼圖 <=512px、GLB <6MB。
- **獨立臉幾何驗證**：同一頂點拓樸，消除每人頭頂高度平移後比較 head-front face，pairwise RMS 1.035cm–2.248cm；不等於人類一定能辨識角色。you vs jie 只有 1.035cm，外貌仍相近。
- **發布阻擋**：四 GLB 都沒有 8 個原本要求的 ARKit facial blendshapes（glTF morph target count = 0）。尚未驗證走路/說話動畫、動態衣服碰撞，另外 4 位人物也未生成。 
- **可後續嘗試但尚未整合**：MakeHuman 2026-10-24 更新的 Hair editor asset pack、Faceunits 01 ARKit CC0 pack、官方 High-detail hair 並逐件查授權；原生 512px 低負擔 NPC 版應與高精緻近景 LOD0 分開驗收。
