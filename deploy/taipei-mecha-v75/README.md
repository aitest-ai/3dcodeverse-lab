# 真正臺北機甲 v7.5 — Vercel Release 資產建置入口

此資料夾**不是遊戲原始碼與模型本體**，而是經驗證的部署啟動器。完整遊戲仍在使用者原始 ZIP 裡，**尚未傳進 Vercel**。

## 先決條件與唯一待補資產

請把前次交付的原始檔「臺北機甲_v7.5_正式Web部署候選_含原始城市雲端驗證.zip」當作 GitHub Release 的二進位附件發布，大小 **59,898,926 bytes**，SHA256：
`78704c156b8667b4a47a898616edf305e783b5b7a61d7aeed17b8d7e3972dab6`

取得實際附件的直接 HTTPS 下載網址後，在 Vercel 專案「環境變數」設定：
`TAIPEI_MECHA_ASSET_RELEASE_URL=https://github.com/aitest-ai/3dcodeverse-lab/releases/download/<tag>/<asset.zip>`

請不要使用虛構的 tag 或網址。此頁沒有內嵌下載地址，缺資產時**明確失敗**，不會用臨時方塊模型假冒 v7.5 完整版。

## 部署專案

- Vercel Team：`tests-projects-abe7fd9e`
- Git Repo：`aitest-ai/3dcodeverse-lab`
- 專用 branch：`feat/taipei-mecha-v75-vercel-deploy-bootstrap-20261106`
- Root Directory：`deploy/taipei-mecha-v75`
- Framework：Other / None；Build Command：`python3 build_from_release.py`；Output：`dist`
- Preview Only：不要覆蓋先前 `taipei-mecha-dev-preview.vercel.app` 或其他網站

檢查步驟：下載 GitHub Release 附件 → SHA-256/ZIP CRC/路徑 → 原本 145 項資產／GLB/Node 49 檔語法 → 由官方固定版 `shwang1979/slop-taipei@1d70708fc92a088b779c8c0e22677adb64966a1b` 取回臺北街景 → `patch_slop.py` → 真正的 JS、OSM、機甲與敵機 GLB 靜態網站 → WebGPU 瀏覽器測試。

2026-11-06 Vercel Sandbox 已成功 shallow-clone 以上固定版本，五個城市重要 Git blob 100% 相符；本地也已核對原玩家、3 款敵機 GLB 和 JS。但目前**尚未有 Release 直接下載連結、尚未部署完整遊戲、尚未通過實機 WebGPU 三波戰鬥**。本 PR 僅為部署預備，不等於完成上架。

保留所有舊版 ZIP；不更動 main 與現有公開站。