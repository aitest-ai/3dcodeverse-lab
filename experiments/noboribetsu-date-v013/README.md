# V013 跨 AI 交接｜從原版 V002 + V012 建立商家街路緣

**來源不可替換：** 使用者保存的 `Noboribetsu_Date_V002_Complete.zip` 及 `Noboribetsu_Date_V012_R1_Runtime.zip`，不使用 V103 等不相關舊角色流程。

1. 另建空資料夾，解壓 V012 Runtime（包含 `dist/`）。
2. 使用 Python + numpy、trimesh、scipy：

```bash
python build_v013.py Noboribetsu_Date_V002_Complete.zip ./v012 ./v013_selective_road_grass.json
python integrate_v013.py ./v012 ./v013 ./v013_selective_road_grass.json
python verify_v013.py ./v012 ./v013 ./v013_selective_road_grass.json ./Noboribetsu_Date_V013_R1_Selective_Road_Edges.glb ./qa
python clean_replay_v013.py Noboribetsu_Date_V012_R1_Runtime.zip Noboribetsu_Date_V002_Complete.zip ./v013 ./replay_qa.json
```

第三步獨立 GLB 由 `trimesh.Scene()` 導出，在 SourceQA 包中另附現成 GLB。V013 patch JSON 是網頁正式載入的彩色透明幾何，並非模型本體或地形資料修改。

3. 一般電腦可在 V013 根目錄以 `python start_v012_local.py` 啟動 localhost，在 Chrome/Edge 開啟顯示網址。此環境中使用虛擬子資源的 WebGL2 腳本是隔離測試，**其中雜湊適配與相機放置 hook 絕不能整合進正式網站**。
4. 先完成 Android 真機、原生 HTTPS/WebCrypto 與 Blender 正式回寫，才可將 PR 升級為可發布。

V013 獨立分支從 V012 建立，保留 V011 補洞與 V012 路緣，新增的 2436 triangles 只作 B 場景非碰撞渲染。V004／V005 舊石邊與基座要優先保留。`V004` 鏡位的改良極不顯著，不可誇稱全面美術通過。