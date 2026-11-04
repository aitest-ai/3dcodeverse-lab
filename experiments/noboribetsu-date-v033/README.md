# 登別伊達時代村 V033 R1｜原 V004 屋頂接縫根因隔離與原網格修改候選

**QA-only、Inspector-only。** 直接從 V031 Draft PR #133 的原始檢視器重建，**不繼承 V032 被美術拒絕的屋脊瓦列**。不修改 V031 146 個完整網站檔案、正式網站、碰撞、路線或其他舊版。請保持 Draft，勿合併、勿部署。

## 發現

以真正 Chromium + Xvfb + SwiftShader WebGL2，在相同屋瓦鏡位依序關閉 V030 和 V031 GLB 後，**原 V004 屋頂依然有白色橫帶與鋸齒狀瓦緣**。因此 V031 厚邊只是部分原因，白帶可能屬於原始建築構件／原模型接合，不應只靠增加屋瓦或抹平上層 GLB 來「修正」。同棟高等学問所缺少可量測的正交建築資料，不能以「学問所寺子屋」照片替代。

## 本輪實際產物

- 基底 **V031 Inspector.zip** SHA256 `661eb6a6d18d4f430ccd0ed1a0b2805548793dd4fe6b662542212dc4e64730e5`，共 32 檔，其中 **30 檔逐位元不變**；只更新 index.html / app.js；另加入 2 份新 GLB、README、契約與啟動腳本，V033 Inspector 共 38 檔。
- V033 A（trim）直接從 V031 3 Mesh／180 片原瓦片網格移除**末排 36 片瓦、合計 360 個多餘的向下厚邊三角面**。仍保留 6,480 頂點、3 Mesh、180 片瓦、6,840 三角面。原 GLB SHA 不變。
- V033 B（blend）在 A 的基礎上僅調低 864 個既有表面頂點，最大 **0.003 模型單位**，沒有新增瓦片、紋理、建築輪廓或額外碰撞。3 Mesh／6,840 三角面。
- 新版 UI 可在 **V031／A／B** 三種模式互斥切換；**預設 V031**，不把 A/B 當成定稿。也能取消 V030/V031 勾選觀察 V004 原始屋頂。
- V031 原 GLB SHA256 `3971f06b4bbba86432db3df09e486295e57d272f0ba4b187dbc0d4bdc7b1e763`
- A GLB SHA256 `c4391fbe3df863edc77a36b847ee62d47a3fd4a639c12919c2f945d03183bfed`
- B GLB SHA256 `0e9aa5090a906b783682f567ebfc4f4c8b2b2b89cd2b89eb892b4771f28f09bb`

## 真實驗收與界線

- 真 Chromium WebGL2 **10/10 GLB** 載入，屋瓦近景／屋簷兩鏡位 × V031/A/B 六張截圖成功，0 JavaScript page errors；430×932 **手機瀏覽器模擬**切換 PASS。
- 額外 4 張 WebGL2 原生模型隔離圖（V004-only、V030、V031、V033 B）證明原屋頂本身就有白帶／不規則邊。
- 原封 V031 Inspector 重播，兩個更新的 JS/HTML 與 A/B GLB **SHA-256 一致**；原 30 份其他檔案完全不變；新 GLB 重讀無零面積三角面，原 x/z 覆蓋範圍及 PBR 材質保留。
- **美術改善不足**：影像變化很小，且 V004 原始幾何的白帶仍存在，所以不升級完整遊戲 Runtime。本版不是美術 PASS，也不承諾 FPS／實景比例提升。
- **Blender/bpy 不可用**：未執行 Blender Native，無 .blend 或 Cycles；Android 真機、正式私人網站 HTTPS/CDN、現地測量均未驗。
- 本分支只保存可公開交接與檔案 SHA。SourceQA.zip 才包含完整經 Python 實測的 build/replay、Chromium QA、GLB、截圖與未執行 Blender source-ready 腳本；不在 GitHub 上傳私有大型 3D 場景。

## 獨立交付雜湊

- Inspector.zip SHA256 `b1a430f27f390bc284ba5febbdcd07b5ea45c1e281c5b2308d16c5fb38356339`，38 檔。
- SourceQA.zip SHA256 `d82ecf5b0ed87a765555761e3885f6e340ce57e907a77feb20ac6180c8a07eaa`，31 檔。
- Comparison.png SHA256 `457b6a5380317de307aea48d0493de55db7f73a9f2c3f6409fe5ec965ee32715`，Review.html SHA256 `4b7298f1db0158483768af1ec0cc7d6d65f5ed085d57848e2c72003c127f2de0`。

解壓獨立檢視器後啟動 START_V033_Windows.bat 或 Python HTTP server，在 http://127.0.0.1:8765/ 用 WebGL2 瀏覽器操作。SourceQA 重播：`python src/replay_v033.py V031_Inspector.zip NEW_EMPTY_WORKSPACE`。不直接使用 file://。

**下一輪應隔離 V004 原始瓦面／白帶屬於哪個 mesh、是否真有幾何錯誤，查同棟資料，再決定是否修改原始屋頂；不能直接消除可能屬於真實建築構件的白色帶。**

保持 Draft，不自動合併、部署、替換 V031 Runtime 或更改分享權限。