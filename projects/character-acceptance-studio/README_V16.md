# 雙身形跑步手型驗收場 0.16.0

本輪回到 Vivi 與 Vita，修正跑步時過度張開的手型。更新 Run 的 30 根手指與 2 根上臂旋轉；其餘六段、骨盆、腿、根位移、衣鞋、蒙皮與原解析度貼圖保留。兩位是原生比例不同的人物：Vivi 152 joints，Vita 155 joints，腿長約相差 27%，掌寬約相差 17%。不是同人物換色。

下載同一個 Actions artifact 裡的 Runtime 與 Sources ZIP，解壓到同一個 `Character_Studio_0.16.0` 目錄。只看網頁需要 Runtime；修改及重建需要兩包。未安裝 Python 時先安裝 Python 3，再執行：

```sh
python START_STUDIO_V16.py --open
```

瀏覽器開啟 `http://localhost:8810/web-v16/`。Windows 也可雙擊 `START_WINDOWS_V16.cmd`。選 Vivi 或 Vita，勾選「同鏡位比較」後，A 是本輪最新基準，B 是新候選。預設 Run，可切換 Idle、Walk、Start、Stop、TurnLeft、TurnRight；支援暫停、速度、逐格、循環、前／側／背面、雙手及衣襬近景，並可匯出帶版本與雜湊的觀察 JSON。影片與四個相位的連續畫面在 `evidence-v16/index.html`。

來源與授權見 [THIRD_PARTY_V16.md](THIRD_PARTY_V16.md)。原 `.vroid` 工程未取得，Sources 包包含原 VRM、衍生可編輯 Blender 工作副本、原貼圖及本輪修改前後母檔。查看 `library-v16/catalog.json` 的 `editable.path` 開啟對應版本；原始母檔保持不動，另存副本後編輯。

重建需要 Blender **5.2.3 LTS**。從空白工作目錄執行以下指令會讀取固定的 Vivi 0.3／Vita 0.2 母檔，輸出到 `work/v16-build`；已存在的候選資料夾會拒絕覆寫：

```sh
blender -b -t 4 --python-exit-code 1 --python scripts/build_hands_v16.py
```

只修改新版 Run 手指及上臂旋轉後，可將另存母檔匯出成新的候選 GLB：

```sh
blender -b -t 4 --python-exit-code 1 --python scripts/export_hands_v16.py -- --character vivi --mother my-vivi.blend --output my-vivi-candidate.glb
```

這個匯出器會拒絕其餘動作、幾何、權重、骨架、材質或時間軸的變更，避免默默丟失修改。要修改衣物或整段動作，需建立對應的完整資產匯出流程。新匯出檔必須重新驗收並取得新版本與雜湊。

跨專案以 `asset_id + version + model.sha256` 固定取用。`scripts/pin_hands_v16.py` 可核對並複製指定 GLB，拒絕覆寫目的檔。全部候選維持 `art_approved=false`、`game_ready=false`。不要直接替換地圖人物。

較深的握拳試作會在 PIP 指節產生交叉，已拒收。採用版本增加 MCP 指根彎曲、保留較小的中節彎曲；Vivi 上臂額外外展 2–20°，Vita 2–16°，依跑步相位避讓裙片；不是完整握拳控制器。手臂仍使用前版近似固定 62.5° 肘彎曲，衣服版型與身形沒有在本輪重做。手機真機、完整衣物碰撞、自然度與人工美術驗收仍未完成，詳見 `evidence-v16/acceptance-summary.json`。
