# 人物、服裝與動作驗收場 0.3.0

本階段修正 Harbor 的領片／領巾、胸前衣片、袖口與下襬，對 V29 阿伯的腰臀衣襬做獨立配版，並以實際 pelvis→neck 軸修正跑步前傾。**兩位仍是待人工美術驗收的候選**，`art_approved=false`、`game_ready=false`。原 0.2.0 母檔、GLB、貼圖、骨架及其獨立交付包不覆寫。

## 開啟

下載 Runtime_Source ZIP 解壓後執行：

```sh
python3 START_STUDIO_V03.py --open
# http://localhost:8769/web-v03/
```

Windows 可執行 `START_WINDOWS_V03.cmd`（需 Python 3）。左側選 Harbor／阿伯，選 Idle、Walk、Run、Start、Stop、TurnLeft、TurnRight。保留 60fps 逐格、速度、循環、串接、世界／跟隨位移、正側背與肘袖／胸腋／衣襬／腳部鏡位、PNG／WebM、固定 hash 的觀察 JSON。

**A=0.2.0 修改前，B=0.3.0 修改後**，兩位所有七段都有真對照，共用鏡位；本輪時長／根位移相同。取消「跟隨人物」可看原生 GLB 世界移動。起停與左右轉身串接不用 crossfade；任意 Run 轉換未納入。

Runtime 包附 `OPEN_STUDIO_V03.html`，嵌入真正程式、四份 A/B GLB 與各自 profile，不用 CDN／登入／付費服務。可由同一 localhost 開 `/OPEN_STUDIO_V03.html`；本環境禁止 file://，雙擊離線開啟未測。

Evidence ZIP 疊加解壓到相同 `Character_Studio_0.3.0` 根目錄，可由工作室底部「多視角動畫證據」開圖庫：384 張四鏡位＋64 張近景／世界位移、12 支四鏡位影片。影片每鏡位只有 8 個獨立取樣相位，24fps 是容器重複格，不代表 GPU 效能或逐瞬間的美術通過；請在驗收場連續播放。

## 母檔與重建

本版 Runtime 包保留 0.2.0 基準與 0.3.0 母檔／GLB／原尺寸貼圖、原上游 sources／作者授權、骨架設定、完整修改前後網格及權重記錄。本包不重複附 0.1.0 的候選及影片；它們仍保留在 Git 與原交付包。各 ZIP 內的 SHA 索引只涵蓋該包實際內容。

```sh
python3 scripts/bootstrap_blender.py --dest work/tools
python3 scripts/rebuild_v03.py --blender work/tools/blender-5.2.3-linux-x64/blender --output work/v03-rebuild
python3 scripts/verify_motion_v03.py --root work/v03-rebuild --out work/rebuild-numerical-qa.json
python3 scripts/verify_regression_v03.py --root work/v03-rebuild
```

需要 Blender 5.2.3。兩位在獨立 Blender CPU 背景程序中重建，預設只寫 `work/v03-build/`；指定輸出也禁止指向 `assets/` 或 `sources/`。不需 MPFB 外掛、GPU、外部動作模型或服務帳戶。

`build_character_v03.py` 讀取各自 0.2.0 原生 local channels，不搬用其他骨架；`garment_repairs_v03.py` 保存局部修版過程與原拓樸來源，`garment-change-log.json` 逐項保存 before／after。Harbor 新增衣片與袖口的拓樸有明確變動，阿伯保留原 MRT 衣服拓樸／UV，腰腹權重另有逐點轉移記錄。原身體、表情、鞋子、褲子與 rest bones 不變；貼圖不降解析度。

在 Blender 母檔的 NLA 中 solo 欲檢查的同名軌，或將其餘六軌靜音，再逐格檢查；七條軌是獨立匯出片段，不是同時混合播放的完整表演。網頁會直接選取各個 GLB clip。

只核對已交付版：

```sh
python3 scripts/verify_motion_v03.py
python3 scripts/verify_regression_v03.py
python3 scripts/verify_locks_v03.py
python3 scripts/build_standalone_v03.py
```

最後一步用 esbuild 0.25.12（或 `ESBUILD_BIN` 指向已裝執行檔），只有建置需要 Node；操作不用。冷讀母檔可在每次獨立 Blender 程序執行 `verify_editor_v03.py`，環境變數 `STUDIO_CHARACTER` 選角色，`STUDIO_V03_ROOT` 預設 `assets`。瀏覽器量測／截圖需 Playwright、Chromium；影片需 ffmpeg，這些測試工具不隨包安裝。

## 固定取用

`assets/registry-v03.json` 以 ID＋0.3.0＋完整 GLB SHA＋profile SHA 固定版本，沒有 latest。`scripts/pin_asset_v03.py` 預設拒絕未核准資產；只有指定 `--candidate-review` 才能複製到隔離審查目錄。ID／版本／hash 不符或目的地已存在即停止，不自動更新地圖。

服裝與姿態的改善、失敗與未測分開列在 `docs/GARMENT_STAGE_V03.md`、`evidence-v03/visual-review.json`。原 V111／彩虹橋精確資產仍缺，不退回 V103。沒有合併 PR、修改 main 或部署其他地圖網站。
