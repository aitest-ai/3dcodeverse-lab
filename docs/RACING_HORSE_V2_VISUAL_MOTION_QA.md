# 賽馬 V2｜實際 Blender 5.2.3 精修＋40 點奔馳檢查

日期：2026-10-30。**這份文件只紀錄實際已執行的建模、匯出、渲染與量測，不代表達成照片級寫實。**

## 已驗證的工作流程

1. 從 [Quaternius 原始 CC0 馬](https://quaternius.com/packs/ultimateanimatedanimals.html) 先前成功產出的、仍可編輯之 `Horse_blender5.blend` 與 `Horse_White_blender5.blend` 開始。
2. 檢查模型重複位置頂點：原始每匹約 4,442 個 mesh 頂點，約 75% 是 glTF 扁平法線的重複頂點。**直接細分會產生破碎板片**，第一次 V2 CI 雖通過 GLB 結構驗證，但圖片不合格，不可使用。
3. 修正後使用 `bpy.ops.mesh.remove_doubles(threshold=0.000001)` 焊接實際重合位置，再於原始 Armature modifier 之前進行一次 Catmull–Clark；保留原本的蒙皮權重、不同材質區段及 NLA 動作。
4. 調整 GLB 真正支援的 PBR 固定材質參數（例如毛色、roughness、coat weight）。**不使用無法隨 GLB 帶出的 Blender 專屬噪聲節點冒充有皮毛貼圖**。
5. Blender Cycles CPU 真正渲染每匹四個視角，交付可編輯 `.blend` 與帶 13 段動畫的 `.glb`。
6. 額外重新開啟新的 V2 BLEND，單獨啟用 Gallop Action，取 **40 個影格子時間點**，量測四隻腳下肢骨末端的軌跡並繪製 SVG。注意它是**關節代理點**，不是四個實際蹄底接觸點。

## 已實際成功的 GitHub Actions

- [V2 外觀、幾何及 GLB 驗收 #6](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41005528336) — 成功，Artifact `racing-horse-V2-6`。
- [V2 Gallop 40 點軌跡檢查 #2](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41005979210) — 成功，Artifact `horse-V2-stride-2`。

| 量測 | 深棕馬 | 白馬 |
| --- | ---: | ---: |
| V1 GLB 三角面 | 2,182 | 2,182 |
| V2 GLB 三角面 | 13,092 | 13,092 |
| 重合位置頂點合併 | 3,307 | 3,307 |
| V2 建模頂點 | 6,548 | 6,548 |
| GLB skin 與骨架 | 1 skin／50 joints | 1 skin／50 joints |
| 保留原始動畫 | 13 | 13 |
| V2 Cycles 真正畫面 | 正／側／背／斜角 | 正／側／背／斜角 |
| Gallop 時序測試 | 40 點／4 腿 | 40 點／4 腿 |

所有幾何、PBR 與動畫數據皆為**匯出後 GLB 內的實際值**。未使用 AI 生圖取代 Blender 視覺證據。

## Gallop 關節軌跡（相對模型總高度）

| 下肢骨末端 | 垂直移動範圍／模型高度 | 近地區間最大每步橫向位移／模型高度 |
| --- | ---: | ---: |
| 前左 | 15.37% | 4.39% |
| 前右 | 15.04% | 4.05% |
| 後左 | 24.73% | 4.36% |
| 後右 | 23.94% | **5.61% — 需檢查是否滑步** |

量測資料：`stride_qa.json`、`gallop_stride_chart.svg`。高度採原始 Blender 場景單位，並沒有校正成實際公尺。**不能把這些值稱作物理接觸滑步距離、跑步速度或真實賽馬 gait 正確度**。尤其兩匹馬使用相同源骨架和 Gallop 動作，數據相同是合理的。

## 真正的美術品質檢查

**V2 可接受的改進：** 馬身平滑曲面、軀幹輪廓、基本 coat/hoof PBR 參數；兩匹沒有原先破形板片／尖刺，動畫結構完整。

**仍須修正：** 肩胛與臀部肌肉、前膝／後跗關節的精準形狀、蹄尖與球節、耳／鼻細節；鬃毛及馬尾依然是較厚的塊狀幾何，且目前沒有照片級皮毛、UV 影像貼圖，也沒有騎師／馬鞍。V2 是**風格化平滑原型**，不是寫實賽馬高模。

馬腿解剖的權威參考：
- [University of Minnesota Extension — Horse conformation](https://extension.umn.edu/agriculture/animals-and-livestock/horse/conformation-of-the-horse)
- [Oregon State Extension — Hoof and Leg Anatomy](https://extension.oregonstate.edu/sites/extd8/files/documents/9121/osu-version-horse-hoof-leg-anatomy.pdf)

## 高品質 V3 模型候選與下一步

- [BlendSwap Horse Rigged All Gaits](https://blendswap.com/blend/28627)：**CC0**、作者 `fdoss001`、有 Walk、Trot、Canter、Gallop、毛髮系統和馬鞍／韁繩，Blender 2.9 原始檔約 **584 MB**。最符合賽馬目標，但**尚未合法取得原始檔或在 Blender 5.2 實測**。若網站需要登入，必須由授權的使用者正常下載，不能繞過。
- [OrelvysRodriguez 70.5K Triangle Horse](https://sketchfab.com/3d-models/horse-e62e8fae743b40b7b8c382ccca863725)：較高面數，**CC BY**，需正常下載／保留作者授權；是否含可用 Gallop 動作待查。
- [Warhorse Lite](https://literock-studios.itch.io/warhorse-lite)：有 2K PBR、9.9k triangles、4 段動畫，但不包含 Gallop，且**禁止轉售或重發原資產**；不可直接放進本庫公開資產包。
- 先用 V2 同時保留 web runtime 的遊戲原型；更高品質模型如能合法取得，應另生成 V3，再利用 UniRig／Rigger 或人工骨架重新綁骨。**不要直接替換原始 GLB 而以為所有動畫都能移植。**

## 開發檔案

- `scripts/horses/horse_v2_polish.py`：焊接／曲面／GLB PBR／真實 Blender 渲染。
- `scripts/horses/validate_horse_v2.py`：跨 V1/2 獨立檢查 13 clips、skin、三角面和 PBR。
- `scripts/motion/horse_stride_audit.py`：40 點 Gallop 代理蹄軌跡與 SVG。
- `.github/workflows/racing-horse-v2.yml`、`.github/workflows/racing-horse-stride.yml`：正式 CI。
- `examples/racing-horse/index.html`：兩匹馬、Gallop／Walk／Idle、速度、跑道前進測試（需 HTTP server；**遊戲內實機仍待驗收**）。

保持在 `feat/racing-horse-cc0-pipeline`／Draft PR #13，不影響 `main`、人物或機甲現有成果。
