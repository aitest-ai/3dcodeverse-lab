# 登別伊達時代村 V005 R1｜第二段商家街 source-ready

## 本分支與資料來源

此工作為 V004 Draft PR #64 上的**獨立堆疊式擴建**，不覆寫 V002／V003／V004、不合併任何 PR、不更新私人網站。

- 新增路線：沿凍結 V002 OpenStreetMap 中心線 67.7093 m；總長 197.7239 m。
- 新增建築位置：わらじ屋 `way/283905573`、うつろい館 `way/283905580`，來自 V002 凍結 OSM。店家用途依 `edo-trip.jp`；所有立面、屋高、屋瓦、柱子與招牌均是**作者推估的原創模型**，不是精確實景還原。
- 保留 V004 與前版完整高品質資產。新增三份 GLB；不開放室內、不加入第三人稱。
- 提供 `v005_dem_profile.json` 為衍生的 **V002 GSI DEM 高程截面**，非實測鋪面。路寬 6 m 與渲染層高差是工程假設。
- 不包含 V002/V004 私有完整模型 ZIP、官方照片或 V003 正式 Blender 母檔。

## 使用者端離線預覽

請下載私人檔案庫的 `Noboribetsu_Date_V005_R1_Runtime.zip`，解壓縮、執行包內 `start_server.py`，再以本機瀏覽器開啟啟動器顯示的網址。正式 WebGL2、Android 與私人 CDN 均**尚未驗收**。

## 可重跑建置（須自行提供保留的 V004 R1 Runtime ZIP）

環境：Python 3.11+、`numpy`、`trimesh`、`Pillow`、`scipy`，Node.js（檢查），選用 Blender 5.2 LTS。建議在新空目錄處理，不與舊版共用輸出。

```bash
# 以下命令均在此 README 所在的 scripts/ 上一層執行
export DATE_V005_ROOT="/absolute/path/to/empty/v005-runtime"
export V004_RUNTIME_ZIP="/absolute/path/to/Noboribetsu_Date_V004_R1_Runtime.zip"
python scripts/prepare_v005.py "$V004_RUNTIME_ZIP" "$DATE_V005_ROOT"
python scripts/build_v005_extension.py
python scripts/integrate_v005_runtime.py
node scripts/test_navigation_v005.mjs
python scripts/verify_v005_assets.py
```

`build_v005_extension.py` 從同目錄讀取 `v005_dem_profile.json`，它的來源幾何 SHA-256 在程式裡強制檢查。想重新產生高程截面時，必須額外提供**真實且雜湊正確的 V002** `data/scene_geometry.json`，執行：

```bash
python scripts/derive_dem_profile.py /path/to/scene_geometry.json scripts/v005_dem_profile.json
```

以上為執行檔與來源重播，**不是**宣告執行端已通過真正 WebGL2 或 Blender 美術驗收。

可選擇在有 Blender 5.2 的機器執行：

```bash
DATE_V005_ROOT="$DATE_V005_ROOT" blender -b -t 4 --python scripts/blender_v005_extension_only.py
```

輸出只是新路段的獨立可編輯 `.blend`，不包含 V002/V003/V004 已完成場景，也不會覆寫舊母檔。

## 已有測試與未完成閘門

**已完成**：3 個 GLB 回讀、782 個 A/B 碰撞點、完整往返模擬、680 個路面對地形抽查、10 份輸出的 SHA-256 clean replay、舊 V004 50 個檔案中 46 個 SHA 不變。

**未完成**：真正 WebGL2 內載入與遮罩灰色 OSM 量體、私人網站登入/CDN、Android 真機、Blender 原生回寫與同鏡位 Cycles 實景對比。請勿合併 PR、對外發布或宣稱完整遊戲驗收通過。

交付另見 `Noboribetsu_Date_V005_R1_Delivery_Report.md` 與 `Noboribetsu_Date_V005_R1_Validation.json`。