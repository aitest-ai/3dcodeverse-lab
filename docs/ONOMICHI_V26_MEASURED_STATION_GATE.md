# 瀨戶內騎行世界 V26｜74m 道路「九站點現地證據」與原版人車包絡查核

## 真正完成的內容
沿用 V25 真正的使用者私人 V06 Runtime、V15 Halows、V23 GSI Blender 地形與原 V06 人物／自行車／渡船，不重新生成簡化人物或路面。源版：V25 Draft PR #124，私人 V25 full SHA `5fe5b9f35ef31c693c867b2773f808aca15c44ea18096557d06c22ff39b5c3b2`。

OSM way `388716484` 由 377 端至 317 端的 74.364m 中心線，按來源的 **77 個樣本**建立 S00–S08 **九個地理查核站點**（0m、10m...70m、74.364m），每點具 WGS84 經緯度、里程與原 GSI **地面估算值**，尚未具備真實瀝青路面高度。來源 OSM XML SHA `5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76`；V23 GSI 衍生 2m 高程格網 SHA `03726ce15167b760f6a738c1862097c258857299cae7a32353a84931c44cdbf1`。

V26 私人工程新增：
- `review/onomichi-v26/index.html`：實際可操作的 9 站地理路線圖與現地量測表，日期、來源 URL、量測者、真正有效淨寬、路面高、路緣高度、標誌、障礙及備註；可選點、匯入／匯出來源一致的 JSON。不自動蒐集定位或上傳資料。
- `review/onomichi-v26/V26_Field_Stations.json` 與 `V26_Field_Schema.json`：所有現地量測欄位預設為 null/unknown，**沒有虛構道路淨寬**。非來源資料的輸入必須有日期、量測者與來源網址，測試能拒絕無來源的淨寬。
- 以真正 V06 單車可見外包寬 **0.59478m** 建立模擬用包絡，側向額外距離由人設定（0–0.6m），並即時顯示剖面和數值。但這**不是法定或物理安全距離、不能代表騎乘淨空與碰撞 PASS**。若輸入現場量測寬度，只能提供初步幾何比較，尚需審查動態騎姿與車輪／路緣碰撞。
- 維持 V25 真正 GLB 3D 檢視器的入口與原 V24 真 GLB 離線渲染比較圖；不重新產生低品質替代角色／單車，也不將技術示意框當成道路 Mesh 或 Navmesh。
- `scripts/v26_evidence_gate.py` 和 `review/onomichi-v26/v26_gate.test.mjs`：缺乏來源即拒收，不自動將任何道路變成可騎，來源異常也不授權主程式修改。

## 實測／權限尚未完成
- 9/9 個站點目前道路寬、路緣高度、路面高程、照片／號誌仍皆為未知。不能推論自行車可以合法通過 `access=no,bicycle=yes` 的住宅路段；OSM 的標記語義不等於 2026 現地道路合法、安全。
- 真 3D 原版 V06 人物與單車騎乘、全寬連續掃掠、兩端路口轉向、路面與 GSI DEM 垂直資料對位、Android／瀏覽器 WebGL2 實玩仍未通過。因此 **零新增道路加入 `data/world.json`、沒有更新主網站**。
- 只有在現地照片、道路淨寬、路緣與通行權實際查明後，才能建立另行審查的 Blender 路面候選，**不能從橘色中心線直接生可騎道路**。

## 實際私人交付
- 完整 `Onomichi_V26_Full_Runtime_Field_Evidence_QA.zip`：230,563,673 bytes；SHA256 `273764a261dfe095aa5cc1b792c85e44448069169daad667596b9223068cb816`；326 檔，ZIP CRC PASS。
- 增量 `Onomichi_V26_Incremental_Field_Evidence_Patch.zip`：133,722 bytes；SHA256 `00381d01900dc81c7300dc56975bc4a50cb79c206c33103a37a924f1c907ce90`；10 檔，ZIP CRC PASS。
- **保留 V25 11 個原版保護檔** SHA 全同，僅 V26 工作副本的 `index.html` 增加一個 QA 連結。原 V06 Node 測試 21/21 PASS，新 V26 Node 5/5 PASS，共 **26/26**。
- Playwright Chromium 以真實來源文字注入獨立 DOM 的桌面、手機版操控（點選站點、假設包絡滑桿、錯誤來源拒收、重新儲存）PASS、零 JS 錯誤。測試中的原模型圖來自 V24 真 GLB 離線渲染。**DOM 測試不是完整 Three.js 3D 瀏覽器操作或 Android 實玩**，不能拿它做 WebGL 合格證據。

## GitHub 公開內容
本 Draft PR 僅保存 OSM/GSI 衍生九站位置、來源與驗證器、CI 和本交接說明。使用者私人 V06／V25 約 230MB Runtime 與人物、單車、渡船、GLB 仍只在用戶私有交付包，未公開提交 GitHub。GitHub CI 綠燈只表示公共來源測試，不等於已查核私人 GLB 或已部署。

未經明確授權：不合併 main、不變更舊站或分享狀態、不覆蓋任何舊版。
