# 登別伊達時代村 V032 R1｜屋脊前緣接縫 QA（候選未通過美術驗收）

> **本輪 QA-only／standalone inspector：不更改 V031 完整遊戲 Runtime。** 堆疊 V031 Draft PR #133。請保持 Draft，不自動合併、不部署、不覆寫正式網站或任何舊版。

## 目的與實作

V031 高等学問所上層局部瓦面面積 x 4.75–16.75m／z 56.06–57.06m。原 V004 真正的 ridge_tile GLB 已存在，不能再次自創或替換整條屋脊。V032 製作一排 **36 片、3 Mesh／1440 三角面**的屋脊前緣接合候選，沿用 V031 原有三套瓦片 PBR 材質，渲染專用、碰撞不變、原屋脊不變，GLB bytes **399,012**。

候選 GLB SHA256：`def326cfd37b2bbbd704917b521e5d6b25f5b65a8cd82220f483c6f82dea8892`。

依 V004 原始模型採樣，ridge_tile 三角面最小 z 約 57.28168、候選瓦最大 z 約 57.19560；差約 **0.08608 模型座標單位**，只是一維 z 向間隔，不是最短 3D 淨距，更非現場測繪。既有作者屋面斜坡 fit RMS 約 0.00617m，不是原建築工法確認。

## 真 Chromium WebGL2：工程 PASS、美術 FAIL

- 在 V031 Inspector 的 **8 份原始 GLB** 上另外載入一份 V032 GLB，總計 **9/9**。桌機 Xvfb+Chromium+ANGLE SwiftShader 真 WebGL2、屋脊／瓦片／街景三組固定鏡位 ON/OFF **六張截圖**成功，JS page error 0。
- V032 屋瓦獨立開／關、V031 與原 V004 屋瓦全域切換、Chrome 430×932 直式**模擬**行動裝置測試均 PASS（不是 Android 真機）。
- **視覺 FAIL**：近景看到規律突起、鋸齒狀亮邊，新增的一整排瓦不夠自然，仍可能加重而非減少接縫感。因此本版設為**預設關閉**，不整合進 V031 遊戲 Runtime，不宣稱美學品質提升。
- 從原封 V031 Inspector.zip／SourceQA.zip 在全新目錄重新建立，V032 GLB、app.js、index.html SHA256 一致；不能覆寫已存在工作目錄。
- 尚未執行 Blender 原生 .blend／Cycles；沒有正式 HTTPS 私人站、Android 真機、長時 FPS、現地尺寸驗收。

## 精確來源

V031 完整 Runtime：`57882e06ad6f9256c3150ff562656eb745b24331fe0c9893c777c351dde394f0`（**未修改**）。

V031 Inspector.zip：`661eb6a6d18d4f430ccd0ed1a0b2805548793dd4fe6b662542212dc4e64730e5`。

V031 SourceQA.zip：`465cef192382e919effa98dc0c3aa28230b808fe4e76cab7f1bca2df03c9f571`。

本輪獨立 Inspector.zip：`f5415e902dbec93f10dfcc97f16f2957ccf65cf16bd40d395e791bd81b89a25e`（約 5.9MB）。

本輪 SourceQA.zip：`8e8378898e44706dacc12b934ab14211f58f26b513da7a95b2f8ed59875cfba0`（約 1.3MB）。

GitHub 只存品質結論、SHA 契約與來源定位，不提交私人原始建築 GLB、完整 80MB Runtime。完整可重播的 build_v032.py、patch_inspector_v032.py、replay_v032.py、test_inspector_v032.py、blender_candidate_v032.py、六張真 WebGL2 PNG、模型與驗收 JSON 均在獨立 SourceQA.zip。Blender 腳本只是待執行候選，不能冒充已完成 .blend。

## 重播與啟動

```bash
# 將 SourceQA.zip 的 scripts/*.py 放在同一資料夾
python replay_v032.py V031_Inspector.zip V031_SourceQA.zip NEW_EMPTY_WORKSPACE
# 直接使用交付的 V032 Inspector.zip 則可解壓後啟動：
python -m http.server 8765 --directory /path/to/V032_Inspector
```

瀏覽器開啟 http://127.0.0.1:8765/；預設不開啟 V032 瓦列，需要手動勾選才會顯示。不要用 file:// 雙擊。

## 後續正確方向

下一輪先取得高等学問所**同棟**可辨識、可信的正面及斜側屋頂照片，釐清原有白色簷口/屋脊與瓦面邊緣的構造，再以 Blender 原生模型局部替換而非不斷疊加新屋瓦。無現地資料就維持作者候選，不能把「学問所寺子屋」照片當作同棟測繪。

**維持 Draft、不合併、不部署。**
