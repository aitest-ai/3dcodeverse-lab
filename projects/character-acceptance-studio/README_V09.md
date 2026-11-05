# 四足動物驗收工作室 0.9.0

本輪提供柴犬左右弧線轉向的 A/B 比較，以及棕馬／白馬原版 13 段動畫的接地與循環診斷。人物工作室 0.8、既有動物與馬的正式 Release 保留。這些檢查不構成人工美術或地圖整合核准。

## 啟動與操作

解壓 Runtime ZIP，執行：

```bash
python3 START_STUDIO_V09.py --open
```

開啟 `http://localhost:8787/web-v09/`；Windows 可雙擊 `START_WINDOWS_V09.cmd`。需要 Python 3 與支援 WebGL 的瀏覽器，觀看時不需 Blender、Node 或模型帳戶。模型與 Three.js 已內附，使用 localhost 讓 SHA-256 驗證可運作。

左側切換柴犬、棕馬、白馬。動作下拉選單搭配播放／暫停、速度、逐格、時間軸及循環使用；正／側／背、全身、前足與後足近景可檢查關節及足底。可匯出 PNG、6 秒 WebM 與包含角色 ID、版本、SHA、時間、鏡位的觀察 JSON。

柴犬新增 `WalkTurnLeft`、`WalkTurnRight`：四個 Walk 週期走完 90°，半徑約 0.917 m。循環時累積根位移與朝向，四輪繞回。A 是本輪「只轉根節點」的失敗對照，B 是足端位置與支撐期足掌方向修正候選；不是原作者或前版已發行的轉向。取消同鏡位比較可單獨看 B。既有 12 段動畫精確保留，原 9 段其他動作仍未驗接地。**沒有製作起停、原地轉身或直走與弧線的任意切換混合。**

馬是原版 2.3.0，沒有修改動作；轉向與 A/B 按鈕停用。選 Walk／Idle／Gallop 時，頁面顯示最低蹄面、問題時刻及循環接縫，可按「跳至最低蹄面」直接查看。原地動畫未設定移動速度，腳滑尚未評定。既有兩馬的 Walk 約 11 mm 穿地，Gallop 約 15 mm 穿地、全網格首尾跳接約 136 mm，**尚未通過這些驗收**。

「足端高度」是目前變形網格的測量；柴犬的「預定支撐」來自原生四足相位計畫，不是物理引擎判定。馬使用明確等比例觀察縮放與固定地面偏移，不代表生物尺寸已校正。鏡位以固定世界軸命名，轉向中相對角色的方向會改變。[連續畫面與錄影](evidence-v09/index.html) 可逐張檢視。

## 母檔與重建

Runtime 可直接看三個動物。Sources ZIP 解壓到同一 `Character_Studio_0.9.0` 資料夾後，可下載母檔、原始貼圖與原生來源，並獨立重建本輪柴犬，不需要前版 ZIP。包含柴犬 A/B 五段 FK 母檔、前版三段母檔、原生 12 段母檔，以及馬原版母檔／貼圖。其他 9 段原生柴犬動作應從原生母檔編輯，未放進本輪五段 FK 工作副本。

使用 Blender **5.2.3 LTS**（自行安裝並將 `blender` 換成實際路徑）：

```bash
# 輸出至新的 work/v09-build，已存在輸出時拒絕覆寫。
blender -b -t 4 --python-exit-code 1 --python scripts/build_shiba_v09.py

# 動作編輯後另外匯出候選；沒有 --mother 時冷開本版 B 母檔。
blender -b -t 4 --python-exit-code 1 --python scripts/export_motion_v09.py -- --mother /your/edited-copy.blend --output /your/new-candidate.glb
```

A 母檔重匯出加 `--variant baseline`。匯出器重取樣本輪母檔中的五段動作，保留其餘九段原 GLB 軌；浮點重算可能產生新 SHA，仍需重新驗收。修改幾何、權重、rest、材質或貼圖時會拒絕動作匯出，避免靜默丟棄改動，需另走完整幾何輸出流程。

## 固定取用

新柴犬：`quaternius-shibainu-grounded-review / 0.2.0`

SHA-256：`922427fae1ced358766e21c3cf1d9a0f78602c5aacbc739db7580e32d9b2cbff`

```bash
python3 scripts/pin_motion_v09.py --id quaternius-shibainu-grounded-review --version 0.2.0 --sha256 922427fae1ced358766e21c3cf1d9a0f78602c5aacbc739db7580e32d9b2cbff --dest ./work/shiba-review --review-candidate
```

不自動更新地圖、不覆蓋目錄。pin 會保留骨架設定、視圖縮放、根位移設定與已知限制；馬的 ID／版本／模型 SHA 仍是原 2.3.0，另附此工作室診斷設定。新版馬診斷骨架表同時列 `first_key_s`、`last_key_s`、`key_span_s`；Three.js 的播放時長包含首鍵前停留時間，不能拿首尾鍵之差代替完整時間軸。

## 驗收範圍

柴犬兩段新增轉向以 120 Hz 實際瀏覽器取樣：足掌中心最大漂移約 0.155 mm，足掌邊緣約 2.614 mm，足底未穿地；這不等於零滑移或完整美術通過。全表見 [驗收摘要](evidence-v09/acceptance-summary.json)、[交接點](docs/CHECKPOINT_V09.md)、[來源授權](THIRD_PARTY_V09.md)。

程式／結構、Blender 冷開、實際 Chromium 分開記錄；影片可能因 CPU 軟體繪圖掉格。手機真機、人工美術、Godot／遊戲地圖、斜坡、任意速度、完整自碰撞未測。馬只完成診斷，沒有接地／轉向修正版；原始 `.blend` 不含 IK 約束，需另建相符的求解設定。下階段依已定位的時間點修正馬的 Gallop 尾端與蹄部接地。
