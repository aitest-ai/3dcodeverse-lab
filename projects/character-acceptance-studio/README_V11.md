# Character Lab 0.11：前進與鎖蹄候選

日期：2026-11-05（臺灣時間）。接續 [v10 Draft PR #156](https://github.com/aitest-ai/3dcodeverse-lab/pull/156) 的 `b8f734b66c148be2b960203b3de63a096f74a931`，獨立分支 `feat/character-studio-v11-horse-world-walk-20261105`。本輪只處理馬匹 Walk 的世界移動；所有既有人物、服裝、原始馬匹、main 與其他網站保留。

## 開啟與操作

從本輪 Draft PR 的成功 Actions 下載 review artifact，解開外層 ZIP，再把 Runtime 與 Sources 解到同一資料夾 `Character_Studio_0.11.0`。Runtime 本身即可瀏覽；Blender 母檔下載／編輯需要 Sources。

```sh
python3 START_STUDIO_V11.py --open
```

Windows 可執行 `START_WINDOWS_V11.cmd`。網址 `http://localhost:8795/web-v11/`；不可直接用 file:// 開啟。無 CDN 或帳戶需求，Python 3 + 支援 WebGL 的瀏覽器即可。檔案下載先核對 SHA-256，載入進度／錯誤／重試可見。

左側切棕馬／白馬；預設 `WalkWorld`。A 是本輪「僅加位移」的滑蹄試驗，B 是鎖蹄候選。勾選同鏡位比較、切正／側／背與前後足近景。可暫停、60 fps 逐格、調速度、循環、錄製 6 秒、匯出問題紀錄。關閉「跟隨位移」看世界前進；開啟時地面格線仍反映前進。其他 13 段 v10 動作原樣保留，並不自動獲得 WalkWorld 的驗收結果。

## 本輪結果與限制

- 新增 50 骨原生 `WalkWorld`，0.8 m/s、週期 1.166667 秒、每輪 0.933333 m。速度以既有顯示尺度量測，並非馬匹真實生物尺寸／速度認證。
- 來源前蹄支撐速度擬合 0.829–0.872 m/s，後蹄 1.422–1.429 m/s，不能單靠一個根位移速度消除滑步。候選採逐蹄支撐軌跡、穩定蹄面方向與原腿長 IK；身體姿勢下修 20 mm。未縮放腿長、身形或貼圖。
- 實際 Chromium + SwiftShader，240 Hz 取樣三個累積世界週期：A 最大支撐蹄面位移約 334.3 mm；B 低於 1 mm 驗收門檻（實測約 0.0004 mm，屬數值結果）。B 最低蹄面約 +3.0 mm，循環交接小於 0.1 mm。
- **仍待修正／判斷**：約 2.14% 週期只有一個預定支撐蹄；尚無質量分布、地面反作用力或真正 COM 驗證。接地規劃不等於物理接觸。20 mm 姿勢下修與擺蹄曲線的自然度須人工美術驗收。
- 白馬保留自己的頂點對應、材質分區與鬃毛。它與棕馬是同一解剖身形，**不是第二種身形**。

## 檔案與固定取用

| 用途 | 位置 |
| --- | --- |
| 可操作工作室 | `web-v11/` |
| B GLB／完整母檔／設定／來源 | `library-v11/horse-{brown,white}-walk-world-review/0.1.0/` |
| A 比較試驗 | `library-v11/horse-{brown,white}-walk-translation-trial/0.1.0/` |
| v10 直接來源 GLB／母檔 | `inputs-v11/v10/` |
| 未改動原版／貼圖／授權 | `library-v04/horse-{brown,white}/2.3.0/`、`sources-v04/horses/` |
| 鎖定 ID＋版本＋SHA | `config-v11/horses.lock.json` |
| 腳相位、速度擬合與姿勢適配 | `config-v11/walk-plan.json`、`config-v11/experiments.json` |
| 可編輯的可攜式 TRS 曲線 | `motion-v11/horse-world-curves.json` |
| 130 張實際瀏覽器連續畫面、兩段 WebM | `evidence-v11/index.html` |
| 分類驗收與原始量測 | `evidence-v11/acceptance-summary.json`、`*-world-contacts.json` |

B 固定 ID：`horse-brown-walk-world-review@0.1.0`、`horse-white-walk-world-review@0.1.0`。完整 GLB SHA：

```text
brown b5036b2f646bd7026d66aacf41249509ec1d44f0957124bf9c271c6d4125ddc9
white 8a95e2c2398a005e91d5b755fb80571b1ac415c3eb69ddec64841cb54dbea99d
```

```sh
python3 scripts/pin_horses_v11.py --id horse-brown-walk-world-review --version 0.1.0 --sha256 b5036b2f646bd7026d66aacf41249509ec1d44f0957124bf9c271c6d4125ddc9 --dest ./my-review-pin --review-candidate --include-mother
```

拒絕錯誤 SHA 或已存在目的地。這是供驗收的明確取用，不會更新任何地圖。載入端須套用 profile 的顯示尺度一次，WalkWorld 根節點已包含單輪原生位移；循環時外層累加公尺位移。不可把單輪根位移與外層累加重複套用。

## Blender 編輯與重建

實測 Blender **5.2.3 LTS**，CPU 背景模式；沒有桌面 GUI 或 GPU 渲染宣稱。完整 B 母檔有 14 段骨架動作，另有 `WalkWorld_Root` 物件動作，原始貼圖打包於母檔。檢查 WalkWorld 時，將 `AnimalArmature` 指派 `WalkWorld`，`StudioTravelRoot_v11` 指派 `WalkWorld_Root`，24 fps、frame 0–28；其他原地動作須清除 root action 並把 root location 歸零。髮尾與骨架只各套一次外層位移。

重建本輪 GLB（拒絕覆寫）：

```sh
STUDIO_V11_OUT=./work/my-rebuild blender -b -t 4 --python-exit-code 1 --python scripts/build_horses_v11.py
```

每次重新求解，先與文字曲線比對（容差 1e-5 component），再匯出固定 float32 曲線，保證跨建置 GLB 雜湊一致。數值求解不符就失敗，不會靜默取舊結果。

編輯母檔後輸出新候選：

```sh
blender -b -t 4 --python-exit-code 1 --python scripts/export_horses_v11.py -- --id horse-brown-walk-world-review --mother ./edited.blend --output ./new-candidate.glb
```

此匯出器只支援 WalkWorld 與配對 root action 修改；若改到幾何、權重、材質、rest、物件父子或其他 13 段動作，會拒絕。重新匯出會有新 SHA，必須再做瀏覽器與人工驗收。從原始 2.3.0 重建 v10 輸入可用 `STUDIO_V10_OUT=./new-inputs blender ... --python scripts/build_horses_v10.py`；不要覆寫既有輸入。

## 驗收分類

| 類別 | 狀態 |
| --- | --- |
| 程式／結構／原始資料保留／版本與 SHA | 通過；13 段原片段與舊 BIN 精確保留，幾何編輯拒絕匯出 |
| Blender 冷開母檔與重新匯出 | 通過；6548 身體頂點 × 5 時點 × 2 馬與瀏覽器比對，最大約 0.002 mm |
| 本輪 Blender 離線渲染／動畫 | 未製作；未沿用 v10 畫面當成本輪證據 |
| 瀏覽器實際操作與世界鎖蹄 | Chromium 軟體繪圖通過；130 張連續畫面＋兩段實際錄影 |
| 手機真機／GPU 效能 | 未測；390px 桌面視窗只算排版檢查 |
| 人工美術／自然步態／物理平衡 | 未測；單蹄支撐時間、姿勢下修列為待修正／判斷 |
| Godot／遊戲／地圖整合、起停、轉向、斜坡 | 未測 |

軟體繪圖會掉格，WebM 真實編碼時長見 `video-probes.json`，不以其推論手機效能。交付為 90 天 retention 的 Actions artifact，可能受倉庫政策影響而提前失效；程式、設定與文字曲線持續留在 Draft PR，可重建。沒有發布正式 Release 或自動合併。

下一階段優先：依真人／獸醫步態參考重整支撐相位與重心，人工比較 20 mm 姿勢變化，再接起步、停步；確認後才測真正不同體型的四足角色。
