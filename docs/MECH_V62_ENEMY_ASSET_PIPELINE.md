# 臺北機甲 v6.2 — 3 款真正 Blender 敵機、15 骨架／6 動畫

## 本輪交付性質

新的 Blender 角色，不是 AI 示意圖，也不是用少數立方體取代現有 v5.0 模型。使用 2026-10-30 成功的 GitHub Actions Run \`41003028145\`、artifact \`blender5-v50-4\` 中經 Blender 實際製作的 v5.0 BLEND 做母檔，為 3 款角色新增獨立的硬表面裝甲與武裝、保留源 15 根骨架、Mecha_Idle/Run/Fire/Punch/Dodge/Hit 六段動畫、八張法線材質與 24 張基底 PBR 貼圖。原遊戲玩家 GLB \`296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c\` **不修改**。注意：GitHub 原始母檔的二進位 SHA 與 Windows 包既有 .blend 不完全相同；敵機另存新的檔案，並不宣稱新敵機與玩家幾何逐位元相同。

## 三款外觀

| 角色 | 建模 | 原始骨架與動畫 |
|---|---|---|
| assault 突擊 | 外張肩甲、前胸脊條、後方雙推進器、腕部刀刃、分離護腿 | 15 骨架、六動畫、276 GLB meshes |
| ranger 遠距 | 電磁長軌砲、七段線圈、背側目標感測器、導引面板、細長肩甲 | 15 骨架、六動畫、282 GLB meshes |
| heavy 重裝 | 重肩甲雙側砲塔、雙莢艙／18 飛彈口、厚胸前護板、左臂盾與加強鞋底 | 15 骨架、六動畫、316 GLB meshes |

產生程序：\`scripts/blender5/mecha_enemy_v62.py\`，官方 Blender 5.2.3 LTS，使用 GH Actions \`.github/workflows/mecha-v62-enemies.yml\` 並驗證 Blender 官方 SHA，真實 4 視角 Workbench PNG。完整 ZIP 另外包含每款 .blend 可編輯母檔、GLB、四視角 PNG、報告 JSON 及所有既有玩家角色資產。

## 遊戲接法

\`examples/threejs/mech-enemy-glb-v62.js\` 是完整 Windows ZIP \`mech-enemy-glb-v62.js\` 的相同 source blob，使用 GLTFLoader + SkeletonUtils.clone（不能用 Object3D.clone 複製骨架）、角色分別載入本機 \`models/enemy_{assault,ranger,heavy}_v62.glb\`，保留原敵機 AI／碰撞／HP／警示環／建築射線。動畫使用主腳色已製作的原始動作，遮掉 root translation，以防原遊戲控制器與 AnimationMixer 各移動一次。載入失敗就留下 v6.1 程序化備用敵機，三款 GLB 僅各載入一次並共享材質，重置時釋放角色 instance，關閉時統一釋放資產。

## 測試與限制

- Blender CI 三款 .blend/.glb 實際產出並通過骨架、六動畫、法線貼圖、四視角 render 檢查。
- 獨立 Windows ZIP Node + Python **58/58** 項自動化測試 PASS，其中 v6.2 新增檔案格式／角色差異／材質／安裝程式冪等／GLB 失敗回退／root masking 模擬驗證。
- **尚未做 Windows WebGPU 實際畫面、真實 101 街道五分鐘關卡、3D 手臂武器／盾牌動畫穿模、記憶體和真實 GPU FPS 測試。** 不可把 GH Actions 或模擬動畫通過冒充實機遊玩。
- 無外部非授權模型，新增幾何是此程式產生；保留 Blender Python 建模來源及原 v5.0 母檔出處。
- 沒有合併 PR、沒有動 \`main\`、沒有改原本臺北公開網站。此 Draft PR 依賴 v6.1 Draft PR #63，且前序版本仍保持未合併。
