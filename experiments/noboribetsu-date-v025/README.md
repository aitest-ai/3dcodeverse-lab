# 登別伊達時代村 V025 R1 — 同幾何微 PBR 與 Blender Native 驗收門檻

此分支堆疊 V024 Draft PR #116。**勿自動合併、部署、覆寫舊網站或更改分享權限。**

## V025 實際產線
- 從精確 V024 Runtime.zip SHA-256 `256ad79b619065e2e1188662608a86578ac8468372fedb53ceedeef995a19cb0` 乾淨重建。
- 保留 V024 五個 mesh／792 三角面／全部頂點位置與原始顏色貼圖，新增四張粗糙度貼圖（metallicRoughness 的 G channel）及四張非常輕微的切線空間法線貼圖。新模型 `dist/assets/v025_v004_pbr_microdetail.glb` 為 2,136,700 bytes。
- B 場景顯示可開關 V025 材質。關閉 V025 可回到 V024；V024 關閉後可繼續使用 V023；不觸碰 A 骨架。
- V025 JSON 與 GLB 經正式 Runtime 原生 WebCrypto SHA256、長度、Mesh/面數/貼圖數及來源 V024 雜湊核對，失敗拒絕載入；QA 專用 SHA adapter 不包含於正式 Runtime。
- 原 131 檔中 127 個 SHA 不變；只有 app.js、index.html、qa.json、scene_view.json 修改，新增 README/GLB/材質契約三個檔案；輸出 **134 檔**。來源重播 **134/134 SHA256 完全一致**，原 V004、V021–V024 GLB、CollisionWorld、472 路線點、13 個柱廊導引點全不變。

## 實測但要區分的結果
- 真 Chromium WebGL2 獨立 V004 建築載入 + V024/V025 近景、斜角 4 張同鏡位 PNG：PASS；新舊 bounding box 完全相同。
- 在隔離 Chromium ANGLE SwiftShader **整個 B 場景載入成功**，進場、V025 開→關→開、V024 fallback 及真 W 鍵約前進 1.278m：PASS（QA 中斷前寫入 JSON）。
- 後續近景測試逾時，沒有完整 B 場景同鏡位 A/B 截圖，也沒有 Android 真機、正式私人網站 HTTPS/CDN、長時間 FPS 驗收。
- 新舊 WebGL 模型截圖平均像素絕對差近景 0.265、斜角 0.059（0–255 通道值），僅證明材質差異很小，**不可宣稱大幅改善美學**。
- 所有新材質為作者原創程序化貼圖；官方風格僅做外觀方向參考，不是高等學問所現地量測模型。

## Blender Native 與 Cycles 未通過的門檻
目前執行環境沒有 Blender 可執行檔或 bpy，也無法下載，因此**本輪沒有 .blend 母檔或 Cycles 渲染成品**。完整 SourceQA 包保存：
- `source/blender_native_v025.py`：真正執行時才匯入 V004/V021/V022/V024/V025、使用 glTF Y-up→Blender Z-up 正確座標轉換 `(x,y,z)→(x,-z,y)`，確認新舊 AABB 相同，固定相機近景／斜角各渲染 V024/V025 共 4 張 Cycles PNG，打包貼圖保存 .blend，最後輸出 `V025_native_validation.json`。異常會 fail-closed。
- `build_v025.py`／`patch_v025.py`／`replay_v025.py`／`qa_v025_source.py`／`render_v025_isolated.py`／`qa_v025_browser.py`，以及 WebGL2 實際截圖、完整 B 部分觀測紀錄和檔案雜湊。

重播：
```bash
python replay_v025.py /path/to/Noboribetsu_Date_V024_R1_Runtime.zip /path/to/NEW_V025_DIRECTORY
# 在 Blender 可執行的電腦上：
blender -b --python blender_native_v025.py -- /path/to/NEW_V025_DIRECTORY /path/to/NATIVE_OUT
```

GitHub 保存來源定位與驗收契約；完整個人場景 GLB、Runtime、Blender 待執行腳本及 QA 由獨立交付檔保存，不把大型私人資產推到 GitHub。**維持 Draft。**
