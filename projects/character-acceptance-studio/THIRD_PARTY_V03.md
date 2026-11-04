# 0.3.0 作者、來源與修改鏈

沿用 `THIRD_PARTY_NOTICES.md` 的 Quaternius、MakeHuman／MPFB、MRT 與既有專案作者記錄及其原始授權。沒有新增外部人物、衣物、動畫模型權重或更改原授權。Three.js 0.170.0 與 MIT notice 保留，不使用執行期 CDN。

本版來源鏈：原 PR137／V29 → Draft PR142 的0.1.0 → Draft PR145 commit `30d0165b7d387442befc02aca5b4207e305bf69d` 的0.2.0 → 本次專案撰寫的局部配版／表面適配、閉合袖口及實際胸頸軸姿態修正 → 新0.3.0。來源 SHA 在各角色 `report.json`，GLB SHA 在 `asset_manifest.json`，設定 hash 在 `registry-v03.json`。

原作與第三方 CC0 授權仍保留，新修改是使用者授權的專案貢獻，不把所有專案程式／造型重新宣告 CC0。不宣稱真人捕捉、Kimodo／NVIDIA 推論或自行訓練。Blender／esbuild／Playwright／Chromium／ffmpeg 是外部製作與測試工具，沒有把它們或付費外掛／模型權重包進交付。

`RUNTIME_FILES_V03.sha256`、`EVIDENCE_FILES_V03.sha256` 分別完整索引本版兩包實際內容。原0.1／0.2交付包保持不變；原 sources 全41檔的精確子集仍依 `sources/SOURCE_FILES.sha256`。原完整 artifact 的上游索引並不表示每個歷史檔都隨本包附帶。
