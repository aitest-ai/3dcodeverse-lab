# 人物、服裝與動作驗收場 0.7.0

本階段改善 Vivi 跑步偏蹲，並讓腿較長、155 joints 的 Vita 以自己的骨架、衣鞋與接觸點完成待機、走路和輕跑適配。Vivi 保留原來 152 joints；沒有重塑身形、等比例放大衣服或直接複製不相容的局部動畫。

## 啟動與切換

解壓 `Character_Studio_0.7.0_Runtime.zip`，執行：

```bash
python3 START_STUDIO_V07.py --open
```

開啟 `http://localhost:8779/web-v07/`。Windows 可雙擊 `START_WINDOWS_V07.cmd`；埠號可用 `--port 8780` 改變。Python 3 以外無啟動依賴，模型與 Three.js／VRM 載入器均為本地檔，無 CDN／帳戶需求。

- 左側選 Vivi 或 Vita；預設 A/B 同鏡位比較，取消「同鏡位比較」只看新版 B。
- Vivi 提供七段動作及前版的連續起停／左右轉身；本階段只改 Run，另外六段 GLB 動畫完全保留。
- Vita 目前提供 Idle、Walk、Run。起步、停步和轉身尚未製作，相關連續按鈕停用，不用不存在的動作代替。
- 時間軸以 **B 新版的真實片段秒數** 為準，A 依同一相位重取樣。Vivi 新 Run 為 0.7 秒，A 為約 0.933 秒；A 在比較模式會加速，不是兩者原速或同秒數比較。截圖紀錄包含各自片段時間。
- 支援暫停、60 fps 逐格、調速、循環、正／側／後、胸腹、手、裙片及腳掌近景；可看當前髖高、膝彎曲與軀幹傾角。可保存畫面、錄影及匯出人工觀察 JSON。
- `evidence-v07/index.html` 提供實際瀏覽器連續畫面與兩段 WebM；不是離線渲染或生成圖片。

要編修／重建，另把所需的 `Character_Studio_0.7.0_Vivi_Sources.zip`、`Character_Studio_0.7.0_Vita_Sources.zip` 解壓至同一 `Character_Studio_0.7.0` 資料夾。Runtime 已包含兩位角色，來源包按角色分開，保留完整解析度貼圖，不以檔案大小取代品質判斷。

## 固定版本與比較基底

| 角色 | 本階段版本 | A 比較基底 | 原生骨架／腿長 |
|---|---|---|---|
| `vroid-vivi-motion-review` | `0.3.0` | 前版已修衣物／轉身的 `0.2.0` | 152 joints；腿長約 0.632 m |
| `vroid-vita-motion-review` | `0.1.0` | `vroid-vita-motion-experiment / 0.1.0`，本階段低骨盆試作，未通過 | 155 joints；腿長約 0.804 m |

Vita 原 VRM 沒有動畫。A 是明確標示的專案試作，不是原作者動作或正式成品；A/B 都提供自己的母檔與 SHA。Vita 約長 27% 的腿長用自己的接觸點、步幅及原生掌面計算。輕跑週期皆為 0.7 s，但根位移速度不同：Vivi 約 1.489 m/s，Vita 約 1.895 m/s；地圖應讀取相應版本資料，不硬套同一移動速度。

精確 GLB／母檔雜湊、來源、設定在 `library-v07/catalog.json` 與各角色版本資料夾的 `files.json`、`skeleton-profile.json`、`adaptation.json`。腳本、作者與授權見 [THIRD_PARTY_V07.md](THIRD_PARTY_V07.md)。原 `.vroid` 工程仍未取得；提供原 VRM、原始解析度貼圖及衍生 Blender 工作母檔。

## 已測、失敗與未測

詳細結果：[evidence-v07/acceptance-summary.json](evidence-v07/acceptance-summary.json)。工程數值不等於美術核准，所有候選保持 `art_approved=false`、`game_ready=false`。

| 類別 | 本階段範圍 |
|---|---|
| 程式／來源 | 原始網格、權重、rest、材質、貼圖／VRM metadata 的位元組保留；Vivi 六段未改動畫精確保留；版本／雜湊鎖、重新匯出與覆寫防護 |
| Blender | 冷開母檔、實際網格對比、重新烘焙／匯出；沒有做離線美術渲染 |
| 真實瀏覽器 | Chromium + SwiftShader；Vivi Run、Vita Idle/Walk/Run 以 120 Hz 檢查實際變形頂點，含中間幀；全網格循環接縫、鏡位、切換、控制及單獨顯示 |
| 姿勢 | 記錄支撐期膝彎曲、髖高、軀幹傾角；改善偏蹲，並保留彎曲，未用鎖直膝蓋掩蓋問題 |
| 接地／衣物 | 實際鞋底及分接觸段腳滑；指定裙片／腿部和手部 Skin 的三角面交叉。原獨立指甲嵌合另列；不是全身實體／衣物自碰撞核准 |
| 失敗試作 | 過高騰空骨盆造成腿伸展不足、裙骨重複疊加、Vita 走路偏蹲的中途候選已淘汰；Vita 低骨盆 A 僅作失敗對照 |
| 手機／美術／其他引擎 | 手機真機、人工美術、Godot／地圖內驗收未測。390 px 桌面排版不等於手機真機 |

仍需人工審視步態風格、手臂擺動、衣襬布料感、完整胸口／腋下／腰臀碰撞，以及不同地形和速度。此版是輕跑候選，不是高速衝刺、真人動捕或自行訓練 AI。未新增動物動作；既有柴犬、馬和 20 個模型庫均保留，入口在前階段說明。

## 可重現編修與取用

本次實際使用 Blender 5.2.3 LTS（e13b728c6880）、4 CPU quota、16 GiB、無 GPU。在 Runtime + 對應 Sources 解壓資料夾執行，將 `blender` 換成自己的程式路徑：

```bash
blender -b --python-exit-code 1 --python scripts/build_vivi_v07.py
blender -b --python-exit-code 1 --python scripts/build_vita_v07.py
```

只讀固定來源，輸出到 `work/v07-build/`。可用 `STUDIO_V07_OUT` 指定另一個工作資料夾；不覆寫登錄版本。Vivi 直接輸入是前版 0.2 母檔／GLB、原始 GLB 與接觸設定；Vita 使用自己的原始 GLB／Blender 工作副本及 Harbor 0.3 動作參考。共用原生腿長 IK、步態相位、掌面語意、量測與檢查工具；接觸區、步幅、站距、衣物鬆量及來源權重同步按角色記錄。

複製母檔修改動畫後，匯出新候選：

```bash
blender -b --python-exit-code 1 --python scripts/export_motion_v07.py -- --character vita --mother /path/to/edited-copy.blend --output work/my-vita-candidate.glb
```

匯出器拒絕覆寫及網格／權重／rest／材質／貼圖變更，避免悄悄捨棄服裝編修。服裝拓樸變更需建立新的幾何版本與匯出流程。冷開再匯出的浮點差可能產生新 SHA，不能冒用登錄版本。

```bash
python3 scripts/verify_motion_v07.py
python3 scripts/pin_motion_v07.py --id vroid-vita-motion-review --version 0.1.0 --sha256 <catalog.json 中的完整 SHA-256> --dest work/vita-isolated-review --review-candidate
```

固定 ID＋版本＋雜湊，不會自動替換其他地圖。`--review-candidate` 僅准隔離驗收；目的地存在即拒絕。CI 重驗來源鎖、結構與已保存證據，不宣稱 CI 重新執行瀏覽器或人工驗收。

重跑幾何／瀏覽器驗證：先 Blender 執行 `scripts/check_blender_v07.py`，再在網頁啟動後用 Playwright 執行 `scripts/check_browser_v07.cjs`，最後 Blender 執行 `scripts/check_crossings_v07.py`。後者讀取瀏覽器實際輸出的頂點串流。畫面腳本為 `scripts/capture_motion_v07.cjs`。Blender／Chromium／Playwright／FFmpeg 為外部工具，沒有打包或假稱桌面 GUI 驗收。
