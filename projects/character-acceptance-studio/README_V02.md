# 人物、服裝與動作驗收場 0.2.0

本階段把 v0.1 的原地走跑與實驗起停／旋轉，改成兩位角色各自烘焙的**實際根位移、支撐腳、起停踏步與兩步轉身**。保留全部 v0.1、上游母檔及授權；所有新資產仍是候選，`art_approved=false`、`game_ready=false`。

## 開啟與操作

下載 Runtime_Source 包後解壓，於解壓資料夾執行：

```sh
python3 START_STUDIO_V02.py --open
# http://localhost:8767/web-v02/
```

Windows 可執行 `START_WINDOWS_V02.cmd`（需 Python 3）。沒有 CDN、登入或模型服務費。完整 `OPEN_STUDIO_V02.html` 已嵌入程式、A/B 四個 GLB 和各自骨架設定，可用同一伺服器開啟 `/OPEN_STUDIO_V02.html`。本環境拒絕 file://，雙擊離線開啟未測；建議使用 localhost。

1. 選 Harbor 或 V29 阿伯。B 是 0.2.0；A 是固定的 0.1.0 **修正候選**，不是原始上游真人動作。載入顯示 bytes 進度並核對原生 SHA-256，錯誤時停止。
2. 兩位都有 Idle、Walk、Run、Start、Stop、TurnLeft、TurnRight，共 14 段。可暫停、±1 格（60fps）、時間軸、調速、循環。阿伯 A 沒有起停／轉身，對照時明確留白，不虛構修改前片段。
3. 「跟隨人物並顯示地面位移」預設開啟；取消後看 B 在世界座標真的前進，配合「世界位移」鏡位。跟隨只是檢視器抵消平移，GLB 本身包含根位移與轉向；A 的移動網格仍只是舊配速參考。
4. 「待機→起步→走→停步」和「左轉→待機→右轉」會連續播放 B、累積位置與朝向，**不用 crossfade 補縫**。可中斷逐格看。其他任意動畫組合、尤其跑步轉換，不在本輪接續驗證範圍。
5. 正／側／背／全身、肘袖、胸腋、衣襬、膝、腳底鏡位共用相機；A/B 預設同步動作比例，取消後同步秒數。因為起停長度有變，兩種比較意義不同。
6. PNG、6 秒 WebM、觀察 JSON 保留；觀察包含 ID、版本、完整 hash、動作／時間、相機、根位移與接續狀態。數值／單筆觀察通過不自動核准美術。

## 交付位置

- `assets/{harbor-courier-review,taiwan-oldman-review}/0.2.0/`：真正 BLEND、GLB、原尺寸貼圖、各角色骨架語意／rest transforms／比例、動作取樣、匯出與修改報告。阿伯另附 `shoe-weight-changes.json`，644 個鞋頂點的前後權重。
- `assets/registry-v02.json`：A/B 個別版本、hash、profile hash、根位移軌跡與來源鏈。
- `sources/`、`THIRD_PARTY_NOTICES.md`：沿用已核對的 Quaternius、MakeHuman／MPFB、MRT 與專案作者記錄；未引進新服裝、模型權重或有帳戶需求的服務。
- `evidence-v02/`：程式、母檔冷讀、真實 Chromium／Three.js 動作與鞋網格檢查，另附失敗歷史，不能當成通過候選。
- Evidence 包解壓到同一資料夾後，`evidence-v02/frames/` 是實際 framebuffer 連續畫面，`videos-v02/` 是 12 支四鏡位影片。影片每鏡位只有 8 個獨立取樣相位，24fps 是容器重複格，不能用來宣稱效能或細微連續性通過。瀏覽器可直接連續播放與逐格。

完整驗收分層、數字與缺陷見 `docs/MOTION_STAGE_V02.md`；上游盤點仍見 `docs/INVENTORY.md`。V111／彩虹橋精確交接資產仍缺，不回退 V103。

## 重建，不覆寫

需要 Blender 5.2.3；可用既有 `scripts/bootstrap_blender.py` 下載並驗證官方 archive SHA。實測 CPU 背景模式，沒有 GPU／桌面 Blender 宣稱。

```sh
python3 scripts/bootstrap_blender.py --dest work/tools
work/tools/blender-5.2.3-linux-x64/blender -b --threads 2 --python-exit-code 1 --python scripts/build_motion_v02.py
python3 scripts/verify_motion_v02.py --root work/v02-build --out work/v02-rebuild-qa.json
# 重新冷讀已交付母檔；不儲存或改寫：
work/tools/blender-5.2.3-linux-x64/blender -b --threads 2 --python-exit-code 1 --python scripts/verify_editor_v02.py
python3 scripts/verify_motion_v02.py
python3 scripts/build_standalone_v02.py
```

建置讀取精確 v0.1 母檔；預設只寫 `work/v02-build/`，可用 `STUDIO_V02_OUT` 指向另一個隔離目錄。`update_registry_v02.py --publish` 會拒絕以不同 GLB hash 覆寫已存在的 0.2.0；後續修改須使用新版本資料夾及重新驗收。重建 standalone 使用 esbuild 0.25.12，`ESBUILD_BIN` 可指向已裝執行檔；操作時不用 Node。證據重建需 Playwright、Chromium、ffmpeg，瀏覽器腳本可用 `BASE_URL` 指定伺服器。

## 地圖固定取用

```sh
python3 scripts/pin_asset_v02.py --id harbor-courier-review --version 0.2.0 --sha256 4a3f2aa7da8d92b4bc611a9f77e1bd930707f4328d519f9b2bbbdedef2552235 --dest work/review-harbor --candidate-review
```

工具預設拒絕未核准候選；`--candidate-review` 僅限隔離審查。精確 ID＋版本＋hash＋profile hash 必須吻合，目的地已存在就停止，沒有 latest 或自動更新。新 GLB 的根節點已帶平移／yaw，遊戲控制器應提取位移或使用內含位移，避免重複加速；地圖整合、Godot、手機真機及人工美術仍未測。本階段不更新網站、不合併 PR。
