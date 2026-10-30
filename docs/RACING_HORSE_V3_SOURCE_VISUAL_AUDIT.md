# 賽馬 V3｜高模來源實測與嚴格驗收（2026-10-30）

## 這次不是直接細分原本的馬

先前 V2.2 兩匹 Quaternius CC0 馬確實有 **50 骨、13 段原始動畫**，可在 Three.js 測試；缺陷是肌肉、蹄、頭型與鬃毛解剖不夠細緻。這一輪特別測試了「網格數量較高是否一定讓馬更逼真」。

### 實際 Blender 5.2 測試 A：Innerscene 原創 CC0 靜態馬

官方頁面：https://www.innerscene.com/tools/library/3d-parts/standing-horse-01d8563f

從網站公開的 JS 取得**站方自己提供**的下載路徑：`/api/library/standing-horse-01d8563f/download`，無需登入，不繞過任何權限。

[已實際執行且成功的 Blender 5.2 四視角渲染](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41015815565)，Artifact `horse-v3-anatomy-review-2`，含原始下載的 GLB、編輯用 BLEND、四張 Cycles 真正圖片和品質報告。

| 驗收 | V2.2 動畫馬 | V3 高面數靜態候選 |
| --- | --- | --- |
| Triangle | 約 13,092 | **208,238** |
| Vertices | 6,548 + 765 髮束 | 104,752 |
| Meshes | 2（本體＋纖維） | 32 |
| Skin | 1、50 bones | **0** |
| Animations | **13** | **0** |
| Image textures | 無照片級材質貼圖 | **0** |
| Bounding box | 遊戲內標準化 | 0.706 × 2.526 × 2.143 模型單位 |
| Blender 真實外觀 | 風格化、相對自然的馬體 | 胸臀像圓球、四肢欠缺真實球節、蹄尾偏簡化零件 |
| 判定 | **保留可用基底** | **外觀未過，淘汰** |

**重要授權資料一致性警告：**公開頁面原先載明 GLB 大小 **4,990,516 bytes**、SHA-256 `0ca21251cd3d98d2af263885a5ab21147057b1fd152f08a1f8703f9bc0ebe2cd`，但 API 實際下載為 **4,990,756 bytes**、SHA-256 `a4ce47c4cdc181830b5134d69598a27b4378d17f08081bbe324f7f9ad78dee90`。模型本身通過 GLB 2.0 格式與 Blender 渲染，但資料不一致，**維持 quarantine；不能稱為已驗證可分發來源，也不應入正式 GitHub runtime**。

本次測試結論：**高面數不等於真實、也不等於可以拿去跑 Gallop**。

### 實際來源授權查核 B：BlendSwap Horse Rigged All Gaits

頁面：https://blendswap.com/blend/28627 ，作者 fdoss001 標示 CC0、584MB、Walk/Trot/Canter/Gallop、鬃毛動態、鞍具。

但該頁留言指出原始馬身網格來自 **Tarnyloo**：
https://blendswap.com/blend/17172 ，Tarnyloo 的原版馬身是 **CC BY**，且非 fdoss001 原創。除非原作者能確認新權利授與，該 584 MB 作品不能整包視為 CC0 無須標註；**即使使用，也應保留 Tarnyloo 及其馬體來源的 CC BY 署名**。下載需使用正常 BlendSwap 登入流程，不得規避。

### 其他可考慮的高模候選

1. [CreativeMachine Horse Rig，Sketchfab](https://sketchfab.com/3d-models/horse-rig-bd71883bad9845389ef4ec2801004801)：**CC BY**、約 42K triangles、21.3K 頂點，具有馬骨架；是否能完整重現 Gallop 還沒檔案實測。授權可追溯，但下載仍要依 Sketchfab 正式流程。
2. [Warhorse Lite，Literock](https://literock-studios.itch.io/warhorse-lite)：可免費商業使用的 PBR 馬，有 2K texture、骨架、4 段動畫，**不含 Gallop**；作者不允許單獨重散發資產，不能上傳公開 GitHub 原始檔。
3. [WildMesh horse free demo，Sketchfab](https://sketchfab.com/3d-models/horse-realistic-3d-model-demo-free-65d6a70a6721495f938c93e80a5998e4)：82K triangles、52K 頂點，但 **CC BY-NC**，若預期未來商業遊戲不適合。

## V3 正式角色的新驗收門檻

為避免未來 AI 只追逐高模，新增：
- `scripts/horses/v3_audit_cc0_standing_horse.py`：從合法公開 URL 下載並比對站方 hash / file size，未通過立即 quarantine。
- `scripts/horses/v3_inspect_static_candidate.py`：Blender 5 真實匯入、4 角 Cycles、統計網格、身高、動畫、骨架和材質。
- `scripts/horses/v3_acceptance_gate.py`：檢查網格、蒙皮、Gallop/Walk/Idle、UV/PBR、原始授權／hash、人眼解剖審查及完整跑步動作。**沒有人體審查簽核不可宣稱高寫實合格**。
- `.github/workflows/racing-horse-v3-static-render.yml` 與 `.github/workflows/racing-horse-v3-gate.yml`：可獨立重跑。

## 結論與推薦下一步

V3 高模候選已**實際下載、渲染並淘汰**，不改 V2.2 主模型，不破壞現有 13 Clips 與兩馬角色。

下一版先測 **Sketchfab CreativeMachine CC BY 馬** 或經完整署名的 **Tarnyloo 原始網格**。需先依官方規則取得合法原始檔，再進行 Blender 5 骨架、表面、重新綁定、腳蹄動作、肌肉輪廓驗收；如果素材存取需要登入，應由授權使用者正常下載或提供檔案，不能假裝已匯入。

- [GitHub 賽馬 PR #13](https://github.com/aitest-ai/3dcodeverse-lab/pull/13) — 未合併 main。
- [V2.1 / V2.2 前一輪可用版本](RACING_HORSE_V21_V22_QA.md)。
