# Racing Horse V2.1 / V2.2 — 可重複實作與真實驗收

日期 2026-10-30。這個版本建立在 **已通過 Blender 5.2.3、50 骨、13 段動畫**的原始 Quaternius CC0 深棕馬和白馬上。所有修改留在獨立 PR #13，沒有覆蓋 main。

## V2.1 — 馬蹄表面實測，不再把骨頭尾端當蹄底

已成功的 Actions：https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41012482918

- 用 `scripts/motion/horse_hoof_surface_qa.py` 重新開啟原始 V2 BLEND，單獨啟用 Gallop。
- 讀取實際 Armature-deformed mesh 中 material='Hooves' 的網格（每蹄 **75 個頂點**）；40 個子影格、四蹄取最底部約 8.3% 頂點求中心。
- 實測「接近各蹄自身最低位置」時的最大逐格水平位移／模型高度：
  - 前左 3.3329%
  - 前右 3.7627%
  - 後左 5.0184%
  - 後右 4.5073%
- 舊版以後右腿骨尾端估計出 5.61% 最嚴重；實際接地材料頂點顯示後左蹄更高。**不能把舊的骨端位移叫做真正蹄底滑行**。
- 匯出 `hoof_surface_qa.json`／`hoof_surface_trace.svg`；兩匹馬採用相同來源動作，量測相同。

## V2.1 — 不改原始 Gallop 的移動速度校正

計算程式：`scripts/motion/horse_root_motion_fit.py`。成功的 CI：[Root Motion Calibration](https://github.com/aitest-ai/3dcodeverse-lab/actions/workflows/racing-horse-motion-calibration.yml)。

將四蹄合計 **46 個接近最低位置的連續區間**，以最小平方擬合角色 root 於原始 Blender local Y 的移動量：

- `root_translation_y_source_units_per_action_frame = -0.373507705`
- 不額外移動角色時，逐格接地區間 XY RMS 殘差：`0.152943` 原始場景單位
- 採用擬合速度後殘差：`0.066121` 原始場景單位
- 估算平均殘差降低 **56.77%**。這是原地跑動的**軌跡配對計算**，不是動態碰撞、腳蹄物理、坡道 IK、或真實跑速。沒有重寫現有的 13 段 Action。
- 網頁版 `examples/racing-horse/index.html` 在開啟沿跑道移動後，根據 `race_motion_calibration.json`、Gallop 的 glTF 時長與模型正規化縮放，估計橢圓賽道前進速度。Walk 沒有獨立擬合，其移動係數仍是啟發式；Idle 固定停止。
- 真正遊戲中的腳蹄接地是否正確，仍需接入地面碰撞、腳蹄表面檢測與動態 IK 後測試。

## V2.2 — 髮束、皮毛與馬蹄 PBR 改善

- 原始碼：`scripts/horses/horse_v22_finish.py`
- 成功 CI：[V2.2 Blender Cycles](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41013238601)
- Artifact：`horse-v22-5`（含兩匹馬各自 `.blend`／`.glb`／四視角實際 Blender Cycles PNG 與品質報告）。
- 皮毛 roughness 從 V2 約 .37 提升至 .67，明顯降低反光塑膠條紋；鬃毛 .78，馬蹄 .72。
- 在原始 Hair material mesh surface 上取樣，每匹建立 **153 組**短髮束（765 額外頂點）；以原始髮面頂點權重綁定相同 50 根骨，實際 GLB 保留兩個 skinned meshes。
- 依然保持 50 骨和 **13 段原始動畫**；新增 geometry and PBR 不取代原馬網格。
- **美術驗收仍有限制**：只是小幅改善層次，並非照片級鬃毛或毛髮模擬。馬肩、臀肌肉、前膝、後跗關節和蹄部真實解剖仍要真正高精度馬模型；不要誤稱全部修復。

## 嚴格版本管理及安全

- V2.2 的第一個 CI 雖然出圖成功，獨立驗證曾錯把 GLB「Mesh datablock 名稱」當成「節點物件名稱」，產生偽陰性。確認 GLB 實際節點 `ManeTail_IndividualWisps` 已匯出，改用 node 名稱核對；CI 最新版本已成功。
- 完整模型驗收要同時看材質、真實 Blender 圖片、網格與動作；不應以單一 CI 綠燈等同高寫實。
- 來源 Quaternius Ultimate Animated Animals **CC0**。更寫實的第三方馬模型／Blender 場景必須依作者或平台授權，不能繞過登入或將非 CC0 模型當成本庫可再分發資源。
- 成品輸出有效期限依 GitHub Actions Artifacts 設定（目前 14 天）；有需要可由工作流程再生成。

## 直接測試

`examples/racing-horse/index.html` 提供可選 Gallop／Walk／Idle、速度倍率、沿橢圓跑道移動。使用 `Racing Horse V2.2 — Package Playable WebGL Demo` 的 Artifacts 才會包含最新 V2.2 GLB＋`race_motion_calibration.json`。需於本地資料夾執行：

```bash
python3 -m http.server 8000
```

再開啟 `http://localhost:8000`。**網頁語法與模型結構經自動檢查，但瀏覽器操作、手機 FPS、真實碰撞仍需實機驗收。**

## 下一階段 V3

與其把現有 13k triangles 的 Quaternius 模型無限細分，應優先測合法取得的高精度馬（例如 BlendSwap Horse Rigged All Gaits 等），補足馬的解剖正確性、真實毛髮、鞍具騎師、速度與關節動作轉換。目標是用這一輪建立的 hoof-mesh 檢測及速度擬合，驗證新馬的 Gallop，而不是只看單張漂亮渲染。
