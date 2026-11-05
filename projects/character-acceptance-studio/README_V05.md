# 人物與動物動作工作室 0.5.0

本階段把既有開源模型庫中的 **Vivi 與柴犬** 做成可操作的同鏡位 A/B 動作驗收場。原 20 項模型庫、Harbor／V29–V31、來源母檔及網站皆保留。新檔是待審候選，不會自動取代地圖資產。

## 啟動與操作

下載 `deliveries/Character_Studio_0.5.0_Runtime.zip` 並解壓縮。Windows 安裝 Python 3 後雙擊 `START_WINDOWS_V05.cmd`；其他系統在解壓後目錄執行：

```sh
python3 START_STUDIO_V05.py --open
```

開啟 **http://localhost:8773/web-v05/**。所有模型、貼圖、Three.js 與 VRM 載入器均在本機，無須 CDN、模型帳戶或 GPU 服務。不要直接以 file:// 開 HTML；SHA-256 驗證需要 localhost 或 HTTPS。連接埠已使用時加 `--port 8775`。

左側選 Vivi 或柴犬，預設 A/B 同步顯示。A 是適配初稿／原生動作重烘焙，B 是接地修正候選；不是原作者曾提供 Vivi 走跑的宣稱。切換任一側片段會同步另一側同名動作。可播放／暫停、速度調整、60 fps 逐格、時間軸、循環、正／側／背／全身／胸腹／腳部鏡位、自由旋轉、骨架及 VRM 表情。載入前逐檔核對大小與 SHA，失敗顯示錯誤及重試，不先放木頭人。

「跟隨位移」保持人物置中，地面網格隨根位移移動；取消可看真實世界移動。Walk／Run／Gallop 循環時累積根位移；Start／Stop／Turn 是單次片段，應關閉循環逐段檢查。此版可切片段，尚未提供遊戲狀態機與跨片段混合。

「儲存畫面」「錄製 6 秒」「匯出觀察 JSON」可留存當下鏡位、片段、時間、版本及雜湊。`evidence-v05/index.html` 提供預錄的實際瀏覽器連續畫面；即時觀察仍以 `web-v05/` 為主。錄影在軟體 GPU 上會掉格，不能把影片長度或本機 fps 當成手機效能。

## 交付與固定取用

| 資產 ID | 版本 | 本階段內容 |
|---|---|---|
| `vroid-vivi-motion-review` | `0.1.0` | 152 個原生關節，Idle、Walk、Run、Start、Stop、TurnLeft、TurnRight；軀幹適配、向前彎肘、手掌朝內、鞋底接地、裙骨烘焙 |
| `quaternius-shibainu-grounded-review` | `0.1.0` | 46 個原生關節；修正 Idle、Walk、Gallop，另 9 段原生動畫原封保留且未做接地驗收；約 0.40 m 肩高的指定遊戲尺度 |

每個目錄包含 `model.glb`、`baseline.glb`、`adaptation.json`、`skeleton-profile.json`、`baseline-profile.json`、`motion-audit.json`、`asset_manifest.json`、`report.json` 與 `files.json`。母檔在 Sources ZIP 的同目錄 `model.blend`；原解析度貼圖、原生輸入、授權證據及既有動作參考也包含在 Sources ZIP。兩包解壓到同一個 `Character_Studio_0.5.0` 目錄。

Vivi B SHA-256：`2bc4896cafe97ccded0b739629e523486c44548df2e5f4a3af96a20d1a78e2c7`

柴犬 B SHA-256：`52561dc53ad291ded9b9cc726253b9b72344469acdd24a5d68a815c7380b3329`

未經美術核准只允許隔離驗收匯出，範例：

```sh
python3 scripts/pin_motion_v05.py --id vroid-vivi-motion-review --version 0.1.0 --sha256 2bc4896cafe97ccded0b739629e523486c44548df2e5f4a3af96a20d1a78e2c7 --dest review-vivi-010 --review-candidate
```

腳本拒絕版本／SHA 不符、來源遭修改、缺少明確候選用途及覆寫目的地。目錄沒有 `latest` 自動替換機制。A 對照資產 ID 為相同 ID 加 `-before`，仍是失敗／中間候選。

## 可編輯母檔與可重現流程

使用 Blender **5.2.3 LTS**。在 Blender 打開修正母檔，NLA 的 Idle 軌預設開啟；同名 Armature 與 `StudioRootMotion_v05` 兩條軌一起切換。每次只啟用一個片段。新母檔為 60 Hz 烘焙 FK；原生柴犬 IK 母檔另保留。Vivi 為 VRM 匯入工作副本，沒有取得 .vroid 工程，Blender 材質亦不等於瀏覽器 MToon 外觀。

兩包均解壓後，在目錄執行：

```sh
blender --background --threads 2 --python-exit-code 1 --python scripts/build_vivi_v05.py
blender --background --threads 2 --python-exit-code 1 --python scripts/build_shiba_v05.py
```

結果寫入 `work/v05-build/`，不覆寫已交付 `library-v05/`。`STUDIO_V05_OUT` 可指定另一個工作輸出目錄。A 由保留的輸入與建置腳本重建；B 有直接可編輯母檔。`prepare_registry_v05.py` 僅供建立尚不存在的版本目錄，拒絕覆寫本版。

從母檔重新匯出新的候選檔：

```sh
blender --background --threads 2 --python-exit-code 1 --python scripts/export_motion_v05.py -- --asset vroid-vivi-motion-review --output work/vivi-edited.glb
```

加 `--mother <修改後.blend>` 可輸入另存的母檔。此匯出流程更新**骨架與根動作**，並完整沿用原 GLB 網格、蒙皮、材質、貼圖及 VRM metadata；**不匯出 Blender 的網格、權重、貼圖或材質編輯**。腳本會比對網格、蒙皮、rest rig、shape keys、圖片與材質，偵測這些修改時拒絕匯出，避免悄悄遺失編輯。若做服裝拓樸／權重修改，需要另建幾何匯出版本並重新驗證。新檔 SHA 會改變；未自動註冊或核准。已實際執行兩個母檔的重新匯出，浮點差異與驗證結果在 `evidence-v05/export-roundtrip.json`。

## 本階段實測結果與限制

| 驗證層級 | 已做 | 未完成／不能推論 |
|---|---|---|
| 程式／檔案 | 原始 BIN 前綴與網格、蒙皮、材質、貼圖、VRM extension 逐位元組保持；所有新動畫值有限；版本、SHA、pin 拒絕案例 | 不代表步態自然或服裝無穿模 |
| Blender | 實際背景建置、冷開母檔逐格對照與重新匯出；152／46 關節各自保留 | 沒有桌面人工操作；沒有把離線數值稱為渲染圖 |
| 真實瀏覽器引擎 | Chromium + Three.js/MToon 實際載入操作；A/B 多角度連續截圖、WebM、播放／逐格／錯誤重試；10 段修正片段 120 Hz 原生蒙皮頂點接地取樣 | 為自動操作的真實瀏覽器，不是使用者人工驗收；雲端以 SwiftShader 軟體繪圖 |
| 接地量測 | 修正後取樣均未穿地；Vivi 最大接觸水平漂移約 1.69 mm；柴犬約 0.14 mm；烘焙幀瀏覽器與 Blender 接觸點最大誤差小於 0.001 mm | 是指定接觸頂點／接觸相位的結果，並非全身碰撞證明；不含未修正的 9 段動物動畫 |
| 手機 | 390 px 瀏覽器排版已測 | 手機真機、觸控流暢度、耗電及記憶體未測 |
| 美術／遊戲 | 由助理檢視實際瀏覽器多視角，保留 A/B 問題對照 | 人工美術、使用者驗收、Godot／Unity、地圖整合均未測；全部 `art_approved=false`, `game_ready=false` |

Vivi 初稿走／跑最深約穿地 2.74／3.31 cm，柴犬原生重烘焙走路約 1.35 cm。本版修正取樣的最低鞋底／腳掌高約 1.58–3.00 mm（預留 3 mm 接地間隙，插值會改變最小值）。六段循環動作的首尾網格已在瀏覽器扣除根位移後比對，最大差異小於 0.001 mm（`browser-loop-seams.json`）。完整每段數值在 `evidence-v05/browser-contacts.json`；接觸漂移按腳、接觸 ID 與 heel/flat/toe 分段量測。

已知待改：Vivi 裙襬仍是簡化骨骼跟隨，沒有布料碰撞模擬；手指保持來源張開姿勢，跑步手型仍需放鬆；全身／服裝穿模尚未全面排除。犬隻保留風格化長腿比例與作者軀幹／尾巴動作，接地修正不是獸醫或真實步態驗證。Start／Stop／Turn 為獨立可播放片段，跨片段狀態機與混合尚未完成，不能直接當成正式地圖控制器。

兩者可以共用：檔案鎖、來源授權、語意／單位規則、A/B 鏡位、接地採樣與證據流程。不能共用：骨頭數、骨長、人體步態與四足接觸相位、腿部 IK 鏈、裙骨與腳掌定義。柴犬不算第二種人類身形的服裝適配；既有 Harbor／Oldman 在前階段保留，本階段新增 Vivi 的獨立適配。其他模型仍從 [0.4.0 的 20 項候選庫](https://github.com/aitest-ai/3dcodeverse-lab/blob/7bd1e577d2867e3c4772f2655c8285cae5ac0700/projects/character-acceptance-studio/README_V04.md) 選取，不能直接套上此版骨架動畫。

下一步：使用者在驗收場確認輪廓與步態；針對手指、裙襬碰撞與片段銜接修正，再選另一個人型（例如 KayKit 或 Victoria）及牧場動物逐一適配。未核准前維持隔離候選，無自動部署／合併／地圖更新。
