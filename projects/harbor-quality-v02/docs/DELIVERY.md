# v02 交付與接續

- Draft PR：https://github.com/aitest-ai/3dcodeverse-lab/pull/137
- Branch：`feat/harbor-quality-v02-20261103`
- Base：`feat/harbor-walk-framework-20261103`（PR #134）；不自動合併此鏈，不部署。
- 本地來源：獨立 `projects/harbor-quality-v02/`；原 v01 資產與原型保持不變。
- 已成功的真 Godot CI：https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41578361400 。之後若只有驗收文件／截圖更新，不代表重新做過未變更的美術或硬體認證。
- GitHub artifact 不是永久資產登錄，本輪 Runtime／Source ZIP、母檔、圖像與影片另外交付 Google Drive，含獨立 SHA-256。
- Unreal workflow 是未實跑的 self-hosted 交接候選；runner 需合法引擎，首次 workflow_dispatch 註冊亦可能需依儲存庫既定審查流程進入 default branch。本 PR 不自行合併以啟用它。

下一階段：先以角色實際多視角及原生引擎近景審查造型／材質，再完善衣服皺褶、NPC 外觀差異、腳掌鎖定與環境美術；於桌機 GPU 實測。Unreal 需取得具備 UE5.6 的授權 runner 才能驗證。不要重做已通過的原作 ZIP 研究或覆蓋 v01。
