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
