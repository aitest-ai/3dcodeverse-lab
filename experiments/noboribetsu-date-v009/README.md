# V009 接手說明：登別伊達時代村商家街側牆精修

**這份 V009 不是新的整座公園。它是 V008 的修正候選：保持約 231.57 公尺可步行路線、完整高品質場景、碰撞和 A/B；變動只在變裝攝影館側牆。**

## 開啟

下載 `Noboribetsu_Date_V009_R1_Runtime.zip`，解壓至新資料夾：

```bash
python start_v009_local.py
```

本機瀏覽器開啟 `http://127.0.0.1:8769/`；若 WebGL2 無法使用，改點 `review_v009.html`。請以自己的電腦／手機實際開啟測試；本輪環境無 GPU WebGL2 context，不能宣稱已測過 3D 畫面。

## 來源與重播

需要使用者既有的 `Noboribetsu_Date_V008_R1_Runtime.zip`。**不可拿 V003/V005 舊版本取代新版，也不可覆寫 V008。**

1. 把 V008 ZIP 解壓到新的 `base/`。
2. `python build_v009_utsuroi.py base/dist/assets/v008_waraji_architecture.glb base/dist/scene_view.json outputs`
3. `python integrate_v009.py base .`，會產生新的 `runtime/`；若已存在，會拒絕覆寫。
4. `python render_v009_compare.py runtime outputs`（需要原 V008 渲染腳本，或改用本包自足 `v009_vtk_actor.py`）；`python make_v009_review.py`
5. `node test_v009_runtime.mjs`、`DATE_V006_ROOT=runtime node test_v009_navigation.mjs`、`python verify_v009_delivery.py`。

工作資料夾的腳本依工作根目錄組織。GitHub 的來源腳本相同，移動到新目錄時可按以上方式配合相對路徑執行。

## 來源可信度

- OSM 平面：凍結的 V002 園區幾何，並非測繪現況。
- 變裝攝影館用途：官方 https://edo-trip.jp/facility/utsuroi-kan/
- **2026 年完整外觀照片不足，側牆模型是美術修正候選，非精確還原。**
- 所有官方／第三方照片只做外部比對，不打包。
- Blender 輸出腳本只生成獨立可編輯建築 `.blend`，**未執行，非完整 V002/V003 Blender 母檔**。
- GitHub 不存放私人大型 GLB 與全部 runtime；實際資產在交付 ZIP。

## 保護原始工作

一律從 V008 ZIP 建立新資料夾、V009 僅使用獨立分支與 Draft PR。不得合併、覆寫舊網站或將程式檢查當作 Android／WebGL 真機通過。