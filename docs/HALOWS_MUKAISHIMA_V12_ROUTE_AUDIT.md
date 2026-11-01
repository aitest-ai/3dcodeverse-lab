# Halows 向島店 V12｜連通性 QA（非導航）
 
## 起點與範圍
- Source: `scripts/blender5/halows_site_v09_data.py` (Git blob `a4af2bae722236664297cab363099e4b4dce498b`)。
- Parent: `feat/halows-mukaishima-v11-facade-materials`，只新增獨立道路幾何驗收工具與離線 2D QA 預覽，不改 V11 幾何、V06 Runtime、main 或網站。
- OSM way 661155704 定位 Halows A 棟；4 條 OSM road way，39 個節點、39 條邊，同一連通群。這僅為店區固定 snapshot，不含渡船碼頭→超市的完整自行車路線。
- 先前 V06 的人物、單車、渡船和介面原封不動；所有建模候選依舊保留。

## 實際計算
- 田尻西 (`1296327484`) → 南側 service access (`6191315885`)：**66.5m**，沿 OSM `trunk`（國道 317）中心線。
- 田尻西 → 東側 service access (`6191315891`)：**61.5m**，沿 `tertiary` 中心線。
- 距離均是鎖定資料內的幾何最短路徑，**不是**批准騎行的導航建議，沒有現場自行車通行、斑馬線、路緣坡口、車道寬度或坡度的實測。
- 若圖上線段共用 node ID，可證幾何連接；不能因此證明實際路權、安全與無障礙進出。
- 2.70m 店區整地、18m 地形羽化與高程快照延續舊版估計，未提升為竣工測量。

## 交付與重現
- 腳本：`node scripts/research/halows_route_v12_audit.mjs --write`（Node 22；不需 Blender、外網、字型或 API）。
- 報告：`outputs/halows-v12-route-audit/report.json`。
- 離線示意圖：`outputs/halows-v12-route-audit/route-preview.html`，另附固定版 `examples/halows-route-audit-v12.html`；按鈕切換南／東路徑。這是 2D QA，**不是** 3D Runtime。
- 工作流程 `.github/workflows/halows-route-v12.yml` 在獨立分支建立 Artifact，提供同一份報告與預覽。

## 下一輪整合前的必過 Gate
1. 核對渡船登岸點、東西橋實際轉向及真正騎行可用道路（不能從國道 317 車道或 Halows 汽車箭頭推論）。
2. 查核進出道路與店門、停車與步行導引，區分可騎行／須牽車／禁止進入；取得可靠照片或現場證據。
3. 才能為缺少的區段建立可見幾何與連續掃掠碰撞，放入高品質原角色／自行車，處理橋上橋下與車路分流。
4. 以固定鏡位實測 V11 材質、遠近 LOD 與整體光照；瀏覽器和 Android 路線往返與控制手感需另驗收。
5. 未通過不合併 main、不更新使用者原網站；不把經過 GitHub Actions 視為「可遊玩已通過」。

## 來源與授權
- OpenStreetMap：ODbL，© OpenStreetMap contributors。 https://www.openstreetmap.org/copyright
- 日本國土地理院：既有 GSI DEM5A 快照與授權鏈，詳 V09 文檔。
- Halows 官方店面／汽車進出圖：https://www.halows.com/stores/detail/77 （僅外觀與汽車動線研究，不當自行車導航）。
- JB 本四高速島波海道騎行指引：https://www.jb-honshi.co.jp/english/shimanamicycling/howto/index02.html （一般路段依藍線指引、尾道至向島建議渡船）。
- 本輪成果為自行開發的幾何路網檢查及 SVG 示意，沒有附帶官方照片、商標字型或第三方地圖貼圖。
