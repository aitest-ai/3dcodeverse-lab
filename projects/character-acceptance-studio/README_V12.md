# Character Lab 0.12：四拍與支撐驗收

日期：2026-11-05（臺灣時間）。接續 [v11 Draft PR #157](https://github.com/aitest-ai/3dcodeverse-lab/pull/157) 的 `048999387b1c641499ecb0f7436d2d55cc855246`，獨立分支 `feat/character-studio-v12-horse-support-20261105`。本輪完成馬匹 WalkWorld 時序修正與支撐診斷，不修改既有人物、服裝、母檔、main 或其他地圖網站。

## 啟動與操作

從本輪 Draft PR 的成功 Actions 下載 review artifact，解開外層 ZIP，再將 Runtime 與 Sources 解到同一資料夾 `Character_Studio_0.12.0`。Runtime 可單獨瀏覽；母檔下載／編輯需要 Sources。

```sh
python3 START_STUDIO_V12.py --open
```

Windows 可執行 `START_WINDOWS_V12.cmd`。網址 `http://localhost:8799/web-v12/`，不可直接以 file:// 開啟。需要 Python 3 與支援 WebGL 的瀏覽器，無 CDN 或額外帳戶需求。

左側選棕馬／白馬，預設 WalkWorld。A 是完整 v11 原版候選；B 是 v12 四拍支撐候選。可播放、暫停、60 fps 逐格、改倍率、循環、切正／側／背／蹄部近景、錄製 6 秒與匯出觀察紀錄。載入有進度、SHA 驗證、錯誤與重試。

按「比較 v11 單蹄區間」會自動切到 WalkWorld 的 1.120 秒，改為俯視支撐：A 只有一個預定支撐蹄，B 有三個。開關「顯示預定支撐區與軀幹投影」可隱藏輔助線；綠色為預定支撐、橙色為擺動，兩側時序條使用各自版本的相位。關閉「跟隨位移」可觀察實際世界前進。

**紫點是四個肩關節頭的平均投影，不是真正重心。** 支撐區由預定支撐蹄的實際蒙皮蹄面頂點建立凸包。投影在區域外僅是幾何診斷，沒有質量、慣性、地面反作用力或動態穩定性的證明。

## 結果與範圍

| 項目 | v11 A | v12 B |
| --- | --- | --- |
| 最少預定支撐蹄 | 1 | 2 |
| 單蹄區間 | 2.142857%／每輪 25 ms | 0 |
| 兩蹄／三蹄區間 | 82.142857%／15.714286% | 85.714286%／14.285714% |
| 四次落蹄間隔 | 不等距 | 各 0.291667 秒 |
| 實測支撐蹄面最大滑動 | 約 0.0004 mm | 約 0.035 mm，低於 1 mm 門檻 |
| 最低蹄面高度 | 約 +3.0 mm | 約 +3.0 mm |
| 軀幹投影在支撐區外的取樣比例 | 約 53.3% | 約 42.9%，仍需觀察 |

相位 LH .19 / LF .44 / RH .69 / RF .94，支撐比例 15/28，保留 0.8 m/s、1.166667 秒週期、每輪 0.933333 m 及 20 mm 身體姿勢下修。身體參考點的軌跡與根位移未變，幾何關係的差異來自支撐區重排；不能稱為「物理重心已修好」。

實測使用 Chromium + SwiftShader，240 Hz × 三個累積世界週期；每側分別使用自己的支撐相位，不拿新相位套到舊版。除了算蹄數，也檢查預定支撐蹄的實際高度、整塊蹄面位移與循環接縫。數值是離散動畫／插值結果，不代表物理量測精度。原有 50 骨、所有節點／rest、幾何、權重、貼圖、其他 13 段動畫與根位移精確保留。

步態文獻支持左後→左前→右後→右前的四拍順序與兩／三蹄支撐；常見真馬後肢支撐比例約 0.60–0.70。本輪 0.5357 與現有顯示速度未達真馬運動學認證，較長支撐的候選曾出現原生腿長不可達，詳 experiments.json。來源素材與比例並非生物尺寸校正，還需要自然度與動態平衡驗收。

## 交付位置與固定取用

| 用途 | 位置 |
| --- | --- |
| 可操作工作室 | `web-v12/` |
| B 模型、完整母檔、來源與骨架設定 | `library-v12/horse-{brown,white}-walk-support-review/0.1.0/` |
| A v11 原版 GLB 與完整母檔 | `library-v11/horse-{brown,white}-walk-world-review/0.1.0/` |
| 原始素材、貼圖與授權 | `sources-v04/horses/`、`library-v04/horse-{brown,white}/2.3.0/` |
| 固定 ID＋版本＋SHA | `config-v12/horses.lock.json` |
| 相位／來源文獻／失敗試驗 | `config-v12/walk-plan.json`、`references.json`、`experiments.json` |
| 可編輯可攜 TRS 曲線 | `motion-v12/horse-support-curves.json` |
| 162 張瀏覽器連續畫面、兩段 WebM | `evidence-v12/index.html` |
| 分類驗收與原始量測 | `evidence-v12/acceptance-summary.json`、`*-world-contacts.json`、`support-math.json` |

版本均為 0.1.0，ID 為 `horse-brown-walk-support-review`、`horse-white-walk-support-review`。完整 SHA 見鎖定清單與 ZIP 清單。取用須指定 ID、版本與 SHA：

```sh
python3 scripts/pin_horses_v12.py --id horse-brown-walk-support-review --version 0.1.0 --sha256 <鎖定清單中的完整SHA> --dest ./my-review-pin --review-candidate --include-mother
```

拒絕未知組合與已存在目的地。這是驗收用候選，不會自動替換任何地圖。載入端須套用 profile 的顯示尺度一次；保留的 `StudioTravelRoot_v11` 包覆節點包含單輪原生位移，外層按公尺累積每輪位移。不能重複套用根位移。

## 可編輯母檔與重建

實測 Blender **5.2.3 LTS**，CPU 背景模式，沒有 GUI／GPU 宣稱。A、B 都有 14 段骨架動作與配對 `WalkWorld_Root`，原始貼圖已打包。檢視 WalkWorld：`AnimalArmature` 指派 WalkWorld、`StudioTravelRoot_v11` 指派 WalkWorld_Root，24 fps、frame 0–28。檢視其他原地動作時，清除 root action 並將 root location 歸零。

已解開 Runtime＋Sources，可輸出到新的資料夾重建 B：

```sh
STUDIO_V12_OUT=./work/my-rebuild blender -b -t 4 --python-exit-code 1 --python scripts/build_horses_v12.py
```

每次重新求解、與文字 TRS 曲線比較（容差 1e-5 component），再輸出固定 float32 曲線，GLB SHA 必須相同；母檔依該次輸出計算 SHA。匯出器拒絕覆寫。

編輯後輸出新候選：

```sh
blender -b -t 4 --python-exit-code 1 --python scripts/export_horses_v12.py -- --id horse-brown-walk-support-review --mother ./edited.blend --output ./new-candidate.glb
```

只支援 WalkWorld 與配對 root action 修改；若改到幾何、權重、材質、rest、父子關係或其他動作，會拒絕此動作專用匯出。新 SHA 必須重新驗收。完整乾淨倉庫可設定 `BLENDER_BIN`、`NODE_PATH`、`CHROMIUM_PATH` 後執行 `scripts/run_validation_v12.py`，重建 v10→v11→v12 並測試下載包；不要在已有生成輸出的資料夾執行整條流程。

## 驗收分類與下一步

- 程式、來源保留、鎖定取用、匯出保護：通過；舊二進位、13 段動作與根位移保留。
- Blender 冷開母檔：每馬 6548 身體頂點 × 五時點與瀏覽器比對；本輪沒有離線渲染或離線動畫影片。
- 瀏覽器實際操作：兩色 A/B、14 段動作、支撐跳點、輔助顯示、跟隨、逐格、倍率、錄影與雜湊錯誤測試；詳實際報表。
- 手機真機／GPU 效能：未測；390px 桌面視窗只驗排版。雲端軟體繪圖錄影可能掉格。
- 人工美術、真正 COM／地面力／動態平衡、完整自碰撞：未測。軀幹參考點仍可能位於支撐區外。
- 起步、停步、轉向、斜坡、Godot／遊戲／地圖整合：本輪未製作或未測。
- 白馬保留自己的頂點對應、材質分區與鬃毛；它是同身形變體，**不是第二種身形**。

下一階段製作起步／停步過渡，持續檢查支撐與身體銜接；人工自然度通過前仍保留候選狀態。新的二進位使用 90 天 retention 的 Actions artifact，可能受倉庫政策調整；程式與文字曲線保留在 Draft PR。沒有正式 Release、自動合併或網站更新。
