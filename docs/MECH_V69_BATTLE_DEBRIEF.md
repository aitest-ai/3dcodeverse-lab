# 臺北機甲 v6.9｜本場結算、敵機實際傷害歸因與離線實機驗收

此分支接續 v6.8 Draft PR #82。保留 main、原 Slop Taipei 公開網頁、既有完整 Windows ZIP、145 份 Blender／GLB／貼圖及先前所有 Draft PR，**不自動合併或部署**。

## 實際完整版交付（獨立 ZIP，不在 GitHub 建模參考庫內）

- `mech-battle-debrief-v69.js`：從真正的遊戲射線及 HP 扣除產生 `player_hit`、`relay_hit` 等事件，依 assault/ranger/heavy 統計當場對玩家與中繼站的 HP 傷害。不推論角色位置信息，不留原始攻擊軌跡、玩家姓名／GPS。
- `mech-debrief-ui-v69.js`：三波交戰秒數、各波實際失血、三類敵機真正造成的傷害、當場側閃及重新尋路、下次測試觀察重點。勝敗後顯示、可關閉／重開、手機排版可捲動，支援減少動態設定。沒有自動儲存或傳輸。
- 保留原 v6.7 `taipei-mecha-v67-battle-aggregates` 單場 JSON，讓 v6.8 多場分析器繼續正常使用；角色細項只存在遊戲 RAM 中，重新開始一場會清空，不暗中修改舊 JSON 格式。
- `qa/v69_playtest_checklist.html` 是完全自給自足的離線單檔 HTML，可手動核對 WebGPU、實際臺北 101 OSM、關卡三波、重裝第二階段、敵機街角、盾牌穿模及真實 GPU FPS；只有使用者按「匯出」才下載驗收 JSON。
- Windows `patch_slop.py` 先檢查新 JS 與離線清單再觸碰原城市，正常重複安裝不重複插入 addon。啟動器使用新 v6.9 獨立城市資料夾，不覆寫旁邊 v6.8 版本。

## GitHub 共用參考模組

`examples/threejs/mech-battle-debrief-reference-v69.js` 是較小的純 JavaScript 參考，只示範真正角色扣血和各波中繼站損傷；完整 Windows 模組有更多畫面資料、觀察重點與 UI，**不宣稱本參考檔與完整 Windows 模組逐位元相同**。`tests/mecha/v69-debrief-reference.mjs` 和 `.github/workflows/mecha-v69-debrief.yml` 測試此參考。

## 完整候選版驗證與限制

完整 Windows ZIP 內的 Node/Python 測試（包括之前所有戰鬥／角色／城市安裝安全測試與 v6.9 新結算、DOM、安裝、HTML 安全測試）**91／91 通過**；原 v5.0 玩家機甲 GLB SHA-256 `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`，145 份舊版資產未改。隔離 Chromium 以 page.set_content 測試過手機／桌面結算與清單、上傳合成 JSON、關閉與重設，**不是在真正 Windows WebGPU 遊戲中截圖或驗證 GPU FPS**。

使用者有需要實機測試時，先從完整 ZIP 的 `qa/V69_PLAYTEST_PROTOCOL.md` 操作；不要用 GitHub 參考程式取代完整遊戲。勝率、哪一型敵機最危險、哪一波最難，都只能在單場真正事件的定義下使用；**不能從單一遊戲或合成資料推斷最佳難度**。
