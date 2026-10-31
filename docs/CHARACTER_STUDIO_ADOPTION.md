# 多樣化人物工作室：來源承接與保留界線

目前為 `01-gray-identity`，版本由 [profiles.json](../assets/characters/studio/profiles.json) 管理。D03、D06 是新的灰模身份候選；**未通過美術驗收、尚非可投入遊戲的完整人物**。既有角色保留原版本，不以新候選覆寫。

來源 commit、交接包大小／SHA-256、既有八角色 GLB／母檔雜湊，見 [reference_lock.json](../assets/characters/studio/reference_lock.json)。此鎖定檔記錄查核時的來源，不能使用浮動分支名稱替代精確版本。

## 1. 比較的來源與採用決定

| 來源 | 鎖定版本 | 查核結論與本輪決定 |
|---|---|---|
| `main` | [`f088f0e584764b3fd37dc1bc0670df99313bec41`](https://github.com/aitest-ai/3dcodeverse-lab/tree/f088f0e584764b3fd37dc1bc0670df99313bec41) | 作為獨立工作分支起點，保留既有工程。`main` 未收錄所有人物候選，不能因此認為既有角色不存在。 |
| V29 八角色參考 | [`0cef2282394b911e61cb3cde169f31be0034af95`](https://github.com/aitest-ai/3dcodeverse-lab/blob/0cef2282394b911e61cb3cde169f31be0034af95/docs/TAIWAN_CHARACTERS_V29_ELDER_FACE_HAIR.md) | 八人是混合版本候選，不是八人同時完成 V29 重建；保留逐角色版本／GLB／母檔 hash。採用原生 MPFB 形態與局部 target 的設計流程，由新腳本重新實作；未複製舊人物幾何。 |
| V30 最初失敗快照 | [`f5c006cfb5c7cd7b54e35d056d6a33aba8bb23e4`](https://github.com/aitest-ai/3dcodeverse-lab/tree/f5c006cfb5c7cd7b54e35d056d6a33aba8bb23e4) | 本輪初次盤點的繞頸候選，[run 41196562272](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41196562272) 因未解析支撐射線而 failure。保留歷史，不能再寫成最新狀態，也不能當成成功產物。 |
| V30 最新候選 | 文件 HEAD [`11cae1df15367cb5a41bdb6b3dc50d61fcc8e146`][v30]；實際建模 [`293b92376c55b5e330e2aac7497055895f035921`](https://github.com/aitest-ai/3dcodeverse-lab/commit/293b92376c55b5e330e2aac7497055895f035921) | 已改為單肩毛巾，對應 [run 41197768336](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41197768336) success；PR #49 仍 Draft、未合併，整體角色美術未通過。保留改良參考，未移植至 D03／D06、不替換八角色 V29 保護基準，也不是 V111 胸口修正。 |
| 基隆河 V110 | 使用者提供的三個完整交接 ZIP，逐包 SHA 鎖定 | 承接來源可追溯、完整解析度保存、母檔冷讀、匯出 GLB 重載檢查的原則。**胸口造型仍有已知問題，包內舊 PASS 不作為本輪美術驗收。** 未移植 V110 服裝、表情、動畫或整張地圖。 |
| 基隆河 V111 | 尚未取得可核對的檔案或 commit | 使用者告知正在修胸口；列為待接收來源，不能宣稱修正已採用。V103 不作替代。 |

未整條合併舊人物或地圖分支。V29／V30 的角色與未合併改良以固定來源保留，後續需要時逐項評估，不能因這一階段未移植而刪除。

### V30 最新快照與建模證據分欄

於 **2026-10-31 12:12:09 UTC** 唯讀核對 GitHub：`main` 仍為 `f088f0e`，V30 比原鎖定 `f5c006c` 前進三個 commit。`bb4f9d7` 先加入真正鄰近表面支撐以補回水平射線未命中，對應 run `41196904855` 結構成功，但來源文件明列繞頸造型仍因擠皺被拒收；`293b923` 改採單肩設計；`11cae1d` 只補交付與限制文件。[V30 固定版本說明][v30]

| 欄位 | 本次核對值 |
|---|---|
| 分支／PR | `feat/taiwan-v30-shui-towel-drape`／[PR #49](https://github.com/aitest-ai/3dcodeverse-lab/pull/49)，Draft、open、未合併；base 為 V29 分支 |
| 最新文件 HEAD | `11cae1df15367cb5a41bdb6b3dc50d61fcc8e146` |
| 實際建模 commit | `293b92376c55b5e330e2aac7497055895f035921` |
| 工作流程 | `41197768336`，API 確認 `completed / success`，11:45:12 UTC 完成 |
| Artifact | `13040584065`，`taiwan-v30-shui-draped-towel-PILOT`，40,394,203 bytes；查核時未過期 |
| Artifact API digest | `sha256:b9bc1d50c3b00add4d756cca1fd61ffc771cbf759d68c0c62efa06440eb86060` |
| 本輪查核範圍 | PR／commit／差異／Actions／artifact metadata；**沒有下載或重新 CRC、雜湊計算、渲染該 V30 artifact** |

API digest 來自 [Actions artifacts metadata](https://api.github.com/repos/aitest-ai/3dcodeverse-lab/actions/runs/41197768336/artifacts)，不可寫成這次工作室已親自驗完 ZIP。`run.pull_requests[].head.sha` 會反映目前 PR HEAD；實際建模版本須看 `run.head_sha` 與 `artifact.workflow_run.head_sha`。最新文件提交不在 V30 workflow 的程式路徑篩選內，沒有因此再執行建模。

相對 `f5c006c`，只有 `scripts/taiwan_v30/draped_towel.py`（+47／−56）及新文件 `docs/TAIWAN_CHARACTERS_V30_TOWEL_DRAPE.md`（77 行）改變；沒有以這次遠端候選更新替換下列八角色的版本或雜湊。

### 八角色保留版本

| ID | 角色 | 版本 |
|---|---|---|
| `you` | 主角 | V26 |
| `jie` | 外送員阿杰 | V26 |
| `boss` | 老闆娘 | V25 |
| `uncle` | 阿財叔 | V24 |
| `bro` | 隔壁攤大哥 | V27 |
| `cop` | 警察大哥 | V28 |
| `oldman` | 騎樓阿伯 | V29 |
| `shui` | 阿水伯 | V29 |

保留包 `taiwan_v29_eight_character_current_bundle.zip` 已通過 CRC，114 項 manifest 核對無差異。既有短姿態／壓力片段不等於已完成待機、走路、轉身、坐下起身；保留不代表本輪重新通過動作或美術驗收。

## 2. 目前真正承接到程式的部分

[build_gray.py](../scripts/character_studio/build_gray.py) 重新實作原生建模與檢查流程。下表的「已實作」指程式具備該路徑；特定產物是否成功，仍須讀取該版本的 `report.json`、模型與實際渲染。

| 項目 | 本輪狀態 |
|---|---|
| 獨立形態 | D03、D06 分別套用 MPFB macro、軀幹／四肢與臉部局部 target；完成形態後才適配骨架，再校準實際米制身高。不是讀入舊人物做等比例變形。 |
| 原生來源保存 | 保留參數化 `.blend` 與清理後可編輯 `.blend`；記錄使用的 target、身體部件來源及 hash。灰模不用皮膚法線，不縮減來源貼圖尺寸。 |
| 圖像真正解碼 | `build_gray.py` 保存原始圖像位元組、尺寸與 hash，讀取像素後打包，再從冷讀母檔核對 packed bytes；承接 V20／V28 的 lazy-image 修正經驗，沒有承接其 512px 上限。 |
| 身體完整性 | 交付副本移除來源 helper 幾何；此操作不等於刪除人體來遮住衣服穿模。本階段沒有衣服或人體遮罩。 |
| 原始部件適配 | 獨立形態完成後，以已鎖來源的官方眼球 MHCLO 重新擬合；保留 helper 到適配完成。本階段閉嘴審查沒有虛構牙舌或表情配件。 |
| 明確權重處理 | `normalize_weights()` 對原生新身體與眼球保留最高 4 個 deform influences、正規化，並記錄截斷前捨棄權重。細分後部分點又產生超過 4 個 influence，實際匯出日誌記錄由 glTF exporter 取最高 4 個並正規化；動態變形尚未驗收，不能宣稱完全未改權重。 |
| 共用語意 | 輸出骨架語意、各角色實際骨長與 rest matrix，保留額外骨頭。**尚未完成動畫重定向**，不得複製舊人物 bind／translation 當作適配。 |
| 匯出後重載 | 刪除場景中的來源 mesh／armature，再載入實際輸出 GLB、核對 bounds，從重載模型輸出全身與無髮臉部圖。 |
| 母檔冷讀 | 另行重新開啟儲存的 `.blend`，核對原生身體頂點數；執行結果留在報告，不以匯出命令成功代替冷讀成功。 |
| 獨立 GLB 結構解析 | [inspect_glb.py](../scripts/character_studio/inspect_glb.py) 不匯入 Blender／建模程式，解析容器、accessor stride／sparse、有限數值與資產結構；不是完整 Khronos validator，也未完成舊流程的動態射線或表情自然度驗收。 |
| 完整資產載入 | [人物檢視器](../examples/character-studio/README.md) 獨立實作真實位元組進度、SHA-256、失敗重試、兩位完成後共同顯示及持續量測；原則參考 V110，未搬入地圖邏輯、舊模型或舊動畫。 |
| 視覺驗收 | 報告固定保留 `art_approved: false`、`game_ready: false`。數值或結構檢查通過不能自動轉成美術通過。 |

本輪沒有移植舊服裝、鞋、髮、表情或動畫。獨立檢視器已實作原 GLB 的串流進度、SHA 核對與重試；全解析度皮膚 PBR、服裝適配與動態自然度仍屬後續工作，不能把參考文件中的能力寫成已實作。

### 第一階段角色設定

| 候選 | 年齡設計／身高 | 主要身份與比例差異 |
|---|---|---|
| D03 高瘦青年 | 24 歲／1.86 m | 較長腿與前臂、纖細軀幹、長橢圓臉與較窄下顎。 |
| D06 較豐滿高齡女性 | 73 歲／1.53 m | 較短腿與相對較長軀幹，分區調整上臂、腹部、腰臀與大腿體積；較短寬臉及年齡相關軟組織形態。 |

年齡與身形是虛構人物的設計目標，不是人口測量標準或年齡推定。灰模檢查骨相、軟組織與比例；皮膚、髮型與自然姿態仍須後續共同建立年齡感。兩人全身使用同一 2.2 m 正交尺度，臉部使用同一 0.38 m 正交尺度；不得為了看起來差異大而分別縮放圖片。

## 3. 未合併、仍須保留的改良參考

下列方法與造型保留在固定 V29 來源、既有八人包及新增 V30 參考中；**不因沒有合併 main 而重做或丟棄，也不代表已移植至 D03／D06**。來源文件記錄的結果是該版本的驗收範圍，本次沒有重新渲染這些既有人物。可重用方法與不可直接套用的特定角色數值分開記錄。

| 固定來源 | 重要改良與需保存內容 | 新人物採用界線 |
|---|---|---|
| [V20 原生整合][v20] | 原生人體與服裝分開，非目標幾何／UV／權重／表情保全；packed bytes 與真實像素解碼；來源與實際 GLB 分別回讀。 | 來源保存、解碼與回讀原則已重新實作；外送員褲腰修整、原壓力動作及 512px 縮圖未移植。 |
| [V21 來源褲腰][v21]、[V22 同側診斷][v22]、[V23 局部內襯][v23] | 在原始服裝上有界修整，排除誤打手臂的射線；用同側腰圈高度修正錯側量測，保留 legacy 數字；V23 只修特定七個內側布邊點並保存外片。 | 保留診斷方法與可編輯修正版。新身形須重查拓樸與可見缺陷，不套舊頂點 ID／位移，不把量測定義更正冒稱新增幾何改善；人體沒有因此刪除。 |
| [V24 皮帶穿搭][v24] | 獨立皮帶與扣環，從原褲裝三角形轉移正規化權重；扣環採共同權重避免像布料折彎，配件可移除。 | 保留阿財叔 V24 成果與配件方法；新人物尚未配皮帶，需對新腰臀與動作重做適配。 |
| [V25 圍裙／頭巾][v25] | 以真正肩部支撐及依權重排除袖子的表面搜尋，修正錯誤腰帶延伸到手腕；圍裙、口袋、繫帶與頭巾為獨立配件。 | 保留原候選和拒收證據，不直接套同尺寸。原裙片偏硬、側背方、頭巾簡化等問題仍要精修；骨架服裝不等於物理布料。 |
| [V26 主角／外送員][v26] | 使用 Blender 求值後的真正手臂表面重建袖子包覆，肩帶有界搜尋實際軀幹；帽領、識別證、頭盔、口罩與背包依 `accessory_group` 分組。 | 保留合法服裝衍生關係、群組與新袖子權重方法，未移植造型。帽領／袖縫、後腰小穿插、安全帽比例、扁平硬折肩帶與口罩表情仍有限制，穿搭不同不等於臉不同。 |
| [V27 原生四角色][v27] | 從不同 MPFB macro／臉部 target 建人，官方 MHCLO 適配、實體 helper 清理及顯式權重整理；官方 Faceunits 與牙／舌／睫毛插值依賴、非零 Morph 和左右組合別名分開說明。 | 原生基底流程已獨立採用；舊四人 10 鍵、新四人 14 鍵及其配件、表情／動畫未移植。保留語意與依賴參考，不把組合別名當新增獨立表情或完整 ARKit。 |
| [V28 鞋／衣襬／法線][v28] | 警察改用依實際腳形製作的包覆鞋與重心權重；只修目標制服衣襬，保留原褲；長者細節使用可真正寫入 GLB 的標準 tangent-space normal。 | 保留警察 V28 修正版及標準材質方法，未移植鞋衣或皮膚圖。鞋頭／光澤和下襬仍有問題；程式選到 0 個褲管修點不能稱褲管已修，皺紋圖不能代替骨相老化。 |
| [V29 臉形／髮紋][v29] | 眼下、臉頰、下顎有界位移並保護眼瞼接觸與鼻嘴；同一位移加入 Basis 與各既有表情鍵，保留相對差值；髮頂接觸檢查避免壓入頭皮；以合法髮圖的不規則層次取代被拒收的週期壓紋並匯出標準法線。 | 保留兩位長者 V29 幾何／來源與方法。D03／D06 由新 target profile 建形，不複製舊臉或髮；既有長者仍年輕、整塊髮型感及皮膚／眼周問題未全解決。 |
| [V30 單肩毛巾][v30] | 改用前後各一垂端的連續單肩布，整列截面支撐而非逐點拉寬，保留配件權重、原花衫幾何／色圖及被拒收繞頸版本的證據。 | 僅保留最新候選參考；未下載本次 artifact、未移植新角色、不替換八角色保護基準。CI success 不構成美術通過。 |

### V30 精確行為與仍待修的造型

`scripts/taiwan_v30/draped_towel.py::build(body, shirt, rig, out)` 相對原 `f5c006c`，從繞頸逐點貼合改為左單肩前後垂端：固定 X 向橫截面保留約 7.4–8.0 cm 寬度，每列 15 條支撐射線對人體／原花衫求整列外移量，要求至少 3 條命中、調整不超過 6 cm，經保守平滑後整列貼合；保留 2.2 mm 厚度、最多 4 個正規化骨架權重及未命中／位移紀錄。這是造型與貼合方法改變，不是只放寬失敗條件。[固定建模程式](https://github.com/aitest-ai/3dcodeverse-lab/blob/293b92376c55b5e330e2aac7497055895f035921/scripts/taiwan_v30/draped_towel.py)

來源文件仍列明：兩端偏平直、長方形，摺痕與肩部轉折有雕塑感；原花衫偏硬版型、大花紋與臉髮年齡感未全面精修。它是來源造型加骨架蒙皮，不會自行甩動／滑落。指定短片段的局部外側檢查不涵蓋全面自交，也不保證任意新動作零穿模；多個時間點只是同一片段的取樣，不能解讀成同樣數量的不同動作。V30 自身沿用 0–2.5 秒片段、來源與回讀各 11 個時間點。[V30 範圍與限制][v30]

**來源沒有正式排定後續修整順序。** 若後續返回 V30，可依已知缺陷建議先修毛巾端部、摺痕與肩部轉折自然度，再查指定動作下的接縫、穿模、自交與蒙皮，然後處理原花衫版型／花紋及臉髮年齡感。這是本工作室的建議，不是來源已核准的清單，也不改變本輪先完成 D03／D06 灰模品質的順序。

## 4. 明確不繼承的舊限制與假設

- **512px／6MB 上限：** 舊版為當時交付採用的尺寸，不是新人物品質規範。不縮減合法原始貼圖或刪除母檔以符合 ZIP 大小；新輕量版本須有持續量測依據、由同一母檔衍生並保持外觀。V110 的較高解析度來源也不等於舊 512px 素材已自動恢復細節。
- **刪人體／遮罩掩蓋不合身：** helper 清理與真正人體分開；新衣鞋依胸口、腋下、腰臀、膝蓋、袖口及腳形重新適配。既有局部修正版保留，不把大面積人體遮罩搬進新身形。
- **舊 bind／動畫陣列搬運：** 不複製原 animation accessor、rest／inverse-bind 或骨頭 translation 假裝完成重定向。共用語意保留各人骨長、比例與額外骨頭；53 骨、10／14 表情鍵不是全庫硬性數量。騎車與騎馬分開適配，短姿態壓力片段不能代替完整待機、走路、轉身與坐下起身。
- **特定角色修整值與未限定的 PASS：** 不直接套用舊頂點 ID、固定腋下／腰部位移、取樣高度或服裝尺寸。零命中不等於所有表面無穿模，CI success 不等於自然好看，圖庫版型不等於互動 3D，軟體 GL 幀率不等於 Android 真機結論。

## 5. V110 已取得的材料與已知限制

已完整取得並核對：

- `基隆河_V110_Polo丹寧與河岸互動.zip`
- `基隆河_V110_Blender可編輯角色.zip`
- `基隆河_V110_完整法線與服裝來源.zip`

三包 CRC 通過；兩個 authoring 分包合併後，兩份 SHA 清單各核對 54 項，均無缺少或不符；14 個唯一貼圖通過檢查，21 個所選原始來源檔可精確還原。取得交接包不代表已取得原作者所有製作腳本。

來源保留 Polo 2048² base／OpenGL normal／roughness、丹寧 2048² diffuse／AO 與 4096² normal、鞋 1024² diffuse。舊皮膚、髮、眉睫、眼牙舌仍有 512² 來源；不得宣稱所有舊材質已恢復高解析度。互動版 1024 法線是另一份衍生品，沒有持續真機效能證據支持把它當成新角色預設壓圖規則。

來源 `.mhclo` 明確標記 Namuhekam Polo、MakeHuman `male_casualsuit04`、`shoes05` 為 CC0；授權文字與來源仍需隨新的資產分包保存。V110 所選 21 個原始檔不含 system eyes／teeth 的 MHCLO；新灰模部件須使用自己的已核對來源，不能說是從 V110 原始包完整承接。

下列做法不能直接沿用：

- **胸口驗收：** V110 已知輪廓問題尚未解除；腋下局部修整與無穿模不能代表胸口、領口、腰臀好看。
- **固定骨架搬運：** V110 `export_runtime.py` 要求既有 rest pose 不變，再搬入 Idle／Walk／Cycle 的 animation accessor。它不是適合新骨長的重定向器；53 骨、10 表情鍵也不是全庫硬性數量。
- **人體遮罩：** 不沿用既有 1,289 頂點丹寧覆蓋遮罩來遮住新身形的不合身；每個身形重新適配服裝、鞋與權重。
- **動作宣稱：** V110 僅有 Idle／Walk／Cycle，Idle 為靜態放鬆姿勢；沒有本次所需完整轉身、坐下與起身。騎車和騎馬後續分開適配。
- **效能推論：** 舊有離線圖、WebGL mock 或無 WebGL2 的錯誤介面，不能證明瀏覽器 GPU 品質或 Android 效能。

V111 尚缺：確切分支／commit、胸口修正母檔、對應 GLB／互動包、來源與材質異動、版本／SHA 清單，以及實際模型前後圖與姿勢驗證。查核時未在可取得的交接檔與候選分支中找到，這表示尚未取得，不能推論它不存在。

## 6. 下一位 AI 的交接規則

先讀本文件、reference lock、profiles 與該產物 `report.json`。先完成 D03／D06 同尺度全身及無髮臉部的實際模型檢視，修掉已知輪廓缺陷，再進入衣服、鞋、髮與表情。待機、走路、轉身、坐下起身逐項產出真實動畫證據；騎車、騎馬另外列版。

大型母檔、原始素材、衍生 GLB 與驗證圖採版本化分包；索引至少保留來源、授權、檔案大小、SHA、重建方式和保存位置。舊來源沒有公開永久下載 URL 時應明寫未提供，不能以暫時連結或未發布的 Release 冒充。地圖以明確 asset ID／版本／hash 取用；不可使用會互相覆寫的 `latest`。

離線 Blender 渲染、實際瀏覽器呈現及 Android 真機量測分別記錄環境與結果。只有相應產物的實測證據，才能把該項標成完成；本文件與來源 lock 本身不構成美術、動作或效能通過證明。

[v20]: https://github.com/aitest-ai/3dcodeverse-lab/blob/0cef2282394b911e61cb3cde169f31be0034af95/docs/TAIWAN_CHARACTERS_V20_SOURCE_INTEGRATION_QA.md
[v21]: https://github.com/aitest-ai/3dcodeverse-lab/blob/0cef2282394b911e61cb3cde169f31be0034af95/docs/TAIWAN_CHARACTERS_V21_UNCLE_SOURCE_QA.md
[v22]: https://github.com/aitest-ai/3dcodeverse-lab/blob/0cef2282394b911e61cb3cde169f31be0034af95/docs/TAIWAN_CHARACTERS_V22_LOCAL_FLY_QA.md
[v23]: https://github.com/aitest-ai/3dcodeverse-lab/blob/0cef2282394b911e61cb3cde169f31be0034af95/docs/TAIWAN_CHARACTERS_V23_INNER_LIP_QA.md
[v24]: https://github.com/aitest-ai/3dcodeverse-lab/blob/0cef2282394b911e61cb3cde169f31be0034af95/docs/TAIWAN_CHARACTERS_V24_BELT_STYLING.md
[v25]: https://github.com/aitest-ai/3dcodeverse-lab/blob/0cef2282394b911e61cb3cde169f31be0034af95/docs/TAIWAN_CHARACTERS_V25_BOSS_APRON_QA.md
[v26]: https://github.com/aitest-ai/3dcodeverse-lab/blob/0cef2282394b911e61cb3cde169f31be0034af95/docs/TAIWAN_CHARACTERS_V26_HERO_COURIER_QA.md
[v27]: https://github.com/aitest-ai/3dcodeverse-lab/blob/0cef2282394b911e61cb3cde169f31be0034af95/docs/TAIWAN_CHARACTERS_V27_MISSING_FOUR_QA.md
[v28]: https://github.com/aitest-ai/3dcodeverse-lab/blob/0cef2282394b911e61cb3cde169f31be0034af95/docs/TAIWAN_CHARACTERS_V28_QUALITY_REVIEW.md
[v29]: https://github.com/aitest-ai/3dcodeverse-lab/blob/0cef2282394b911e61cb3cde169f31be0034af95/docs/TAIWAN_CHARACTERS_V29_ELDER_FACE_HAIR.md
[v30]: https://github.com/aitest-ai/3dcodeverse-lab/blob/11cae1df15367cb5a41bdb6b3dc50d61fcc8e146/docs/TAIWAN_CHARACTERS_V30_TOWEL_DRAPE.md
