# Claude Code / AI coding agents — first read AGENTS.md

本儲存庫已有真實可取得的賽馬資產；**不要重新從零找馬、也不要只讀 main 就認定沒有。**

請先讀：
- [全域 Agent 規範](AGENTS.md)
- [馬匹資產庫機器可讀目錄](assets/horses/registry.json)
- [跨 AI 的 push／PR／pull 協議](docs/HORSE_AI_COLLABORATION.md)

目前馬在 `feat/racing-horse-cc0-pipeline` 分支（PR #13）上。正式模型由 GitHub Release `horses-v2.3.0` 保存：`horse-brown` 與 `horse-white`，各 50 bones、13 clips 與內嵌 PBR。使用 `python3 scripts/horses/horse_assets.py list` 列出，使用 `pull <id> --dest ...` 取得，會驗證 SHA256。

若你產生新的馬種、毛色或馬具，必須以新 ID 新版號獨立建分支，提供 GLB、BLEND、授權、真實渲染、動畫驗證與 PR，審核後才加入可共享庫。禁止覆寫舊正式版或隱瞞尚未驗收的物理滑步。
