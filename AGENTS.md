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

## 🐎 跨 AI 賽馬角色資產庫（所有 Agent 必讀）

**不要只根據此對話上下文判斷馬匹是否存在。** 任何使用者詢問馬匹建模、賽馬、馬動畫、不同馬款、馬模型 GLB／BLEND，先讀：

1. [機器可讀現有馬匹清單](assets/horses/registry.json)：包含 `horse-brown`、`horse-white` v2.3.0，兩匹皆有 50 bones／13 clips 和 PBR，經 Blender + Chromium 確認為可操作風格化原型。
2. [跨 AI 讀取／建立新馬／push PR／pull 已核准馬](docs/HORSE_AI_COLLABORATION.md)：是唯一對外協作流程。
3. [授權資料來源](resources/horses/source_registry.json)：第三方高模尤其應再檢查授權，不可把圖片展示當成已取得模型。

最快命令（需具備私有庫權限、安裝並登入 GitHub CLI）：

```bash
python3 scripts/horses/horse_assets.py list
python3 scripts/horses/horse_assets.py pull horse-brown --dest ./public/models
python3 scripts/horses/horse_assets.py pull horse-white --dest ./public/models
```

- **正式二進位模型**存於 [GitHub Releases — horses-v2.3.0](https://github.com/aitest-ai/3dcodeverse-lab/releases/tag/horses-v2.3.0)；Artifacts 僅是會到期的測試成果。
- 新馬建立新的唯一 ID／版本，真 Blender 建模／GLB 檢查／授權／正側背預覽，於獨立分支送 PR，經核准後才新增到 registry 與發佈新的 Release；**不得覆蓋既有馬**。
- 當前馬資產的協作文件位於 `feat/racing-horse-cc0-pipeline`（PR #13），**尚未合併 main**。其他 AI 必須讀對分支。合併後請改讀 main。
- 嚴禁未授權重發付費／CC BY-NC 素材；CC BY 需保存原作者署名。禁止憑空聲稱已 push/pull、擁有 repo 權限、已完整通過馬蹄物理驗收。
