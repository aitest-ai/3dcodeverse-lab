# 登別伊達時代村 V015 R1｜V004 柱腳接地候選交付報告

日期：2026-11-02。以凍結 V014 Runtime ZIP + 凍結 V002 Complete.zip 為來源；不修改其他版本。

## 已完成
- 依原始 V004 商家街 3 棟建築、實際 `v004_merchant_road.glb` 三角面與 V002 凍結地形取樣，檢查 **22 處柱腳**。
- 其中 **8 處**離道路表面超過 3.5 公分、最高 **14.17 公分**。為高等學問所 4 處與北京亭 4 處，已新增緊貼原有石底的獨立石質支撐：**64 頂點 / 96 三角面**。接地模型完全為視覺層，附原始來源、每處柱腳位置和高度。
- **4 處柱腳埋入地面超過 3.5 公分，尚未修正**（最高埋入 10.80 公分）。沒有擅自抬高整棟建築或改碰撞。
- V014 中央石板開關仍保留；V015 另增「柱腳接地候選」開關，限 B 精修模式。正式 WebCrypto SHA-256 查核與模型契約仍完整。
- V014 共 111 個原檔中 **107 不變、4 個程式／設定檔調整**，新增 `dist/v015_post_grounding.json`，共 112 檔。
- 從原 V014 與 V002 封存重新執行建置，**112/112 SHA256 完全相同**。Node 語法、GLB 回讀、96 面積大於零的三角面和來源雜湊皆通過。

## 瀏覽器與美術驗收界線
- **已在 Chromium + Xvfb + ANGLE SwiftShader 中成功建立 WebGL2，完整 B 場景載入成功；V011～V015 模組資訊包含本輪 8 個支撐。** 實際截圖目前只有補強前畫面；第二張 WebGL2 截圖及完整回歸程序因極低軟體繪圖速度逾時，**不得稱 WebGL2 前後畫面驗收通過**。
- 另提供相同鏡位的 VTK GLB 模型診斷對照，**不是遊戲截圖**。目前視覺上可確認有石質支撐幾何，不代表建築實景比例已通過。
- 原始地形參考為保存資料。屋柱石尺寸為推估，非現地調查。Android 真機、私人網站 CDN/登入、原生 HTTPS/WebCrypto、Blender `.blend` 和 Cycles 仍未驗。
- 測試專用 SHA adapter 只存在 `qa_v015_webgl.py` 隔離測試內，**沒有**放入 Runtime。

## 重建
1. 解壓 `Noboribetsu_Date_V014_R1_Runtime.zip` 至新工作目錄的 `base/`。
2. 將本工程包 `source/` 內的 `build_v015.py`、`integrate_v015.py` 放在 `base/` 同層。
3. 設定 `NOBORIBETSU_V002_COMPLETE_ZIP` 指向**凍結的** V002 Complete ZIP。
4. 依序執行 Python `build_v015.py`、`integrate_v015.py`、`check_v015.py`，再啟動既有 `base/start_server.py`。
5. 若任一來源 SHA-256／模型資料不符合既定版本，停止，不以替代模型冒充。

完整幾何觀察值與剩餘問題詳見 `V015_grounding_audit.json`。本版仍為 Draft Candidate，**不覆蓋網站、不合併 PR**。