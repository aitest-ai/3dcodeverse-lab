# 給其他 AI 的場景交換交接指令

把下面這段完整貼給 Claude、Codex、ChatGPT Work、Copilot、Cursor、Gemini 或任何可使用 GitHub / shell 的 Agent。

> 你現在是我 3D 建模工作流的協作 AI。共用儲存庫是 https://github.com/aitest-ai/3dcodeverse-lab 。
>
> **開始前請先自行讀取**：
> 1. 本庫 \`AGENTS.md\`
> 2. \`docs/SCENE_HUB.md\`
> 3. \`skills/scene-exchange/SKILL.md\`
> 4. 如果需要 Blender 建模，再讀 \`docs/AI_ASSET_PIPELINE.md\`。
>
> **如果上面文件在 main 找不到**，先檢查 PR #24（\`feat/scene-hub-ai-handoff\`）是否已經合併。若尚未合併，從該分支讀取，不能假裝 main 已有功能。
>
> **要取用場景時**：先執行 \`python3 scripts/scene_hub.py list\`，再 \`inspect <scene-id> --verify\`，檢查來源、授權、品質狀態；執行 \`pull <scene-id> --output <你的專案模型資料夾>\`，將場景匯入你自己的 Blender、Three.js、Unity 或 Godot。不能把 Gaussian splats 直接當三角網格或碰撞面。
>
> **要產生並共享新場景時**：先建立新的 Git 功能分支，製作 GLB/PLY/SPZ/場景預覽與來源說明，執行 \`stage\` 登錄場景（唯一的 scene-id），再執行 \`verify --all\`。使用者確認並授權之後，才可執行 \`push <scene-id> --confirm\`，接著開 PR 給其他 AI/人員審查，不可直接覆蓋 main。
>
> **必須明確標示**：哪一個檔案真的產生了、哪些檢查真的執行了、哪些是合成示範、哪些是 HY-World 2.0 真正生成、來源與授權、哪些還沒有通過視覺或物理驗收。HY-World 2.0 Bridge 在 PR #20，只有合併或明確指定分支才可使用；原創山湖漫遊示範不是 HY-World 真正生成的場景。
>
> 如果你無法存取 GitHub、沒有 Git 認證或 GPU，請直接指出限制，交付可用的檔案、補丁或 PR；不要宣稱已推送成功。
>
> 完成後回報：scene-id、格式、來源與授權、檢查結果、分支／PR 網址、如何在另一個專案下載與使用。

## 常用指令對照

先進入 GitHub repo 目錄：

~~~bash
python3 scripts/scene_hub.py list
python3 scripts/scene_hub.py inspect demo-forest-island --verify
python3 scripts/scene_hub.py pull demo-forest-island --output ../other-project/public/models
python3 scripts/scene_hub.py verify --all
~~~

推送新場景（有明確授權且已完成來源審查才執行）：

~~~bash
git switch main
git pull --ff-only
git switch -c feat/scene-hakodate-v1
python3 scripts/scene_hub.py stage hakodate-v1 --title '函館測試場景' --kind triangle_mesh \
  --source '原創 Blender 建模' --license '原創幾何、具授權' --file /path/to/hakodate.glb
python3 scripts/scene_hub.py verify --all
python3 scripts/scene_hub.py push hakodate-v1 --confirm
gh pr create --base main --title 'Add Hakodate scene' --body '來源、授權、比例與驗證狀態'
~~~

同一張場景的重大修訂，建議使用新的 \`scene-id\`（如 \`hakodate-v2\`），避免讓其他專案使用的檔案在不知情下改變。**GitHub 內容與操作權限不是因為看到了這份指令就自動取得**。
