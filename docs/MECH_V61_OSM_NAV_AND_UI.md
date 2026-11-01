# 臺北機甲 v6.1｜真實街廓受限的敵機繞路與戰鬥警示

本 Draft 分支從 v6.0 三波防衛 PR #60 接續，不改 main／公開網站，也不改原 v5.0 GLB／.blend 母檔。

## 已新增可移植程式

- `examples/threejs/mech-enemy-navigation-v61.js`：每敵機每影格限制 A* 擴展數，局部尋找可看見目標的射擊位置。**真實臺北場景碰撞、水域、車流、坡道及建築可通行必須由宿主 `canStep` 回呼判斷；本模組不提供穿牆捷徑。**
- `examples/threejs/mech-enemy-ai-v59.js`：新增選擇性的 navigationTarget 作為移動朝向；原本鎖定目標、攻擊預警、HP 與命中判斷沒有改掉。
- `examples/threejs/mech-mission-presentation-v61.js`：三波提示、守護耐久、倒數及勝敗資訊的本機 DOM 介面，手機版面精簡，不自行改關卡狀態。
- GitHub Actions `mecha-v61.yml` / Node 測試 `v61-nav-and-ui.mjs`：導航可繞過示意方形大樓、不能穿角、單影格擴展數上限、路徑無解保守失敗、資料型別與介面狀態。

## 完整 Windows v6.1（獨立 ZIP 才有）

Windows 版直接修改 v6.0 完整疊加包的 `mech-combat.js`、`mech-addon.js` 與 `patch_slop.py`：
- 真正套用城市原有的 `ColliderGrid`、遮擋射線、陸地高程、橋面、水域與車流到敵機每小段路線；無有效路線不強行移位。
- 修復出生點的水域回退座標漏洞。
- 敵機預警時同步顯示鎖定地點的地面能量環（與敵人頭頂警示環各一份重用幾何），玩家提前閃避仍有效。
- 任務 UI 清楚顯示三波切換、中繼站告急和勝敗結算。
- 原有的 10 份 Blender .blend、v5.0 GLB（SHA256 `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`）、原臺北城市與舊版 ZIP 不受影響。

獨立 Windows ZIP 的 **55／55 Node/Python 回歸測試通過**，其中包含真正的戰鬥 HP、建築遮擋、生成點水域拒絕、預警環顯示、安裝冪等與 2D 離線頁的 JS VM 驗證。GitHub Actions 的測試只涵蓋可移植模組，不能宣稱整個 Windows 3D 場景已驗收。

**仍待人工驗收：** Windows Chrome/Edge WebGPU、五分鐘臺北 101 防衛、真正 45,000 棟建築中的走位與敵機卡點、手機繪圖、GPU FPS／VRAM 及美術品質。此環境 Chromium 開啟本機網頁回傳 ERR_BLOCKED_BY_ADMINISTRATOR；不得以此推定使用者電腦也遭封鎖。敵機造型仍是程序化測試模型，不是新製作的高品質 Blender 機甲。

合併順序：v6.1 → v6.0 PR #60 → v5.9 PR #58 → v5.8 PR #57 → v5.7 PR #54 → 前序 Draft PR。**保留全部 Draft，不自動合併。**
