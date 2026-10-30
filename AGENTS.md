# AGENTS.md｜給所有 AI 模型的工作規範

本儲存庫是使用者的「可驗證 3D 程式建模實驗室」，不是 Blender、Animatica 或 3DCodeVerse 官方原始碼庫。

## 任務入口
1. 優先閱讀 [docs/AI_ASSET_PIPELINE.md](docs/AI_ASSET_PIPELINE.md)。
2. 複製或參考 `scripts/blender5/mecha_smoke.py` 建立新的 `scripts/blender5/<asset_id>.py`。
3. 只能使用原創或已確認授權素材，必須保留來源及授權資訊。
4. 程式使用 Blender 5.2.3 LTS 的 `bpy`，預設只能以 GitHub Actions 的 **背景模式** 建模、匯出與檢查，不能聲稱已具備桌面 GUI 或 Animatica AI 權限。
5. 每一個新任務都必須輸出：`outputs/<asset_id>.blend`、`outputs/<asset_id>.glb`、`outputs/asset_manifest.json`、`outputs/report.json`。命名範例詳見文件。
6. 在本機先執行 `python3 -m py_compile scripts/blender5/<asset_id>.py`（此步只檢查語法）；能執行 Blender 才宣稱模型已生成。不要把「程式碼成功提交」描述為「渲染已成功」。
7. 請使用分支與 Pull Request 提交新作品；不要直接改動現有機甲與工作流程，除非任務明確要求。保留原檔與所有現有動畫。
8. 通過 `python3 scripts/blender5/validate_glb.py outputs` 才表示輸出結構合格。真實動作效果、腳滑、穿模、材質、比例仍需視覺驗收。
9. 模型要能被 Three.js／Unity／Godot 等系統引入，使用標準 glTF 2.0 GLB，不依賴專有 Blender 程式才能播放。
10. 不要提交帳號密碼、API Key、第三方付費外掛程式或其模型權重；無法確定授權時先停止引用該素材。

## 其他 AI 的最快上手方式
閱讀：`https://github.com/aitest-ai/3dcodeverse-lab/blob/main/docs/AI_ASSET_PIPELINE.md`

示範：`https://github.com/aitest-ai/3dcodeverse-lab/blob/main/examples/threejs/load-animated-glb.js`

工作流程：`https://github.com/aitest-ai/3dcodeverse-lab/actions/workflows/blender5-cloud.yml`

**注意：** GitHub 儲存庫保存程式與版本；Blender 在每次 Actions 執行期間暫時安裝，不是常駐 3D 編輯伺服器。新的 AI 若沒有 GitHub 授權，先讓使用者安裝連接器，或以 Fork/PR 方式參與，不得假裝已經寫入儲存庫。

## 🐎 已有的共用馬匹模型（其他 AI 請先讀）

本儲存庫**已經有兩匹可用的風格化賽馬**，不要因為 `main` 暫時沒有完整模型生產程式，就宣稱馬不存在、從零重造。

- 持久版本化 Release：[Horse Library v2.3.0](https://github.com/aitest-ai/3dcodeverse-lab/releases/tag/horses-v2.3.0)，包含 `horse-brown` 和 `horse-white` 的 GLB（各 50 根骨、13 段動畫、PBR 貼圖）、可編輯 Blender 原始檔包、雜湊與授權。
- **跨 AI 完整規格目前位於未合併的賽馬分支**：`feat/racing-horse-cc0-pipeline`（[PR #13](https://github.com/aitest-ai/3dcodeverse-lab/pull/13)）。請從此分支讀取 [docs/HORSE_AI_COLLABORATION.md](https://github.com/aitest-ai/3dcodeverse-lab/blob/feat/racing-horse-cc0-pipeline/docs/HORSE_AI_COLLABORATION.md) 與 [assets/horses/registry.json](https://github.com/aitest-ai/3dcodeverse-lab/blob/feat/racing-horse-cc0-pipeline/assets/horses/registry.json)。
- 在此分支執行 `python3 scripts/horses/horse_assets.py list` 以及 `python3 scripts/horses/horse_assets.py pull horse-brown --dest ./public/models`；需具備私有 GitHub repo 的讀取授權。下載會核對 SHA-256。
- 要新增不同毛色、體型或動作的馬：建立**新 asset ID、版本、獨立分支與 PR**，產出真 GLB／BLEND／驗證圖、紀錄授權與 SHA-256，審核後才發布新 Release。不能覆寫現有版，也不能把未驗證的靜態馬宣稱可 Gallop。
