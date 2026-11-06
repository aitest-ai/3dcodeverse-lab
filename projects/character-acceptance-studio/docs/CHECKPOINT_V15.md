# v15 交接｜2026-11-06 Asia/Taipei

分支 `feat/character-studio-v15-horse-controller-20261106` 從 v14 `b8a0cfd1f8cf83cd6801138c3d658bfd8666338f` 分出；以 v14 分支為 Draft PR base。沒有混入其他分支、改 main、合併 PR、發布 Release 或更新地圖。

範圍：新 ID `horse-{brown,white}-locomotion-review@0.1.0`。保留 v14 原 18 GLB 片段／21 native actions／場景；新增 RestartWalk、WalkTurnLeft、WalkTurnRight 與三個 paired root actions。來源已授權，原母檔保存。完整 build/export/pin/package/review 入口見 README_V15.md。

控制器：SE(2) 累積 world transform；在完整 clip 邊界消耗最新意圖；停下不重設位置；先完成 StopWalk 才能 RestartWalk；停止清除待轉；倒回發新指令會截斷後續事件。新的控制模式 B-only，A 無這三段，不假造對照。

新增明確曲線分成三個 motion-v15 JSON（每檔 < 20 MB），首次源自真 Blender native solver；之後每次鮮算與固定曲線比較，再輸出確定 GLB。Blender 5.2.3 LTS，4 CPU threads，無 GPU。保持每段 240 Hz、週期邊界局部 2400 Hz，bulk FCurve 不用 fc.update()。15° 左轉密集樣本最低可達餘量 1.91 mm；無超伸，門檻明記 1.5 mm，不能當成高角度通用方案。

本機與 CI 要執行的驗收：母檔冷開／原有 actions 和場景 preservation、原生重匯出與破壞性修改拒絕、480 Hz 瀏覽器新三段＋36 秒指令示範、全部身體頂點 native/browser 比對、實際 UI、298 張連續圖與 2 段 WebM、ZIP 全檔 SHA 和獨立重建／解包瀏覽器。`evidence-v15/acceptance-summary.json` 與 `deliveries-v15/verification-v15.json` 為具體結果，未產生前不得宣稱通過。CI artifact 本身要下載核對 outer digest 與 inner indices，才交付。

未測：人工美術、手機真機、GPU 效能、Godot／Unity／地圖、完整自碰撞、真實 COM／地面力。兩色同一身形；人物與服裝、第二身形、廣泛模型庫尚未在本階段處理。已有 20 款庫與人物分支保持原狀。下一步先評估多視角自然度和縮短控制等待，勿直接擴大轉向角或搬到地圖。
