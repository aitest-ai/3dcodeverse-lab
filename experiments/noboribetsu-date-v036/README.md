# 登別伊達時代村 V036 R1｜原屋頂白帶側面連續性檢查

本輪基於 **V035 Draft PR #144**，是獨立 QA／Inspector 候選，**不是 V031 完整遊戲的新 Runtime**。請保持 Draft，不合併、不部署、不覆蓋舊網站。

## 問題的根因與量測（全部是作者 3D 模型內數值）

V035 已確認 V004 原 `plaster_offwhite` 的第 **8／9 面**在指定攝影機角度形成可見白帶，而不是先前 V034 推定的 20／21 面。第 8／9 面位於水平 y=6.72852039，原始面索引 `[3,7,6]` 與 `[3,6,2]`。

V035 的 **B 幾何候選**把原面後緣頂點 6、7 的 y 向下移動 `0.035` 模型單位，但相鄰牆體的三角面沒有移動。Python 以原 48 面的共享邊拓樸核對：
- 白帶表面原有 4 條外框邊，各有一組相鄰面；
- B 模式有 **3 條外框邊**至少一端變動；
- 後緣長邊長度約 **20.1475** 模型單位，兩端都出現 `0.035` 的位置差；
- 另兩條側邊從 0 漸進到 `0.035`。這是**潛在模型縫隙**，不能當作現場建築尺寸或已觀察到的實際漏光。

## V036 真正新建模與操作

- 從原封 V035 Inspector.zip SHA256 `9aba85e945cc4a6cf7a465c867933aaee5570af34ef08453b3fdd0107beda7b1` 建立。
- 所有舊 10 份 GLB 完整保留。原 44 檔中 **42 檔逐位元不變**，僅更新 `app.js`、`index.html`，另增加 README、contract、小型 C GLB，輸出 47 檔。
- 新增 C 材質候選 `assets/v036_edge_preserving_tint.glb`，273 頂點／480 面，完整四條外緣仍在原白帶 y 平面，不修改牆體或原屋頂輪廓。GLB SHA256 `49ad222e94348ba7d474c984c8a4703254937060095925e29ae6de7a2cea1cf3`。
- 檢視器支援「原版／V035 A／V035 B／V036 C」及屋頂側緣固定鏡位。勾選 B 的紅色提示面，只在畫面標示不連續位置，**並非建築原始模型或修復效果**。
- C 邊界位置連續不等於幾何頂點與舊側牆已拓樸焊接；更不代表歷史工法、建築安全或外觀已完成。

## 實測與保護門檻

- 原封 V035 輸入重播兩份獨立資料夾，新 V036 Inspector **47/47 檔案 SHA256 一致**；Node JS 語法、GLB 反向讀入、無零面積三角面、原 GLB 位元組不變都通過。
- 真 Chromium + Xvfb + ANGLE SwiftShader **11/11 份 GLB WebGL2 載入**，桌機原版/A/B/C 屋面及原版/B/C 側面合計 7 張 WebGL2 截圖，Chrome 430×932 手機**模擬** 1 張，0 JS/console errors。
- 固定屋頂鏡位原版與 C 的最大 RGB 通道差 >10 的像素僅 **24 個**。C 是拓樸風險較小的美術候選，但**可見改善不足，未升級完整園區**。
- 正式 V031 Runtime ZIP SHA256 `57882e06ad6f9256c3150ff562656eb745b24331fe0c9893c777c351dde394f0` 原封不變；原 10 GLB SHA 不變。
- **沒有 Blender/bpy**：未實際產出 .blend 或 Cycles；交付 SourceQA 裡的 `blender_native_v036.py` 僅 source-ready，需在真正 Blender 執行。未驗 Android 真機、私人站 HTTPS/CDN、長時 FPS 或同棟建築現地比例。
- 官方僅確認時代村以仙台藩建築風格為背景（https://edo-trip.jp/tw/about/），**無法證明高等学問所白帶是否應存在或材質應為何**。絕不能拿不同建築「学問所寺子屋」照片當同棟測繪。

## 獨立交付 SHA256

- `Noboribetsu_Date_V036_R1_Inspector.zip`：`fce794787e2b647972069aff5545a298859160663b4a014f7b7dd66f13198ce4`
- `Noboribetsu_Date_V036_R1_SourceQA.zip`：`9524e41f0f26a312ebffb227b4bb29ec9cfaed795281b2dd1dd14e373e522e8a`
- Comparison.png SHA256 `f79e845b6fcf9dd1bc5eee7851c8feb6b878296d55c5cc2c4da7da30d10063ed`
- Review.html SHA256 `9b8407b576a602e5d5b758b9c61cbfa4908481711a12159f26ca2eee9c2ae423`

完整程式不是只有文件：獨立 SourceQA.zip 含 `build_v036.py`、`qa_v036_geometry.py`、`qa_v036_browser.py`、`package_v036.py`、Blender source-ready、8 張真 WebGL2 PNG、JSON 報告；GitHub 此 PR 保存來源契約與可公開只讀驗收器，不上傳私人 6MB 原始模型或 81MB 完整園區網站。

重播：
```bash
python src/build_v036.py /private/Noboribetsu_Date_V035_R1_Inspector.zip /new/EMPTY_V036_INSPECTOR
python src/qa_v036_geometry.py /new/EMPTY_V036_INSPECTOR /new/V036_geometry_qa.json
# 測試環境具有 Chromium、Xvfb、Playwright 才可執行：
xvfb-run -a python src/qa_v036_browser.py /new/EMPTY_V036_INSPECTOR /new/BROWSER_EVIDENCE
```
現成 Inspector.zip 可用 `python -m http.server 8765` 本機啟動，Chrome/Edge 開啟 `http://localhost:8765/`。

**保留 Draft。不要合併、不部署、不修改正式站或分享設定。**
