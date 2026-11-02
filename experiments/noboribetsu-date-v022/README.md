# 登別伊達時代村 V022 R1 — 高等學問所屋簷／木樑／格柵候選

**基於 V021 Draft PR #107 的獨立分支。保留 V021 全部已通過的幾何、控制、碰撞、導引及原有 assets。不得合併或部署。**

## 本輪精修
- 原 V004 作者估計的高等學問所建築，不重新打造屋頂、不更動屋瓦 GLB 或門窗開口。
- B 模型新增可切換的視覺專用 `assets/v022_v004_carpentry.glb`，3 mesh／1,068 三角面／62,920 bytes。
- 27 個屋簷下木端面、8 處柱樑接合的薄陰影細節，與 4 段局部格柵的 16 根浮雕木條；不涉及結構安全或測繪精確度。
- V021 8+8 個原有柱腳／木柱候選與其開關保留。V019 13 個中心線導引點與 V018 路線碰撞保留。
- UI 新增「屋簷格柵細節 開／關」，預設開，僅 B 場景顯示。正式 Runtime SHA256 原生 WebCrypto 雜湊與來源資料筆數校驗，不以視覺效果改碰撞。

## 可重建與驗收

依據未變動的 V021 R1 Runtime.zip SHA256：
`576617c32633ca01a576154165ae8aaa0e925f11df0779201e75b89f7af5aa46`

V021 122 檔中 118 檔逐位元相同；只調整 app.js、index.html、qa.json、scene_view.json，新增 README、GLB、source contract JSON，V022 共 125 檔。獨立新資料夾從密封 V021 ZIP 重播，**125/125 SHA256 一致**，Node --check 與 trimesh 重讀 3 mesh 成功。

**WebGL2 證據分層**：
1. 小型建築檢查環境（V004 原立面＋V021 舊細節＋V022 新細節）：Chromium 真 WebGL2 通過，取得正面／斜角各兩張開關對照 PNG。
2. 完整遊戲 Runtime：Chromium 建立真 WebGL2 且 B 場景回報 loaded=true，但在進入即時互動操作後 SwiftShader 渲染測試逾時；**未通過完整 V022 按鈕切換、行走、手機或正式網站測試**。

隔離測試使用 SHA adapter 和相機 hook；兩者不寫入正式 Runtime。沒有執行 Blender 原生 .blend / Cycles、Android 實機、私人站 HTTPS/CDN/登入，沒有現地測量。屋簷、格柵形狀是依現存模型推估的可逆美術候選，並不保證現場相同。

**完整重建腳本**：獨立 V022 SourceQA.zip 收錄 build_v022.py、patch_v022.py、qa_v022_source.py、replay_v022.py、render_v022_model_only.py、qa_v022_webgl.py、package_v022.py、四張 WebGL2 PNG 與 Validation JSON。GitHub 此分支只保存來源契約與交接說明，不上傳包含私有大型 GLB 的完整 Runtime ZIP。

V022 舊版均保留，不更動任何分享權限、部署或現有正式網站。
