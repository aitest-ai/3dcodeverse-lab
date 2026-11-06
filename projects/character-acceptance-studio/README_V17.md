# 雙身形跑步手肘與衣袖驗收場 0.17.0

Vivi 0.5.0 與 Vita 0.4.0 改用隨步態變化的跑步肘角，並保留可編輯的肘窩皮膚／衣料修正形態鍵。Vivi 為 68–92°，Vita 為 68–80°；Vita 的較大彎曲試作會造成更深折疊，已拒收。兩者沿用自己的骨架與身形，沒有複製不相容的骨骼旋轉。

下載同一 Actions artifact 內的 Runtime、Sources ZIP，解壓到同一個 `Character_Studio_0.17.0` 目錄。網頁檢視只需 Runtime；修改及重建需兩包與 Blender **5.2.3 LTS**。

```sh
python START_STUDIO_V17.py --open
```

瀏覽器入口為 `http://localhost:8812/web-v17/`；Windows 可雙擊 `START_WINDOWS_V17.cmd`。選 Vivi 或 Vita，勾選同鏡位比較，A 是固定 V16 基準，B 是 V17 候選。可播放七段動作、暫停、調速、逐格、循環，切換前／側／背面、左右手肘、肩腋近景。「肘窩皮膚／衣料修正」開關可查看相同動作有無局部修正；停用狀態僅供診斷，是已拒收的試作。觀察 JSON 記錄此開關、角色版本、雜湊、相位與鏡位。

`evidence-v17/index.html` 提供 56 張實際瀏覽器連續畫面與兩段錄影，包含同姿勢修正開關比較。CPU 錄影可能掉幀，實際影片長度見 `video-probes.json`，不是手機或 GPU 效能測試。

母檔路徑見 `library-v17/catalog.json` 的 `editable.path`。Sources 保留前後版本母檔、原 VRM、原解析度貼圖、原生骨架與修改腳本。原 `.vroid` 工程未取得，Blender 檔是可編輯衍生工作副本。來源、作者、授權與輸入雜湊見 [THIRD_PARTY_V17.md](THIRD_PARTY_V17.md) 及 `docs/INPUTS_V17.json`。

從未產出候選的工作目錄重建：

```sh
python scripts/bootstrap_inputs_v17.py
blender -b -t 4 --python-exit-code 1 --python scripts/build_arms_v17.py
```

輸出至 `work/v17-build`，拒絕覆寫已存在版本。離線 Sources 已含固定輸入，不需帳戶；乾淨 Git checkout 首次需讀取固定的同庫 V16 Actions artifact，或指定 `bootstrap_inputs_v17.py --artifact 已保存的V16外層.zip`。該舊 artifact 到期後，請使用本版 Sources 內的 `inputs-v17`；不要改成下載「最新版」。

另存新版母檔後，可編輯 Run 的左右前臂旋轉、Body 的 `Run_ElbowSleeveCorrective` 形態鍵座標及其 Run 權重曲線，匯出新候選：

```sh
blender -b -t 4 --python-exit-code 1 --python scripts/export_arms_v17.py -- --character vivi --mother my-vivi.blend --output my-vivi-candidate.glb
```

匯出器拒絕基礎網格、UV、權重、骨架、材質、其他動作、修改器或驅動器等超出範圍的變更；這些修改需要完整資產匯出流程。原網格與貼圖位元組保留，Run 的新 morph 會改變局部表面；切回其餘六段則恢復原表面。Blender 預設以 60 fps 烘焙，局部擬合及瀏覽器碰撞以 120 Hz 檢查。

跨專案需以 `asset_id + version + SHA-256` 固定取用，可用 `scripts/pin_arms_v17.py --help` 複製候選與來源資訊；不得自動替換地圖人物。新匯出需重新驗收與新版本。

本版程式／Blender／瀏覽器證據分列於 `evidence-v17/acceptance-summary.json`。局部衣袖交叉已修正，但來源模型原有腋下皮膚自交仍保留；未檢驗完整衣服包覆、厚度、所有姿勢與遊戲控制器轉場。手機真機、人工美術、Godot／地圖實測未完成，所有資產維持 `art_approved=false`、`game_ready=false`。動作仍是專案程序化候選，不是動捕、AI 訓練或布料模擬。
