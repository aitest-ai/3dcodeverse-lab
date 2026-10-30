# 賽馬 V2.3｜真正 UV / PBR 貼圖與 WebGL 瀏覽器驗收

日期：2026-10-30。基底：Quaternius CC0 原始 Horse／Horse White，經 V2.2 完成焊接／平滑表面、150+ 組可蒙皮鬃尾纖維。V2.3 **不宣稱已取得照片級馬匹的新解剖模型**，只聚焦可實際交付的皮毛材質及瀏覽器可用性。

## 1. Blender 真正可攜的 PBR 材質升級

GitHub Actions 成功驗收：
https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41017062152
Artifact `racing-horse-v23-2`

- 新增 `scripts/horses/v23_make_coat_textures.py`：不使用第三方來源，以已固定種子自行生成每匹 1024×1024 `coat_albedo.png`、`coat_normal.png`、`coat_roughness.png`，保留可再次生成的程序。**為細節模擬，不是掃描真馬皮毛**。
- 新增 `scripts/horses/v23_blender_pbr.py`：使用 Blender 5.2.3 `smart_project`，產生真正 `UVMap`（26,184 UV loop corners），將三張貼圖接至 Principled BSDF，Pack All，保存 BLEND 和 GLB。
- **從匯出的 GLB 而非 Blender 來源再次檢查**：
  - Main material 同時有 `pbrMetallicRoughness.baseColorTexture`、`normalTexture` 與 `metallicRoughnessTexture`，共 3 張 GLB 內嵌圖片。
  - 動畫仍有 **13 clips**（含 Gallop、Walk、Idle），骨架 **50 joints**；纖維仍以原始 bone weights 跟隨主體，未重建。
  - 深棕馬 GLB 3,693,280 bytes，白馬 3,635,768 bytes；比 V2.2 增加是因為真正帶入了圖檔。
- Cycles 真正渲染兩匹馬各 4 視角（正／側／背／45度）。右側 V2.3 在肩腹有輕微細膩毛色起伏，白馬外觀差異較小。
- **限制**：主模型仍是同一套低多邊形馬解剖拓樸；頭型、肩胛、跗關節、蹄部、鬃毛及尾巴還沒達到真賽馬的高寫實標準；不可以把貼圖改善說成重新雕出真實肌肉。

## 2. 真正的 Chrome + WebGL 而不僅是 HTML 語法

實際成功：
https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41018572531
Artifact `racing-horse-v23-webgl-10`

- 新增 `.github/workflows/racing-horse-v23-browser.yml`、`scripts/horses/v23_browser_smoke.mjs`。
- Three.js 鎖定 `0.181.0`，**離線打包** `three.module.js`、`three.core.js`、GLTFLoader、OrbitControls、BufferGeometryUtils，無須外部 CDN。
- 早期實際 Chromium 測試曾因少打包 `three.core.js` 發生 404，導致模型即使檔案正確也無法使用。已修復並採 Playwright 捕捉資源錯誤。
- 在 Ubuntu Chromium / SwiftShader WebGL 實際載入、渲染、操作：
  - 兩匹 V2.3 真 GLB 都成功進入場景。
  - WebGL 畫布真正建立並顯示兩匹馬。
  - Walk／Gallop 切換、動畫速率及沿跑道前進操作都通過，零 JS errors。
  - 按鈕 `近看馬匹`、`觀看跑道` 的相機預設切換通過。
  - 保存 `browser_front.png` 與 `browser_racing.png` **真實 Playwright Chromium 截圖**。
- 賽道前進速度根據 V2.1 馬蹄實際 mesh 取樣後的 root 運動估算；**不是馬蹄碰撞、物理 IK 或真人賽馬速度**。
- 瀏覽器測試不表示手機 FPS、長時間循環、腳蹄滑步或真實賽道的碰撞已完成。

## 3. 用戶如何直接操作

從上述成功 Actions 中的 Artifacts 下載 `racing-horse-v23-webgl-10`，解壓後於 `index.html` 所在資料夾執行：

```bash
python3 -m http.server 8000
```

開啟 http://localhost:8000 。應可看到兩匹馬、下方動畫與速度控制，以及近看／跑道鏡頭按鈕。**不能直接雙擊 file:// HTML，因為瀏覽器會限制模組與 GLB 的本地存取。**

## 4. 高品質 V3 下一候選 — 未解決的來源條件

[CreativeMachine Horse Rig（Sketchfab）](https://sketchfab.com/3d-models/horse-rig-bd71883bad9845389ef4ec2801004801) 約 42K triangles、21.3K vertices，**CC BY**，但 Sketchfab 正式下載需要符合平台登入與授權機制，至今尚未取得原始模型 bytes。即使取得，它在展示頁主要是靜態 pose rig，**Gallop 尚需自行動畫綁骨驗證**；不能直接認定它比現有模型更適合可玩的賽馬遊戲。

其他 208K triangle 的 Innerscene CC0 靜態馬已真實下載、渲染與淘汰：高面數≠高品質、網站公布的 SHA256／大小也與下載 bytes 不符。保持獨立 quarantine、絕不覆蓋已驗證 V2.3。

下一個實質 V3 里程碑必須是：合法下載高品質馬體 → Blender 實際四視角 → 已核准來源和 SHA256 → 骨架／完整 Gallop retarget → 蹄部整個循環與 Chrome WebGL 驗證。

## 5. 版本安全

所有 V2.3 / V3 檢驗都保留在 Draft PR #13 的 `feat/racing-horse-cc0-pipeline`，`main`、機甲、人物原始專案不受影響。以上 Actions Artifacts 有保存期限 14 天，原始碼可重跑。
