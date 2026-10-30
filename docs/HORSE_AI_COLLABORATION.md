# 跨 AI 馬匹模型資產庫｜Horse Asset Hub

這是 **ChatGPT、Claude、Codex、Copilot、Cursor 與其他能操作 GitHub 的 AI 共用的操作規範**。任何 AI 只要讀到此頁，應知道「我們已有兩匹真正可用的賽馬模型」，如何取得、如何推出新款馬，以及如何回拉最新已核准資產。

**唯一可信入口**：`assets/horses/registry.json`（機器可讀）；`AGENTS.md` 是儲存庫的 AI 規範。開發分支：`feat/racing-horse-cc0-pipeline`，[PR #13](https://github.com/aitest-ai/3dcodeverse-lab/pull/13)。**PR 未合併 main 前，請在 GitHub 讀取這個分支；不要錯讀 main 以為沒有馬。**

## 一、目前已完成的資產

| 資產 ID | 版本 | 內容 | 授權 | 驗證狀態 |
| --- | --- | --- | --- | --- |
| `horse-brown` | 2.3.0 | 原版 Quaternius 深棕馬，並加入 UV/PBR、鬃毛纖維 | Quaternius CC0；程序材質原創 | Blender 5.2／Three.js Chromium 真正通過 |
| `horse-white` | 2.3.0 | 原版 Quaternius 白馬，並加入 UV/PBR、鬃毛纖維 | Quaternius CC0；程序材質原創 | Blender 5.2／Three.js Chromium 真正通過 |

**兩匹都是風格化遊戲馬，不是寫實賽馬高模。** 每匹約有 50 根骨頭、13 段原始動畫，包含 `Gallop`、`Walk`、`Idle`，GLB 含影像貼圖。來源與 SHA-256、動畫清單、版本都在 `assets/horses/registry.json`。

模型正式下載集中至本儲存庫 [GitHub Releases — horses-v2.3.0](https://github.com/aitest-ai/3dcodeverse-lab/releases/tag/horses-v2.3.0)。舊 Actions 暫存模型有約 14 日有效期，不應當永久資產庫。

## 二、任何 AI 如何「Pull 回來自己用」

必須先有此儲存庫的讀取權限。Private GitHub Repo 需要使用者授權；其他 AI 不能只靠網址繞過私有庫權限。

**方式 A：最快、推薦（需要 GitHub CLI `gh`，已登入）**

```bash
gh auth status
gh repo clone aitest-ai/3dcodeverse-lab
cd 3dcodeverse-lab
git checkout feat/racing-horse-cc0-pipeline
python3 scripts/horses/horse_assets.py list
python3 scripts/horses/horse_assets.py pull horse-brown --dest ./public/models
python3 scripts/horses/horse_assets.py pull horse-white --dest ./public/models
```

這個程式優先從 Releases 下載，並驗證 SHA-256、檔案大小、GLB 2.0、50 骨及 13 段動畫，避免接到錯誤版本。Releases 若尚未存在，才嘗試 **已驗證但會過期** 的 Actions Artifact 作備援。

若要使用 Blender 原始檔與貼圖：

```bash
gh release download horses-v2.3.0 -R aitest-ai/3dcodeverse-lab -p 'horse-brown-v2.3.zip' -D ./incoming-horses
```

解壓後有 `.blend`、原創 `coat_*.png`、真實多角度 PNG 與授權說明。要拿整合後的 HTML 專案，則請看 [V2.3 WebGL QA](RACING_HORSE_V23_PBR_BROWSER_QA.md) 或 GitHub Actions 正式測試包。

**方式 B：只有 GitHub Connector，沒有 CLI 的 AI**

讀 `AGENTS.md` → `assets/horses/registry.json`，核對 `id` 和 `model.sha256`；有權限的連接器或 Releases API 下載 `release_file`。如果連接器只能讀 Repo 文字、不能下載 Release 二進位檔，應明確說明缺少能力，使用者可自行下載 ZIP 提供，不得假稱已取得。

## 三、其他 AI 怎麼「Push 新馬」到同一個庫

例如其他 AI 想做一匹 `horse-palomino`，不要覆蓋 `horse-brown` 或 `horse-white`。應建立**新 ID＋新版本**，再發 PR 等核准。

1. 先讀 `AGENTS.md`、`assets/horses/registry.json`、本文件。以 `feat/horse-palomino-v1` 建立新分支。
2. 可以從已核准的 CC0 馬衍生不同毛色、花紋、馬具，也可以合法匯入另一款馬體；**不得假稱已解決真實肌肉／步態**。
3. 先產出真 Blender `.blend`、有蒙皮且可用的 `.glb`、正側背預覽 PNG、來源授權、`report.json`、`validation.json`。若用既有馬的骨架，確保有 50 bones、13 clips；若是不同 rig，需完整驗證 `Gallop`、`Walk`、`Idle` 的實際動作。
4. 二進位檔先上傳 GitHub Actions Artifacts，**不要把大檔直接 push 進一般 Git 歷史**。把模板 `assets/horses/examples/submission.example.json` 複製到 `assets/horses/submissions/horse-palomino.json`，填入真實 SHA-256、作者、授權、來源 URL、CI run ID／artifact name、各種動畫及圖片。
5. 執行 `python3 scripts/horses/validate_horse_submission.py ... --glb 路徑`，確認 hash／骨架／動畫。所有結構檢查通過仍須看真正 Blender 多視角圖片與 WebGL。
6. `git push -u origin feat/horse-palomino-v1`，`gh pr create --base feat/racing-horse-cc0-pipeline`（**PR #13 合併後改為 base main**）。在 PR 描述中附來源授權、已驗證 Actions URL、視覺比較、缺陷、版本。
7. 核准後將新馬加入 `assets/horses/registry.json`，給新 `id` 和 `version`，以 GitHub Release 新 tag 分發。**絕不修改或覆寫已核准版本的 Release 檔案**；舊使用者可以重現舊馬。
8. 其他 AI 更新 Git 分支，再執行 `horse_assets.py list/pull` 即可發現新馬與下載。GitHub Release Tag 永遠指到固定版本，不靠對話記憶。

未建立 `assets/horses/submissions` 目錄時，可先加一個 `.json` 檔，GitHub 會自動形成資料夾。

## 四、發版規則與安全

- **正式使用者資產來源**：GitHub Releases（持久性）。Actions Artifact 僅測試快取，會到期。
- **編輯中的 AI 產物**：分支／PR。沒通過審查前不出現在正式馬資產名錄。
- **版本管理**：ID 不重用，例如 `horse-palomino`；每次有破壞性變更請升 `2.3.0 → 2.4.0` 或 `3.0.0`。原版不得被新內容直接蓋掉。
- **授權**：Quaternius 本批是 CC0，可重散發；若是 CC BY 模型，保留署名與變更說明；未授權、CC BY-NC、限制轉售原始模型的來源，禁止盲目發布到公開資產包。
- **私有性**：私有 Repo 的 Release 也需要授權。不要把 GitHub PAT 放到程式或 Prompt。
- **驗收界線**：合法來源、GLB 結構、動畫 clip 數、骨架權重不等於真實物理步態、解剖或產品品質。
- **GitHub 事件**：新的手動 `workflow_dispatch` 要出現在 main 預設分支才可由 Actions UI 點選，分支上的開發中 workflow 不一定能手動啟動。請先通過 PR 合併。參見 GitHub Actions 官方規範。

## 五、可直接貼給任何其他 AI 的交接指令

> 你現在接手我的 3D 賽馬角色資產工作。GitHub 私有儲存庫為 `aitest-ai/3dcodeverse-lab`，開發中的馬匹資料在分支 `feat/racing-horse-cc0-pipeline`。請先閱讀儲存庫根目錄 `AGENTS.md`、`docs/HORSE_AI_COLLABORATION.md` 與機器可讀 `assets/horses/registry.json`。現成 `horse-brown`／`horse-white` v2.3.0 各有 50 骨、13 動畫、GLB/PBR，請優先透過 `scripts/horses/horse_assets.py pull` 或 Release 正式標籤 `horses-v2.3.0` 取得，核對 SHA-256，不要重造或聲稱模型不存在。如需新增馬款，請保留舊版，建立新的 asset ID、Blender GLB＋BLEND、授權來源、3 視角圖片與驗證 JSON，在獨立 Git 分支提交 PR。新資產未經授權及品質審查，不可擅自覆蓋已核准版。請把完成的資產發佈為新版本的 GitHub Release，並更新 registry，讓其他 AI 和遊戲專案能 pull 使用。沒有 GitHub 權限或二進位下載能力，請先說明，不可假稱已經 push 或 pull。
