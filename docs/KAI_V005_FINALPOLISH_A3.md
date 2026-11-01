# 北海道開拓之村 V005 FinalPolish A3｜Blender 回寫與跨 AI 交接

狀態：**A3 runtime 已完成 Chromium/WebGL 驗證；Blender 母檔回寫與 native 五鏡位仍等待 pinned V005 source artifact。**

本專案範圍固定為：

1. 14 舊島歌郵局
2. 15 舊山本理髮店
3. 16 舊渡邊商店

**不得新增第四棟。**

## 版本角色

| 層級 | 狀態 | 用途 |
|---|---|---|
| V005 原始候選 | 保留 | 原始回復基準與 Blender master |
| FinalPolish A | **ROLLBACK BASELINE** | 已驗證的草緣＋全域封閉窗後暗面小修 |
| A2 郵局樹籬 | **EXPERIMENTAL / NOT PROMOTED** | 僅保留可重現實驗，不納入正式回寫 |
| FinalPolish A3 | **PREFERRED RUNTIME CANDIDATE** | A + 16 號商店一樓局部窗後可讀性 overlay；未來 Blender 回寫目標 |

## 固定 SHA-256

- V005 Blender master：
  `7ead93b961f243c3521244a509e53546c73e27af4539a89a303a2e28c632ddbc`
- V005 baseline environment GLB：
  `32ddd3721e75b95f54ade22304e4d383930e4411507b0858f7d957f7171462d4`
- FinalPolish A：
  `752887763308bf71342b0d9ac292fc0f30ffa2e30d0ec6639e7373bb03cd5a55`
- A2（實驗、不可升格）：
  `45d9beb938e876e55c37b93237b6344b88db202f832e39d5641f2d8a4ffb0265`
- FinalPolish A3：
  `8df3ada77443c390556e71c873d43dd65fe67996716e08ecfaff4e5faf60e27f`

## FinalPolish A 已驗證內容

### 草緣

只處理 V005 clustered grass 靠街窄帶。runtime A 從 56,769 個草三角片中移除 547 個，約 0.96%，用來打散等距排隊感。

不碰：

- 低石緣
- 郵局通路
- 郵筒與綠籬
- 建築、階梯、門檻、平台
- 理髮店梯架、木桿、斜撐
- 已修補的理髮店上部雨遮側縫

### 封閉窗後暗面

A 全域封閉暗面：

- dark depth：`(0.055, 0.050, 0.044, 1.0)`
- inner reveal：`(0.070, 0.063, 0.052, 1.0)`

玻璃本體 transmission 與 roughness 不變；沒有新增任何室內家具或未確認房間。

## A3 新增內容

A3 **不包含 A2**。

16 舊渡邊商店一樓十扇長店面的兩個 backing/reveal mesh 具有唯一 ownership，因此只在這兩個 mesh 上建立局部材質，不影響：

- 16 號二樓三扇窗
- 郵局玻璃
- 理髮店玻璃
- 任何建築幾何
- 草地與植栽
- node transform
- glass transmission / roughness

A3 局部材質：

- store-local dark depth：`(0.075, 0.068, 0.055, 1.0)`
- store-local closed reveal：`(0.088, 0.080, 0.066, 1.0)`

目的只有降低「一樓整片黑洞」感，仍保持明顯封閉、無室內內容。

## A3 Browser 驗證

接受的 Chromium/WebGL2 測試：

- environment SHA 與 A3 manifest 相符
- visitor SHA 相符
- 進入 `ready`
- 0 page error
- 0 request failure
- 接受的 A3 run 沒有 `CONTEXT_LOST_WEBGL`
- 商店同鏡位可見些微窗後退縮，但仍維持暗色封閉狀態

A3 結構差分：

- binary geometry chunk 與 A **byte-identical**
- nodes / accessors / bufferViews 與 A 相同
- A 既有 materials 全部不變
- 只新增 2 個 store-local materials
- 只有 mesh 295、296 的 material index 改指向局部材質

因此 A3 可作目前偏好的 runtime 局部 overlay，A 仍保留做 rollback。

## A2 為何不升格

A2 只輕微塑形郵局兩叢樹籬：

- 左樹籬最大垂直位移約 8.7 cm
- 右樹籬最大垂直位移約 9.6 cm
- 深度最大約 2 cm
- 僅 12 個 leaf/twig POSITION accessors 改變

輕量真三角面審查方向合理，但完整 V005 在目前 SwiftShader 中，雖曾進入 `ready` 並通過 env/visitor SHA，後續多鏡位拍攝發生 `CONTEXT_LOST_WEBGL`。因此 A2 只保留實驗，不進正式 Blender 回寫。

## Blender 5.2.3 回寫

專用 workflow：

`.github/workflows/kaitaku-v005-finalpolish-a.yml`

目前 workflow 的正式目標為 **FinalPolish A3**：

1. 讀取 pinned baseline V005 environment GLB。
2. deterministic 產生 A。
3. 在 A 上 deterministic 套 A3，得到固定 A3 SHA。
4. 讀取 pinned `mainstreet-v005.blend`。
5. Blender 5.2.3 套用 A 草緣／全域窗後暗面。
6. Blender 5.2.3 只對 16 號一樓兩個 backing/reveal mesh 建立 A3 局部材質。
7. 原 master 不覆寫，另存 A3 candidate `.blend`。
8. 產生五張固定 Cycles CPU inspection views。
9. 上傳 A3 candidate artifact。

A2 不會被這條正式 workflow 套用。

## 來源檔傳遞

V005 master 約 456 MB，baseline environment GLB 約 380 MB，**不提交進 Git history**。

workflow 只接受同一 repository 的 Actions artifact，預設名稱：

`kaitaku-v005-source`

artifact 必須包含：

```text
mainstreet-v005.blend
kaitaku-mainstreet-v005.glb
```

workflow 在 Blender 啟動前會先核對固定 SHA；不同來源立即停止。

目前 ChatGPT/GitHub connector 沒有直接上傳 Actions artifact 的能力，因此 full Blender job 尚未執行。這個限制不得改寫成模型或 Blender 失敗。

## 五個 native inspection views

預定輸出：

1. Mainstreet overview
2. Shimauta front
3. Shimauta side detail
4. Watanabe front
5. Watanabe side detail

使用原解析度材質、Cycles CPU、32 samples；不先縮貼圖、不換舊模型、不加第四棟。

## 尚未完成

- pinned V005 source artifact 尚未進 GitHub Actions
- Blender A3 candidate `.blend` 尚未實際產生
- native Blender 五鏡位尚未產生
- native Blender re-export 與 runtime A3 parity 尚未驗證
- Android 真機尚未測試

在上述項目完成前，PR 保持 Draft，不合併 main。
