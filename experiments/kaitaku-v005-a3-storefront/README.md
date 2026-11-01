# V005 A3 商店一樓窗後可讀性 overlay

狀態：**BROWSER-VALIDATED RUNTIME OVERLAY**。

父版本固定為 FinalPolish A：
`752887763308bf71342b0d9ac292fc0f30ffa2e30d0ec6639e7373bb03cd5a55`

A3 固定輸出：
`8df3ada77443c390556e71c873d43dd65fe67996716e08ecfaff4e5faf60e27f`

## 為什麼另做 A3

FinalPolish A 已改善整體封閉窗後暗面，但 16 舊渡邊商店一樓十扇長店面仍偏整片黑。樓上三扇窗不需要再一起調亮，所以 A3 不修改共享 A 材質，而是只讓兩個**唯一 ownership** 的一樓 store backing mesh 改指向兩個新複製材質。

- `16 Closed shallow storefront backing` → local dark depth `(0.075, 0.068, 0.055, 1)`
- `16 Closed shallow storefront backing V005 inner reveal` → local reveal `(0.088, 0.080, 0.066, 1)`

玻璃 transmission / roughness 不變，沒有增加家具、房間、燈光或任何未確認室內。

## 結構驗證

- Binary GLB geometry chunk 與 A byte-identical。
- nodes / accessors / bufferViews 完全相同。
- 所有 A 原有 materials 完全相同。
- 只新增兩個 local materials。
- 只有 mesh definitions 295、296 的 material index 改指向新材質。
- 本地從 A 重跑得到 byte-identical A3。

## Browser 驗證

完整 V005 前端 + A3 environment 在 Chromium/WebGL2 SwiftShader 進入 `ready`，environment 與 visitor SHA 都符合 manifest。

採用的商店同鏡位測試：
- 0 page error
- 0 request failure
- accepted run 沒有 `CONTEXT_LOST_WEBGL`
- 一樓窗後稍微更可讀，但仍明顯保持暗色封閉狀態

因此 A3 可以作為目前偏好的 **runtime 局部 overlay**；FinalPolish A 仍保留為 rollback baseline。

## 和 A2 的關係

A3 **不包含** A2 郵局樹籬實驗。A2 仍未升格，不能把兩者混成一個已驗收版本。

## 仍未完成

- Blender 母檔未回寫。
- Blender native 五鏡位未完成。
- Android 真機未測。
- 不新增第四棟。
