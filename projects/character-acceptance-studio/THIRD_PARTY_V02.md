# 0.2.0 來源、作者與授權補充

本版沿用 `THIRD_PARTY_NOTICES.md` 的逐項來源與作者、原授權檔及 `sources/SOURCE_FILES.sha256`，沒有新增外部人物、服裝、動畫模型權重或變更原授權。專案撰寫的支撐腳／起停轉身規劃與鞋權重修正，屬本次專案修改，不宣稱自行訓練或把整個專案重新授權為 CC0。

來源鏈為原 PR137／V29 → Draft PR142 commit `9c769f52b9d042327b92fc1ba7b64c6e476c07d6` 的角色個別母檔 → `scripts/build_motion_v02.py`／`gait_plan_v02.py`／`shoe_weights_v02.py` → 新 `assets/*/0.2.0/`。原骨架來源、動作來源、作者與個別 CC0 標頭保留；新 `report.json` 記錄讀入母檔 SHA，`asset_manifest.json` 記錄 GLB SHA，`registry-v02.json` 記錄 ID／版本／GLB 與設定 hash。

原 `FILES.sha256` 是 0.1.0 交付索引，保持原狀。本版兩個交付包分別內含 `RUNTIME_FILES_V02.sha256` 與 `EVIDENCE_FILES_V02.sha256`，精確涵蓋各包實際附帶的檔案，含原始解析度貼圖與生成 HTML；兩包自己的 ZIP SHA 記錄在 `deliveries/receipt-v02.json`。失敗歷史的 PNG／JSON 供追蹤，不在候選 registry。
