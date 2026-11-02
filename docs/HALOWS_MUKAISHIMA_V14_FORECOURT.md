# 瀨戶內騎行世界｜Halows V14 入口、雨棚與地面接縫的 Blender 候選

## 已實際承接
- Base PR #83：`feat/halows-mukaishima-v13-glb-geobridge`，不改 main、現有 V06、網站或其角色／自行車／渡船。
- 精準繼承 V11 原建模腳本 Git blob `12480d7767a179b4453331617ad6d856ac418685`。V14 只執行其幾何建構前段，**不執行 V11 導出階段**，本次另存 `.blend` / `.glb`。來源若變更會立即拒絕重建，不默默降級或用方塊取代。
- 真實世界座標沿用 V09 `OSM way 661155704`、WGS84 原點 `34.39702355,133.19961285`、20m 可讀 GSI DEM5A 子採樣、固定道路 OSM 快照。2.70m 店區整地、18m 羽化屬估計，仍非測量。

## 視覺精修
- 保留 V11 雙面日文／英文招牌、拱形入口與玻璃推拉門；調整奶油／粉色暖度及低對比牆縫，加入門柱陰影、金屬門檻及雨棚收邊。
- 補屋頂外緣蓋板、低調屋頂服務線，避免整面像無分格平滑方塊。實景沒有核對的排水細節全部標為美術假設。
- 補已建停車場外緣與前場側邊低矮接合條，目的是改善模型接縫；**沒有新增合法進出口、路緣坡口、行人穿越線、騎行藍線或真實通路**。
- 追加柱腳與小型五金。新增兩張自主程序原創屋頂、地面貼圖，全部打包原生 `.blend` 與 GLB；舊 V11 兩張貼圖也保留。
- 保留 V11 原本 4 個固定同鏡位參考：`site_aerial`、`forecourt`、`entry_eye`、`tower_identity`；另有 `apron_detail`、`roof_edge`、`facade_oblique`，共 7 張真正 Blender render。
- V14 所有額外修改只在新分支中，原 V11 Artifact 仍是基準。

## 驗收分層
- **Blender 建置**：`.github/workflows/halows-v14.yml` 使用 Blender 5.2.3 LTS，校驗官方 SHA256 後產出 `.blend`、GLB、PNG、manifest、report、site_lock。
- **結構**：`validate_glb.py` 必須通過；GLB 必須有原 V11 的招牌與玻璃構件，也必須有 V14 的屋頂蓋板與停車場接合條，含至少 4 張貼圖。
- **真實圖片**：絕不以程式執行成功直接宣稱美術品質通過。必須對照 V11 原 render，同一鏡位核對色溫、鋪面、入口與畫面邊角。候選結果可能仍需要修整。
- **仍未通過**：V06 世界垂直基準與 V14 接地、人物騎姿、可通行掃掠、渡船路線、東西橋轉向、Halows 合法自行車進場、Browser WebGL/Android 互動性能。
- **渡船限制**：尾道駅前／富浜、土堂／兼吉目前可用；福本渡船 2025/03 停航。不得把尾道大橋當主遊玩騎車替代路線。

## 授權與資料來源
- 造型參照 Halows 官方歷史照片：https://www.halows.com/stores/detail/77；只用於眼睛比對，沒有複製其圖片像素、商標照片或網路貼圖。
- OSM contributors © / ODbL：https://www.openstreetmap.org/copyright
- GSI DEM5A 來源沿用 V09 文檔，不宣稱新增 5m 真測繪。
- 尾道市官方自行車渡船安全提醒：https://www.city.onomichi.hiroshima.jp/site/onomichikanko/59215.html
- 本州四國連絡高速道路島波騎行指引：https://www.jb-honshi.co.jp/shimanamicycling/howto/index02.html
- 交接給其他 AI 時，先讀本檔與 `docs/HALOWS_MUKAISHIMA_V13_GEO_BRIDGE.md`，勿直接覆寫 V06 Runtime。建議下一步先補 V06 原始編輯包、建築平面 Y 對位、法規通行和地形完整驗收，再做 3D 對接。
