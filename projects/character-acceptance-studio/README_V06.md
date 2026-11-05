# 人物、服裝與動作驗收場 0.6.0

本階段精修 Vivi：手指自然彎曲、跑步前裙片避讓、轉身軸向扭轉，以及連續起步／走路／停步／左右轉身。A 是保留的上一版 `0.1.0` 接地候選，B 是新 `0.2.0`；並非把最早失敗初稿當 A。身形、原始網格、蒙皮權重、材質與貼圖完整保留；沒有宣稱人物比例已經通過美術驗收。

## 開啟即時驗收場

1. 解壓 `deliveries/Character_Studio_0.6.0_Runtime.zip`。需要編修時，把同版 Sources ZIP 解壓至相同 `Character_Studio_0.6.0` 資料夾。
2. 安裝 Python 3，執行 `python3 START_STUDIO_V06.py --open`；Windows 可雙擊 `START_WINDOWS_V06.cmd`。
3. 開啟 `http://localhost:8775/web-v06/`。預設同鏡位載入 A/B，顯示下載進度並驗證 SHA-256；不顯示替代木頭人。可改用 `--port 8780`。
4. 在動作選單切換 Idle、Walk、Run、Start、Stop、TurnLeft、TurnRight；使用暫停、速度、±1 格（60 fps）、時間軸與循環。點「連續驗收」可播放完整起停或左右轉身流程。
5. 切正面、側面、背面、左右手、裙襬、腳掌近景；滑鼠可旋轉及縮放。「跟隨位移」控制鏡頭居中，取消後可看實際根位移。可錄影、下載畫面、記錄部位與時間並匯出觀察 JSON。

即時入口是網頁 WebGL；證據頁 `evidence-v06/index.html` 提供真實瀏覽器連續畫面與 WebM。Sources 不含 Blender 安裝程式；本次實際建置使用 Blender 5.2.3 LTS、CPU、無 GPU。解壓後不依賴 CDN、模型帳戶或付費服務。

## 成果與版本

| 項目 | 固定內容 |
|---|---|
| 角色 | `vroid-vivi-motion-review`，原生 152 joints，完整原衣鞋、表情與原解析度貼圖 |
| 新版本 | `0.2.0`，GLB SHA-256 `2c26ef8a2c2462d90a95e8402f6f8a01960d12c4512d8cc647d90671d86594a5` |
| 比較版 | `0.1.0`，GLB SHA-256 `2bc4896cafe97ccded0b739629e523486c44548df2e5f4a3af96a20d1a78e2c7` |
| 母檔、設定、來源鎖 | `library-v06/vroid-vivi-motion-review/0.2.0/` 的 `.blend`、GLB、profile、adaptation、manifest、report、`files.json` |
| 上游 | pixiv VRoid β2 Vivi，CC0 原素材；原 `.vroid` 工程未取得，提供 VRM 原檔與可編輯 Blender 工作副本 |
| 前階段庫 | [20 個人物／動物候選與授權](https://github.com/aitest-ai/3dcodeverse-lab/blob/7bd1e577d2867e3c4772f2655c8285cae5ac0700/projects/character-acceptance-studio/README_V04.md)、[Vivi／柴犬原生骨架動作驗收](https://github.com/aitest-ai/3dcodeverse-lab/blob/477cfb9135038af3dbc00309d0a8998aadbcef88/projects/character-acceptance-studio/README_V05.md)，均保留，未被這版取代 |

來源、作者、授權及修改範圍見 [THIRD_PARTY_V06.md](THIRD_PARTY_V06.md)。每個輸出有 SHA-256；保留上游所有原始貼圖，沒有降成 512 px。此版是角色個別修正，不能直接把指關節角度或裙骨係數當所有身形的共用模板。

## 實際驗收範圍

詳細數值與測試結果見 `evidence-v06/acceptance-summary.json`，可從證據首頁開啟。

| 類別 | 狀態及限制 |
|---|---|
| 程式／檔案 | 檢查原二進位區塊、網格、權重、材質、貼圖、rest rig、版本雜湊、可修改動畫範圍；CI 重驗保存的證據，並不重新跑瀏覽器 |
| Blender | 冷開新母檔，實際評估七段 FK 網格、重新匯出及與瀏覽器比較；離線美術渲染未做 |
| 瀏覽器 | Chromium + SwiftShader 實際載入播放、120 Hz 中間幀鞋底／指定交叉檢查、全網格片段銜接、逐格、表情、錯誤與重試；真實畫面保留 |
| 手部 | 僅手掌／手指 Skin 自交；保留原模型每手五片獨立指甲與原生指甲嵌合，不把這些當新手指相互穿插 |
| 衣物 | 檢查指定前裙片與腿部三角面交叉；不是全身實體碰撞、衣物自碰撞、接觸厚度或布料模擬通過 |
| 起停／轉身 | 預定相位的連續流程與世界位移銜接；未實作任意時間的遊戲狀態切換／速度混合。位置連續不等於速度與加速度已核准 |
| 手機 | 390 px 桌面視窗排版已測；手機真機效能、觸控、散熱未測 |
| 人工美術／遊戲 | 未測，`art_approved=false`、`game_ready=false`。Godot／其他地圖未整合或發布 |

仍需人工檢視手型美感、跑步裙襬布料感、腋下／胸口／褲襠等未納入碰撞區域，以及轉身鞋底的毫米級漂移。不要把未測項目當通過。

## 重現與編修

在 Runtime + Sources 解壓資料夾內，將 `blender` 換成自己的 Blender 5.2.3 路徑：

```bash
blender -b --python-exit-code 1 --python scripts/build_vivi_v06.py
```

只讀前版固定母檔、GLB 與原始 VRM GLB；產出到 `work/v06-build/vroid-vivi-motion-review/0.2.0/`。可用 `STUDIO_V06_OUT` 指定另一個建置資料夾。建置包含指關節、跑步前裙骨、轉身軸向與最後 15% 收尾，再 60 fps 烘焙。原動作參考來自專案 Harbor／既有 gait planner，不是真人動捕或自行訓練 AI。

複製新母檔後在 Blender 編修動畫，另匯出候選：

```bash
blender -b --python-exit-code 1 --python scripts/export_motion_v06.py -- --mother /path/to/edited-copy.blend --output work/my-next-candidate.glb
```

匯出器拒絕覆寫，且會拒絕網格、rest rig、權重、貼圖或材質變更，避免動畫匯出悄悄丟掉服裝修改。要改服裝拓樸／版型，應建立新幾何版本與其專用匯出流程。冷開再匯出會有浮點差與新的 SHA，不冒用原版本雜湊。

```bash
python3 scripts/verify_motion_v06.py
python3 scripts/pin_motion_v06.py --id vroid-vivi-motion-review --version 0.2.0 --sha256 2c26ef8a2c2462d90a95e8402f6f8a01960d12c4512d8cc647d90671d86594a5 --dest work/vivi-review-pin --review-candidate
```

固定取用必須同時指定角色 ID、版本、完整雜湊，目的地存在即拒絕；目前只允許隔離候選驗收，不會自動更新基隆河、北海道牧場、洞爺湖或其他地圖。

重跑數值驗收：先以 `STUDIO_V06_MODEL` 指向要測的母檔資料夾執行 `scripts/check_blender_v06.py`，再啟動網頁，以 Playwright 執行 `scripts/check_browser_v06.cjs`，最後 Blender 執行 `scripts/check_crossings_v06.py`。瀏覽器輸出的暫存頂點在 `work/v06-qa/`，碰撞使用這些真實變形結果。截圖／錄影腳本為 `scripts/capture_motion_v06.cjs`。檢查與建置工具是外部依賴，不隨 ZIP 打包。
