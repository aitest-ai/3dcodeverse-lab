# 臺北機甲 v7.4｜真正戰鬥事件的煙霧與局部爆炸光影

## 工作版與原則
承接 v7.3 Draft PR #96，不動 main、不部署舊版公開臺北網站、不替換原本 15 根骨架的玩家機甲、三款 v6.3 精修敵機、Blender 母檔／貼圖或真實臺北 OSM 街景。**完整 Windows v7.4 ZIP** 才含真正的 `mech-combat.js`、`mech-addon.js`、`mech-atmosphere-v74.js`、安裝器與全部 GLB；這個 GitHub PR 保存可獨立驗證的共用曲線與版本交接，**不是整份可執行遊戲**。

## 實際加入 Windows 遊戲的特效
- 在原本的 `muzzleFlash`、`detonate`、真實 HP 死亡、建築立面破裂與 OSM 安全生成後的重裝機登場呼叫 v7.4 氣氛模組。傷害、原始射線、碰撞與任務勝敗完全由 v7.3 原始戰鬥程式決定，特效不可反向影響。
- `mech-atmosphere-v74.js` 使用 Three.js `Sprite`／`SpriteMaterial` 和一次性程序產生的徑向 RGBA `DataTexture`，讓灰煙逐漸上升、膨脹及淡出；不使用圖庫、遠端 CDN、影片或材質來源不明資產。短暫 `PointLight` 自動衰減並回收，`castShadow=false` 避免額外陰影繪製。
- 使用者**手動**完整／平衡／精簡模式：最多煙霧 36／22／9，單次大型爆炸生成 12／7／3，局部爆炸光源最多 3／1／0。預設仍為**完整品質**；不降低 GLB 多邊形、PBR 貼圖解析度、城市、武器、敵機或物理。
- 原本機甲受擊鏡頭回饋加入有上限的短促事件衝擊；依事件、距離與品質衰減，尊重使用者關閉震動及系統 `prefers-reduced-motion`，不切換原始臺北相機。
- 各次更新只使用有上限的 dt，不在背景下載素材；`reset/dispose` 會釋放 Smoke SpriteMaterial、共享 DataTexture 和局部光源，避免殘留。
- `qa/v74_atmosphere_lab.html` 是完全離線、不需外部資源的 **Canvas 2D** 視覺實驗室，供觀察上升／擴散／淡出和品質上限。它清楚標示並非真正臺北 3D WebGPU 畫面；遊戲面板按鈕僅開啟同源離線檔案。
- Windows `patch_slop.py` 先檢查兩份新 JS 與 HTML，缺檔拒絕修改原城市；獨立 v7.4 啟動器不覆蓋相鄰 v7.3／舊版安裝。

## GitHub 可重用核心
`examples/threejs/mech-atmosphere-curves-v74.js` 是完整 ZIP `mech-atmosphere-curves-v74.js` **逐位元完全一致的原始碼**，Git blob SHA `3d15df7457cc86a1ba4a87670b68dbd3a552f463`。內含煙霧／光源動畫曲線、品質設定與鏡頭衝擊數值。GitHub Actions `mecha-v74-atmosphere.yml` 跑 Node 22 測試。完整版 `mech-atmosphere-v74.js` 本身需 Three.js WebGPU 和正式上游城市，請從完整 ZIP 取得。

## 真正驗證與不能宣稱的部分
- v7.4 完整遊戲 Node/Python **115／115** 項（39＋38＋38，三個獨立無重複批次）回歸通過，包含真實戰鬥的 HP 死亡才產生煙霧、三檔品質差異、場景重置、GLB 完整性、OSM 安裝與缺檔保護。
- 離線 2D HTML 在隔離 Chromium `page.set_content` 完成桌面與手機實際渲染、按鈕互動、品質切換與清空，非 Windows 開啟本機頁面的驗證。
- **尚未驗證：真正 Windows Chrome／Edge WebGPU 全城戰鬥畫面、PointLight 在特定 GPU 的成本、GPU FPS／VRAM、五分鐘臺北 101 任務的視覺驗收。** 原 v7.3 CPU 計數不是 GPU 效能。
- 真實遊戲的 SHA256 與清潔解壓測試報告由完整 ZIP 及單獨的交付報告提供；不應捏造未執行測試。

保留前序所有 Draft PR，不自動合併或更新網站。
## 最終 v7.4 完整 ZIP 的乾淨解壓驗收（2026-11-02）

- 檔案 `臺北機甲戰鬥_v7.4_動態煙霧與局部爆炸光影完整整合包.zip`：**63,976,901 bytes**，SHA-256 `dff4da6ab4fc9c716ae1636778de621b5aa0df4d9bff4a8ba373fc455b6b472f`。
- ZIP 519 個檔案項目、518／518 SHA-256 逐檔相符、CRC PASS，145 份舊版 assets 完全一致，玩家原 GLB SHA-256 仍為 `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`。
- 完整回歸為 **115／115 Node/Python PASS**，三個分開執行的 39／38／38 項批次（不是單次不中斷）。其中歷史版 HUD／啟動器「v7.3」文字檢查更新為目前 v7.4，未跳過行為測試。
- 將**最終 ZIP**重新解壓至全新目錄，12 項重要測試（包含真 HP 擊毀、爆炸煙霧、三檔模式、原模型雜湊、v7.3 舊特效、三波關卡、城市安裝兩次及缺檔拒絕安裝）全部再次 PASS。
- 隔離 Chromium 桌面／手機畫面證據是獨立 **Canvas 2D 示意實驗室**，不是臺北真實 WebGPU 畫面。未量測真正 GPU FPS、VRAM 或正式遊玩。
