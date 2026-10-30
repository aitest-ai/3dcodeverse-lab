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

## 🐎 已可讓其他 AI 共用的馬匹模型庫

正式雙馬版本 [Horse Library v2.3.0 GitHub Release](https://github.com/aitest-ai/3dcodeverse-lab/releases/tag/horses-v2.3.0) 已提供深棕馬、白馬的 GLB、BLEND、PBR 貼圖、SHA256 及授權說明。兩匹模型各 50 bones／13 動畫，已在 Blender 5／Chromium WebGL 實測通過，屬風格化遊戲原型。

**跨 AI push／pull 規範目前在獨立賽馬分支** [`feat/racing-horse-cc0-pipeline`](https://github.com/aitest-ai/3dcodeverse-lab/tree/feat/racing-horse-cc0-pipeline) 的 [HORSE_AI_COLLABORATION.md](https://github.com/aitest-ai/3dcodeverse-lab/blob/feat/racing-horse-cc0-pipeline/docs/HORSE_AI_COLLABORATION.md) 和 [registry.json](https://github.com/aitest-ai/3dcodeverse-lab/blob/feat/racing-horse-cc0-pipeline/assets/horses/registry.json)。其他 AI 應先閱讀再造新馬，依新 ID／PR／Release 版本管理，不覆蓋既有資產。
