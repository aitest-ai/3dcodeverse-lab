# Character Lab 0.14：馬匹步行接縫修正

2026-11-06（Asia/Taipei）。接續 [v13 Draft PR #159](https://github.com/aitest-ai/3dcodeverse-lab/pull/159) 的 `fac4b1c99de06a0d6a75617a231ecb8626e6dcf5`，獨立分支 `feat/character-studio-v14-horse-smooth-20261106`。本輪處理既有馬匹步行與起停銜接；人物、服裝、其他地圖和母檔未覆寫。

## 啟動與驗收

下載成功 Actions 的 review artifact，解開外層 ZIP，再把 Runtime 與 Sources 解到同一個 `Character_Studio_0.14.0` 資料夾。Runtime 可單獨操作；下載母檔及重建需要 Sources。

```sh
python3 START_STUDIO_V14.py --open
```

Windows 可執行 `START_WINDOWS_V14.cmd`。網址 `http://localhost:8806/web-v14/`，需要 Python 3 與 WebGL 瀏覽器；套件內含 Three.js，無 CDN／付費服務或額外帳戶需求。

- 左側選棕馬或白馬。A 是**原封保留的 v13 鎖蹄候選**，B 是本輪接縫修正版；兩者同鏡位、同根位移、同接地時序。A 並非前輪未鎖蹄失敗試驗。
- 預設播放完整「起步 → 步行兩輪 → 停步」。選單可單獨播放全部 18 段動作；此輪只修改 `WalkWorld`、`StartWalk`、`StopWalk` 的身體曲線。
- 「跳至循環接縫」停在完整序列的步行交界，切到後足近景。可選 1/60 或 1/240 秒逐格、調速、暫停、拖曳時間、切前／側／後／關節鏡位、錄影及匯出觀察。
- 「多視角證據」提供 560 張實際瀏覽器畫面和兩段 WebM；每格附 ID、版本、SHA、動作時間與鏡位。錄影可能因軟體繪圖掉格而縮短編碼時長，請用互動播放判斷正常速度。
- 綠／橙標示預定支撐／擺動；紫點是四個 shoulder 骨頭的平均投影，**不是物理重心**。重播完整序列會重置起點，尚非可中斷的移動控制器。

## 修改範圍與結果

v13 首尾位置已接齊，但步行交界仍有約 0.3694 m/s 的單邊表面速度差（1/240 秒取樣）。縮小取樣間隔後仍約 0.356 m/s，確認存在烘焙曲線的速度跳變。

v14 在原生 `Walk` 的循環首尾各 **1.5%（17.5 ms）** 建立局部 TRS Hermite 過渡，加上保留原接縫姿勢的四次曲線約束，再正規化旋轉，再使用既有固定腿長與世界鎖蹄求解。一般身體曲線 240 Hz，交界附近加密至 2400 Hz；這是局部動畫取樣密度，並非瀏覽器需要跑 2400 fps。修正區外的原生輸入姿勢、原有步幅、速度、20 mm 姿勢下修、3 mm 蹄面高度均沿用。密集取樣也暴露舊通用橋接器在 `D-window` 恰好相等時會外插的邊界問題；本輪專用 evaluator 已修正，舊檔保持原狀。

先前首尾各 12% 的試驗，以及未保留原接縫姿勢的 1% 試驗，都增加較大時間間隔下的速度變化，未採用。試驗與來源皆保留，不把失敗候選當成成品。本輪 1/240 秒交界速度差約由 0.369 降至 0.139 m/s；1/60 秒約 0.621／0.622 m/s，並非所有尺度都下降。最終 A/B 數據請見 `evidence-v14/acceptance-summary.json`、`joins-and-root.json` 和本階段 checkpoint；六種取樣間隔分開呈現，避免把正常加速度與線性烘焙殘餘速度差混為一談。**仍不宣稱數學上完全 C1 平滑或已通過人工自然度驗收。**

根節點三段動畫的 channel、sampler、存取資料保持原封不動；其他 15 段動作、節點、rest、幾何、權重、材質、原解析度貼圖及來源 BIN 前綴精確保留。完整序列仍為 9.333333 秒、5.6 m，巡航 0.8 m/s。這是既有原生骨架的程序修正，不是新動捕或自訓模型。

## 資產位置與固定取用

| 內容 | 位置 |
| --- | --- |
| 瀏覽器工作室 | `web-v14/` |
| B 完整 GLB／Blender 母檔／profile／修改紀錄 | `library-v14/horse-{brown,white}-walk-smooth-review/0.1.0/` |
| A 原封保留的直接輸入 | `library-v13/horse-{brown,white}-walk-transition-review/0.1.0/` |
| 原始來源與材質 | `sources-v04/horses/`、`library-v04/horse-{brown,white}/2.3.0/` |
| ID＋版本＋SHA-256 | `config-v14/horses.lock.json` |
| 文字 TRS 曲線 | `motion-v14/horse-smooth-curves.json` |
| 前後比較與分類驗收 | `evidence-v14/index.html`、`acceptance-summary.json` |

從 lock 取得完整 SHA 後固定取用：

```sh
python3 scripts/pin_horses_v14.py --id horse-brown-walk-smooth-review --version 0.1.0 --sha256 <lock內的完整SHA256> --dest ./horse-smooth-review --review-candidate --include-mother
```

拒絕錯誤 ID／版本／雜湊和已存在的目的地。v13 A 不重新發行為 v14；需舊版時使用其原來鎖定檔。profile 的顯示比例只套用一次；根位移已在 GLB 中，完整序列只加上前段累積距離。不得因為別的專案更新而自動替換。

## Blender 編輯與可重現匯出

四套完整母檔各有 50 骨、18 段骨架動作及 3 段 root action。Blender 5.2.3 LTS、24 fps；`AnimalArmature` 指派動作，`StudioTravelRoot_v11` 同步指派相應的 `WalkWorld_Root`、`StartWalk_Root` 或 `StopWalk_Root`。其他原地動作清除 root action 並將 root location 歸零。

```sh
STUDIO_V14_OUT=./work/new-rebuild blender -b -t 4 --python-exit-code 1 --python scripts/build_horses_v14.py
blender -b -t 4 --python-exit-code 1 --python scripts/export_horses_v14.py -- --id horse-brown-walk-smooth-review --mother ./edited.blend --output ./new-candidate.glb
```

密集母檔關鍵格以整批排序寫入，避免一般插鍵及 `FCurve.update()` 合併相距 0.01 frame 的關鍵格；冷開與回匯另行驗證。

重建必須重新求解，與固定文字曲線比較（component 容差 1e-5），再輸出固定 float32 GLB；完整 GLB SHA 應一致。Blender 母檔按該次實際檔案記錄 SHA，不宣稱跨機儲存位元一致。

匯出器只允許三段身體動作修改，保留根位移及片段長度。改變原有動作、根曲線、幾何、權重、rest、材質、父子關係會被拒絕。新匯出仍是未驗收候選，須重做接地、接縫與畫面檢查，另建 ID／版本／SHA。

直接重建依賴已包含在 Runtime＋Sources。完整倉庫流程 `scripts/run_validation_v14.py` 會依序重建 v10→v11→v12→v13→v14、冷開母檔、瀏覽器量測、擷取畫面、打包及乾淨解壓重建；不要在已有輸出的目錄跑全流程。

## 驗收邊界與下一步

程式檢查、Blender 冷開、瀏覽器蒙皮表面與實際操作分開記錄。手機真機、GPU 效能、人工美術、真正 COM／地面力、完整自碰撞、Godot／遊戲／地圖均未測；390px 桌面視窗只驗排版，本輪未另製離線渲染。

兩色共用同一解剖身形，**不是第二種身形適配**，也不代表原任務的人物與服裝已完成。沒有新增呼吸待機、任意相位中斷、停止後不重置的再起步、倒退、轉向或斜坡動作。下一步先依實際 A/B 播放做自然度與後腿關節驗收，再建立可中斷起停控制，保留人物／服裝與另一身形的待辦。

僅提供 Draft PR 與 review artifact，預設保留 90 天；未發布正式 Release、合併 PR 或更新其他網站。
