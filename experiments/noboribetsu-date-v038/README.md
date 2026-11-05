# 登別伊達時代村 V038 R1｜高等學問所灰泥屋面共用頂點整體對齊（QA Candidate）

**本分支疊加 V037 Draft PR #149。不要合併、不要部署、不要覆蓋 V031 完整園區或任何私人網站。**

## 建模根因及實作

V034–V037 已確認 V004 原始 `plaster_offwhite` 有兩個可見的大型屋面三角面（索引 #8、#9），單純改色不能解決過高的白帶；V035 B 只移動兩面下緣、與相鄰側牆分離，有接縫風險。本版不增加瓦片，也不重做原始 GLB，而是**從原始 GLB 複製出新的 F 候選**：

- 直接改動 V004 `plaster_offwhite` 的**四個共用頂點 ID 2、3、6、7**，Y 方向 -0.225 **模型單位**。原高約 6.72852039，候選高約 6.50352049。
- 相關側牆在同一個 32 頂點／48 三角面的原始 Mesh 內共享頂點、一起變形；面索引不變。其他 16 組 V004 Mesh 與 V037 檢視器另外 12 份 GLB（共 13 份舊 GLB）逐位元不變。
- **以原始 GLB 的二進位 float32 原位置修改，沒有重新輸出其他模型或變更材質、碰撞或路線**。候選 GLB 1,208,064 bytes，SHA256 `d9232643103378644ea89b780126a8c516c1a41da70edfaa2542916da558e1a0`；新舊 GLB 位元組長度相同，僅 12 bytes 實際不同。
- 模型內初步量測，鄰近瓦片頂點的 y 高度有部分落在 6.45–6.59；**這不是同棟現地量測或屋頂建築規範**。F 移動四個共用頂點可避免 V035 B 在同一灰泥 Mesh 內的外緣高度斷裂，但不能自動保證與其他獨立瓦片／木作網格的接合。
- 獨立檢視器可切換「原版／V037 D／V037 E／V038 F」及原先所有來源診斷。F 僅候選、預設仍為原 V004，不放入完整遊戲。

## 實際來源與 WebGL2 驗收

- 唯一基底 `Noboribetsu_Date_V037_R1_Inspector.zip`，SHA256 `ff86ba6e7e64f69505aa5aa5d6cacfd2d73dba3da04e57043e67891fced2f453`。
- 原 53 檔中 **51 個完全不變**，僅修改 `app.js`、`index.html` 以接入 F 版；新增 GLB、README、contract、Windows 啟動腳本、檔案清單，總共 **58 檔**。從原始密封 V037 ZIP 在兩個獨立空目錄重播，**58/58 SHA256 一致**。候選 geometry 17 Mesh、plaster 32 vertices / 48 faces，無零面積三角面；原始 13 GLB 沒有重寫。
- **真正 Chromium/Xvfb/SwiftShader WebGL2**：14/14 GLB 載入成功；屋瓦近景／側面／簷口／街道四個固定鏡位，各原版與 F 一張，取得 **8 張真正 WebGL2 PNG**。另有 **430×932 行動版 Chromium 模擬** 1 張，JavaScript/console errors 0。原版→F→V037 E→原版切換通過。
- 固定鏡位最大 RGB 通道差 > 10 的像素：屋瓦近景 **66,985**、側面 **26,788**、簷口 **17,910**、街道 **4,986**。**只是畫面差異，不等於畫質提升、現地正確性或效能加速。**

## 獨立美術驗收結論（尚未批准）

F 版可見白色橫帶顯著縮小，但瓦緣仍偏規律；右側轉角深色缺口在前後畫面都存在，**沒有在本輪修復或通過接合驗收**。因此維持 **工程 PASS、候選美術研究，不整合 V031 完整園區**。原 V031 遊戲路線、碰撞、正式網站不變。

**Blender/bpy 執行環境未提供**，沒有真正 .blend／Cycles；SourceQA 包內提供 `blender_native_v038.py` 待具備 Blender 的電腦實際執行。Android 真機、正式私人站 HTTPS/CDN/登入、長期 FPS 與同棟高等學問所測量均未驗證。

參考：官方 https://edo-trip.jp/tw/about/ 提供仙台藩相關背景；2008 年旅人照片 https://summermom.pixnet.net/blog/posts/3023691927 有標示高等學問所，但非正交測量，不能作為屋頂高度的直接來源；「学問所寺子屋」更不可混充同棟。

## 交付與重播

- **Inspector ZIP**：`2078d61d53a9f52fcf76064b5abfc05fc7117753be4565d383884f5e40727f38`（58 檔）。
- **SourceQA ZIP**：`85fa116905105f85335257c63f355bd72e01f49a1abeaa6aac94654e3bb294a5`（19 檔，真正 Python 建置／來源 QA／Chromium QA／Blender 待執行腳本、九張真實 PNG、驗證 JSON、F GLB）。
- Comparison.png、Review.html（完全離線四視角拖曳）、Delivery_Report.md、Validation.json 另行交付。
- GitHub 只保存可公開程式／SHA 與交接說明；私人原始全部 GLB 不推送 GitHub。

```bash
python source/build_v038.py /path/to/Noboribetsu_Date_V037_R1_Inspector.zip /path/to/NEW_EMPTY_V038
python source/qa_v038_source.py /path/to/V037_Inspector.zip /path/to/NEW_EMPTY_V038 /path/to/qa.json
# 在有 Chromium、Xvfb 與 Playwright 的 Linux 環境才執行：
xvfb-run -a python source/qa_v038_webgl.py /path/to/NEW_EMPTY_V038 /path/to/evidence
# 有 Blender 的電腦才可解鎖 native gate：
blender -b --python source/blender_native_v038.py -- /path/to/NEW_EMPTY_V038 /path/to/NEW_EMPTY_NATIVE_OUT
```

**KEEP DRAFT. DO NOT MERGE OR DEPLOY.**
