# 多樣化高品質 3D 人物工作室：主要交接入口

本工作室先完成少量不同身形與年齡設計的角色，再供不同地圖依明確版本取用。目前為 **`01-gray-identity` 灰模候選階段**；`art_approved: false`、`game_ready: false`。可重建、可載入及幾何確實不同，都不等於人物已自然、好看或可直接投入遊戲。

工作位於 `feat/diverse-character-studio`，由 `main` 的 [`f088f0e584764b3fd37dc1bc0670df99313bec41`](https://github.com/aitest-ai/3dcodeverse-lab/tree/f088f0e584764b3fd37dc1bc0670df99313bec41) 獨立開始，交付入口為 [Draft PR #50](https://github.com/aitest-ai/3dcodeverse-lab/pull/50)。不自動合併，也未發布本工作室的公開 Release。既有 V29／V30 人物、基隆河或其他地圖不會因新增工作室候選而被覆寫。

本文件描述實際程式介面與後續適配規則。**每一版的圖片、檔案索引、驗證結果與未解缺陷，統一讀取 [CHARACTER_STUDIO_GRAY_REVIEW.md](CHARACTER_STUDIO_GRAY_REVIEW.md)**；該紀錄尚未列出的結果不可推定為通過。現有來源的保留與採用界線見 [CHARACTER_STUDIO_ADOPTION.md](CHARACTER_STUDIO_ADOPTION.md) 和 [reference_lock.json](../assets/characters/studio/reference_lock.json)。

## 1. 當前兩位候選與修訂範圍

角色設定與候選版本以 [profiles.json](../assets/characters/studio/profiles.json) 為準。目前設定版本為 `0.1.0-gray.3`。

| 角色 | 穩定資產識別碼 | 年齡／身高設計目標 | 主要比例與臉型方向 |
|---|---|---|---|
| D03 高瘦青年 | `studio-d03-young-slender` | 24 歲／1.86 m | 較長腿與前臂、纖細軀幹、長橢圓臉與較窄下顎。 |
| D06 較豐滿高齡女性 | `studio-d06-older-fuller` | 73 歲／1.53 m | 較短腿與相對較長軀幹，分區調整上臂、腹部、腰臀及大腿體積；較短寬臉與年齡相關軟組織形態。 |

上述歲數是虛構人物的設計目標，不是從模型推估出的生理年齡，也不是人口測量標準。年齡感仍須由骨相、軟組織、皮膚、髮型與姿態共同成立；灰模只能審查其中一部分。

`gray.3` 針對先前實際檢視發現的 D06 成熟感不足、後枕至頸部的突兀階差，以及兩人較直硬的嘴縫提出修訂。**增加 target 或更新 profile 說明不代表缺陷已修好**；須看本版匯出後重載的全身與臉部圖，以及同版瀏覽器呈現。完成這些審查前，不以增加角色數、髮型或衣服掩蓋問題。

## 2. 程式、來源與工作分工

先讀儲存庫的 [AGENTS.md](../AGENTS.md) 與 [AI_ASSET_PIPELINE.md](AI_ASSET_PIPELINE.md)，再使用本工作室的獨立路徑。

| 路徑 | 實際責任 |
|---|---|
| [bootstrap.py](../scripts/character_studio/bootstrap.py) | 取得固定 Blender、MPFB 與官方眼睛來源，核對鎖定雜湊，建立隔離的背景執行環境。 |
| [run.py](../scripts/character_studio/run.py) | 依 bootstrap 狀態逐位重建 D03／D06、執行兩種結構檢查，最後比較兩份母檔。 |
| [build_gray.py](../scripts/character_studio/build_gray.py) | 各自套用 macro／局部形態、適配骨架與眼睛，保存兩種母檔，匯出 GLB、重新載入、渲染並冷讀母檔。 |
| [inspect_glb.py](../scripts/character_studio/inspect_glb.py) | 真正解碼 GLB 二進位資料，包括 stride、sparse 與 normalized accessor；檢查幾何、權重、骨架、morph、動畫與影像。 |
| [compare_gray.py](../scripts/character_studio/compare_gray.py) | 冷讀兩份 clean 母檔，核對原生拓樸對應，比較全身與共同頭部區域的幾何及骨長比例；不寫回母檔。 |
| [prepare_review.py](../scripts/character_studio/prepare_review.py) | 將同版實際 GLB、原始網頁檔及固定 Three.js 打包成可執行檢視器，保留模型位元組。 |
| [examples/character-studio](../examples/character-studio/README.md) | 共用尺度的正／側／背及無髮臉部檢視器；包含真實進度、SHA-256 核對、同版重試與連續量測。 |
| [browser_review.cjs](../scripts/character_studio/browser_review.cjs) | 使用 Playwright／Chromium 操作實際 WebGL 頁面、保存截圖與量測，執行雜湊失敗及重試情境。 |
| [character-studio.yml](../.github/workflows/character-studio.yml) | 本分支的背景重建與暫存 artifact 工作流程；不是常駐 Blender 桌面服務。 |

目前固定 Blender `5.2.3`、MPFB `2.0.18` 的 commit `6ff1eb358f6c1959ced77e79e6dd2406d9a71f49`，官方眼睛來源固定 MakeHuman commit `a8bc2d54ff0ac92e78ff71431b1023eda42bf482`。精確下載 URL、SHA-256、Git blob 與授權原文來源鎖在 bootstrap 內，執行後保存在 runtime 狀態及原始素材 manifest。Three.js 固定 `0.187.0`；官方套件的 SHA-512 SRI 與七個交付檔的 SHA-256 鎖在 `prepare_review.py`。

此流程不使用付費服務，不建立憑證，不改 HOME 或既有授權。新增素材前需有可核對的來源、作者、授權及修改紀錄；不能把「網頁可下載」當成可修改、可隨專案交付的授權。

## 3. 從原始碼重建

以下命令從儲存庫根目錄執行。使用 Linux x64、Python 3.12 以上及官方 Blender 所需系統函式庫；本分支 workflow 列出其 CPU 背景渲染環境的安裝項目。建模所需 NumPy 使用 Blender 隨附版本；bootstrap、實體 GLB 檢查器與 viewer 打包腳本使用 Python 標準庫，不需另做 pip／npm 安裝。

第一次選用新的專屬 `runtime` 目錄。Bootstrap 只重用自己建立且來源鎖定相符的環境；既有手動安裝目錄不應被它接管。

```bash
python3 -B scripts/character_studio/bootstrap.py --runtime runtime

STUDIO_VERSION="$(python3 -B -c 'import json; print(json.load(open("assets/characters/studio/profiles.json", encoding="utf-8"))["version"])')"

python3 -B scripts/character_studio/run.py \
  --runtime runtime \
  --outputs "outputs/${STUDIO_VERSION}"

python3 -B scripts/character_studio/prepare_review.py \
  --outputs "outputs/${STUDIO_VERSION}" \
  --out "outputs/${STUDIO_VERSION}/viewer"

python3 -m http.server 8765 \
  --bind 127.0.0.1 \
  --directory "outputs/${STUDIO_VERSION}/viewer"
```

開啟 <http://localhost:8765/>。伺服器命令會持續執行；後續瀏覽器測試在另一個終端進行。不要直接雙擊 HTML，因為 ES modules、模型讀取與 WebCrypto 需要適當的來源環境。

`run.py` 拒絕已存在的產物根目錄；`prepare_review.py` 拒絕已存在的 viewer 目錄。先保存正在進行的改動、確認 profile 版本，再建立新版本或新的候選目錄。不要使用 `build_gray.py --replace-candidate` 覆蓋已交接或正在比較的結果，也不要把不同版本的兩位角色湊成一個包。

`runtime/bootstrap_state.json` 保存 Blender 路徑與本任務專用的 `BLENDER_USER_CONFIG`、`BLENDER_USER_EXTENSIONS`；`run.py` 會讀取它們。狀態檔的絕對路徑屬於該次 runtime，不能直接搬到另一台機器當成已安裝環境。來源下載、雜湊或目標解析失敗時先解決明示原因，不改成舊人物或其他 Blender／MPFB 版本繼續產出。

已有經核對的 `three-0.187.0` 目錄時，可在打包命令加上 `--vendor /path/to/three-0.187.0`；七個檔案仍須全部符合鎖定雜湊。未提供此參數時，腳本從固定官方 npm 套件下載、核對 SRI，再讀取指定檔案。檢視器打包完成後，本機執行不依賴 CDN。

如只需先檢查來源鎖與解碼器回歸，可執行下列命令；它們不會生成角色，也不構成美術驗收：

```bash
python3 -B scripts/character_studio/bootstrap.py --check-locks
python3 -B scripts/character_studio/inspect_glb.py --self-test
```

## 4. 產物與兩種可編輯母檔

以下 `<id>` 為 `d03` 或 `d06`。每位角色的資料放在 `outputs/<version>/<id>/`。

| 產物 | 用途與保留要求 |
|---|---|
| `<id>_parametric.blend` | 保留 macro／局部 target 與 helper 的參數母檔。繼續改身形、適配部件與後續 FaceUnits 時，從此來源延續。 |
| `<id>.blend` | 清理 helper 後的可編輯母檔，保留原生網格、骨架與同一母檔的細分表面。 |
| `<id>.glb` | 本版實際匯出檔；可獨立載入，不能拿舊版 GLB 冒充同版 LOD。 |
| `textures/` | 原始影像來源副本；灰模可能未使用它們，但仍須保存原尺寸、位元組與授權。母檔另保留 packed 資料及冷讀核對紀錄。 |
| `profile.json`、`measurements.json` | 實際使用的角色設定、設計身高及量測身高／比例。肩與髖的 joint span 是骨中心距離，不是皮膚或服裝外寬。 |
| `rig_semantics.json` | 共用語意到本角色骨名、實際骨長、rest matrix、座標約定與額外骨頭。 |
| `asset_manifest.json`、`report.json` | 資產 ID／版本、來源、產物大小與 SHA、冷讀／重載紀錄、實際圖與尚未完成項目。 |
| `renders/` | 從實際匯出後重載的 GLB 產生正面、側面、背面、正面臉部、臉部三分之四與臉部側面圖。 |
| `glb_inspection.json`、`validation.json` | `run.py` 分別產生的二進位實體檢查與既有 manifest 結構檢查報告。單獨執行工具或 workflow 時，以命令實際指定的報告檔名為準。 |

版本根目錄的 `comparison.json` 保存兩份母檔的幾何比較；`viewer/` 保存可執行頁面、原始 GLB、`models/registry.json`、來源證據及校驗清單。Viewer 的 registry 使用 `report.json` 的實際 `height_surface_m`，並核對來源報告記錄的 GLB 大小與 SHA；不拿設計身高代替量測，也不修改 GLB 去配合登錄。

**19,158 個含 helper 頂點、13,380 個 clean 原生身體頂點與一級 Catmull–Clark 細分，是目前固定 MPFB 適配器的契約，並非全角色庫品質或效能門檻。** Helper 是來源建模輔助幾何；移除 helper 不等於刪除人體遮住衣服穿模。這一階段沒有服裝遮罩，也不以刪除胸口、腋下或腰臀人體解決造型。

目前交付的表情鍵與適配動畫均為 **0**；manifest 的 `clips: []` 與 `animated: false` 是刻意的階段標示。原生形態 target 保留在參數母檔，不能因此宣稱 runtime 已具備表情。

## 5. 驗證要分清楚證據範圍

### 結構與幾何

`inspect_glb.py` 解碼真正的 BIN 資料，包含交錯 stride、sparse 替換與隱含零值 accessor，核對有限數值、索引界限、權重與實際 morph 變化，並摘要骨架、動畫及影像。它不是完整 Khronos Validator，也不判斷比例、表情或動作自然度。只讀 accessor 的 `min/max`、表情名稱或 sparse 筆數，不能證明模型真的有正確變形。

`compare_gray.py` 重新開啟兩份 clean 母檔，先核對依序排列的 polygon connectivity，再比較原生 rest surface。它可檢查兩人是否只是同一幾何經等比縮放、旋轉和平移，並提供骨長比例；共同頭部區域包含耳朵與頭顱，不能改稱「純臉部」比較。差異數據不會保證身份差異、年齡感或美術品質。

來源母檔、實際 build script 與 profiles 的 SHA 都須保留；單一 commit 標籤不能取代工作目錄實際程式與設定的核對。

### 實際模型的視覺審查

先看 GLB 重載後的圖，再看同版 GLB 在瀏覽器與指定遊戲中的呈現。逐項檢查比例、全身與臉部輪廓、眼球／眼瞼、鼻唇下顎、後枕頸銜接、材質與法線接縫、陰影、穿模與自然度。全身及臉部比較使用相同投影尺度；不要各自裁成等高來掩蓋身高或頭身比差異。

灰模階段顯示中性材質與無髮頭型。後續恢復材質、加髮或衣服後，要重新審查真實輸出，不能把灰模合格直接延伸成完成品合格。成果圖必須來自真實產物；AI 概念圖可作設計討論，不能代替此處的驗收截圖。

### 瀏覽器、軟體 GL 與真機

檢視器會等兩份完整 GLB 通過位元組下載、SHA 核對與材質準備後一起顯示；失敗提供同版本重試。它保留各自尺度，只平移至共用地面與左右位置。沒有低品質佔位、舊人物替換或依低 FPS 自動降解析度的流程。

目前已取得 SwiftShader 軟體 WebGL 載入實際模型的部分畫面；這不構成完整瀏覽器測試通過。初輪負向雜湊／重試情境曾在同時存在多個軟體 WebGL 場景、背景仍執行 Blender 渲染時出現 `Target crashed`，該次須記為未完成。測試腳本已改為先釋放正向場景，再執行負向與重試；是否完成重跑以本版審查紀錄為準。

具備既有 Node.js、Playwright 與 Chromium 環境時，可在上述 localhost 伺服器運作期間執行：

```bash
node scripts/character_studio/browser_review.cjs \
  http://localhost:8765 \
  "outputs/${STUDIO_VERSION}/browser-review"
```

使用新的結果目錄；此測試腳本本身不提供與建模腳本相同的拒覆寫保護。`CHARACTER_STUDIO_CHROMIUM_BIN` 可指定已有的 Chromium 執行檔。腳本不安裝瀏覽器、不建立帳號；缺少依賴時回報環境缺口，不能把未執行的測試記成通過。

成功執行時應有完整 `browser_review.json`、連續量測與實際截圖；仍須人工看圖。量測需記 renderer、解析度、像素比、暖機及有效採樣期間、p50／p95／最大幀間隔、draw calls 和 triangles。手機寬度的 viewport 只測版面，不是 Android 真機。**目前完整遊戲與 Android 真機尚未測試**；軟體 GL 低 FPS、面數或骨數不能單獨推定手機能力。若未來需輕量模式，先取得持續量測依據，再從同一母檔產生保持外觀一致的 LOD。

## 6. 共用骨架語意與後續動畫適配規則

目前骨架是在每位角色各自完成原生身形與臉部 target 後才適配。共用的是語意，不是要求所有身形的骨長或骨頭總數相同。

| 語意 | 本 MPFB 適配器骨名 |
|---|---|
| root／hips | `Root`／`pelvis` |
| spine_lower／spine_middle／spine_upper | `spine_01`／`spine_02`／`spine_03` |
| neck／head | `neck_01`／`head` |
| upper_arm／forearm／hand，左右側 | `upperarm_l/r`／`lowerarm_l/r`／`hand_l/r` |
| thigh／shin／foot，左右側 | `thigh_l/r`／`calf_l/r`／`foot_l/r` |

精確對應與額外骨頭以各角色 `rig_semantics.json` 為準。其 `head_m`、`tail_m`、`length_m` 為世界空間米制量測；目前 `rest_matrix` 來自 Blender `Bone.matrix_local`，是 **armature 空間**，不能直接視為相對父骨的動畫局部矩陣。Blender 使用 Z-up、朝向 −Y，GLB runtime 為 Y-up；跨引擎時須明記座標與四元數乘法約定。

動畫重定向尚未實作完成。後續實作必須遵守下列規則，並用每位角色的實際姿態驗證：

1. 依語意對應骨頭，從來源與目標 rest matrix 推導所需的父子局部 rest quaternion 與骨軸轉換，再映射相對 rest 的旋轉差；保留目標自己的骨長與 bind pose。
2. 平移動畫只保留 root／hips 必要的位移，明確區分 root motion 與原地動作。四肢使用本角色 rest offsets，不能複製來源 translation 把短腿拉成長腿。
3. 依目標腿長、步速與步頻調整步幅，再重解手足 IK 及接觸。接觸區間要檢查中間幀、腳滑、腳掌離地、膝肘扭轉，不能只修少數關鍵幀。
4. 坐下以實際椅面、髖部與足底位置適配；指定應用姿勢依道具接觸點解算。騎車的踏板／車把與騎馬的鞍座／腳鐙／韁繩是不同接觸關係，須分開適配、命名及驗收。
5. 每位至少交付並檢查待機、走路、轉身、坐下，以及指定應用姿勢的實際片段；動作與表情皆須在匯出後 GLB 及使用場景中看圖驗收。

V110 原有 bind／rest 假設與 animation accessor 搬運方式不適用於這兩位新比例。保留舊動作來源供研究，但不可直接接上新骨架就宣稱重定向完成；也不為迎合固定骨數而刪除需要的骨頭。

## 7. 從灰模進入表情與服裝

### 表情的來源順序

本階段只有原生眼睛，採 closed-mouth 審查；牙齒、舌頭與 FaceUnits 的逐角色適配尚未完成。進入表情階段時，從完整參數母檔建立新候選：

1. 在本適配器完整 **19,158 頂點、含 helper** 的身體上加入所需 FaceUnits／表情來源，保留精確來源及雜湊。
2. 讓眼睛、眼瞼相關部件、牙齒、舌頭及其他附屬物依該角色的形態與表情重新 fit／傳遞變形，檢查權重和位置。
3. 保留完整參數母檔，再在交付副本完成 target／child 處理後移除 helper。不能先刪成 13,380 頂點，再用依賴完整來源索引的 FaceUnits 程式補表情。
4. 匯出後重新載入，確認 morph 的實際二進位位移與需要的法線資料，再看閉眼、嘴唇接觸、笑容、說話及混合表情是否自然、是否仍維持本角色身份。

不同臉型的表情不能只共用相同數值就當作完成。表情鍵名字、數量或非零位移都不保證自然度；不要搬舊模型的 morph accessor 取代新拓樸與新臉型的適配。

### 每個身形獨立適配服裝與鞋

優先採用授權清楚、可修改及隨專案交付的基底、髮型、服裝與鞋子，保留可編輯母檔、原始貼圖與來源。每件服裝須對各角色重新量測、fit、修改輪廓與厚度、調整權重；鞋子的鞋楦、足底與踝部需隨足型和步態重做適配。

胸口與領口是明確的品質關卡。靜態及動態至少檢查胸部輪廓、領口貼合、腋下拉扯、袖口、腰臀、膝部與鞋面，包含鬆量、布面方向、接縫、厚度、法線、陰影及自然度。沒有穿模只是一項必要條件。保留完整人體，不以大面積刪除胸、腋或腰臀遮掩不合身，也不把同一尺寸硬套所有人。

V110 已知胸口問題仍需看實際修正來源，V111 尚未取得可核對的修正檔；包內舊 PASS 不能解除這個關卡。若之後製作兒童或青少年，另採適齡基底與日常服裝，建立相符的頭身、軀幹與四肢比例，不縮小成人充當兒童。

## 8. 版本保存與跨地圖取用

儲存庫保存程式、來源鎖、角色設定、資產索引、驗收紀錄與適量 QA 小圖。大型 GLB、參數／clean 母檔、完整原始素材及原尺寸貼圖採版本化 ZIP 分包交付；不為縮小 ZIP 刪除可編輯母檔。

每個分包索引至少記錄 **精確檔名、實際 byte 大小、SHA-256、包含的 asset ID／版本、對應來源 commit 與程式／設定雜湊、授權證據、交付位置及可用範圍**。先按實際檔案計算，再寫索引；不得填範例值或假設暫時下載 URL 是永久來源。大檔封存不等同發布公開 Release，目前並無本工作室的公開 Release。

本分支 Actions artifact 保留 **30 天**，只作執行證據與暫時下載；它不是永久素材保存位置。需要完整交接時，依已確認的交付位置保存同版分包與索引，並核對還原後的雜湊。參數母檔、clean 母檔及 GLB 要能由同一版本索引對回。

地圖整合使用 `asset_id + version + SHA-256` 明確鎖定，為地圖自己的引用建立版本記錄。`profiles.json` 的新版本、外觀 tag 或較新的檔名，都不能自動替換舊地圖角色；不使用浮動 `latest` 或共用可覆寫檔名。升級先在獨立整合候選檢查比例、材質、動畫接觸及遊戲呈現，再依既有核准流程更新引用。

## 9. 下一位 AI 的接續入口

先盤點工作分支、未提交修改、正在執行的 build／render，以及既有產物目錄；已保存的灰模與舊人物參考都要保留。依序閱讀本文件、來源採用紀錄、reference lock、profiles、本版審查紀錄與兩位的實際 `report.json`。

下一個具體關卡是確認 D03／D06 的同尺度比例、D06 成熟感與後枕頸銜接、兩人的嘴唇輪廓。先修仍可見的問題並保存新版本的真實比較圖，再進入服裝、鞋、髮、表情及動作。任何新增內容都不能讓尚未解除的缺陷從報告中消失。

讀不到交接包、母檔或最新修正時，列出確切缺少的檔案與影響；不要自行退回 V103、舊候選或粗糙模型。提交時更新實際結果、分包索引與已知限制，保持 Draft PR 的可審查性，不自動合併、不改公開／私人設定，也不把規劃中的完整遊戲能力寫成已完成。
