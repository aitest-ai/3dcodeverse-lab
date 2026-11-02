# 登別伊達時代村 V016 R1｜石基座高程診斷，而非新增建築
此版本**堆疊在 V015 Draft PR #91**，保留 V002～V015 所有版本與私人預覽，不合併、不部署。

## 關鍵更正
V015 所列四個「埋地柱腳」數值，其實是 **高等學問所與北京亭兩條連續石基座**上的 4 個地面高程取樣點，不是 4 個可單獨替換的石墩。V004 真正的 `stone_foot` GLB 具有五個連續石材區塊，涉案兩條各高約 0.55m；局部埋地 0.0621–0.10804m，尚可見 0.44196–0.48790m。此坡地情況不能單憑埋地深度判定建築缺陷。

## 本輪實作
- 在原 V015 執行包**不改任何 3D 建築**，新建 `v016_grade_inspection.json`；B 場景新增預設關閉的「基座取樣診斷」控制，顯示 4 個黃色環狀**診斷標記**。標記不是新石墩，無碰撞；A 場景不顯示。
- V015 已完成的 8 處懸空支撐、V014 石板、V011 地形補洞、V012/V013 路緣及 231.5664m 路線全部保留。
- V015 原 112 個 Runtime 檔案中 108 個 SHA 不變，只更新 app.js、index.html、scene_view.json、qa.json；新增診斷 JSON 後共 113 個檔案。
- 從原 V015 Runtime + SourceQA 完全重新解壓重建，**113／113 SHA 完全一致**；ZIP CRC 與 Node --check 通過。

## 驗收界線
- 已在 Xvfb/Chromium/SwiftShader **真正建立 WebGL2**、載入完整 B 場景；診斷控制實際觀察 `false → true → false`，四個標記成功建立，V015 八處支撐與 V011～V014 保留，無頁面載入錯誤。
- 第二張「顯示診斷標記」的實際 WebGL2 截圖因 SwiftShader 極低幀率逾時，**不宣稱真正 WebGL2 前後畫面驗收通過**。
- 同鏡位比較圖用 VTK 從原 GLB 幾何渲染，明確標示不是 WebGL 截圖。
- 測試用 SHA adapter 僅存在隔離 QA。正式 Runtime 仍以原生 `crypto.subtle.digest` 驗證，未在私人正式 HTTPS 瀏覽器驗收；Android 真機與 Blender Native/Cycles 尚未測。沒有新增永久石質修正。

## 重播
備齊未修改的 V015 Runtime.zip 與 V015 SourceQA.zip。解壓到新工作目錄 `base/`、`source/`，將本目錄 `scripts/build_v016_audit.py`、`scripts/integrate_v016.py` 等複製到工作根目錄，依序執行。每次驗證 SHA 及原來源，不能用任意新檔替代凍結來源。完整私有模型不加入 GitHub。

原始交付已新增保存在私人 ChatGPT Library `/Noboribetsu_Date_V016_R1/`：Runtime ZIP、SourceQA ZIP、GLB 真實來源診斷圖、Review HTML、交付報告、SHA 清單。

**Draft，不合併、不部署、不覆寫舊版。**
