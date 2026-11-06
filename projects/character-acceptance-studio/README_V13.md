# Character Lab 0.13：有限直線起步與停步

日期：2026-11-06（Asia/Taipei）。接續 [v12 Draft PR #158](https://github.com/aitest-ai/3dcodeverse-lab/pull/158) 的 `a6240e57f3154a0fa3060916d41edac1ddd74d0d`，獨立分支 `feat/character-studio-v13-horse-transitions-20261106`。本輪完成馬匹起停候選與可操作驗收；既有人物、服裝、母檔及其他地圖維持原狀。

## 啟動與操作

下載本輪成功 Actions 的 review artifact，解開外層 ZIP，再把 Runtime 與 Sources 解到同一個 `Character_Studio_0.13.0` 資料夾。Runtime 可單獨操作；母檔下載與重建需要 Sources。

```sh
python3 START_STUDIO_V13.py --open
```

Windows 可執行 `START_WINDOWS_V13.cmd`。網址 `http://localhost:8803/web-v13/`；需要 Python 3、支援 WebGL 的瀏覽器，不能直接用 file://。套件內含 Three.js，不需 CDN 或其他帳戶。

- 左側選棕馬／白馬，預設同鏡位 A/B，播放完整「起步 → 步行兩輪 → 停步」。可暫停、60 fps 逐格、調倍率、拖曳時間、切正面／側面／背面／蹄部近景／俯視、顯示骨架、錄影及匯出觀察。
- A 是**本輪新建的未鎖蹄過渡試驗**，不是 v12 已有或通過驗收的動作。它與 B 使用相同身體姿勢混合、加減速路徑；B 再解算世界座標的蹄部固定點。A 預期有腳滑、穿地及片段跳接，禁止當正式模板。
- 「起步接地檢查」「停步接地檢查」跳到對應時刻；時序條與蹄面高度協助對照預定支撐和實際蒙皮表面。紫點只是四個原生 shoulder 骨頭的平均投影，**不是物理重心**。
- 關閉「跟隨位移」可觀察實際世界移動。「完整起步 → 步行 → 停步」重新開始會重置起點；不是連續停止再起步、任意相位中斷或轉向控制器。
- 動作選單可單獨選 `StandReady`、`StartWalk`、`WalkWorld`、`StopWalk`、`StandStopped`。其他 14 段既有動作原樣保留；切換預覽不代表已完成任意動作間混合。

## 路徑與實測

完整序列長 **9.333333 秒**、行進 **5.6 m**，顯示尺度與 v12 相同。`StartWalk`、`StopWalk` 各 3.5 秒，中間原版 `WalkWorld` 兩輪共 2.333333 秒。加速與減速各 2.333333 秒，路徑速度由 0 漸變至 0.8 m/s 再回 0；身體用 1.166667 秒的平滑權重混合原生 Idle 參考姿勢與 Walk。這是程序動作，不是真人／真馬動捕，也沒有訓練模型。

保留 v12 的 20 mm 身體姿勢下修與 3 mm 蹄面安全高度，未拉長骨頭。預定支撐時蹄面固定於世界點；擺動時以平滑曲線移至下一落點。首尾四蹄落地，全程至少兩蹄預定支撐。兩個站姿片段是固定姿勢，沒有新增呼吸待機或原有 Idle 任意相位的銜接。

| 項目（兩色實測相同） | A 未鎖蹄試驗 | B 起停鎖蹄候選 |
| --- | --- | --- |
| 支撐蹄面最大滑動 | 約 466 mm | 約 0.035 mm |
| 最低蹄面高度 | 約 −31.1 mm | 約 +3.0 mm |
| 起步／步行的最大表面接縫 | 約 117 mm | 小於 0.001 mm |
| 步行／停步的最大表面接縫 | 約 117 mm | 小於 0.001 mm |
| 首尾預定支撐蹄 | 4／4（實際穿地） | 4／4，實際接地高度通過 |

Chromium + SwiftShader 以 240 Hz 取樣完整序列，每馬 2241 時點；量測實際蒙皮蹄面的高度與整片移動，不只算時序蹄數。數值是離散動畫與插值結果，不代表物理量測精度。Blender 5.2.3 LTS 冷開四套母檔，逐片段與瀏覽器比對全部 6548 個身體頂點。

**速度接縫仍有已知限制。** 以 1/240 秒的單邊表面速度估算，B 起步／步行與步行／停步接縫約 0.36943、0.36942 m/s；保留的 WalkWorld 自身循環基準約 0.36939 m/s。新銜接沒有明顯超過舊循環基準，但不能稱為完全 C1 平滑。根位移起終點的有限差分速度小於 0.001 m/s，位置與解析路徑一致；仍需改善原有步行的局部表面速度差與人工自然度。

軀幹參考投影約 40.2% 的整段取樣仍在支撐區外。此比例受有限序列與站立區間影響，不能直接當作 v12 循環的改善比例；沒有質量、慣性、地面反作用力或真正 COM 的動態平衡驗證。

## 交付與固定取用

| 內容 | 位置 |
| --- | --- |
| 可操作工作室 | `web-v13/` |
| B GLB、完整母檔、適配設定、修改紀錄 | `library-v13/horse-{brown,white}-walk-transition-review/0.1.0/` |
| A 未修正比較試驗與母檔 | `library-v13/horse-{brown,white}-transition-baseline/0.1.0/` |
| 直接輸入的 v12 GLB 與完整母檔 | `library-v12/horse-{brown,white}-walk-support-review/0.1.0/` |
| 原始來源與貼圖 | `sources-v04/horses/`、`library-v04/horse-{brown,white}/2.3.0/` |
| 鎖定 ID＋版本＋SHA | `config-v13/horses.lock.json` |
| 可編輯文字 TRS 曲線 | `motion-v13/horse-transition-curves.json` |
| 380 張實際瀏覽器畫面、兩段 WebM | `evidence-v13/index.html` |
| 分類驗收與原始量測 | `evidence-v13/acceptance-summary.json`、`*-transition-contacts.json`、`joins-and-root.json` |

所有 B 版本均為 0.1.0；完整 SHA 與母檔雜湊見 lock、catalog、adaptation 與 ZIP 清單。固定取用：

```sh
python3 scripts/pin_horses_v13.py --id horse-brown-walk-transition-review --version 0.1.0 --sha256 882fc780b7f0ed00c85dfa98afc6a4615fdeda5c6ae0cb53469b8f5e27880b2d --dest ./my-transition-review --review-candidate --include-mother
```

拒絕未知組合、錯誤雜湊、既有目的地及 A 對照。依 profile 套用顯示尺度一次；`StudioTravelRoot_v11` 保持原名。單片段內根位移已烘焙；完整序列只在外層加上前段累積距離，不能再乘速度或重複位移。操作版未寫入任何地圖。

## Blender 編輯、匯出與重建

四套母檔均保留 50 骨、18 段骨架動作與 3 段配對 root action。`AnimalArmature` 指派欲看的動作；起步／停步需同步將 `StudioTravelRoot_v11` 指派 `StartWalk_Root`／`StopWalk_Root`，原有 WalkWorld 配 `WalkWorld_Root`。24 fps；新起停 frame 0–84。站姿或其他原地片段要清除 root action，將 root location 歸零。

已解壓 Runtime＋Sources，可在 Blender 5.2.3 重建至新資料夾：

```sh
STUDIO_V13_OUT=./work/my-rebuild blender -b -t 4 --python-exit-code 1 --python scripts/build_horses_v13.py
```

每次重新求解並與文字 TRS 比較（component 容差 1e-5），才輸出固定 float32 GLB；不能略過新求解。GLB SHA 應相同，母檔按該次實際檔案計算雜湊，不宣稱跨機 Blender 儲存位元一致。來源與目的地都不覆寫。

編輯後匯出新的未驗收候選：

```sh
blender -b -t 4 --python-exit-code 1 --python scripts/export_horses_v13.py -- --id horse-brown-walk-transition-review --mother ./edited.blend --output ./new-candidate.glb
```

匯出器只接受四個新動作與起停配對 root action 修改。幾何、權重、材質、rest、父子關係或原有 14 動作改動會被拒絕；若改了時序或路徑，須重新產生適配設定並驗收，不能沿用舊 schedule、版本或 SHA。

完整乾淨倉庫設定 `BLENDER_BIN`、`NODE_PATH`、`CHROMIUM_PATH` 後執行 `scripts/run_validation_v13.py`，會重建 v10→v11→v12→v13、量測、截圖、打包及乾淨解壓重建。下載包提供直接 v13 重建所需依賴，完整歷史重建請使用倉庫；不要在已有生成輸出的資料夾執行全流程。

## 驗收分類與下一步

- 程式、來源 14 動作與原始二進位保留、原生腿長、固定取用、匯出保護：有實測報告；A 明確失敗，不可取作模板。
- Blender 冷開、瀏覽器表面一致性：有實測；本輪未製作離線渲染。
- 瀏覽器：實際 A/B、全程起停、18 片段預覽、播放操作、鏡位、錄影與錯誤重試。錄影使用 CPU 軟體繪圖，可能掉格，實際編碼時長與是否到達序列終點另列。
- 手機真機、GPU 效能、人工美術、真正 COM／動態平衡、完整自碰撞、Godot／遊戲／地圖：未測。390px 桌面視窗只驗排版。
- 白馬是同解剖身形的另一材質／鬃毛變體，**不是第二種身形適配**。本輪也不代表人形與服裝工作已完成。
- 任意相位中斷起停、停止後不重置的再起步、倒退、轉向、斜坡、原有 Idle 連續過渡：尚未製作。

下一階段先改善原有步行接縫的局部速度差與起停自然度，再擴展可中斷控制。保留 review candidate；Actions 二進位預設保留 90 天，無正式 Release、自動合併或網站更新。
