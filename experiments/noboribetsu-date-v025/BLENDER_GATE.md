# V025 Blender 原生驗收流程（尚未執行）

**嚴格區分 source-ready / 已實測 native。** 雖然已完成程序化 PBR、新 GLB／Runtime、isolated WebGL2 圖與完整 B 中部分 UI/移動的實測，但是目前沒有 blender binary 或 bpy，不能宣稱 .blend 存在。

正式 Native Gate 必須在可執行 Blender 的環境，使用交付 SourceQA 的原封 `blender_native_v025.py`，執行：
```bash
blender -b --python blender_native_v025.py -- /path/to/V025_runtime /path/to/EMPTY_NATIVE_DIR
```
必要條件：完全相同的 V024 與 V025 GLB 雜湊，V004/V021/V022 GLB 全部存在，Blender import 確實成功、同鏡位範圍確認、V024/V025 bounding box 允差不超過 0.001 Blender unit；正確的 glTF Y-up 與 Blender Z-up 轉換必須用 `(x,-z,y)`；兩個相機位各一組 V024/V025 Cycles 影像共 4 張，圖檔和 .blend 都必須存在且有非零大小，打包圖片及生成 SHA 清單與 `V025_native_validation.json`。

原始 V024 Blender 匯入腳本曾直接將 Three.js XYZ 當作 Blender XYZ。本版**新增候選修正腳本與邊界 fail-closed 防呆**，並沒有在 Blender 中實測其轉換結果。成功執行前，native gate 一律顯示 *PENDING*。

不得把 Chromium 截圖、Python 編譯通過、三角面與 SHA 查核，當作 Blender .blend/Cycles 驗收成功。