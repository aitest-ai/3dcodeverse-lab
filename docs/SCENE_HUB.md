# Scene Hub｜所有 AI 共用的 3D 場景交換中心

> 正式入口：[AGENTS.md](../AGENTS.md) → 本文件 → [`scripts/scene_hub.py`](../scripts/scene_hub.py) → [`scenes/catalog/`](../scenes/catalog/)。
> Repo: `https://github.com/aitest-ai/3dcodeverse-lab`

## 目的與界線

這個 Hub 不是 HY-World GPU 推論伺服器，也不是 Blender API、3DCodeVerse 官方工具或 ChatGPT 永久安裝的插件。它是多個 AI Agent、不同專案可以共用的 **Git + JSON 資產索引 + 可驗證複製工具**。

來源可以是：Blender 程式化建模、世界重建的 triangle mesh、HY-World 2.0 的 Gaussian splats、原創 PLY/GLB、Unity/Godot/Three.js 專案。**存放的是已取得、具授權的成果檔**，不是把模型權重提交 GitHub。

> 注意：`feat/hy-world2-format-bridge` 的 HY-World 匯入器及山湖漫遊示範仍在 [PR #20](https://github.com/aitest-ai/3dcodeverse-lab/pull/20)，直到合併為止都不能當作 `main` 已具備的正式功能。
>
> [山湖漫遊示範網站](https://hyworld2-mountain-river-demo.vercel.app/) 為**原創程序模型，不是 HY-World AI 推論結果或真實地形**。它也不是本 Hub 裡的 `demo-forest-island` 同一份模型。

## 目錄慣例

```text
AGENTS.md                         # 所有 AI 的協作規則
CLAUDE.md                         # Claude 入口
.github/copilot-instructions.md   # GitHub Copilot 入口
.cursor/rules/scene-hub.mdc       # Cursor 入口
skills/scene-exchange/SKILL.md    # 可給 AI Agent 主動閱讀的技能說明
scripts/scene_hub.py              # list / inspect / verify / pull / stage / push
scenes/catalog/<scene-id>.json    # 每個場景一份 manifest，避免集中索引衝突
scenes/assets/<scene-id>/*       # 小型資產，避免大型檔案直接放 Git
```

索引是 **每個場景一份 JSON**，不是所有 AI 同時改同一個 `registry.json`。這樣 AI A 新增基隆河、AI B 新增函館時比較不容易產生合併衝突。

## 其他 AI：首先列出可用場景

任何有 Git CLI + Python 3.10+ 的環境：

```bash
git clone https://github.com/aitest-ai/3dcodeverse-lab.git
cd 3dcodeverse-lab
python3 scripts/scene_hub.py list
python3 scripts/scene_hub.py inspect demo-forest-island --verify
python3 scripts/scene_hub.py verify --all
```

### 從另一個專案取得 scene（Pull）

已經 clone Hub 時：

```bash
python3 scripts/scene_hub.py pull demo-forest-island --output /path/to/your-game/public/models
```

如果你只有 Python 腳本，但目前工作在另一個專案，也可讓工具自動淺層 clone 官方 Repo：

```bash
python3 /path/to/scene_hub.py pull demo-forest-island \
  --repo https://github.com/aitest-ai/3dcodeverse-lab.git \
  --ref main \
  --output /path/to/your-game/public/models
```

它會複製模型到 `public/models/demo-forest-island/`，同時放入 `scene_manifest.json`，並逐檔驗證 SHA-256 與檔案大小。若已存在同名資料夾，會**拒絕覆寫**，請先備份、改目的地或明確管理版本。

**Pull 不等於已經通過美術、物理及真實地理驗證**。讀取 `review_status`、`source`、`license`、`asset_kind`，並確認權限適用於你目前使用的專案。

> 不要嘗試把 Gaussian Splatting `.ply` 用一般 `PLYLoader` 當作 triangle mesh。3DGS 建議透過 Spark 等 splat renderer 顯示，碰撞幾何另外建置；`.glb` 可用 GLTFLoader；真正有面的 `.ply` 可用 PLYLoader／Blender 處理。

## AI 製作新場景後登錄（Stage）

範例：已完成一個新的、具有使用權的臺灣河岸 GLB，先在自己的功能分支：

```bash
git switch main
git pull --ff-only
git switch -c feat/scene-keelung-river-001

python3 scripts/scene_hub.py stage keelung-river-001 \
  --title '基隆河岸測試場景' \
  --kind triangle_mesh \
  --source '原創 Blender 程序生成；參考資料與來源記錄在專案說明' \
  --license '原創幾何；確認可在本公開 repo 分享；參考素材另附來源' \
  --description '河岸步道與橋梁的概念場景，尚未進行實景精度查核' \
  --file /path/to/keelung-river-001.glb

python3 scripts/scene_hub.py verify --all
```

此時產生：`scenes/catalog/keelung-river-001.json` 與 `scenes/assets/keelung-river-001/keelung-river-001.glb`。

## AI 將新場景 Push 到共用 Repo

先人工確認來源授權、大小、沒有機密資訊及產物品質，才執行：

```bash
python3 scripts/scene_hub.py push keelung-river-001 --confirm
# 之後由具 GitHub 權限的 AI 或使用者開 PR，再由另一個人/AI 審查、合併到 main
# GitHub CLI 方式：gh pr create --base main --title 'Add keelung-river-001 scene' --body '含場景來源、授權、比例及驗證結果'
```

`push` 只會提交該場景目錄與對應 manifest；不會更新其他場景，也不會覆寫 `main`。它會拒絕在 `main/master/release/*` 分支執行。只有擁有 GitHub **寫入權限和可用 Git 認證** 的 AI 才能完成推送；其餘 AI 可以 Fork/PR、交 ZIP 或請你授權。

若人工驗收未完成，請保留 `review_status: unverified`；即使 `verify --all` 通過，也只是檔案完整性檢查。

### 為什麼不讓 AI 直接 push 到 main？

因為其他 AI 有可能在不同時間處理同一張地圖。應使用「一個場景 ID、一個分支、一個 PR」進行差異比對，避免整份地圖被另一個 AI 不小心取代。

## 大檔案與模型權重

`stage` 對單檔設 20 MiB 的保守上限，避免造成 Git repo 長期膨脹。較大的 `.glb`、`.blend`、`.spz` 檔案可考慮 GitHub Releases、Git LFS 或授權合適的物件儲存空間，再在 manifest 登錄固定版本 URL、SHA-256 與來源授權。**本版 CLI 只支援儲存於 Git checkout 的資產檔；外部 URL 資產目前尚不支援直接 pull**，不得自行把大型 asset 假裝已可下載。

`GitHub Actions Artifacts` 有保存期限，不適合作為長期唯一的資產倉庫。**HY-World 2.0 模型程式碼和權重遵循騰訊專屬授權；不可推定具有 MIT／Apache 使用權**。上游照片、模型、掃描資料也要個別確認。

## 最低驗收要求

| 項目 | 程式自動驗證 | 需要額外驗收 |
| --- | --- | --- |
| JSON 格式、場景 ID、資產路徑 | ✅ | — |
| SHA-256 與 bytes | ✅ | — |
| 網格面是否合理、法線、比例 | ❌ | Blender/Three.js 實際檢查 |
| 3DGS 可正常顯示 | ❌ | Spark/WebGL 真實渲染 |
| 物理碰撞／NavMesh | ❌ | 實際遊戲測試 |
| 是否真實還原橋梁／道路／建築 | ❌ | 多視角影像、GIS 實景查核 |
| 授權／商用限制 | ❌ | 逐筆人工判斷 |

## 常用指令

```bash
python3 scripts/scene_hub.py list
python3 scripts/scene_hub.py inspect demo-forest-island --verify
python3 scripts/scene_hub.py pull demo-forest-island --output ./my-app/public/models
python3 scripts/scene_hub.py verify --all
python3 scripts/scene_hub.py stage --help
python3 scripts/scene_hub.py push --help
```

## 給其他 AI 的工作原則

1. 進入 Repo 後，**先讀 `AGENTS.md` 與本文件**；需要建模再讀 `docs/AI_ASSET_PIPELINE.md`。
2. 取得檔案前一定要檢查 `source`、`license` 和 `review_status`；不能看到檔名就宣稱模型可商用、可實景漫遊。
3. 若需要 HY-World，先檢查 PR #20 的正式合併狀態；未合併前以分支讀取。
4. 不可以宣稱任何編譯、GPU 推論、Blender 轉換、WebGL 渲染已完成，除非有可核實的執行紀錄。
5. 未經授權不執行 `push`，不儲存憑證，也不能宣稱沒有 GitHub 權限卻已更新使用者的 repo。