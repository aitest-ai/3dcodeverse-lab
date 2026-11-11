# Character Studio 0.18.0 — 雙身形肩腋描邊修正候選

新增 Vivi 0.6.0、Vita 0.5.0，固定比較來源是 V17 的 Vivi 0.5.0、Vita 0.4.0。局部 MToon 描邊遮罩減少反面描邊從肩腋摺疊穿出形成的暗色三角，保留其他輪廓線、原材質色彩與原解析度貼圖。所有幾何、權重、骨架、七段動畫與 V17 袖口保留。

Vivi 在指定跑步姿勢可見暗塊減少。Vita 同一姿勢及本輪抽查的其他姿勢未觀察到明顯像素差異，列為遮罩載入／動作相容性候選，**Vita 外觀改善尚未驗證**。

**這是顯示修正，不是幾何碰撞修復。** 肩腋仍有摺疊，來源皮膚交叉仍存在；人物比例、動作自然度及遊戲就緒未獲人工批准。本輪袖口細分試作在 Vivi 的待機／起停／轉身等片段新增交叉，已拒收，未列入可選資產。沒有新增外部角色；既有 20 款人物／動物庫保留原版本與候選狀態。

## 啟動與檢查

將同一次交付的 Runtime、Sources ZIP 解壓到同一個 `Character_Studio_0.18.0` 資料夾。只有 Runtime 也可使用瀏覽器；母檔與原 VRM 下載連結需 Sources。

```sh
python START_STUDIO_V18.py --open
```

開啟 http://localhost:8816/web-v18/ ，Windows 也可執行 `START_WINDOWS_V18.cmd`。選 Vivi 或 Vita，勾選同鏡位比較：A 為固定 V17，B 為 V18 候選。切換 Idle、Walk、Run、Start、Stop、TurnLeft、TurnRight；可暫停、改速度、60fps 逐格、循環及檢查起走停轉序列。

Run 0.175 秒的肩部近景容易看見來源暗塊；切換「局部肩腋描邊遮罩」，可在相同幾何與姿勢下比較。再檢查正／側／後、肩部、左右肘及手部近景。可匯出觀察 JSON、PNG 與瀏覽器錄影。連續畫面索引：`evidence-v18/frame-catalog.json`；兩份實際瀏覽器動畫：`evidence-v18/{vivi,vita}-run.webm`。

## 母檔與可重現匯出

每個版本目錄內包含 `model.blend`、`model.glb`、`skeleton-profile.json`、`adaptation.json`、`outline-mask.json`、`textures/shoulder-outline.png`：

- `library-v18/vroid-vivi-motion-review/0.6.0/`
- `library-v18/vroid-vita-motion-review/0.5.0/`

新遮罩為 2048×2048、10px 羽化，修改約 1.20% 像素。母檔內 packed image 名稱 `V18_Shoulder_Outline_Width`，Tops 材質自訂屬性指向此圖。原始貼圖全部保留。Blender 原生材質預覽不等同 MToon，描邊外觀以瀏覽器驗收。

Blender 5.2.3 LTS，背景 CPU 即可重建，無需 GPU、新帳戶或付費：

```sh
python scripts/bootstrap_inputs_v18.py
blender -b -t 4 --python-exit-code 1 --python scripts/build_surface_v18.py
# 僅 fresh checkout 需要凍結目錄
python scripts/prepare_registry_v18.py
```

重建寫入 `work/v18-build`。若資料夾已存在，設定 `STUDIO_V18_OUT` 到新目錄，避免覆寫。直接來源 V17 的 GLB、母檔與 profile 都在交付包內，可離線重建；fresh checkout 首次需下載固定 GitHub artifact。來源與 SHA 見 `docs/INPUTS_V18.json`。同主機 GLB 重建逐位元一致；母檔序列化雜湊可能跨次執行改變，以每次實際包內 catalog 為準。

本版匯出器只接受 packed 描邊遮罩的編輯。把新 2048px PNG 載入同名 image，Pack 並儲存為另一份母檔，再執行：

```sh
blender -b -t 4 --python-exit-code 1 --python scripts/export_surface_v18.py -- --character vivi --mother /path/edited.blend --output /path/new-candidate.glb
```

匯出拒絕覆寫檔案，也拒絕幾何、權重、UV、骨架、動畫、原圖片、材質或設定變動。完整母檔可另行編輯，但那些修改需要新的完整匯出流程。新匯出不會自動加入已固定的目錄。

## 驗證範圍與已知缺陷

- 程式與資產：原 BIN 前綴、所有幾何／拓樸／屬性、七段動畫、rest／skin、原圖片保持；唯一原擴充欄位變更是 Tops 的 `_OutlineWidthTexture`。
- Blender：母檔冷開、完整狀態比較、精確重新匯出、允許遮罩編輯、拒絕幾何編輯；提供七段指定姿勢的表面座標。
- 瀏覽器：實際 Chromium WebGL／SwiftShader CPU；兩種身形、七段 60Hz 原表面一致性、每段母檔表面對照、遮罩像素切換與恢復、播放／逐格／速度／序列／SHA 錯誤。390px 為模擬視窗。
- Blender 離線美術渲染、手機真機、本版 Godot、人工美術：未測。CPU 錄影可能掉格，不作硬體效能承諾。
- 已知缺陷：肩腋幾何摺疊、原袖口折線、原皮膚交叉。V17 特定 Run 120Hz 手臂區域已知 Vivi 9、Vita 3，並非全身碰撞數；本版幾何與動作完全不變，不重述為修復成功。

兩身形各自保留原生骨長、權重與 profile。共用的是局部描邊遮罩流程；兩者 UV 相同，因此可沿用同一批 47 個已核對的肩部面。其他 UV、拓樸或動物不能直接套用這張遮罩。

袖口拒收紀錄在 `docs/CUFF_REJECTED_V18.json`，演算法保留在 `scripts/v18/experimental/`，未進入 build／catalog。Vivi 60Hz 檢查新增交叉幀：Idle 25、Walk 4、Run 0、Start 17、Stop 14、TurnLeft 6、TurnRight 10；Vita 細分只做母檔與瀏覽器試作，完整碰撞未完成。不可把這些失敗試作當成成品。其他試作見 `docs/TRIALS_V18.json`。

下一階段優先修復肩腋實際幾何／權重與袖口接地形變，逐姿勢確認；通過後再擴充其他身形與動物。

## 固定取用與授權

授權、作者、來源及修改紀錄見 `THIRD_PARTY_V18.md`。每次交付按 `library-v18/catalog.json` 的 ID＋版本＋SHA-256 取用，不使用 latest。僅匯入隔離驗收場：

```sh
python scripts/pin_surface_v18.py --id vroid-vivi-motion-review --version 0.6.0 --sha256 <完整雜湊> --review-candidate --dest /new/review-folder
```

不修改 main、不合併 PR、不發布網站或 Release，不替換其他地圖資產。完整驗證結果見 `evidence-v18/acceptance-summary.json`。
