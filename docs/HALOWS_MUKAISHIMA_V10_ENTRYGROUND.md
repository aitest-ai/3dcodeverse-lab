# Halows 向島店 V10｜入口深度、地形接合與同鏡位檢查

## 工作隔離與來源
- Parent: feat/halows-mukaishima-v09-geosite / commit fe938dd0f65f4f8f5ef2584397654d5ff036d0bc，V09 專用 Blender CI #41277292007 成功。
- V10 獨立分支及 Draft PR，基底指向 V09 分支；不覆寫 V07–V09、不合併 main、不更新舊 Runtime／網站。
- 承接 V09 OSM way 661155704、本地 ENU 原點、方向、Route 317、service roads 及 GSI DEM 快照。site_lock 的來源 ID 仍是 V09，不冒充新測繪。

## 真正核對了 V09 產物
- V09 實際 Blender 輸出的 BLEND／GLB、四個同鏡位 PNG、manifest、site_lock 與 validation 取自成功 artifact 13070804708。
- 在 PNG 中可見：店面玻璃疊在不透明主建築塊表面、入口粉紅塔樓不通透、整體曝光偏暗、停車區與地形接邊很生硬。
- 專案既有泛用 Blender mecha workflow 在 V09 SHA 上失敗，不等於 Halows 專用工作流程失敗；V09 專用 workflow 結論 success。

## V10 本輪製作
1. 主建築改成中空屋殼（樓板、屋頂帶、兩側牆、後牆、前緣上下構件），不再在落地玻璃背後放整塊實牆。
2. 塔樓入口改成兩側門柱和上方過梁，保留原招牌、雨棚、入口尺度；中性深色遮蔽片只是讓未知店內不穿幫，不是復原內裝。
3. 為玻璃外觀補窄框、門檻及低調的鋪面接緣。精確分格、門位置、路緣坡道仍是估計。
4. 改善停車場、路面和地表用色，加入渲染專用的軟補光，保留 V09 的 site_aerial、route317_arrival、forecourt、north_overview 同鏡位，新增 entry_eye 人眼高度鏡位。
5. 修正報告誤把羽化寫成 10m 的錯誤；模型仍沿用原本實際 18m 的羽化計算。

## 授權與資料界線
- Halows 官方門面照片：https://www.halows.com/stores/detail/77
- 尾道市 Cycle Oasis 清單：https://www.city.onomichi.hiroshima.jp/site/onomichikanko/1312.html
- OSM 來源／ODbL、GSI 標高及授權沿用 docs/HALOWS_MUKAISHIMA_V09_GEOSITE.md。20m 是 DEM 可讀子採樣，不是完整 5m 測繪重建。
- 沒有實際新資料支持的店內商品、店門座標、停車場人車動線、自行車合法進場口及東西橋轉向一概不自行認證。
- Blender 補光不等於 GLB 已打包完整遊戲光照；Three.js／其他 Runtime 必須另外驗證。

## 驗收 Gate
- GitHub Actions Blender 5.2.3 LTS 必須真的產生可編輯 .blend、.glb、site_lock.json、asset_manifest.json、report.json 和 5 張 PNG。
- 通過 scripts/blender5/validate_glb.py，並以 V09 同鏡位照片對照玻璃深度、塔樓入口、鋪面邊緣及整體亮度。
- 人物和自行車尺度、碰撞與鏡頭、進店與單車停放、渡船往返、Browser/Android 實玩，全部維持待驗證，不能把 Blender CI 綠燈當成遊戲通過。
