# 臺北機甲 v7.2｜真實城市牆面／路緣殘骸接觸與碎片停留

## 版本、來源與交接

本 Draft 從 v7.1 PR #90 延續，不修改 main／公開 Slop Taipei 網頁／前序 ZIP，保留 145 份舊版資產，包含 15-bone 玩家 GLB、三款 v6.3 精修敵機 GLB、可編輯 Blender 母檔和所有貼圖。真實臺北地圖仍由上游 `shwang1979/slop-taipei@1d70708fc92a088b779c8c0e22677adb64966a1b` 下載，並非另造街景。

此共用 GitHub 分支真正保存與完整 Windows ZIP **逐位元完全相同**的 `examples/threejs/mech-wreck-environment-v72.js`：
- Git blob SHA-1：`56024caa5f7ccc69f26638010e3632cefd248ffa`
- 檔案 SHA-256：`84a10c8f7ab4c52dcceba23e7f9da4bf5ad777509821f37b621502c5b79989c8`

其 Node 測試在 `tests/mecha/v72-environment.mjs`。完整 Windows 遊戲實際整合程式 `mech-cinematic-v72.js`、`mech-combat.js`、`patch_slop.py`、Windows 啟動器、全部 GLB／Blender 檔案、108 項回歸測試，則在另交付的 ZIP。**不要把 GitHub 單一純計算模組誤當整份可執行遊戲。**

## v7.2 修正與界限

1. 原 v7.1 地形接地仍保留。新版在原始機甲 GLB 傾倒時，以三個主要裝甲代理點和八個地面支撐點計算傾倒候選，讓原 Slop Taipei `ColliderGrid`／`pointInBuilding`／`rayBuilding` 核對**從直立到側倒的掃掠路徑**，避免薄牆在兩個端點都空的情況下漏檢。確認有完整 OSM 建築牆面時縮小傾角；沒有成功查到可用地面則保守退回上次高度。建築毀損後有效缺口會沿用原 `isHoleAt` 查詢。
2. 視覺碎片每影格最多 24 個地形查詢配額、12 個牆面檢查配額（每碎片最多兩個查點），配額不足時不作未檢查的水平移動。撞到原始 OSM 墻體的金屬碎片停止並少量反彈，不修改來源建築或玩家／敵機物理。
3. 一小部分碎片必須經過原 `getGroundHeight` 確認接觸可信路面且速度接近零才能停留最多 7 秒；最多同時 24 個停留碎片，超過上限照正常時間消失。缺資料／不合理高架高度不會產生漂浮常駐碎片。
4. 原有特效總上限 110 個碎片、5 架暫留死亡 GLB、8 個能量環仍保留；清空關卡會卸載真正 GLB 動畫混合器、環材質及共用幾何。未改武器傷害、AI 路線、波次、相機操作。尊重減少動態效果設定。
5. 前版 `mech-cinematic-v70.js`、`mech-cinematic-v71.js` 和 `mech-wreck-ground-v71.js` 全部保留。v7.2 更新真正遊戲 `mech-combat.js` import，新模組如果缺檔則 `patch_slop.py` **在碰城市檔案前**拒絕安裝。

## 可重現驗證與未完成事項

- 工作目錄 Node/Python **108／108 PASS**，三組獨立各 36 項，包含舊版真光束擊殺、原始玩家 GLB 雜湊、真城市 JavaScript 安裝器重複安裝、薄牆掃掠、接地停留、未知高度拒絕、五架原始 GLB 殘骸與限額查詢。測試基於 Three.js mock，**非真實 Windows GPU**。
- 最終 ZIP 共 **485 檔案項目、484／484 SHA-256 全相符、CRC 通過**，ZIP SHA-256 `a02c410c05fdbcfbf054028865332bc57cb1b380c906aa2c509fe60f8076852a`，63,630,127 bytes；145 份舊版 assets 逐位元不變，主角原始 GLB SHA-256 `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`。
- 從最終 ZIP **乾淨解壓**再獨立重測 **12／12 關鍵測試通過**，包括實際遊戲死亡流程、街廓薄牆、碎片接地、安裝阻斷與冪等。
- Windows WebGPU 實際臺北街道畫面、真實路緣穿模、GPU FPS／VRAM、五分鐘實戰、不同顯示卡效能 **尚未驗收**，不應把代理模型或 Node 單元測試宣稱為完整物理、實機通過或美術通過。完整包有 `qa/V72_MANUAL_ACCEPTANCE.md`。

請將本 PR 保持 Draft，先審查 v7.1 #90 與更早的未合併鏈，**不要自動合併或更新正式網站**。
