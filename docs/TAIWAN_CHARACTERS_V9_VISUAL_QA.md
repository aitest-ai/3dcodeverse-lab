# V9 臺灣街頭四人物開源衣裝與臉部品質驗收

日期：2026-10-30　GitHub Actions 成功執行：https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41056645985

## 技術檢驗

已在 GitHub Actions 實際用 Blender 5.2.3 + MPFB 2.0.18 匯出 4 GLB、16 張 Cycles 真實渲染，原生上衣與褲子都是分離的 `.mhclo` 網格。獨立 Python 檢驗 24 個檔案完整、每個 skinned GLB 有骨架、每個人體真正 13,380 頂點、所有 embedded texture <=512px、四個 GLB 分別小於 6MB。

|人物|GLB bytes|上衣 MHCLO|下著 MHCLO|
|---|---:|---|---|
|you|3,830,868|namuhekam_male_polo_shirt (CC0)|cortu_cargo_pants (CC0)|
|boss|3,731,880|toigo_fisherman_sweater (CC0)|toigo_wool_pants (CC0)|
|uncle|3,377,712|toigo_basic_tucked_t-shirt (CC0)|toigo_wool_pants (CC0)|
|jie|3,553,832|elvs_crude_t-shirt_male (CC0)|cortu_cargo_pants (CC0)|

## 監工結果

- **you**：與 V8 視覺幾乎無變化，主角臉仍很普通；皮膚光滑、髮型雕塑感明顯，尚未符合近景遊戲人物。
- **boss**：紅色針織衫下擺原先的黑色斷裂減少；眼袋與臉部年齡微變形外觀差異很有限，老闆娘仍然顯得過度年輕。
- **uncle**：已更換真正不同版型的休閒 T 恤，避免與主角同一款 Polo 衫；臉部仍偏光滑，髮際線形狀尚不自然。
- **jie**：V8 的過度尖下巴、突出的嘴唇及灰白髮色修正，V9 臉更正常、頭髮改為深色；**但領口過低、褲頭有黑色破碎邊緣，未合格**。

## 尚未完成的規格

**所有 V9 GLB 的 glTF morph target 目前仍是 0**：MakeHuman 臉部形態調整已烘焙進模型，但沒有製作原本要求的 8 個可動畫 ARKit 式表情。其餘四位角色亦尚未加入新流程，沒有完成走路/表情/穿衣動態檢查，所以 V9 只准稱為 `STRUCTURE_PASS_VISUAL_REVIEW_REQUIRED`。禁止合併 main、不得宣稱為正式八角色遊戲素材。

## 下一輪優先處理

1. JIE 過低的 T-shirt 領口與褲頭穿模（考慮替換版型，而非只換色）。
2. 官方 `faceunits01` 提供 ARKit 風格 54 facial shape units，應以官方形變資料製作、烘焙各角色身份後再加表情 shapekey，避免重新使用固定世界座標變形。
3. 老闆娘的中年皮膚紋理、眼下細節和顴骨不對稱；其他人物的毛髮材質與皮膚微細節。
4. 可進一步測試 CC-BY 的 `shirts02`（官方含 Elvaerwyn 兜帽外套）或 `shirts03`，但必須在 manifest 保留作者、原始頁面、授權及改作說明，不能誤標為 CC0。

相關官方來源：https://www.makehumancommunity.org/assets/assetpacks/shirts01.html ; https://www.makehumancommunity.org/assets/assetpacks/pants01.html ; https://static.makehumancommunity.org/assets/assetpacks/faceunits01.html ; https://www.makehumancommunity.org/assets/assetpacks/shirts02.html
