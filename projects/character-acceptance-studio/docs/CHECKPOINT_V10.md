# 交接點 0.10.0 · 2026-11-05（臺北）

基底：Draft PR #155，`ae7f433caf8fbeb28b18e31368014a691a4e8e37`。新分支 `feat/character-studio-v10-horse-grounding-20261105`；不修改 main、舊版工作室、母檔、馬匹正式 registry／Release 或任何網站。

## 成果與位置

`README_V10.md` 為啟動／下載／重建入口；`config-v10/horses.lock.json` 固定原來源和候選 GLB SHA；`scripts/v10/horse_solver.py` 是原生鏈求解與循環接合，`build_horses_v10.py` 只替換 Walk/Gallop。新候選為 horse-brown-grounded-review、horse-white-grounded-review，0.1.0。兩馬各 50 骨、13 clips，原 GLB 其他 11 clips、舊 BIN、網格、蒙皮、材質、貼圖與 rest 精確保留。

生成目錄 library-v10、evidence-v10、deliveries-v10 不將二進位檔提交 Git。按照馬匹資產規範「二進位檔先上傳 GitHub Actions Artifacts，不要把大檔直接 push 進一般 Git 歷史」，由本輪 workflow 完整生成、驗證並上傳 review artifact，保留設定 90 天；以遠端 artifact 實際到期時間為準。未擅自核准或發布正式 Release。

## 已定位與修正

原 Gallop GLB 尾幀取整且首鍵偏移 1/24 秒，原生動作 14.4 尾幀本身仍未閉合（身體約 105.76 mm，主要右後腿／蹄）。候選在首尾各 12% 週期接合局部 TRS，保留原步態中段；之後在原始彎曲半平面，以兩節鏈保長求解蹄部高度。蹄方向保留，沒有提高軀幹／根節點。GLB 烘焙 120 Hz，以 240 Hz 瀏覽器重算變形表面檢查中間幀。

原版 Walk 最低約 -11.20 mm、Gallop -15.11 mm；本輪兩馬約 +1.31 / +1.93 mm；全網格首尾位置差為 0。Blender 冷開五個時間點的 6,548 個身體頂點與瀏覽器差異最大約 0.00137 mm。這不是世界腳滑、動力學或美術核准。

兩馬身體頂點順序不同、材質分區不同、鬃毛資料不同。空間對應後 6,548 個身體頂點中 6,457 個精確相同，其餘 91 個差異不超過約 0.000001 原生單位，骨權重一致；屬同身形毛色版本，不能宣稱第二解剖身形適配。各自使用來源對應表，保留材質和鬃毛。

首次候選曾因清除 NLA 後未標記保留而使冷開母檔只剩 3 個動作；冷開檢查攔下，已修為全 13 動作保留。失敗工作副本只在 work/v10，不會進入交付。最初離線預覽側面裁到鼻端，已改為按實際全模型邊界取景。

## 驗證與待辦

程式／結構、Blender 冷開與六張 CPU 靜態預覽、Chromium 實際操作／240 Hz 接地、100 張連續畫面／兩段 WebM 分開記錄於 evidence-v10；本機乾淨 ZIP 解壓、兩個 GLB 逐位元一致重建、實際瀏覽器操作已通過，見 config-v10/local-acceptance.json。CI／遠端下載結果由 PR 補充。三者不取代人工美術。CPU 軟體繪圖可能掉格，桌面 390px 不算手機真機。

下一步：量測步幅與世界速度、設計馬匹支撐期接地計畫，再做鎖蹄／重心檢查。現候選仍原地步態，沒有 world root trajectory；世界腳滑、起停、轉向、斜坡、自碰撞、手機、Godot／地圖、人工美術未測。不要把接地與位置閉合通過直接整合成正式遊戲步態。

既有台灣衣物、基隆河 V110／V111、彩虹橋來源缺口沿用前版；不退回 V103。全部 art_approved=false / game_ready=false。
