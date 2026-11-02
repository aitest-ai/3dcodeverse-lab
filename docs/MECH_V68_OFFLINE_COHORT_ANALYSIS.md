# 臺北機甲 v6.8｜離線多場比較與難度評估

此 Draft PR 從 v6.7 PR #79 延續，不合併 main、不覆蓋舊版、玩家機甲、三款 v6.3 Blender 敵機或臺北 OSM 公開場景。完整 Windows 版在獨立 v6.8 ZIP 中，並非全部在這個跨 AI 資產實驗室。

## 可重用 GitHub 核心

- examples/threejs/mech-cohort-reference-v68.js：純 JavaScript 比較參考，嚴格讀取 v6.7 戰鬥 JSON 格式，按三難度分組，跳過內容相同的紀錄，排除未完成與部署失敗計算勝率，提供 Wilson 95% 比例區間及每波實際抵達樣本數。
- tests/mecha/v68-cohort-reference.mjs、.github/workflows/mecha-v68-cohort.yml：Node 22 自動驗證。
- 這是比完整 Windows 分析引擎較小的可攜參考版；**不宣稱和完整 Windows JS 位元內容完全相同**。

## 實際 Windows v6.8 完整包新增

- 保留 v6.7 戰鬥核心、傷害、控制、原始 145 份既有資產及原始單場紀錄 JSON schema（taipei-mecha-v67-battle-aggregates，version 6.7）。
- 新增 mech-battle-cohort-v68.js、qa/v68_battle_compare.html（完全獨立 HTML，自帶離線 JS/CSS），可批次匯入 50 個、累積最多 200 場記錄；單檔不超過 1MB；拒絕其他版本、負數、非法波次或過大檔案。
- 三種難度比較：有效勝敗場次 n、勝率及 95% 區間、勝利場次時間中位數、每波交戰時間、玩家／中繼站失血、尋路次數。勝率分母只含已結束的 victory、defeat、time-expired。錄製中、中途離開與部署失敗顯示但不進勝率分母。
- 預設去除內容完全相同的紀錄，使用者可明確允許合法相同資料；合成示範 15 場與真實上傳完全隔離、禁止匯出為真實 CSV。
- 使用者自己選檔；不自動上傳、不儲存在 localStorage、不包含裝置識別碼、GPS、玩家真實資料、地圖座標或操作時間戳。僅手動輸出匿名彙總 CSV。
- 機甲面板按「開啟多場比較（離線）」另開本機城市 /qa/v68_battle_compare.html，安裝器缺新模組／HTML 會先拒絕修改原城市；正常安裝兩次無重複掛載。

## 測試與限制

完整 Windows ZIP 的 Python/Node 86 個隔離回歸測試已各別取得通過結果：83 個在主要測試程序顯示 PASS、3 個大型安裝測試在其執行環境遭總程序時間限制後改單獨重跑且退出碼 0。不能把這項分批驗證描述成一次不中斷的完整單程序測試。
隔離 Chromium 透過 page.set_content 成功測到桌面／手機排版、示範、JSON 上傳、重複資料與 CSV 控制；直接 file:// 導覽因管理政策 ERR_BLOCKED_BY_ADMINISTRATOR 被擋，所以 **Windows 的 WebGPU 遊玩、真正遊戲開新頁與玩家難度研究尚未驗收**。
Wilson 區間是描述比例的不確定性，無法替代隨機化研究或排除玩家自選難度的混雜偏差。不得因為示範資料的勝率就自動調整遊戲數值。

下輪請由完整 v6.8 ZIP 讀取真正 Windows js、.blend、GLB 與 QA，而非用這個參考核心取代完整遊戲。所有前序 PR 保持 Draft，不自動合併。