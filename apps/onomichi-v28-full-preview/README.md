# 瀨戶內 V28 真正完整遊戲｜獨立 Vercel 預覽

這個資料夾只保存靜態網站的**部署程式**，不保存原版大型 GLB、使用者 Drive 檔案或臨時下載連結。Vercel 建置期間需提供加密環境變數 `V28_ARCHIVE_URL`，內容為擁有者授權的、具有效期的 HTTPS ZIP 下載網址。

`python3 build.py` 會：下載完整 ZIP；核對 **235,696,298 bytes / SHA256 2b83e637fca50f20eb4237b9ebc3ae52a4264079a686819b44d694c7978905d1**；驗證 12 個受保護程式與模型及 world.json 每個資產的 SHA256；只輸出原版遊戲所需資產到 dist/。原版 src/main.mjs、src/avatar.mjs、GLB 均逐位元組不變，**不是展示版，不要用假的人車替代**。不輸出原 ZIP、Blender 母檔或大型生成過程資料。

本機測試可改用 `V28_LOCAL_ZIP=/absolute/path/Onomichi_V28_Full_Original_Runtime_Plus_Wheel_Contact_Lab.zip python3 build.py`；建置成功後在 dist/ 以 `python3 -m http.server 8765` 預覽。Vercel 專案設定 rootDirectory=`apps/onomichi-v28-full-preview`，buildCommand=`python3 build.py`，outputDirectory=`dist`，framework=null，SSO 保護 all。

**限制**：V28 遊戲內建原有短程行走、騎行與渡船控制，但沿線實際道路淨寬、路緣和騎行合法性尚未現地驗收；Halows V15 是獨立展示候選，不能說已成為可騎連續路段；亦未證明 Android 真機和所有人物手腳動畫均正常。本部署僅供私人遊戲體驗與開發 QA，不作實際導航。

**金鑰與再部署：** 建置時的一次性 Drive URL 具有有效期，不應寫入程式碼、CI、PR 或建置紀錄；到期後新建置前需重新取得授權來源網址。此專案與 V30/V31 的工具預覽分開，避免修改原網站或覆蓋舊版本。