# HY-World 2.0 整合實驗：第二輪可操作場景

## 已完成
- **[線上 3D 展示](https://hyworld2-mountain-river-demo.vercel.app/)**（WebGL2）
- **[獨立可下載展示](https://github.com/aitest-ai/3dcodeverse-lab/blob/feat/hy-world2-format-bridge/examples/threejs/hyworld-mountain-river-lab.html)**（整個互動程式放在單一 HTML 中；瀏覽器下載後可離線執行）
- 以程序建模建立原創森林／溪流／木橋／木屋場景，39,330 三角網格，117,990 頂點
- 模型可用材質、線框、混合三種模式檢查，包含 WASD 漫步、環繞與地標聚焦
- 支援以 ASCII PLY 匯出，並重新匯入 ASCII 或 little-endian binary 的**三角網格 PLY**
- 已以自動化測試完成 PLY 匯出→匯入的來回驗證；面數相同
- 獨立展示壓縮包及原生 PLY、GLB、VTK 離線預覽圖已在 ChatGPT 本輪回答交付（壓縮包不推到 GitHub）

## 存在的限制
- 此示範場景是**原創程序建模**，不是 HY-World 模型推論結果，不代表北海道真實場景。
- 官方 HY-World World Generation 需要昂貴的多 GPU 推論環境，這一輪沒有取得官方生成的實際場景。
- Spark Gaussian Splatting 需另外透過 `examples/threejs/load-hy-world.js` + SparkRenderer 載入；目前 3DGS 真實場景還沒通過視覺驗收。
- 在本次自動化測試環境中，Chromium 被政策限制 WebGL2，改使用 VTK/EGL 離線渲染驗證網格外觀；使用者一般瀏覽器的 WebGL2 正式視覺驗收仍待確認。
- 場景網格和生成世界的尺度／座標／碰撞正確性仍需進一步查核。

## 原有實驗路線
`scripts/hyworld2/pack_world.py` → `world_manifest.json` → `examples/threejs/load-hy-world.js` → Three.js / Spark；有面的三角網格也可以在 Blender 建立 GLB，再送到既有動畫與遊戲工作流。避免把 Gaussian Splatting 直接誤判成三角網格。

## 技術驗證摘要
用一個可重複生成的原創 3D 世界建立遊戲資產，透過二進位 PLY 導入 `trimesh`，確認 117,990 頂點與 39,330 面；使用 GLB 轉換後再載入仍有 39,330 面。UI 以 Playwright 模擬 WebGL API 測試互動流程，並用 VTK 渲染三種視角驗證幾何外觀。

本輪只驗證橋接資料與基本功能，非 HY-World AI 推論品質測試。
