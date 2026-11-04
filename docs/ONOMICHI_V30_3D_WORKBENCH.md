# 瀨戶內騎行世界 V30｜原版人物 × 單車 WebGL2 騎姿工作臺

承接 V29 Draft #139 的八點原版接觸距離量測。本輪新增真正可在瀏覽器運行的獨立 Three.js 3D GLB 工作臺：以本地 GLB 選檔、SHA256 檢查、原 Cycle 動畫、相機旋轉、人物預覽位置調整、模型節點與八個接觸點校準，再匯出 V29 格式的真 3D 世界座標。保持 Draft，不合併 main 或部署網站。

## 來源與安全界線

原人物 GLB SHA256：
4dab76c398f4c30c3aa62ef88e389b28974018c01fd271c08bf029d840d263d1

原自行車 GLB SHA256：
7cb53e92247cf081354c1551b91ae812aab56be7c07748ed00764f0d2c844ece

使用者必須在自己的電腦選擇兩份原 V06 GLB。本程式要求 GLB 2.0 header、兩個 SHA256 均一致且人物真正具有 Cycle 動畫。拒絕簡化模型，模型只在本機記憶體解碼，不提供上傳 API。原模型、原渡船、Halows V15、地形、道路、data/world.json 與 src/main.mjs 完全不變。

工作臺只改暫時的角色 root 位置，並將測試用 marker 放在真實 glTF 節點上。骨頭原點不能自動當成正確手掌／腳掌：必須選擇模型節點、調 XYZ 本地偏移，並在真 3D 畫面人工確認。變更位置／offset 中止當下採樣。來源結果可本地儲存 JSON，與原模型二進位分離。

本 V30 只是獨立 Cycle 片段預覽，沒有整合 V06 AvatarDriver／BicycleDriver、原渡船與街景碰撞。人為標記「轉彎」只是測試分類，並非真的路線轉彎或輪胎物理運動；絕不據此宣稱合法道路可騎。

## 建置與操作

公開 Repo 來源：
- apps/onomichi-v30-3d-audit/index.html：雙欄響應式 UI。
- apps/onomichi-v30-3d-audit/main.mjs：Three.js、原 GLB SHA 與 Cycle 驗證、真 3D 畫面、八點 marker、V29 JSON 匯出。
- apps/onomichi-v30-3d-audit/rules.mjs：來源 SHA／marker 檔案驗證。
- apps/onomichi-v30-3d-audit/build.mjs 和 package.json：從 npm 打包 Three.js 的離線版 dist。
- tests/test_onomichi_v30_rules.mjs：純程式安全測試。
- tests/test_onomichi_v30_browser.py：真正 Chromium WebGL2 空工作臺、鏡頭與行動版型測試；**不是私有 GLB 實際驗收**。

GitHub Actions 成功後，可下載名為 Onomichi_V30_Standalone_GLBFingerprint_Pose_Viewer 的 artifact，解壓縮進入 dist 資料夾，在資料夾執行以下指令：

    python3 -m http.server 8766

瀏覽器開啟 http://127.0.0.1:8766/ ，從 V28 私人原始包選人物／單車 GLB，等待來源核對，手動校準 8 個節點後勾選確認、開始採樣並匯出 JSON。

對應的 V29 Python 驗證：

    python3 scripts/research/onomichi_v29_contact_gate.py --capture Onomichi_V30_True_GLBS_Isolated_Pose_Capture.json --actor-glb /private/original_actor.glb --bike-glb /private/original_bike.glb --output V30_contact_QA.json

## 尚未驗收

目前未能從私人檔案庫取得原 V28 完整 Runtime，因此目前只完成公開原始碼與 WebGL2 工作臺測試，還沒有在此環境直接載入真 V06 Actor/Bike GLB 或視覺確認原版手腳接觸。獨立 3D 看得到原模型也不等於原遊戲已可騎。Android 實機、現地 2026 道路淨寬、坡口、標誌、路緣、柏油高度、自行車路權與物理碰撞仍未通過。

OSM way 388716484 74.36m 為研究來源，GSI 高程不等於路面。Halows 官方店外觀與汽車路線：https://www.halows.com/stores/detail/77。汽車箭頭不可當作自行車法定通行許可。

下一階段 V31 再接真正 V06 主遊戲 AvatarDriver/BicycleDriver 與原場景運動驗證，不覆蓋舊網站或原版本。
