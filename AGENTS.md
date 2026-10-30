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

## 新增：跨 AI 3D 場景交換中心（Scene Hub）

**任何 AI 若要尋找、下載、建立、交換、提交場景地圖（PLY／GLB／SPZ／3DGS），請先讀 [docs/SCENE_HUB.md](docs/SCENE_HUB.md)。**

- 指令：`python3 scripts/scene_hub.py list`、`inspect <scene-id> --verify`、`pull <scene-id> --output <dir>`、`stage`、`verify --all`、`push <scene-id> --confirm`。
- 每個場景獨立索引在 `scenes/catalog/<scene-id>.json`，小型資產在 `scenes/assets/<scene-id>/`；必須紀錄來源、授權、SHA-256、bytes、驗收狀態。
- Pull 會核對雜湊值、不覆寫現有目錄；Push 只允許使用者明確同意後，從**功能分支**送出，仍須開 Pull Request，禁止直接改動 `main` 或其他 AI 的場景。
- 檔案完整性成功不等於美術品質或實景地理正確。Gaussian splats 與有三角形面的 PLY 不能混同。新的工具不代表 HY-World GPU 推論已跑通。
- HY-World 2.0 匯入器和山湖漫遊原型目前位於 [PR #20](https://github.com/aitest-ai/3dcodeverse-lab/pull/20) 的 `feat/hy-world2-format-bridge` 分支；直到合併前**不可宣稱 `main` 已支援它**。
- 給其他 AI 可以直接貼 [跨 AI 交接指令](docs/AI_SCENE_HANDOFF_PROMPT.md)；對跨 AI 工具請參閱 `skills/scene-exchange/SKILL.md`。這是工作庫指令文件，不是自動裝進所有 AI 平臺的外掛程式。
