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


## 高品質多物種 3D 建模（2026-10 新增）
若任務包含人物、動物、機甲、建築、掃描素材、AI 圖像轉 3D、PBR 或重拓樸，還必須先閱讀 `docs/HIGH_FIDELITY_3D_TOOLCHAIN.md`，以及 `resources/open_3d_tool_catalog.json`。
- 用 `python3 scripts/assets/tool_catalog.py --category animal` 查找工具；先判斷授權、硬體和實際是否已安裝。
- 任何大型 AI 權重不得直接 commit。GPU 工具先在獨立可授權環境測試，輸出 GLB 再進入本庫 Blender 5 的 CPU 驗收。
- 可用 `scripts/assets/glb_quality_report.py` 收集拓樸／PBR／骨架／動畫指標；不可以統計數字冒充藝術或解剖品質合格。
- Poly Haven API 只能依 `scripts/assets/polyhaven_search.py` 目前已實作的中繼資料查詢來描述；不能宣稱該外部資產已下載／導入。
- 來源授權需依序追蹤程式、模型權重、生成作品／素材、服務條款；Hunyuan3D 2.1 屬自訂授權，不能誤稱 MIT／Apache。
