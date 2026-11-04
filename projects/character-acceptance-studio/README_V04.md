# 角色與動物模型庫 0.4.0

這一階段回應「現有身形不理想，希望多找可修改的人物、VTuber 與動物」。交付 **20 個可在瀏覽器切換的模型項目**：KayKit 4 種遊戲人物＋1 兜帽變體、VRoid beta 的 Vita／Vivi／Victoria Rubin、Quaternius 10 種動物，以及專案既有棕馬／白馬。現有 Harbor 與阿伯的 0.3 資產、母檔、驗收結果繼續保留，沒有因擴充而變成正式核准品。

這些是完整原作者模型的選型候選，保留各自風格與原生比例。KayKit 是刻意大頭短肢的卡通人物；VRoid 是動漫風；動物是風格化模型。沒有以增加數量替代品質驗收，也沒有將它們描述成寫實人物或已完成自然步態修正。

## 啟動與使用

下載交付的 **Runtime** 與 **Sources** ZIP，解壓到同一個 `Character_Library_0.4.0` 資料夾。只要 Python 3，不需要 Node、Blender、帳號、GPU 服務或 CDN：

```sh
python3 START_STUDIO_V04.py --open
```

Windows 可雙擊 `START_WINDOWS_V04.cmd`。網址 `http://localhost:8771/web-v04/`。Runtime 包可單獨用來看全部模型；Blender 編輯與完整來源驗證還需要 Sources 包。請先解壓 ZIP，勿在 ZIP 檔案預覽器裡直接執行。

- 左側按遊戲人物／動漫／動物篩選，或搜尋作者、名稱與 ID。
- 各模型顯示實際存在的原生片段。17 個項目帶動畫，合計 532 個片段項目（包含同組動畫跨角色重複）；3 個 VRoid **沒有動畫**，顯示參考姿勢並停用播放，提供原生表情檢查。
- 暫停、30 fps 逐格、時間軸、0.1–2 倍速、循環、正／側／背／頭／胸腹／腳掌鏡位，以及骨架顯示。
- 同鏡位 A/B 可選不同模型與各自片段；依片段長度比例同步，不將一套骨架的通道搬到另一套。「等高檢視」只做顯示縮放，資產檔不變；不同來源的絕對尺寸尚未校準。
- A/B 是**不同模型選型比較**，不聲稱修改前後效果。原有 v0.3 的修正對照仍在 [上一階段](https://github.com/aitest-ai/3dcodeverse-lab/pull/147)。
- 可下載 PNG、錄製 WebM、匯出含 ID／版本／SHA／鏡位／時間的觀察 JSON。觀察「通過」不會自動核准地圖取用。
- 來源資訊區提供 GLB、骨架設定、原生母檔或工作副本、VRM 下載。先取得 Sources 包才能開啟 Blender 檔。

啟動器從原 GLB 容器無損還原重複的 VRM／GLB 來源副本與貼圖；逐一檢查 SHA，遇到不同內容會拒絕覆寫。這是交付去重，不是降解析度或重新編碼。所有原始貼圖尺寸保持不變。

## 模型、來源與編輯

`library-v04/catalog.json` 是固定目錄，`intake.json` 記錄來源接收資料。每個項目有 GLB、`.blend`、manifest、report、skeleton-profile、validation 與原始解析度貼圖；既有馬匹保留原資產 ID／2.3.0 版本／雜湊，其餘接收資產以各自 ID 的 1.0.0 版本管理。

12 個動物／馬有原始可編輯 Blender 母檔。5 個 KayKit 與3 個 VRoid 有從原生 GLB/VRM 匯入的 **Blender 工作副本**，不冒稱原作者母檔。KayKit 免費包未提供 .blend；VRoid 未取得 .vroid。VRM 原檔及語意完整保留，瀏覽器用 three-vrm 3.3.0 的 MToon 與表情，沒有啟用髮衣物理；標準 Blender glTF 匯入不保證 MToon／表情語意／SpringBone 往返。需使用完整 VRM 編輯流程時另做適配。

詳細作者、授權與未取得項目見 [THIRD_PARTY_V04.md](THIRD_PARTY_V04.md)。原始來源逐檔雜湊在 `sources-v04/SOURCE_FILES.sha256`。骨架設定保留節點父子、原始 TRS／矩陣、關節、語意對應、原生 Blender rest 矩陣／頭尾／骨長與相對骨長；沒有強迫不同人或四足動物使用相同骨數、姿態或比例。

### 可重現接收／匯出

實際使用 Blender 5.2.3 LTS 背景模式、CPU 與 Chromium SwiftShader；環境沒有 GPU 裝置。沒有執行生成動作模型或自行訓練。

```sh
# 恢復重複來源與貼圖，拒絕不同內容覆寫
python3 scripts/restore_library_v04.py
# 原始 GLB/VRM 直接保留；動物 glTF 只做無損 binary 封裝
python3 scripts/build_library_v04.py
# 逐檔來源、所有 accessor、動作／骨架／貼圖位元組驗證
python3 scripts/verify_library_v04.py
# 一個資產一個 Blender process；開啟來源，或建立工作副本並讀取實際資料
blender -b --python-exit-code 1 --python scripts/prepare_editable_v04.py -- kaykit-knight
```

Blender 編輯時先將要修改的 `.blend` 複製到自己的工作目錄，保留原始鎖定檔。新匯出到尚不存在的路徑：

```sh
blender -b work/my-knight.blend --python-exit-code 1 --python scripts/export_editable_v04.py -- /absolute/path/work/new-knight.glb
```

此新匯出是待驗候選；原生 GLB 的無損重建與 Blender 修改後重新匯出是不同操作。不可承諾編輯後位元組一致，VRM 亦不能靠一般 GLB 匯出保留全部專用語意。重新驗收後建立新 ID 或版本，不覆寫 1.0.0／2.3.0。

### 跨專案固定取用

```sh
python3 scripts/pin_library_v04.py \
  --id kaykit-knight --version 1.0.0 \
  --sha256 60428e3abc09ba83e595d256e3af8c5c976b46cdae599f0802fc82b4a3445168 \
  --dest work/knight-review --review-candidate
```

匯出內容附來源授權、骨架雜湊與 `game_ready:false`。未指定審查用途、錯誤版本／雜湊、已存在目的地會拒絕。這不是將候選安裝到正式地圖的核准。

## 實際驗證與限制

| 類別 | 本階段證據 | 尚未涵蓋 |
|---|---|---|
| 程式／二進位 | 20 GLB 結構；58 來源檔雜湊；所有 accessor 可解碼且有限；來源幾何／骨架／動畫 buffer／貼圖原位元組保留；取用保護 | 不等於完整 Khronos 規範驗證、人體比例或碰撞驗收 |
| Blender | 20 母檔或工作副本實際開啟、骨架／mesh／shape key／材質貼圖讀取；工作副本另行冷開啟 | 沒有 Blender GUI／離線成片美術驗收；10 個舊動物母檔保留未使用的遺失參考圖節點，材質未引用它們 |
| 瀏覽器 | Chromium 實際載入全部20模型；17模型的532片段各抽3時點；352張正側背／關節／跑步樣本畫面；實際操作、原生VRM表情、逐格與A/B、錯誤SHA攔截、取消過期載入 | 不是每影格碰撞或步態分析；沒有 Safari／Firefox 驗收；來源原地動作未加入地圖速度與接地修正 |
| 錄影 | 實際 MediaRecorder；6秒操作計時；實際編碼長度見 `evidence-v04/recording-qa.json`，軟體繪圖有掉格 | 不能把計時長度稱為完整6秒流暢影片或實體GPU效能 |
| 手機 | 390px 版面模擬 | 手機真機、觸控／效能、WebGL相容性未測 |
| 人工與遊戲 | 仍為候選；已有模型的歷史審查另保留 | 人工美術、自然動作、服裝穿模、動物蹄腳接地、各實景地圖與其他引擎均未新核准 |

[畫面圖集](evidence-v04/index.html) 可按模型、片段與視角瀏覽；JSON 索引包含固定版本與實際鏡位。所有 `art_approved`／`game_ready` 保持 false。

下一階段優先從比例與風格合適的完整模型建立修改分支：動漫角色需要專屬 rest pose／軸向／比例檢查與動作重定向，動物先校準實際尺寸與腳掌／蹄接地，服裝依目標身形修正。可再沿用接收腳本加入更多原作者模型；未下載的連結不算已交付。
