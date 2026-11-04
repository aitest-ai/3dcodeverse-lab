# 人物、服裝與動作驗收場 0.1.0

一個真正載入固定 GLB、可播放/逐格/同鏡位比較並保存觀察的網頁工作室。所有角色仍為 Draft 候選，`art_approved=false`、`game_ready=false`。

## 直接操作

交付包中的 `OPEN_STUDIO.html` 已嵌入實際 Three.js 程式、兩位角色的前後 GLB 及骨架設定，沒有 CDN、帳戶或服務費。完整HTML已以localhost方式實測；本雲端瀏覽器政策拒絕 file://，因此「下載後直接雙擊開啟」本輪標為未測。建議先使用下方localhost啟動方式，再開啟 `/OPEN_STUDIO.html` 或 `/web/`。此檔由 scripts/build_standalone.py 生成；Git 保留可重建程式，完整交付包另附生成檔。

需要一般網頁伺服器或開發時：

```sh
python3 START_STUDIO.py --open
# http://localhost:8765/web/
```

Windows 可執行 START_WINDOWS.cmd（需 Python 3）；伺服器預設只綁 localhost。也可用自己的靜態 HTTP/HTTPS 伺服器。不要直接以 file:// 開 web/index.html，請改用完整 OPEN_STUDIO.html 或啟動伺服器。

1. 左側選 Harbor 或 V29 騎樓阿伯。來源與候選均核對完整 bytes/SHA-256；載入中只有進度，錯誤不退回其他人物。
2. 選待機/走路/跑步；Harbor 另有**實驗**起步、停步、左右90°轉身。阿伯未提供起停/轉身，選單明確停用。
3. 暫停、時間軸、±1格（30fps）、0.1–2倍、循環；原地模式可開啟實測配速網格。網格不是即時腳部 IK。
4. 正/側/背/全身與肘袖、胸腋、衣襬、腳底鏡位；A/B 比較共用一台相機與絕對時間。Harbor A是原 PR137；阿伯 A是本次重定向初稿，**不是原 V29 的走跑**。
5. 儲存PNG、錄製6秒WebM，或依部位記錄通過/失敗/未測，再匯出包含精確資產雜湊及鏡位/時間的 JSON。單筆觀察通過不自動成為正式美術核准。

## 母檔與重建

- `sources/harbor-v02/`：PR137 原母檔、原GLB、來源貼圖、授權與原程式，保留不變。
- `sources/oldman-v29/`：V29 原母檔、原中性/姿態GLB、來源/授權標頭，保留不變。
- `assets/harbor-courier-review/0.1.0/`：新候選 BLEND/GLB、完整貼圖、65骨設定、動作取樣與清單。
- `assets/taiwan-oldman-review/0.1.0/`：重定向初稿/修正版各一份 BLEND/GLB、完整貼圖、53骨設定與量測。
- `evidence/`：實際瀏覽器/匯出/獨立解析/冷讀證據；各類驗收見 docs/ACCEPTANCE.md。

原生 MPFB 母檔需 Blender5.2.3；4.3.2 無法開啟它的壓縮格式。本輪下載官方 Linux 5.2.3 並驗證官方 SHA-256。可選：

```sh
python3 scripts/bootstrap_blender.py --dest work/tools
work/tools/blender-5.2.3-linux-x64/blender -b --threads 4 --python-exit-code 1 --python scripts/build_harbor.py
work/tools/blender-5.2.3-linux-x64/blender -b --threads 4 --python-exit-code 1 --python scripts/retarget_oldman.py
python3 scripts/vendor/inspect_glb.py work/rebuilt-assets/harbor-courier-review/0.1.0/harbor-courier-review.glb
python3 scripts/vendor/inspect_glb.py work/rebuilt-assets/taiwan-oldman-review/0.1.0/oldman-retarget-candidate.glb
# 核對已交付的固定版本（不改寫母檔）：
python3 scripts/verify_registry.py
python3 scripts/build_standalone.py
```

最後一步使用固定 esbuild0.25.12（或 ESBUILD_BIN 指向已裝的執行檔），只在建置時需要 Node/npm；操作交付 HTML 不需要。重建預設只寫入 `work/rebuilt-assets/`，不覆寫 sources 或已交付的 assets。可用 STUDIO_BUILD_ROOT 指定另一個獨立工作目錄；新正式候選須另建立下一版目錄、重新驗收，再人工更新目錄與雜湊，不覆寫既有發布版。`scripts/update_registry.py`只整理本版已選定的published assets，並不是自動發布/升級器。Blender匯出器可能產生不同二進位雜湊，故每次重建都重新量測/核對/驗收，不能硬沿用舊hash。

## 未來地圖固定取用

`assets/registry.json` 的 ID、version、candidate.sha256 與 profile_sha256 是取用依據，沒有 latest。正式模板安裝預設拒絕本版所有候選；如只作獨立審查，可明確指定：

```sh
python3 scripts/pin_asset.py --id harbor-courier-review --version 0.1.0 --sha256 <registry的完整SHA256> --dest work/review-copy --candidate-review
```

目的資料夾已存在、ID/版本/雜湊不符時會停止，不覆寫地圖、不自動更新。需要人工美術通過與對應地圖實測後，另建立正式版本，不能直接修改本版核准旗標。

來源盤點見 docs/INVENTORY.md；已知缺陷、待驗與下一步見 docs/ACCEPTANCE.md。未合併main，未部署或更新任何其他專案網站。

完整ZIP的 `FILES.sha256` 包含生成的 OPEN_STUDIO.html；Git版未重建HTML前，這筆生成檔會尚未存在。母檔/GLB已在獨立工作目錄重建，3份GLB與交付版逐位元組SHA完全相同，見evidence/rebuild-qa.json。`sources/oldman-v29/UPSTREAM_ARTIFACT_SHA256SUMS.txt`是原始完整上游artifact的索引，不是宣稱該artifact每個歷史檔都隨本包附上；本包精確來源子集見sources/SOURCE_FILES.sha256。
