# 臺北機甲 v7.3｜原始高品質 3D 保留的效能診斷與手動特效品質控制

## 本次真正完成的交付

本 Draft PR 接續 v7.2 PR #93。完整遊戲在獨立 ZIP：`臺北機甲戰鬥_v7.3_效能診斷與畫面品質控制完整整合包.zip`。**不更新公開 Taipei 網站，不修改 main 或合併前面 Draft PR，也不覆蓋 v7.2 ZIP、原始 .blend、3 款 v6.3 敵方 GLB、原玩家 15-bone GLB 或原臺北 OSM 城市。**

本 repo 保留可供其他 AI 與 3D 引擎直接沿用的 **兩份與 Windows v7.3 ZIP 逐位元相同的原始碼**：
- `examples/threejs/mech-quality-v73.js`：Git blob SHA `2bd8d66a710a1349ae9dd469675606e20949b3e8`；手動完整（預設）／平衡／精簡，控制**只有粒子碎片數、查詢取樣頻率、落地碎片上限、能量環視覺尺度**，絕不降低 Blender GLB、材質貼圖解析度、OSM 地圖、玩家武器或敵人傷害。
- `examples/threejs/mech-performance-v73.js`：Git blob SHA `ddcd3e1713fdd9f3487cd42a7a5c7a4ef8b01662`；RAM-only 更新間隔 P50/P95、單一機甲 addon CPU P50/P95、`renderer.info` 上次 draw calls／三角面／材質/幾何計數、死亡 GLB／碎片／牆面查詢峰值；排除頁面停止等超長間隔。無世界座標、使用者識別碼、網路請求或自動儲存。
- `tests/mecha/v73-performance-quality.mjs`、`.github/workflows/mecha-v73-performance.yml`：Node 22 CI。

**嚴格定義：更新呼叫間隔不是實際 GPU FPS；addon CPU 只是機甲模組，不包含原城市其他程式／WebGPU GPU queue；renderer.info 不能用來推算 VRAM。** 不可使用上述資料宣稱已通過 Windows WebGPU 實機畫面驗收。

## 完整 Windows ZIP 裡新增的功能（非整套上傳此 GitHub）

- `mech-cinematic-v73.js` 沿用 v7.2 完整地形／OSM 建築掃掠檢查、原始三型 GLB、殘骸釋放與重置，新增 `setQuality`。切換後僅新生成的視覺碎片依檔位設定：完整 100%、平衡 70%、精簡 40%，保留原 v7.2 各種上限並減少落地碎片／查詢頻率。完整品質預設、不自動調低。
- `mech-combat.js` 正式 import v7.3 新的 Three.js 特效，提供 `setVisualQuality`，沒有改實際 `rayBuilding`、建築破洞、機甲 HP、三波進攻、敵機 AI 或 v7.1/7.2 舊檔。
- `mech-addon.js` 在原控制面板增添效能摘要、展開詳情、手動切換品質、手動匯出 JSON 與離線診斷頁按鈕。不會被動降低畫質、不上傳數據。
- `qa/v73_performance_lab.html` 不使用 CDN、外部 JS、localStorage；能選入 JSON，查看 P95／負載條圖／候選建議，**合成示範資料明確標示不能作為實機證據**。Windows 安裝器 `patch_slop.py` 在更新城市前確認全部新模組與此頁存在；安裝兩次不會重複加入 addon，啟動器使用 v7.3 自己的獨立城市目錄。
- `README_V73.md`、`qa/V73_MANUAL_ACCEPTANCE.md`、完整新舊程式差異、SHA256SUMS 和三組本地回歸報告皆在 ZIP 中。

## 實際測試與界線

- 完整 Windows v7.3 疊加版 Node.js/Python 回歸：**112／112 PASS（38＋37＋37，三個互不重複的獨立批次）**。原始 145 份資產和玩家 GLB SHA `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c` 保持不變。
- 最終 ZIP：**502 檔案項目、501 SHA-256 全部相符、CRC 通過**，ZIP SHA-256 `e940337a8ccc84d34b4dc350a2766c06cd08877fc8719b6be8cd884fa2467383`，63,692,516 bytes。從最終 ZIP 解壓到**全新資料夾**，10 項機甲 CPU／品質／安裝／v7.2 真實戰鬥模擬／結算重點測試再次 PASS。
- **隔離 Chromium** 的 `page.set_content()` 真實渲染桌面／手機（PNG 已交付），並真實測試 JSON 選檔／清除／示範標示。這不是原版 Windows `file://` URL 直接導覽，更不是正式 WebGPU 遊戲畫面。
- **尚未做：** Windows Chrome／Edge 真正 5 分鐘臺北 101 防衛戰、GPU FPS／VRAM、GLB 穿模、美術光影、Android 真實渲染驗收；結果與現有模式效率仍待使用者實機錄影與性能工具評估。

下一個 AI 請以完整 ZIP 及 README 為最新交接源，GitHub 單一模組不是完整遊戲；保留全部前序 PR Draft，勿自動合併或部署。


### 最終品質修正
最後一輪測試抓到能量環 update 局部變數與品質設定同名，已把 ring profile 與 quality profile 區分，使完整／平衡／精簡能量環縮放真正有效。修正後重新分批驗證 112／112 PASS，並從**更新後最終 ZIP**乾淨解壓驗證 10／10 PASS、501／501 SHA-256 一致；不能使用前一次 ZIP SHA。
