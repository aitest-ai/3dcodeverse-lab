# 接手檢查點

目標：可持續製作/修正/人工驗收的人物、服裝、動作工作室；先交付真GLB的端到端瀏覽器版本，保留所有來源與候選。

- 基底main：f088f0e584764b3fd37dc1bc0670df99313bec41。獨立分支feat/character-acceptance-studio-v01-20261104。沒有整條合併其他分支、覆寫母檔、更新地圖或自動合併。
- 核心檔案：assets/registry.json；scripts/build_harbor.py、repair_harbor_clothes.py、retarget_oldman.py；web/index.html/app.js；START_STUDIO.py；可重建OPEN_STUDIO.html。
- 原檔：sources/harbor-v02、sources/oldman-v29。PR50只取binary inspector；PR39只核對合成實驗界線。V31真建模已成功（PR body未同步），但美術未核准，本版不取代shui。V111/彩虹橋仍缺可核對來源，不以V103替代。
- 已驗證：9組程式/來源鎖定檢查；真WebGL2 19項實際UI/負面恢復檢查；5母檔冷讀及packed pixel解碼；2真GLB重新匯入。原生WebCrypto，無GPU/crypto/renderer mock。
- 視覺修正：Harbor袖口及肩帶權重；oldman原V29 BLEND皮膚排序失敗→候選OPAQUE，鞋保留Alpha轉MASK；原圖bytes不變。全服裝藝術與完整動態仍未核准。
- 狀態：候選artifact通過相應程式/技術檢查，art_approved=false，game_ready=false；手機真機/人工美術/新地圖與第二引擎未驗收。Walk還有非零腳滑殘差，Harbor首尾最大關節差約17.8mm。起停/轉身是實驗，阿伯未產出起停/轉身。
- 證據：evidence/program-qa.json、browser-qa.json、blender-cold-read.json、frame-catalog.json；實際連續PNG與videos/前後比較MP4。evidence/history是明確拒收/診斷歷史，不是當前成功候選。
- 環境：17GiB RAM，無偵測NVIDIA；原裝Blender4.3.2；原MPFB母檔需5.2.3，已驗官方SHA安裝於任務work/。Chromium/SwiftShader CPU。file://政策拒絕，單檔完整HTML以localhost驗證；未改政策。聊天預設/codex輸出目錄在此獨立雲端不可寫，成品改以Draft PR內固定版本完整ZIP交付，Git保存可編輯來源及重建程式。
- 下一個真正未完成的依賴：使用者在真工作室逐部位看兩位Walk/Run並匯出觀察，再先精修支撐腳/循環/起停/旋轉步，接著胸領腋及衣襬/褲襠，不以擴充更多人物取代修正。Kimodo/NVIDIA真人流程仍需另核對硬體/權利/帳戶，不自動花費。
