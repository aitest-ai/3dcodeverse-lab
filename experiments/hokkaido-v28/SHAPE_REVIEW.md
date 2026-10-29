# v28 咬鮭魚木雕熊｜獨立頭部＋鮭魚高模原型

**候選原型，不是正式遊戲模型。** 不與 `models/hokkaido-bear/latest` 合併，不覆蓋 v25／v26／v27。

## 為什麼捨棄原本的「反覆移動顎部頂點」

v27 的真實四視角仍顯示鮭魚橫擺鼻端，雖然魚腰近顎距離已到 0.004（模型單位）。因此 v28 必須**重設兩個物件的空間與輪廓**，不得再將數值接觸近似為咬合成功。

## 形態鎖定

- 熊頭：以一體頭骨、上唇、下顎、側面顎關節形成向前開口的 C 形咬合空間。耳朵在體積整合前融合，眼窩透過網格實際凹刻。
- 鮭魚：沿頭吻 → 眼窩 → 鰓蓋 → 厚腹 → 腰身被咬夾縮 → 尾柄縮窄 → 分叉尾鰭建立不同橫截面，腹部不是固定矩形木板。
- 魚腰在 Y=0 附近，約 Z=0.884，上唇下緣約 1.061、下顎上緣約 0.776。幾何推估不是最終藝術結論。
- 不加外貼魚眼球、顎部圓球、假毛紋與完整軀幹，以便純粹檢查咬合。
- 此原型不執行最終毛雕；仍可沿用 v25 的方向性刻痕，但必須等形態確認後才整合。

## 實物參考：只借鑑可觀察的外型，禁止複製賣家 3D 模型

- Japan House London，2023–2024「Bears and Salmon from Hokkaido」展覽：https://www.japanhouselondon.uk/whats-on/bear-and-salmon-from-hokkaido/
- 日本觀光廳對木雕熊的歷史與當代工藝描述：https://www.mlit.go.jp/tagengo-db/en/R6-00288.html
- Hokkaido Magazine KAI 木雕熊工藝與不同風格：https://kai-hokkaido.com/archives/en/town_vol33_woodenfigure/

八雲傳統、旭川職人工藝與愛努木雕不是完全同一條傳承，也不能自動將每件「鮭魚熊」都歸屬同一群體。

## 驗收要求
1. **正面**：上顎在魚身上方，下顎明顯支撐魚腹，魚腰能讀成被夾持而非擺在鼻前；上下唇不得露出鋸齒或浮空補丁。
2. **側面**：必須可見一個真實 C 型口腔、魚身在口中穿過，不被熊頭前端完全擋住。
3. **魚體**：魚頭有明顯鰓蓋與收束的吻端；魚尾柄明顯縮細後再接分叉尾鰭。
4. **幾何**：熊頭與魚體各為真正的 watertight 主網格；前後/頂視角可檢查眼窩、鰓溝與穿模。
5. 任何一項仍未達標，標註 **REJECTED**，不可改寫 `latest`，不可宣稱已通過工藝品質。
6. 最終遊戲整合仍須驗證與既有熊身接縫、腳掌和 3DCodeVerse Harness 管線，v28 僅為獨立模型原型。

## 實際可追溯檔
- `experiments/hokkaido-v28/head_fish.py`：全新原生 Blender 幾何腳本
- `.github/workflows/hokkaido-v28-head-salmon.yml`：真 Blender GLB、Cycles 4 視角、拓樸、接觸量測與 ZIP
- `candidate/v28_head_salmon_real.glb` 與 `candidate/shape_report.json`：待獲取真實建置成品後才審核
