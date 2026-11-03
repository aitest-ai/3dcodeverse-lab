# 港邊散策 · Harbor Walk

原創臺灣港口街區的第三人稱探索原型。以 TypeScript + Three.js + Rapier 實作；角色使用合法 CC0 人體／衣物／動作與原創造型配件，具有真正 GLB skin、65 根骨、七段動畫與微笑 morph。

這是可玩、可修改的第一個垂直切片候選，尚未達商業角色美術、桌機 60 FPS 或手機 30 FPS 驗收。已完成項目與精確測試結果見 `docs/STATUS.md`。

## 直接玩預建版本

交付 ZIP 內已包含 `dist/`。需要 Python 3（無第三方 Python 相依套件）：

```sh
python START_HARBOR.py
```

開啟 `http://127.0.0.1:8123/`。角色工房位於 `/viewer.html`。`--port 8124` 更換連接埠；`--no-browser` 不自動開瀏覽器。請透過 HTTP 執行，不要雙擊 HTML 使用 file://，因為 GLB／WebGL 載入受瀏覽器限制。

GitHub 原始碼不含 `dist/`，先依下一節建置，再啟動。

## 從原始碼啟動

Node.js 24.22.1 和 npm 11.9.0 是本輪實測版本。

```sh
npm ci
npm run dev
```

開啟終端機印出的 Vite 網址。正式靜態建置：

```sh
npm run build
python START_HARBOR.py
```

不需要 REA、Blender、原始遊戲或 API key 就能遊玩。沒有自動部署或任何外部服務寫入。

## 操作與任務

- WASD／方向鍵：移動；Shift：跑步；Space：跳躍。
- 按住滑鼠拖曳：旋轉視角；滾輪：調整距離。
- 靠近居民按 E：對話；Esc：關閉對話。
- 右上「畫質」：標準／省電；「?」：操作說明。
- 找阿澄接下委託 → 跟著地圖收集茶香、樹影、海風三枚印記 → 找書店的阿青交付 → 得到 150 點並可繼續散策。
- 東側有樹、長椅與花臺，需繞行。NPC 巡邏會停下等玩家，沒有 navmesh 自動尋路。

手機版面可顯示，但本版尚無觸控移動或實機效能驗證，需要鍵鼠操作。

## 驗證

```sh
npm test
npm run build
python scripts/validate_glb.py assets
python scripts/check_asset.py
```

真瀏覽器操作驗收需要安裝 Python Playwright、Chromium 與 Playwright 影片編碼器。可依環境自行選擇工作目錄中的快取位置：

```sh
python -m pip install playwright
PLAYWRIGHT_BROWSERS_PATH=/path/to/cache python -m playwright install ffmpeg
CHROMIUM_PATH=/usr/bin/chromium PLAYWRIGHT_BROWSERS_PATH=/path/to/cache python scripts/browser_qa.py
python scripts/review_qa.py
```

先另開終端執行 `npm run dev -- --port 5173`。測試以真鍵盤、滑鼠與 DOM 操作；`window.__harbor.snapshot()` 只讀取狀態，沒有 teleport、直接完成任務或偽造物理接口。腳本 `/usr/bin/chromium` 為本環境預設，`browser_qa.py` 支援 `CHROMIUM_PATH`。

## 角色重新製作

從 `assets/source-lock.json` 所列三份 Quaternius **免費 Standard / CC0** pack 取得合法輸入，檢查 SHA-256 並解壓到同一個來源目錄。不要執行來源 ZIP 內未知腳本。再執行：

```sh
CC0_ROOT=/path/to/cc0 blender -b --factory-startup --python scripts/build_character.py
```

本輪實際使用 **Blender 4.3.2**，沒有冒稱 Blender 5.2.3。輸出 `assets/harbor-courier.blend`、GLB、manifest、report，同步 `public/models/harbor-courier.glb`。圖片可由 `scripts/character_previews.py` 重做。既有 3dcodeverse-lab 的生成流程沒有被覆寫。

## 原作研究與界線

REA 安裝、真實 CLI Evidence、原作 ZIP／Unreal 5.6.1／IoStore 分析與模型研究在 `docs/` 和 `evidence/`。原 EXE 沒有被執行；原作保護素材沒有加入本原型。壓縮模型與藍圖仍受 Oodle 解析依賴限制，沒有虛構骨數、拓樸、IK 或程式解碼成果。

授權與來源見 `THIRD_PARTY_NOTICES.md`。後續 AI 修改請先讀 `AGENTS.md`。
