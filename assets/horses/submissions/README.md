# 新馬投稿資料夾（所有 AI 都能依規範提交）

每款新馬一份 `<asset-id>.json`；請複製 [範例](../examples/submission.example.json)，填入真實作者、授權、SHA-256、Actions run ID 與 Artifact 名稱。

**不要把 .blend/.glb 大型檔案直接存進一般 Git 歷史。** 二進位模型請透過經驗證的 GitHub Actions Artifact 送出，獨立驗收及 PR 審核後，再發布新的 Release。暫存 Artifacts 有有效期限；尚未核准的素材不可標示為正式發佈。

更多資訊：[跨 AI 馬匹協作規範](../../../docs/HORSE_AI_COLLABORATION.md)。

正式模型名單只有 [registry.json](../registry.json)。在這個資料夾建立候選，不代表該馬已獲核准或遊戲可用。
