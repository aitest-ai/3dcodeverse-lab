# 人物驗收工作室 0.8.0

Vita 已補齊待機、走路、跑步、起步、停步、左右轉身，並可連續播放起停及左右轉身流程。Vivi 維持 0.3.0。這是可操作的驗收候選，尚未通過人工美術或正式地圖驗收。

## 啟動

下載 Runtime ZIP 並解壓，執行：

```bash
python3 START_STUDIO_V08.py --open
```

瀏覽器開啟 `http://localhost:8783/web-v08/`。Windows 可雙擊 `START_WINDOWS_V08.cmd`。不需要 Node、Blender、GPU 服務或模型帳戶即可觀看；Python 3 與支援 WebGL 的瀏覽器必須自行具備。檔案已包含 Three.js、VRM loader 與模型，不依賴 CDN。勿直接以 file:// 開啟，SHA-256 驗證使用 localhost 或 HTTPS。

左側切換 Vita／Vivi；動作選單、播放／暫停、速度、逐格、循環與時間軸操作單段動作。上方可切換正面、側面、背面、全身、胸腹關節、手部、衣襬與腳掌。連續驗收按鈕播放「待機→起步→走路×2→停步→待機」或左右轉身。每個版本從自己的 GLB 提取根位移，不共用一組步幅。取消「跟隨位移」可看實際行進距離。

Vita 前版只有 Idle／Walk／Run，這三段在新版精確保留。同鏡位比較只對雙方都具備的片段有意義；選新增動作／流程時會切回新版單角色。前版沒有起停或轉身，沒有假造修改前動畫。Vivi 可沿用上階段 0.2／0.3 對照；時間軸為 B 秒數，A 同相位對照。

「儲存畫面」「錄製 6 秒」「匯出觀察 JSON」會下載到瀏覽器設定的下載資料夾。觀察記錄含 ID、版本、完整 SHA、時間、鏡位與判定。錄影可能因 CPU 繪圖掉格，以實際編碼時長為準。[實際瀏覽器連續畫面](evidence-v08/index.html) 可逐張翻閱，但不能代替即時 3D 操作。

## 母檔、重建與修改

Runtime 可直接觀看兩位角色。Vita Sources、Vivi Sources 按需解壓到同一個 `Character_Studio_0.8.0` 資料夾，以啟用相應母檔／原始 VRM 下載。Vita Sources 包含本輪重建的直接輸入：原生 Vita GLB／衍生母檔／原始貼圖、0.1.0 母檔、Harbor 參考母檔、來源授權；不需要前版 ZIP。完整早期製作鏈仍保留於前版固定提交。

以下指令在解壓根目錄執行，使用 Blender **5.2.3 LTS**。`blender` 需換成實際執行檔路徑；不隨 ZIP 附 Blender 或 Chromium：

```bash
# 從固定來源重建本輪 Vita；輸出至 work/v08-build，不覆蓋版本庫。
blender -b -t 4 --python-exit-code 1 --python scripts/build_vita_v08.py

# 在 Blender 修改母檔副本，再另存新的候選 GLB。
blender -b -t 4 --python-exit-code 1 --python scripts/export_motion_v08.py -- --character vita --mother /your/edited-copy.blend --output /your/new-candidate.glb
```

省略 `--mother` 可冷開本版母檔重新匯出。一般匯出會重新取樣七段動作；浮點重算可產生新雜湊，必須重新驗收。此匯出器只輸出動作；若網格／權重／rest／材質／貼圖已改，會拒絕，避免靜默捨棄修改。衣物或身形修改需另建完整幾何輸出流程。不要把衣物貼到其他身形後宣稱適配完成。

## 固定取用

Vita：`vroid-vita-motion-review / 0.2.0`，GLB SHA-256：

`73810ed0414c723da46dd74dfe227b4c1aec83e4321a6cd0eda0a7ec5f7e7194`

Vivi：`vroid-vivi-motion-review / 0.3.0`，GLB SHA-256：

`1efdd916d4f14b59b27c9baf71bb52fd334fa64d88c67c1484e11a6f4d4814a0`

隔離驗收專案取用範例（拒絕覆蓋已存在的目錄）：

```bash
python3 scripts/pin_motion_v08.py --id vroid-vita-motion-review --version 0.2.0 --sha256 73810ed0414c723da46dd74dfe227b4c1aec83e4321a6cd0eda0a7ec5f7e7194 --dest ./work/vita-review --review-candidate
```

每個角色的 `skeleton-profile.json` 記錄骨名、階層、rest、前向軸、單位、根動作、來源及版本；`adaptation.json` 記錄母檔 SHA、步幅、鞋底點與修改。原始骨長、比例與 155／152 joints 保留，不能直接互貼局部動畫軌。

## 驗收狀態

完整數值與限制見 [acceptance-summary.json](evidence-v08/acceptance-summary.json)、[交接點](docs/CHECKPOINT_V08.md)、[來源授權](THIRD_PARTY_V08.md)。四段新動作於實際 Chromium／SwiftShader 以 120 Hz 取樣：鞋底無穿地，最大接觸漂移約 3.1 mm；兩位角色連續流程的全網格接縫通過。指定衣片／腿部與手部 Skin 交叉為零，不代表全身或衣物自碰撞通過。

程式結構、Blender 冷開／匯出、瀏覽器操作分開列證據。390 px 為桌面瀏覽器窄視窗，手機真機未測；人工美術、Godot／地圖、任意速度混合、斜坡／地形、完整衣物碰撞未測。原生風格化身形與衣鞋版型未改，本階段沒有新增動物。既有 20 款候選、柴犬與馬成果保留；基隆河 V110／V111、彩虹橋及台灣衣物最新來源缺口仍依前階段盤點，不回退 V103。
