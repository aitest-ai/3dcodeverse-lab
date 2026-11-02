# 登別伊達時代村 V026 R1｜高等學問所單窗格立體深度候選

本分支堆疊 V025 Draft PR #117，僅作版本交接與嚴格驗收契約，**保持 Draft，不合併、不部署、不更改正式網站或分享設定**。

## V026 實際製作
- 沿用 V025 原本五個 Mesh、792 個三角面、PBR 色彩／法線／粗糙度貼圖以及原有的 V004 建築位置。
- 選在高等學問所兩柱之間的**非門口**窗格，增加 4 條窄斜角木框（112 面）及 4 條內緣陰影（48 面），做出局部厚度與暗縫。新 GLB 總計 7 Mesh／952 個三角面，2,143,012 bytes。
- 材質已在真 WebGL2 比對後調暗，避免新框明顯偏亮。這是依既有 V025 幾何設計的視覺候選，沒有實地量測；不代表古建築接合方式精確正確。
- V026 B-only 可開關，關閉後回到原 V025；原 V025/V024/V023 模型保留。正式 Runtime 原生 WebCrypto SHA256 驗證新 JSON 與 GLB，失敗拒絕載入。
- 不更動 V004/V021–V025 既有 GLB、A/B、CollisionWorld、472 路線點、13 個柱廊導引點或任何原有道路／碰撞參數。

## 可重播檔案與測試
源自原封 V025 Runtime.zip SHA256：
`edad5d98c6632a7be7ae668cb80f6d6f2e4eb7f3f948507ce99e83f281bbc085`
- V025 **134 檔中 130 檔 SHA256 逐位元不變**；只更新 `dist/app.js`、`dist/index.html`、`dist/qa.json`、`dist/scene_view.json`；新增 README、GLB、JSON，V026 Runtime 共 **137 檔**。
- V026 新 GLB SHA256：`7607df2df69b86e64c397974595c43ba20e55b00ced839e06b4188a4ddf0b90b`。
- 從未改動 V025 ZIP 全新目錄重播，**137／137 SHA256 完全一致**；SourceQA 原模型幾何比對及 Node --check 通過。
- Chromium+Xvfb+SwiftShader 真 WebGL2 獨立 V004 建築場景，V025/V026 近景與斜角共 **4 張同鏡位 PNG PASS**。
- **完整 B 園區瀏覽器測試逾時、沒有足夠的 V026 開關或 W 鍵操作回報，故不得宣稱完整遊玩通過。**
- Android 真機、正式私人網站 HTTPS/CDN/登入、現地尺寸均未驗。

## Blender-native gate 保持 PENDING
本次環境沒有 `blender` 或 `bpy`，沒有產生 .blend 與 Cycles PNG。獨立 SourceQA.zip 包含 source-ready `blender_native_v026.py`，需在有 Blender 的電腦執行，檢查 V025/V026 原幾何保留及新增前後厚度，渲染兩個固定鏡位各兩張 Cycles 圖，儲存 .blend、貼圖與驗收 JSON。

完整重建腳本（`build_v026.py`、`patch_v026.py`、`replay_v026.py`、`qa_v026_source.py`）、WebGL2 圖與驗收 JSON 在獨立交付 `Noboribetsu_Date_V026_R1_SourceQA.zip`，**未提交此 GitHub 分支**，因完整 Runtime 含私有大型 3D 場景，仍由使用者保管。此分支只保存定位、SHA 契約與交接紀錄。

### 重播
```bash
python replay_v026.py /path/to/Noboribetsu_Date_V025_R1_Runtime.zip /path/to/NEW_EMPTY_V026
blender -b --python blender_native_v026.py -- /path/to/NEW_EMPTY_V026 /path/to/NEW_NATIVE_OUTPUT
```

### 下一輪 V027
請勿直接複製 V026 到整條街。先在 Blender 正式產出母檔＋Cycles 比較，並完成整座園區真正的 V026 WebGL2 開關／移動、Android 實機驗收，再做多窗格擴展。
