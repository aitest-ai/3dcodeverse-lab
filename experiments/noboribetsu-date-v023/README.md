# 登別伊達時代村 V023 R1｜高等學問所單窗格 PBR 材質研究

本分支**疊加 V022 Draft PR #109**；不合併、不部署、不覆寫舊版或既有網站。不提交私人完整 GLB / 70MB Runtime。

## 實際成果
- 只選 V004 高等學問所兩根柱之間約 2.49m 的一段**非門口窗格**，B 場景加入可開關、無碰撞的美術候選。
- 新 GLB 6 個 mesh、1,740 triangles、1,434,388 bytes；5 張**自行程序化繪製**的 PBR BaseColor 材質（老木、木框、和紙、灰泥、灰瓦），另有鐵件材質。
- 35 片局部灰瓦、木窗框、障子格柵、木板下緣；僅改外觀候選，不改屋頂／門洞原幾何。
- V022 125 份檔案中 **121 份 SHA256 原樣保留**；僅 app.js、index.html、qa.json、scene_view.json 更新，另新增 README、GLB、JSON。完整 Runtime 共 128 檔；舊 CollisionWorld、472 路線點、13 個柱廊提示全部保留。
- 正式網頁採 **原生 WebCrypto SHA256 fail-closed** 驗證新增 GLB 和 JSON 契約；測試專用 SHA adapter 僅存在 QA 程序，不會寫入 Runtime。

## 驗收
- 從 V022 原封 ZIP SHA256 `9cb0701354db365198edb7d243aac47cb37c216d9243b7ab1a9843fee981a801` 在乾淨目錄重跑 **128/128 檔案 SHA256 一致**。
- Node 語法、GLB 反向讀入、材質數量／貼圖與原始素材差異查核通過。
- Chromium + Xvfb + SwiftShader：**真正 WebGL2 建築小場景**載入 V004+V021+V022+V023，近景、正面、斜角三組開／關六張截圖已輸出。
- 隔離完整網站 Chromium WebGL2 **B 場景載入 PASS**，V023 診斷資料可讀；但**尚未完成走路、開關、操作、Android 真機驗收**。未驗私人正式站 HTTPS/CDN/登入。
- **沒有 Blender 可執行檔**，故尚未產生／開啟 native .blend，沒有 Cycles 真正渲染。交付的 `blender_import_v023.py` 是待 Blender 執行的 source-ready 工具，不是已驗收母檔。

## 誠實的精度界線
官方僅能證明村落採江戶與仙台藩建築風格；場景基礎數據沿用 V004 作者推估幾何，而不是本案現地量測。圖片只作類型參考，**沒有嵌入或重新發行現場照片**。本版不能宣稱「實景等比例復刻」、「建築安全檢查」或「Blender 完成品」。

## 重播流程（獨立 SourceQA.zip 提供完整腳本）
```bash
python replay_v023.py /private/Noboribetsu_Date_V022_R1_Runtime.zip /new/empty_V023_workspace
# Blender 可用的電腦上，再執行：
blender -b --python blender_import_v023.py -- /new/empty_V023_workspace /new/Noboribetsu_Date_V023.blend
```

交付物：Runtime.zip、SourceQA.zip、Comparison.png、Review.html、Delivery_Report.md、Validation.json。Blender 導入腳本及完整程序化紋理來源放在 SourceQA，請勿誤以為已完成 .blend。

**保留 Draft，不合併、部署或更新原有私人網站。**
