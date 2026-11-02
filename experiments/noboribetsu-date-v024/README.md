# 登別伊達時代村 V024 R1｜高等學問所單窗格重疊清理與完整遊戲 QA

本分支堆疊 **V023 Draft PR #113**，保留 V023 原始 PBR GLB、V004/V022 原瓦片、全部舊場景、路線和碰撞。**不要合併、部署、覆蓋私人網站或改分享權限。**

## 已實做
- B 精修場景新增可開關 `v024_v004_window_occlusion.glb`：5 個 mesh、792 triangles、1,122,844 bytes，原 V023 1,740 triangles → 減少 948（約 54.5%）。
- 移除 V023 重複增加的局部 35 片瓦片（840 triangles）與部分簷下木片（108 triangles），而非移除 V004/V022 正式舊模型的屋瓦。
- 紙窗表層 render-only 向前偏移 2cm，降低原格柵與貼圖互相干擾的可能。這是美術候選，不是實測深度、不能當成建築幾何證書。
- 保留 V023 原資產，新增「V024 窗格整合」開關；開啟 V024 時 V023 不同時畫出，關閉 V024 則回到 V023（受其原開關控制）；A 骨架兩者均不顯示。
- 原生 WebCrypto SHA256 在正式 Runtime 對新 JSON 和 GLB 做 fail-closed 驗證，離線測試用 SHA adapter/定位 hook 均不進正式網站。

## QA 與證據分級
- V023 原始 Runtime ZIP SHA256 `dcb632fe8887a70a70b92fe9e513c9b9218d1363dd24de630e79824dfd94b1`；原 128 檔中 124 檔完全不變，只修改 app.js/index.html/qa.json/scene_view.json；另新增 README、GLB 與 JSON，合計 131 檔。獨立乾淨重建：131/131 SHA256 一致。
- 凍結的 V004 原本 GLB、V022 GLB、V023 GLB、472 個路線點、13 個導引點、CollisionWorld 全保留。Node `--check`、trimesh 重讀、UV/三角面及 GLB SHA 驗證通過。
- 真正 Chromium+Xvfb+ANGLE SwiftShader WebGL2：獨立建築視角 V023／V024 比較 4 張同鏡位 PNG 通過（近景、斜角）。
- 同一隔離 Chromium 的**完整 B 精修場景成功載入**、進場按鈕成功、V024 開→關→開成功，且 V024 關閉時 V023 正確顯示。實際 W 鍵按住約 1 秒，位置位移 **1.26972 m**。並取得一張完整 B 柱廊附近畫面。
- **完整場景第二張對照截圖時軟體渲染逾時**，故沒有完整遊戲雙截圖驗收；未測完整長距離往返、效能 FPS、Android 實機或私人 HTTPS/CDN/登入。
- 未執行 Blender 原生 .blend/Cycles；SourceQA 附可在 Blender 環境匯入、編輯並保存 .blend 的 source-ready 腳本，**不宣稱已產生母檔**。

## 私有交接與可重播
完整 `Runtime.zip`、`SourceQA.zip`（含 `build_v024.py`、`patch_v024.py`、`replay_v024.py`、`qa_v024_source.py`、`qa_v024_browser.py`、`render_v024_isolated.py`、`blender_import_v024.py`）、四張同鏡位 WebGL2 模型比較圖、完整遊戲單張截圖、Validation、Comparison、離線 Review.html 均以獨立檔案交付。

重播範例：
```bash
python replay_v024.py /path/to/Noboribetsu_Date_V023_R1_Runtime.zip /path/to/new_EMPTY_V024
python qa_v024_source.py /path/to/new_EMPTY_V024 /path/to/Noboribetsu_Date_V023_R1_Runtime.zip
# 需要 Blender 的電腦上才可執行：
blender -b --python blender_import_v024.py -- /path/to/new_EMPTY_V024 /path/to/V024.blend
```

GitHub 僅保存可公開的規格與交接，不包含私人大型 GLB 場景。**保持 Draft、不合併、不部署。**
