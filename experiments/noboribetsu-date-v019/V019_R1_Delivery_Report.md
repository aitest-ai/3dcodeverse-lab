# 登別伊達時代村 V019 R1｜V004 高等學問所柱廊視覺導引

## 交付結論
已製作 V019 的**可開關中央路線參考**，沒有修正或放寬 V018 已通過的碰撞判定。使用者在 V004 高等學問所附近靠近左側柱廊時看到提示；13 個點均位於原版碰撞系統判定可行走的路線中央。新的提示點是 3D 畫面上的低負擔視覺標記，不是實地測量的安全通道。

## 實際新增
- 中央提示點 13 個，間隔 1.5 公尺，沿既有路線 85–103m，B-only。
- 玩家在 V004 柱廊路段 84.5–105m 會看見提示；偏向左側 0.45m 以上時出現加強提醒。提醒不能阻擋走路。
- 新增「柱廊中央提示 開／關」按鈕，預設開啟，A 骨架不顯示標記。
- 獨立 v019_porch_guide.json SHA256：05d4f157f3762136947c7d3921fa9b4e8aae7a82e258e7c6c70d166640500fe6。正式應用使用原生 WebCrypto SHA256 fail-closed，沒有修改模型驗證模組。

## 已通過的驗收
- V018 原有 117 檔中 112 份逐位元不變，僅 `app.js`、`index.html`、`style.css`、`qa.json`、`scene_view.json` 更新，新增導引 JSON，Runtime 總數 118 份。
- 原 `scene_view` 路線 472 點、約 231.5664m，全部 GLB、貼圖、導航與碰撞資料逐位元未變。
- 13/13 個導引點通過真正 `CollisionWorld` 中心線可行走檢查。
- 從 V018 ZIP 重新建置，118/118 個檔案 SHA256 完全一致；Node JS 語法通過。
- Chromium + Xvfb + ANGLE SwiftShader **確實建立 WebGL2**，實際載入 B 場景與 13 點；畫面開關順序 true→false→true 正確。同一 QA 相機位置 V004 柱廊的真 WebGL2 前後截圖已取得。路面區域（固定 ROI、單像素通道差值 >20）改變約 **2,093 像素**，只是影像輔助指標，不能代表美學或效能提升。

## 未完成與不可推定
- WebGL 測試中用於隔離瀏覽器的 `about:blank` 虛擬子資源，以及 **測試用**長度→已獨立核對 SHA-256 adapter、相機定位 hook，只存在 QA 測試程序，並不在 Runtime。
- Android 實體裝置、正式私人網站 HTTPS/CDN/登入、Blender Native `.blend`／Cycles、現地店門寬度與無障礙規範，均未測或未查證。
- 這輪沒有實作第三人稱，也沒有更動任何舊版或主網站。此版本維持 Candidate/Draft。

## 交接
保留 V018 Runtime ZIP SHA256 99930d2271c9d059e5c724d597a4b01d82a1e6b7d942eb57b919873e1b81ea9e。透過 `replay_v019.py` 指定舊版 ZIP 與新的空白輸出資料夾，使用 `build_v019.py` + `integrate_v019.py` 可離線重建。勿用 V017、V016 代替這個依賴。SourceQA 包保存原始兩張 WebGL2 截圖、驗證腳本、JSON 報告；GitHub 只保存來源程式及測試契約，不上傳私有大型資產。