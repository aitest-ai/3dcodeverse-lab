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