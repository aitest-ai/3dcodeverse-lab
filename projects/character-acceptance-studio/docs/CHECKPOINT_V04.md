# 模型庫 0.4.0 交接

本階段使用者追加：既有人物身形仍不理想，增加網路可修改的開源人物、VTuber、遊戲人物與動物，盡量擴大可用選項。

- 獨立分支 `feat/character-library-v04-open-models-20261104`，基於 v0.3 commit `6d3729627c27f49f5303729a46d4d5f0c041136f`；不更動舊母檔、舊 GLB、main、既有網站或合併任何 PR。
- 20 項模型：5 KayKit（4角色+兜帽變體）、3 VRoid beta CC0、10 Quaternius 動物、2 既有 v2.3 馬。固定目錄 `library-v04/catalog.json`；17 動畫資產，532 片段項目包含重複，不可稱為 532 個獨立動作。
- 原 GLB/VRM bytes 保留；Quaternius glTF 只做無損 binary 封裝；沒有改幾何、身形、衣物、原生動作、骨架 rest 或貼圖解析度。
- 12 原生 Blender 母檔、8 GLB/VRM 匯入工作副本。VRoid .vroid／KayKit 原作者 .blend 未取得。three-vrm 正確載入 MToon/表情；3 VRM 沒有動畫，不能把參考姿勢當 Idle；髮衣物理關閉。
- `START_STUDIO_V04.py --open` → localhost:8771/web-v04/，可搜尋篩選、載入進度／SHA攔截、原生動作、30 fps逐格／速度／循環、同鏡位A/B選型、等高顯示、近景／骨架、錄影與觀察JSON。
- 視覺燈光：PBR 與 MToon 用各自顯示燈強度，降低動漫白色材質過曝；只改檢視場景，不修改素材。
- 驗證：20 結構、58 原始來源、所有 accessor／buffer／image bytes；20 mother/working copy 冷開啟。10 原動物母檔有未被材質使用的缺失參考圖片，保留且記錄在 editor 報告。程式 exit code 不足以判定 Blender Python 通過；使用 `--python-exit-code 1` 和報告內容。
- 實際 Chromium：20 模型、每 native clip 抽3時點、352多角度PNG、20縮圖、native MToon 表情／SHA錯誤／取消過期載入等UI測試。完整資料在 `evidence-v04`；錄影依 ffprobe 的實際長度陳述，不把6秒計時等同6秒流暢畫面。
- 所有 art_approved/game_ready=false；人體自然動作、衣物碰撞、動物尺寸與接地、實體手機、其他引擎／地圖、人工美術未核准。390px測試僅版面模擬。
- 來源與合法權利見 `THIRD_PARTY_V04.md`，全部新下載為公開CC0，不含遊戲拆包、付費SOURCE內容、未確認條款VRoid新品。
- 交付 ZIP 以 runtime 與 sources 分開；省略重複原檔和已內嵌圖檔，由 `restore_library_v04.py` 用驗證過的 GLB 無損還原並拒絕覆寫不同內容。這不是畫質壓縮。完整來源鎖必須在兩包合併恢復後再次核對。

下一步：依實際模型選型做新修正版；先補動漫骨架語意／rest pose／軸向檢查與走跑重定向，動物校準物種合理尺寸、步態速度、腳掌／蹄接地。維持不同骨架家族，不能把人類動作直接搬到四足動物。可再擴 Kenney 與其他原作者資產；尚未下載的連結不得算成交付。
