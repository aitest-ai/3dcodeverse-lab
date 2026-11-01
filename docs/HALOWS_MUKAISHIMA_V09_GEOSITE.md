# Halows 向島店 V09｜真實地理小樣區候選

## 定位
V09 從 V08 Blender 候選另開，不覆寫 V08、不更新瀨戶內網站、不合併 main。

本輪第一次把 Halows A棟放入真實地理骨架：
- OSM building way 661155704 四角作平面位置與方向。
- 本地 ENU 原點：OSM 四角平均，WGS84 約 34.39702355, 133.19961285。
- 長邊方向：約從正東逆時針 19.26266°。
- GSI DEM5A preserved snapshot 作周邊地形參考。
- OSM Route 317 / service-road snapshot 作道路幾何。

## 高程界線
OSM footprint 四角對應的 DEM5A 約 2.25–2.87m；南側服務道路節點約 1.71m。V09 使用 2.70m 作「店區整地平台」估計值，並用 18m 羽化接回 DEM。這是模型整地假設，不是竣工高程或測量成果。

## 路線界線
Route 317 和店區 service roads 只作地理關係與視覺接續。官方しまなみ資料要求一般道路沿 Blue Line；Halows 是尾道市 Cycle Oasis，但汽車進出示意圖不能直接變成自行車導航。

因此 V09 不建立「已認證店門自行車路線」；南／東 access point 只作定位 marker。精確 curb cut、店門與穿越停車場的自行車／步行通路仍待核。

## 資料來源
- Halows 向島店官方頁與店區進出示意。
- 尾道市 Cycle Oasis。
- JB本四高速 Shimanami cycling guidance。
- OSM 2026-10-31 preserved research snapshot，ODbL。
- GSI DEM5A preserved V06 snapshot；地理院タイル標高資料加工。

## 驗收
工作流必須用 Blender 5.2.3 LTS 重建 .blend / GLB，產生 site_aerial、route317_arrival、forecourt、north_overview 四張 Blender 圖，並通過 GLB structure validation。

這仍不是 runtime / browser / Android 驗收；人物與自行車實際入景會在成功 Artifact 取回後另做比例檢查。
