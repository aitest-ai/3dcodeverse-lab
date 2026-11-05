# 馬匹接地與循環驗收工作室 0.10.0

延續 v0.9，只新增兩匹馬的獨立候選：`horse-brown-grounded-review / 0.1.0`、`horse-white-grounded-review / 0.1.0`。原版 `horse-brown`／`horse-white / 2.3.0`、人物工作室和柴犬候選維持原樣。這是接地與循環修正版，尚未通過世界腳滑、人工美術或遊戲整合驗收。

## 下載與啟動

從本輪 Draft PR 的 GitHub Actions **character-studio-v10-review** artifact 下載兩個 ZIP；候選 artifact 設定保留 90 天，以 GitHub 顯示到期時間為準，並非正式永久 Release。完整重建程式與固定輸入雜湊留在 PR。依 [馬匹交付規範](https://github.com/aitest-ai/3dcodeverse-lab/blob/feat/racing-horse-cc0-pipeline/docs/HORSE_AI_COLLABORATION.md)，新二進位資產不加入 Git 歷史、不自動發布正式 Release。

解壓 Runtime，進入 `Character_Studio_0.10.0`：

```bash
python3 START_STUDIO_V10.py --open
```

Windows 可雙擊 `START_WINDOWS_V10.cmd`。網址 `http://localhost:8791/web-v10/`；只需 Python 3 與 WebGL 瀏覽器，模型與 Three.js 內附。載入先檢查 SHA-256，有進度／錯誤／重試。

左側選棕馬或白馬，動作選 Walk／Gallop。A 是原版，B 是本輪候選；取消「同鏡位比較」可單看 B。可播放／暫停、變速、逐格、循環，切正／側／背／全身／蹄部近景；「跳至最低蹄面」顯示原版失敗時刻，並可下載觀察 JSON、PNG、6 秒 WebM。來源、版本、完整 SHA 與母檔連結在頁面詳細資料。其他 11 段原版動畫也可播放，未冒充完成接地驗收。

Walk／Gallop 比較對齊首鍵到末鍵的週期相位；原版的首鍵前停留不納入 A/B 相位比較。A/B 的實際片段時間各記在觀察 JSON，不能當成完全相同的原生秒數。B Walk 週期約 1.1667 秒、Gallop 約 0.6000 秒；沒有虛構世界前進速度。

## 修正與證據

- Gallop 原始 GLB 全網格首尾差約 135.68 mm；原生 Blender 保留小數尾幀後仍約 105.76 mm。新候選在首尾各 12% 週期使用局部 TRS Hermite 銜接，四肢求解後烘焙 120 Hz，首尾姿勢一致。
- Walk／Gallop 使用原生四肢的兩節鏈、原姿勢彎曲側與當下鏈長，前腿上／下段、後腿上／下段分別求解；近端 BackLeg、軀幹與根節點不靠抬高掩蓋穿地。蹄部方向保留，2 mm 軟地面與 4 mm 平滑過渡只修穿地／近地區域。
- 240 Hz 實際瀏覽器取樣，原版 Walk 最低約 -11.20 mm、Gallop -15.11 mm；候選分別約 +1.31 mm、+1.93 mm。首尾全網格位置跳接為 0（數值取樣），不等於動力學或動作美術已通過。
- 每匹 50 根骨、13 段 GLB 動畫；其他 11 段、原始 BIN、網格、蒙皮、材質、貼圖及 rest 定義精確保留。母檔保留全部 13 段可編輯動作，原材質貼圖已打包。
- 棕／白馬不是第二種身形：6,548 個身體頂點經空間對應後一致至約 0.000001 原生單位，權重一致；頂點順序、材質分區和鬃毛資料不同，分別保留、匯出及實測。

`evidence-v10/index.html` 有 100 張實際瀏覽器連續畫面、兩段 WebM 與六張 Blender CPU 靜態預覽；`acceptance-summary.json` 分開列程式、Blender、瀏覽器、手機、人工狀態。影片可能因 CPU 軟體繪圖掉格，實際編碼時長見 `video-probes.json`。

## 母檔、重建與再匯出

Sources ZIP 解壓到同一資料夾，內含兩匹候選的完整母檔、原版母檔、原始解析度貼圖、來源／授權以及必要診斷設定。原始檔不覆寫。

使用 Blender 5.2.3 LTS：

```bash
# 交付版已有 library-v10 候選，因此重建輸出到新目錄。
STUDIO_V10_OUT=./work/rebuilt-v10 blender -b -t 4 --python-exit-code 1 --python scripts/build_horses_v10.py

# 在母檔副本中編輯 Walk/Gallop，再匯出新候選；未指定 --mother 時冷開本輪母檔。
blender -b -t 4 --python-exit-code 1 --python scripts/export_horses_v10.py -- --id horse-brown-grounded-review --mother /path/edited-copy.blend --output /path/new-candidate.glb
```

匯出器只處理 Walk／Gallop。其他動作、網格、權重、rest、材質、貼圖或根轉換變動會拒絕動作專用匯出，需另建完整輸出流程。浮點重算可能產生新 SHA，應重新驗收；不自動覆蓋既有檔。

從乾淨專案 checkout 完整建置與驗證，安裝 Python 3、Blender 5.2.3、Node 22、Playwright 1.57.0、Chromium、FFmpeg 後：

```bash
BLENDER_BIN=/path/blender CHROMIUM_PATH=/path/chromium NODE_PATH=/path/node_modules python3 scripts/run_validation_v10.py
```

## 固定取用

鎖定資訊見 `config-v10/horses.lock.json`。棕馬 SHA：
`3d81fcebd8755b19f6ff3e80bde6adf3d4ecdc41e59a6d80cebfebcbd457c4a6`

```bash
python3 scripts/pin_horses_v10.py --id horse-brown-grounded-review --version 0.1.0 --sha256 3d81fcebd8755b19f6ff3e80bde6adf3d4ecdc41e59a6d80cebfebcbd457c4a6 --dest ./work/horse-review --review-candidate
```

複製模型、骨架設定、顯示尺度、來源與授權，不更新其他地圖。加 `--include-mother` 可一併帶母檔。既有目的目錄或錯誤雜湊都拒絕。

仍未測：世界移動速度與腳滑、斜坡、不平地面、起停／轉向／任意切換、完整自碰撞、手機真機、Godot／地圖、人工美術。下一階段先建立步幅與速度標定，再做世界支撐期鎖蹄，不能把原地接地通過當成世界腳滑通過。
