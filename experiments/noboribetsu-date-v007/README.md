# V007 跨 AI 交接｜只更新兩棟商家街立面

執行順序：

1. 解壓 V006 Runtime.zip 到新資料夾（不要覆寫 V006 存檔）；本輪提供 `v007_east_facades.glb` 加入新 `dist/assets/`。
2. 對 V006 `dist/` 執行：`python refine_v007_facade.py <V006>/dist <V007-outputs>`。來源 SHA guard 必須符合 V005 原始模型。
3. `python integrate_v007.py <V006-runtime-copy-root> <V007-work-root>`；它只修改新副本中的 app.js、index.html、scene_view.json、qa.json，保留所有原有 B/路線/碰撞。
4. `node --check <V007>/dist/app.js`、`node test_v007_contract.mjs`、`node test_v007_navigation.mjs`（設定 DATE_V006_ROOT 至新 Runtime root）、`python verify_v007_integrity.py`。
5. 真 WebGL2/Android/Blender-native/私人 CDN 未通過，不能繼續宣稱已上線或合併 PR。

限制：程式以現有 V006 Runtime (由 V002/V003/V004/V005 演變) 為唯一受信任來源。不會自動從 GitHub 下載私人 GLB。不能以較粗略重生模型替代。

GitHub V007 分支應從 V006 Draft PR #70 的 head branch 建立，保持 Draft；不要合併舊 PR、修改外部預覽設定。

本 ZIP 的 evidence/*.png 全是 GLB→VTK 幾何光照診斷，不是官方照片或 WebGL 截圖。