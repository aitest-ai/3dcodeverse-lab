# 人物 V3｜從原始 BLEND 精修的實際驗收記錄（2026-10-30）

## 為何改變工作流程

先前嘗試以 `bpy.ops.import_scene.gltf` 直接重新匯入已套蒙皮的 MPFB GLB，產生嚴重的髮片、衣物和骨架變形。該次失敗的 Actions 雖有產出 PNG，但**不具遊戲可用性，不可當作成品**。應停用 `scripts/characters/polish_from_glb.py` 這條有缺陷的實驗路徑。

現改成 **原始 BLEND 優先**：

1. 從已通過驗證的 Actions #15 下載 `human_mpfb_blender5.blend` 和 `.glb`。
2. 解析 GLB 的 11 張內嵌 PBR 圖片，抽取為 PNG／JPG。
3. 開啟真正的原始 `.blend`（不是重新匯入 GLB），比對材質圖片名稱，重新連接並 Pack All。
4. 對既有頭髮頂點做溫和的長度變形；不刪除網格、UV、頂點權重或新增漂浮髮片。
5. 保留原本服裝、皮膚、骨架與真實材質，匯出新版 BLEND、GLB。
6. 使用 Cycles CPU 產生正面、側面、背面、斜角、臉部與衣服特寫六張圖。
7. 獨立檢查 GLB 內的 skin、PBR 圖片、網格、人物高度，以及與原始版本一致的骨架。

## 可重複執行的檔案

- `.github/workflows/human-style-polish.yml`
- `scripts/characters/polish_original_blend.py`
- `scripts/characters/contact_sheet.py`

成功執行：[GitHub Actions #10](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/40997241778)，Artifacts：`human-polish-10`，有效期限依 GitHub 設定。

## 實際結果

| 項目 | Studio | Street | Sport |
|---|---:|---:|---:|
| 外觀 | 較短髮長 | 原版長髮 | 中短髮 |
| 人體高度 | 1.6946m | 1.6946m | 1.6946m |
| 人體骨架 | 53 | 53 | 53 |
| 模型網格 | 9 | 9 | 9 |
| GLB Skin | 1 | 1 | 1 |
| GLB 材質 | 9 | 9 | 9 |
| 內嵌貼圖 | 11 | 11 | 11 |
| PBR 圖片成功重新連線 | 11/11 | 11/11 | 11/11 |
| Cycles 六視角 | 完成 | 完成 | 完成 |

注意：**這三版仍是同一件休閒上衣、牛仔褲與鞋子，只測試了不同髮長與微幅材質參數**。它們不能稱為已經完成不同服裝剪裁、高模新髮型、真實物理髮束、動畫變形或臉部表情。

## 下一階段真正應該做的品質提升

- 確保外部 MakeHuman Hair02／Shirts01／Pants01 資產可穩定下載或以授權核對過的鏡像提供，**下載前後要比對檔案雜湊值**。
- 將不同套裝匯入原始 MPFB BLEND，而不是在已綁骨 GLB 上重新創造人體拓樸。
- 實際以不同服裝生成前／側／後／臉／衣服特寫，檢查穿模與蒙皮。
- 進一步用近拍和跑步、彎肘、轉頭姿勢驗證服裝變形；膚質和髮線需個別精修。
- 實測 Three.js／手機 GLB 載入後的記憶體與 FPS。

## 文件真實性

儘管開發腳本中出現 `studio`、`street`、`sport` 這些名稱，**目前可驗收的差異僅限於髮長**；原先的高面數 Bob、Fisherman Sweater、Cargo Pants 等仍待外部資產真正成功匯入。這份文件優先記錄已驗證事實，不誇大品質。
