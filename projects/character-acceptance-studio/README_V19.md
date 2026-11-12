# Character Studio 0.19.0 — 袖口試作診斷與隔離驗收

本階段交付可操作的雙身形交叉診斷場。**沒有新的角色版本通過**：固定使用 V18 的 Vivi 0.6.0、Vita 0.5.0；袖口細分試作在兩者都新增非透明表面交叉，隔離保存，不進入可取用角色目錄。肩腋幾何、原有皮膚交叉與動作自然度仍待修正。既有 20 款人物／動物庫保留；這一輪沒有新增外部模型。

## 使用

把同一次交付的 Runtime、Sources ZIP 解壓至同一 `Character_Studio_0.19.0` 資料夾。Runtime 足以用瀏覽器觀察；母檔與原始 VRM 需 Sources。

```sh
python START_STUDIO_V19.py --open
```

網址 http://localhost:8819/web-v19/ ，Windows 可執行 `START_WINDOWS_V19.cmd`。

1. 選 Vivi 或 Vita。預設只載入 SHA 固定的 V18 模型，保留原比例、完整衣鞋與原解析度貼圖。
2. 在「袖口交叉診斷」選取動作／時間書籤，按「跳到採樣姿勢」。A 為 V18；B 清楚標示「已拒收」。兩者使用同一鏡位與相位。
3. 橘色線框標示袖子三角形，紅色線框標示相交表面。標記會穿透遮擋物，**不是渲染缺陷的輪廓**；關閉「標記三角形」並旋轉鏡位觀察真實外觀。逐格移開採樣時間時，標記與該姿勢的結果會隱藏，避免把舊結果套到新姿勢。
4. 七段動作 Idle、Walk、Run、Start、Stop、TurnLeft、TurnRight 可播放、暫停、調速、60fps 逐格與循環。正側後、肩腋、雙手、雙肘與腳掌近景保留。可下載含模型 SHA、鏡位、採樣三角形和時間的觀察 JSON。
5. 取消「檢視已拒收袖口試作」回到 V18。試作只存在隔離證據索引，固定取用工具不接受試作 ID。

`evidence-v19/index.html` 含兩身形的正／側／後／左袖口 Walk 影片與近景。MP4 由實際瀏覽器 41 張姿勢畫面以 30fps 動畫時間編碼，不是即時效能錄影；原始 PNG 與每格快照保留在 `motion-frames/`、`motion-capture.json`。可在主介面自行即時操作與錄影。

## 結果與方法

V18 的細分試作改到了透明模板末端。本輪按實際袖子貼圖與各角色前臂範圍挑選面：Vivi 86 個源面、增加 154 個頂點；Vita 64 個源面、增加 128 個頂點。原 6648 個 Body 頂點、骨架、權重前綴、原 Run 修正、其他網格、七段動畫和所有原圖保持不變。邊中點以切平面估計曲率，單點位移上限 2.5mm；使用明確三角形切分，避免非平面四邊形自動三角化造成小翻片。

兩身形各 679 個姿勢，七段動作皆以 60Hz 檢查。測試比較變動袖口面對 Body 的交叉，映射至原始三角形配對，排除原本共享頂點的鄰面並消除正反重複。保留原始幾何交叉數；另沿實際交叉線以不超過 0.25 個原貼圖像素的間隔檢查兩側 alpha。這只區分透明模板表面和有貼圖支持的交叉，**不判斷攝影機遮蔽、不證明穿透深度或整個實體碰撞合格**。不涵蓋 Hair／Face 獨立網格、包含關係、布料厚度、所有連續時間、mipmap 或遊戲碰撞體。失敗明細與每段最嚴重採樣書籤見 `evidence-v19/surface-diagnostics.json`。

另做了新增頂點的線性蒙皮偏移補償數值實驗：Vivi 最大約 0.296mm、Vita 約 0.145mm。低秩分解可壓縮這個偏移，但保留圓滑輪廓後仍有交叉；沒有烘焙或接受補償模型。`docs/COMPENSATION_PROBE_V19.json` 是本次本機數值實驗，30Hz 交叉抽查，與主交付 60Hz 拒收試作分開，不是模型訓練成果。

## 母檔、來源與重建

- V18 固定模型與母檔：`inputs-v19/library-v18/vroid-{vivi,vita}-motion-review/{0.6.0,0.5.0}/`。ID、GLB、母檔與骨架設定的雜湊繼續使用 V18 實際 CI 交付。
- 已拒收試作：`experiments-v19/{vivi,vita}-rejected.blend`、`.glb`，以及 `mapping.json`、各自的 manifest。只供修正與重現失敗。
- 原始 VRM、原解析度貼圖與來源 Blender 保留於 `sources-v04/`、`library-v04/`。上游 `.vroid` 工程仍未取得；現有母檔為可編輯匯入版，不能稱為上游原工程。
- `docs/CUFF_SELECTION_V19.json` 記錄本輪人工稽核區域；每位角色仍使用自己的骨長、權重與 rest pose。共用的是診斷／細分方法，不能直接複製這些頂點 ID 到其他拓樸或動物。

Blender 5.2.3 LTS，CPU 背景執行，不需要 GPU、新帳戶或付費。完整包可離線重建；fresh checkout 的 bootstrap 需讀取固定 GitHub artifact。

```sh
python scripts/bootstrap_inputs_v19.py
blender -b -t 4 --python-exit-code 1 --python scripts/build_experiments_v19.py
blender -b -t 4 --python-exit-code 1 --python scripts/check_experiments_v19.py
python scripts/prepare_registry_v19.py
```

已有輸出時不覆寫；重新試作請設定 `STUDIO_V19_OUT=/new/experiment-folder`。這只重建隔離試作，不更新可取用模型。母檔可以編輯，但任意手動幾何／拓樸修改尚未提供通用匯出保證；本階段可重現的是版本化建構腳本與未修改母檔的冷開匯出。`check_experiments_v19.py` 驗證原母檔 GLB 位元一致，不能用它宣稱手動編輯已匯出。可選數值實驗：`blender -b -t 4 --python-exit-code 1 --python scripts/probe_compensation_v19.py`。

## 驗收分類

- 程式／結構：檢查來源 SHA、GLB 結構、原資料前綴、七段動畫、隔離目錄、錯誤處理與整包逐檔 SHA。通過不代表美術品質。
- Blender：冷開母檔、位元一致匯出、60Hz 幾何採樣已做；離線美術渲染未做。兩種袖口試作皆**失敗**。
- 瀏覽器：實際 Chromium／SwiftShader CPU 操作、七段播放、母檔表面比對、書籤、標記切換與失效、雜湊錯誤拒絕、390px 模擬視窗。完整結果以當次 `browser-checks.json` 為準。
- 手機真機、本版 Godot、人工美術驗收：**未測**。
- 肩腋實際幾何修復、全身比例與自然動作改善：**未完成**。沒有拿數值通過代替人眼驗收，也沒有升級其他地圖中的人物。

## 固定取用

```sh
python scripts/pin_surface_v19.py --id vroid-vivi-motion-review --version 0.6.0 --sha256 9f7388ffde3a23a4ace8ae28012058fcdfc4b6aadac286c95555848ac545939b --review-candidate --dest /new/isolated-review
```

仍只是隔離驗收候選。拒收試作沒有 catalog entry，不能以此工具取用。來源作者、授權及修改見 `THIRD_PARTY_V19.md`；固定輸入見 `docs/INPUTS_V19.json`。不修改 main、不合併 PR、不發布 Release／網站、不替換其他專案。下一步以這些已定位姿勢修整衣袖鬆量、皮膚與衣料間距，再處理肩腋幾何；通過雙身形驗收後才建立新角色版本。
