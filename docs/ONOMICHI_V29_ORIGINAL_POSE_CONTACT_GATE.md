# 瀨戶內騎行世界 V29｜原版騎姿接觸證據與獨立驗收工具

2026-11-04。承接 V28 Draft PR #135，來源 head 4f324c2d7989bf45416f82213444ac254e148266。新增獨立原版人物與自行車接觸證據工具；不合併 main、不修改原網站與 V06 遊戲入口、不替換任何人物／自行車／渡船／Halows V15 GLB，也不新增可騎道路。

## 實際完成
1. scripts/research/onomichi_v29_runtime_probe.mjs：只供 V28 獨立檢查頁使用。WebGL2 必須存在，且由原版 THREE.Object3D 明確設定八個接觸點，於原 AvatarDriver/ BicycleDriver 動畫更新後擷取世界公尺座標；需確實記錄 straight、turn、start_stop，最後由使用者在本機另存 JSON，不使用網路。
2. scripts/research/onomichi_v29_contact_gate.py：可離線核對兩份私人原版 GLB 的 SHA256、GLB 結構及原人物 Cycle 動畫。接受真 WebGL2 marker 取樣，拒絕 NaN、缺失接觸點、重複時間、來源不符與 DOM 假冒 3D。輸出左右手－車把、左右腳－踏板四組距離的 median、P95、max（mm），分直行與轉彎統計，不把小距離推定為姿態正確或合法道路。
3. tests：八項 Python 安全測試、四項 Node 假物件測試，這些 PASS 僅為程式和合成資料，不是原 WebGL2 人車遊玩畫面的通過證據。
4. assets/setouchi/onomichi-v29-contact-registry.json：以 V28 原始素材 SHA256、道路及 GSI 來源、全部未完成事項鎖版。GitHub 公開 CI 不含任何使用者私人的原人車 GLB。
5. 完整單機 HTML 圖形檢視器另包含在本輪對話的 V29 工具 ZIP；公開儲存庫不保存人車二進位。

## 原始鎖定
actor SHA256: 4dab76c398f4c30c3aa62ef88e389b28974018c01fd271c08bf029d840d263d1
bike SHA256: 7cb53e92247cf081354c1551b91ae812aab56be7c07748ed00764f0d2c844ece
OSM way 388716484: 74.3638m 地圖研究段，GSI 高程計算 373 個位置。V28 原車分析得軸距 1.08m；GSI 不是實測車道路面。Halows 向島店官方外觀與汽車出入口圖：https://www.halows.com/stores/detail/77 。車輛箭頭不能推斷合法自行車騎行通道。

## 執行可重現的合成軟體測試（非實玩）
python3 -m unittest discover -s tests -p test_onomichi_v29_contact_gate.py -v
node --test tests/test_onomichi_v29_runtime_probe.mjs
python3 scripts/research/onomichi_v29_contact_gate.py --capture tests/onomichi-v29-synthetic-contact.json

最後輸出應為 SYNTHETIC_UNIT_TEST_ONLY，不能宣稱人車手腳接觸、碰撞或 Android 合格。

## 在原私有 Runtime 實際驗證時
請在獨立 V28 研究版而非原遊戲 main.mjs 載入 onomichi_v29_runtime_probe.mjs。先由真 Blender/Three.js 模型確認左右手掌、腳掌、車把握點、踏板接觸點的八個 Object3D 與 localOffset，不能把骨頭起點直接視為正確接觸點。利用 createContactProbe 建立探針，必須傳入真正 renderer、markers 與 browserName；在原生 Cycle 更新後調用 captureFrame(tSeconds,phase)，於使用者操作時觸發 download()。資料不發往雲端。

本機再使用:
python3 scripts/research/onomichi_v29_contact_gate.py --capture V29_Local_Pose_Contact_Capture.json --actor-glb /path/to/private_actor.glb --bike-glb /path/to/private_bike.glb --output V29_Local_Contact_Report.json

即使所有來源檢查成功，狀態只會是 REAL_CAPTURE_SHA_VERIFIED_MANUAL_REVIEW_REQUIRED。仍需以真正 WebGL2 畫面驗證握把、踩踏、人物姿態、車輪與鏡頭；手機與 Android 另測。

## 尚未完成及限制
本輪未能從既有檔案庫實際取得 V28 私人完整 ZIP，所以沒有把 V29 探針直接植入原版遊戲、沒有重新打包原版完整 Runtime，也沒有完成原人車的真 3D 視覺動作驗收。現地 2026 實測路幅、路緣、標誌、路面高程、自行車路權、完整連接路線與物理碰撞亦未核准。V29 只提供可重現的第一道量測與拒絕虛假驗收機制，所有舊版、main 和網站保留不變。
