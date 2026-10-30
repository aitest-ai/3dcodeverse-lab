# 3DCodeVerse Lab｜可驗證的 3D 程式建模工作庫

這是自建整合與實驗工作庫，**不是 3DCodeVerse 官方儲存庫**，也不代表 AI Harness 已在 ChatGPT 中永久安裝。

- 官方開源原始碼：[gaoypeng/3dcodeverse](https://github.com/gaoypeng/3dcodeverse)（Apache-2.0；使用時以官方授權為準）
- 本庫 `main`：安裝指南、Skill、基礎測試及 GitHub Actions
- 本庫 `upstream-3dcodeverse`：官方程式碼的同步快照，獨立分支，不覆蓋 `main`

## 同步官方原始碼

進入 [Actions](https://github.com/aitest-ai/3dcodeverse-lab/actions/workflows/sync-upstream.yml) 執行 **Sync official 3DCodeVerse source**，或等待同步工作流程的首次啟動。流程會下載官方程式，並將快照提交到本庫的 `upstream-3dcodeverse` 分支；**不會執行上游任意程式**。

同步後：
```bash
git clone --branch upstream-3dcodeverse https://github.com/aitest-ai/3dcodeverse-lab.git 3dcodeverse
cd 3dcodeverse
```
也可直接從官方 clone，完全不需等待鏡像。

## 安裝官方 Harness（在 Linux / WSL2 / Codespaces 上）

需要 Python 3.13、Node 20.6+、可連網且足夠磁碟空間；Blender 5.2 LTS 視任務而定。

```bash
# 在本庫 main 分支
bash scripts/install_official.sh
```

腳本會從官方 GitHub 下載到獨立資料夾、建立虛擬環境、執行官方 `harness/setup.sh`，再執行 `3dcodeverse doctor`。**會安裝大量 Python/Node 套件與瀏覽器，不應在不可信的機器或專案中盲目執行。**

AI 自動生成與視覺評分還需要相應的模型／CLI 權限，可能產生費用。不得將 API Key、登入憑證或付費資料集提交到 GitHub。

## 適用範圍

- `skills/verified-3d-modeling/SKILL.md`：可供 AI Coding Agent 閱讀的工作規範，並非 ChatGPT 系統層級的永久技能安裝
- `.github/workflows/sync-upstream.yml`：官方原始碼鏡像到獨立分支
- `.github/workflows/verify-upstream.yml`：僅檢查下載與 Python 語法，**不是完整安裝或生成測試**
- `scripts/install_official.sh`：使用者端安裝腳本

GitHub 是版本庫，不是長駐的生成伺服器。從 GitHub 讀取檔案可透過連接工具；執行 Harness 則仍需要本機、Codespaces 或其他有依賴的執行環境。

## 授權與來源

官方 3DCodeVerse 原始碼遵守其 [LICENSE](https://github.com/gaoypeng/3dcodeverse/blob/main/LICENSE)。研究資料集可能有不同授權，本庫不鏡像資料集。

## Blender 5.2.3 雲端建模／跨 AI 協作（新增）

這個儲存庫現在也提供 **可重用的 Blender 5 雲端骨架動畫工作流程**，與原本 3DCodeVerse Harness 安裝完全分開。

- [給其他 AI 的合作規範：AGENTS.md](AGENTS.md)
- [完整工作流程：AI × Blender 5 → GLB → 遊戲系統](docs/AI_ASSET_PIPELINE.md)
- [範例：機甲膝蓋、腳踝、腳掌和 4 段動畫](scripts/blender5/mecha_smoke.py)
- [自動驗證器（GLB + asset_manifest）](scripts/blender5/validate_glb.py)
- [Three.js 匯入／動畫播放範例](examples/threejs/load-animated-glb.js)
- [Blender 5 GitHub Actions](https://github.com/aitest-ai/3dcodeverse-lab/actions/workflows/blender5-cloud.yml)

**如何讓別的 AI 使用：** 叫它先閱讀 `AGENTS.md` 與 `docs/AI_ASSET_PIPELINE.md`，建立新的 `scripts/blender5/<asset_id>.py`，再由 GitHub Actions 生成 `.blend`、`.glb`、`asset_manifest.json` 和報告；完成後把 GLB 放到它自己的 Three.js、Unity、Godot 等專案。需要具備 GitHub 寫入權限才可直接提交，否則只能提出 Fork/PR 或交付差異檔。

**真實進度：** 腳踝 V3 程式與流程已提交，雲端 Blender 與視覺品質仍需該次 Actions 真的成功執行後再驗收。腳底修正是關鍵影格計算，不等於完整 IK、碰撞或物理模擬。


## 🐎 賽馬 3D 角色（Blender 5 實測）

- [原始 CC0 馬模型、驗收數據與 13 段動畫製作規範](docs/RACING_HORSE_PIPELINE.md)
- [雙馬原始素材／授權與 SHA256 來源目錄](resources/horses/source_registry.json)
- [Blender 賽馬製作及 gallop 動畫驗收工作流程](https://github.com/aitest-ai/3dcodeverse-lab/actions/workflows/racing-horse.yml)
- [賽馬 WebGL/Three.js 即時動畫測試頁](examples/racing-horse/index.html)

已通過 GitHub Actions #29：兩匹 Quaternius 原版 CC0 馬、各 50 根骨、13 段動畫，Blender 5.2.3 匯出 GLB／BLEND，六視角 + 兩張真 Gallop 影格；**屬低多邊形遊戲原型，並非寫實高模**。可在 GitHub Actions Artifacts 下載 racing-horses-29，含兩匹馬及網頁 demo。高模與真實賽馬運動驗收另行進行.

## 🐎 多 AI 共用馬匹模型庫（已上線）

跨 ChatGPT、Claude、Copilot、Codex、Cursor 或其他能操作 GitHub 的 AI 共用：

- **[Horse Library v2.3.0｜正式馬模型 GitHub Release](https://github.com/aitest-ai/3dcodeverse-lab/releases/tag/horses-v2.3.0)**：保存深棕馬、白馬 GLB、可編輯 BLEND／貼圖 ZIP、SHA256SUMS，避免暫存 Actions 到期。
- **[現有資產登錄表](assets/horses/registry.json)**：機器可讀 ID、版本、SHA256、動畫、授權及下載位置；其他 AI 應先讀。
- **[跨 AI 新增、推送、驗收、取回新馬的操作流程](docs/HORSE_AI_COLLABORATION.md)**：新馬請建立新 ID／版本、發獨立 PR、通過來源授權及真正 GLB 驗證，核准後才發新 Release。
- [給 AI 的統一入口](AGENTS.md)；另外有 [Claude](CLAUDE.md)、[Copilot](.github/copilot-instructions.md) 與 Cursor 提示檔。

```bash
# 先安裝、登入 GitHub CLI 並取得此私有庫的讀取權限
gh repo clone aitest-ai/3dcodeverse-lab
cd 3dcodeverse-lab
git checkout feat/racing-horse-cc0-pipeline
python3 scripts/horses/horse_assets.py list
python3 scripts/horses/horse_assets.py pull horse-brown --dest ./public/models
python3 scripts/horses/horse_assets.py pull horse-white --dest ./public/models
```

**實際通過**：[GitHub Release 獨立下載、兩馬 SHA256／50 骨／13 動畫及新馬投稿流程驗證](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41021728481)。現階段此入口在 `feat/racing-horse-cc0-pipeline`（[PR #13](https://github.com/aitest-ai/3dcodeverse-lab/pull/13)），尚未合併 main；其他 AI 必須讀對分支。正式模型已透過 GitHub Release 長期保存，但其他 AI 仍需私有庫授權。
