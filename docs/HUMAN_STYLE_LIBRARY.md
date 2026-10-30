# 人物 3D 高品質精修｜髮型 × 服裝 × 真實來源可追溯

更新：2026-10-30。**品質分層**：已測通的人體基底 ≠ 多造型角色 ≠ 專業遊戲可用角色。
這份文件描述現有 Blender 5.2.3 + MPFB 2.0.18 的實際腳本和開放資源輸入方式，供其他 AI 依規格接續。

## 確認來源與授權

| 素材包 | 原始網頁 | 授權 | 主要用途 | 實際製作狀態 |
|---|---|---|---|---|
| MakeHuman System Assets | https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html | CC0 | 基礎人像、眼睛、髮型、服裝、鞋 | 原版 #12、Cycles #15 已完成 |
| Hair 02 | https://static.makehumancommunity.org/assets/assetpacks/hair02.html | CC BY，作者 Elvaerwyn | 高面數波浪短髮等 | 本 PR 新增，需雲端驗收 |
| Shirts 01 | https://static.makehumancommunity.org/assets/assetpacks/shirts01.html | CC0，分別記錄原作者 | 上衣、毛衣 | 本 PR 新增，需雲端驗收 |
| Pants 01 | https://static.makehumancommunity.org/assets/assetpacks/pants01.html | CC0，分別記錄原作者 | 長褲、工作褲 | 本 PR 新增，需雲端驗收 |
| Hair 01 | https://static.makehumancommunity.org/assets/assetpacks/hair01.html | CC0 | 編髮、短髮候選 | 僅研究／尚未下載 |
| System Hair Materials 01 | https://static.makehumancommunity.org/assets/assetpacks/system_hair_materials01.html | CC0 | 不同髮色材質候選 | 僅研究／尚未匯入 |

授權需按單一素材記錄。**CC BY** 並非 CC0，若輸出含第三方髮型必須保留作者與來源。原始程式碼 MPFB 採 GPLv3+；這不代表所有外掛輸出都是 GPL，也不代表外部素材包沒有額外限制。

## 可切換造型

環境變數 `HUMAN_STYLE`；原本輸出資料夾分別為 `outputs/human_<STYLE>`，每套獨立保存 GLB、BLEND、六張預覽與驗收報告。

| STYLE | 髮型 | 衣服 | 來源授權 |
|---|---|---|---|
| `studio` | Elvaerwyn 波浪 Bob 短髮 | 系統正式套裝、鞋子 | Hair02 CC BY ＋系統 CC0 |
| `street` | 系統 Bob 短髮 | Fisherman sweater＋工作褲＋鞋子 | System、Shirts01、Pants01 均 CC0 |
| `sport` | 系統馬尾 | 系統運動套裝、鞋子 | System CC0 |
| `legacy` | 系統長直髮 | 系統休閒套裝 | 舊版比較基準，System CC0 |

### 執行

```bash
# GitHub Actions 自動下載外掛及素材包後的工作階段範例
HUMAN_STYLE=studio MAKEHUMAN_ASSET_ROOT=.deps/mh_assets \
  blender -b --python-exit-code 1 --python scripts/characters/create_mpfb_human.py
python3 scripts/characters/verify_mpfb_human.py outputs/human_studio
python3 scripts/characters/contact_sheet.py outputs/human_studio
```

實際雲端流程：[`.github/workflows/mpfb5-human.yml`](../.github/workflows/mpfb5-human.yml)。

## 驗收門檻：不僅看一張正面照

- **六張 Cycles / Blender 實際畫面**：正面、側面、背面、斜角、臉部近拍、服裝近拍。
- **骨架和蒙皮**：GLB skin、每件著裝／髮型與身體的位置關係、材質／貼圖數量。
- **服裝品質**：是否有衣服穿過皮膚、手腕／手肘／腰部露底、鞋底在地面之外等。
- **髮型品質**：髮際線、髮尾厚度、穿過肩膀／臉頰，卡片狀或塑膠片狀是否仍然明顯。
- **表情／動作**：現階段尚未加入完整 facial shapes，亦尚未實際測試跑、蹲、轉頭時衣物或髮絲變形；後續進行，不得宣稱已驗證。
- **效能**：GLB 先確認多網格、貼圖、檔案大小，再依網頁／手機目標規格減面、壓圖與重新驗證；高面數頭髮可能犧牲行動裝置 FPS。

### 已知限制

1. 前一輪皮膚與衣服在 Cycles 渲染有真實貼圖，但長直髮仍有一整塊髮板的外觀；新增高模短髮是待實測改善方案。
2. MPFB 的 `game_engine` 骨架可以在 GLB 匯出蒙皮，但不能直接假設已有 Mixamo、遊戲角色控制器或臉部表情。
3. 本輪目標是**建立可挑選風格、可追溯授權、可比較渲染**的角色資料管線，還不是逼真數位人完整製作完成。
