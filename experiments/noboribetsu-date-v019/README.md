# 登別伊達時代村 V019 R1｜高等學問所柱廊中央導引

此分支**從 V018 Draft PR #98 延伸**，不改 V018 既有碰撞、角色、建築、GLB、道路與路線。預覽網頁保持原狀，不自動部署／合併。

## 實際新增
- 依 V018 仍可步行的 V004 路線 s=85–103m，13 個低面數淡綠色環狀中央提示點，間隔 1.5m。
- 新增「柱廊中央提示」開／關，預設開啟，但只顯示於 **B** 精修場景，A 骨架隱藏。可原地關閉，不改玩家位置。
- 玩家在 s≈84.5–105m 的 B 場景接近柱廊時顯示說明；若朝左側偏離中心線超過 0.45m，則顯示加強提醒。
- 新增 `v019_porch_guide.json`，正式 Runtime 用 native `crypto.subtle.digest('SHA-256', ...)`、資料筆數、路線座標及 stage 契約驗證，任一不符即停止；沒有把測試替身塞進正式網站。

## 驗證
- V018 原封的 **117 個檔案中 112 個 SHA256 不變**，只修改 `app.js/index.html/style.css/scene_view.json/qa.json`，另加 V019 JSON；總計 118 檔。
- 13/13 個提示位置以原 `CollisionWorld` 實際碰撞檢查，均可在原路線中央行走；不是店門口或橫向全寬的通行證明。
- 從 V018 Runtime ZIP 乾淨解壓，重新生成 V019，**118/118 個檔案 SHA256 完全一致**。
- 在 Xvfb + Chromium + ANGLE SwiftShader 真正建立 WebGL2，完整 B 場景及提示點成功載入；開→關→開通過，V004 近景同鏡位 WebGL2 PNG 開關差異已保存。
- 隔離 QA 透過 about:blank 的虛擬子資源載入，**僅測試程序**使用由 Python 先對真實模型核對的長度→SHA digest adapter；用於定位的 QA 相機 hook 也**沒有**寫入正式 Runtime。因此尚未驗證私人網站 HTTPS/WebCrypto/CDN／登入。
- Android 真機、Blender Native `.blend`／Cycles、現場店門尺寸與無障礙規範尚未驗證。

## 重新建置
備齊使用者私人的 `Noboribetsu_Date_V018_R1_Runtime.zip`，其 SHA256 必須是
`99930d2271c9d059e5c724d597a4b01d82a1e6b7d942eb57b919873e1b81ea9e`。

```bash
python replay_v019.py /path/to/Noboribetsu_Date_V018_R1_Runtime.zip /path/to/empty_v019_workspace
```

`replay_v019.py` 要與 `build_v019.py`、`integrate_v019.py` 放在同一資料夾，會拒絕覆蓋已存在的目錄。純 Node 測試 `node test_v019_guidance.mjs`，網頁 GPU QA 見 `qa_v019_webgl.py`，後者需 Xvfb/Chromium + Playwright。

完整兩份 ZIP、實際 WebGL2 截圖、HTML 比較頁、交付報告、雜湊清單已獨立保存於私人 ChatGPT Library `/Noboribetsu_Date_V019_R1/`。此 GitHub 分支不提交私有的大型 GLB 或整座園區資料。

**保持 Draft，不合併、不部署、不更改私人網站設定。**
