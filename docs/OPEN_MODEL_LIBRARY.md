# 開源模型庫與跨專案分工

動手建模前先查現成模型。這份文件與 GX10 上 `asset-factory` 的 `docs/開源模型庫.md` 同一套規則。

## 兩邊的分工

| | 本庫（GitHub Actions） | GX10 `asset-factory`（私有） |
|---|---|---|
| 擅長 | Blender 5.2、sand3d 程式建模、骨架動畫 | GPU 圖生 3D、手機壓縮、驗收網頁 |
| 不能做 | 跑生成模型（沒有 GPU） | 跑 sand3d（`bpy` 沒有 Linux ARM 版） |
| 模型庫 | `scripts/library/library.py` 要用才抓；用到的才發 Release | `~/asset-library/` 完整鏡像 |

## 接力方式

- **有結構或要會動的模型：** 這裡建好 GLB，交給 GX10 走路線 E 壓縮、驗證、驗收。
- **造型複雜、不動的模型：** GX10 用路線 B 生成。生成成品有地區授權限制，**不放進這個公開 repo**。
- **模型本身不進 git：** Actions 成品 14 天後就消失，要留用的發 Release。

## 怎麼用

```bash
python3 scripts/library/library.py search --type chair --text wood --limit 10
python3 scripts/library/library.py pull B07H376LF5 --dest public/models
```

Sand3D 的物件在 Actions 執行 **Sand3D build**，填資料集與物件 id，或在分支上：

```bash
python scripts/sand3d/build_object.py --dataset simready --id simready-pail_screwTop_white_glossy_a01
```

資料集的程式是別人寫的 Python，只在 Actions 這種用完就丟的環境跑。

## 來源與授權

| | ABO（`codepawl/abo-glb`） | Sand3D（`Sandflow/sand3d-*`） |
|---|---|---|
| 內容 | 7,953 件真實尺寸的商品模型，以家具、家飾為主；單一網格、不能動 | 約 10 萬件程式寫成的物件，有零件名稱，部分有關節 |
| 授權 | CC BY 4.0（已對照 Amazon 2023-06 的授權檔；論文與 AWS 登記頁仍寫舊的非商用） | 程式與檔案 CC BY 4.0；來源物件各有授權，每筆有 `attribution` |
| 注意 | 有些模型帶品牌標誌，商標不在授權內；簡化版要 `KTX2Loader` | `f_score` 是它自己量的；Objaverse 那批門檻只有 0.70 |

CC BY 要求署名、授權連結、標明修改。`library.py pull` 會寫 `<id>.credit.json`，`build_object.py` 會把署名寫進 manifest 與 report，**這些文字要跟著模型走**。
