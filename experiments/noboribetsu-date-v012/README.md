# 登別伊達時代村 V012 R1｜可重建工程（不含私人原始大型模型）

目標：僅將 V006 最後 33.8425 公尺道路的路緣與草地做一層「可拆除、透明、視覺用」土色／苔色過渡。**不修改 V011 148 格補洞、任何碰撞、A/B 原始模型、路線或原始 GSI/OSM 資料**。

## 從凍結原始檔重建

1. 準備先前真正的 `Noboribetsu_Date_V002_Complete.zip`（含 `data/scene_geometry.json`）及 `Noboribetsu_Date_V011_R1_Runtime.zip`。不要使用更舊模型取代它們。
2. 解壓 V011 Runtime ZIP 到新資料夾 `V011_extracted/`，不要覆蓋舊版。
3. 在本包源碼目錄執行：

```bash
python build_v012_edge.py /absolute/path/Noboribetsu_Date_V002_Complete.zip /absolute/path/V011_extracted/dist /absolute/path/outputs/v012_road_grass_transition.json
python integrate_v012.py /absolute/path/V011_extracted /absolute/path/V012_candidate /absolute/path/outputs/v012_road_grass_transition.json
python validate_v012.py /absolute/path/V011_extracted /absolute/path/V012_candidate /absolute/path/outputs/V012_integrity_qa.json
```

4. 在一般桌面瀏覽器中，從 `V012_candidate/` 執行 `python start_v012_local.py`。開啟 `http://127.0.0.1:8772/index.html`，點「開始步行」，再按「街尾返程」看新的路緣。若環境會阻擋網路導覽，可在 Xvfb + Chromium 使用 `qa_v012_webgl.py` 進行隔離測試；此 QA 使用**測試專用**摘要替身，正式 Runtime 不能使用該替身。
5. `v012_road_grass_fade_editable.glb` 是相同透明頂點色幾何的獨立匯出，可在 Blender 檢視；**Blender 原生 `.blend`、Cycles 或 Android 真機目前未驗收**。

## 驗證限制

- 原 V011 Runtime 101 個檔案中 97 個完全不變、4 個設定／程式檔修改；新增 4 個檔案（路緣 JSON、V012 README、啟動器與差異驗證）。共 105 份檔案，從乾淨來源重建 105/105 SHA 相同。
- Blender／真機／私人網站 HTTPS／CDN 未測。隔離 Chromium WebGL2 與手機直式模擬已通過，但不代表正式部署可用。
- 路緣寬、顏色與細小起伏為美術估計；沒有新增排水溝、測繪路肩或真實高度資料。
- 原始模型與材質、V011 補洞、A 骨架、碰撞保持不變。

## 來源與權利界線

V002 地形來自 GSI，路線與建築外形參考 OSM。重建前應保留原資料授權及來源說明。本包不含官方商用照片或私人 V002 356 MB 完整來源。大型模型只在原 V011 Runtime ZIP 中。其他 AI 應延續 Draft PR，不覆蓋或合併舊分支。