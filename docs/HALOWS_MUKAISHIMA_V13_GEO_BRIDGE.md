# 瀨戶內騎行世界｜Halows V13 真實 GLB 地理銜接（未整合 Runtime）

## 版本來源與保護
- 基底：V12 Draft PR #78 `feat/halows-mukaishima-v12-route-audit`，parent commit `2cb322a0050a668bb70e3681f667bc51f9eec0cd`。
- Halows V11 Blender 5.2.3 真輸出來自 PR #65，成功 Actions run `41289500633`，artifact `13076479348`（2026-11-15 前可從 Actions 取得）。**不可直接以本分支 code 代替真正 GLB。**
- V11 原始 GLB SHA-256：`19d633a04d1821249a9964471f63d530cbd8ed44eba707f2d17052210140ab9e`。原版 .blend、七張 Blender render、兩張程序材質、原始 manifest 與 GLB 均保留於原 Artifact。
- `site_lock.json` SHA-256：`71873821d96c937465fd6cbd3f05d0f6a66c564f4f3cbcd6f6e968b462f2ccf9`。原位置 34.39702355N, 133.19961285E；OSM building way `661155704`。
- 不改 main、舊 V06 Runtime、人物、單車、渡船、既有網頁、V07–V12 檔案。不自動合併／部署。

## 這一輪實際完成
1. `scripts/research/halows_v13_geo_alignment.mjs` 以 WGS84/ECEF 轉 ENU，將 Halows V09 原點對齊 V06 尾道世界。V06 原點 `[133.201729,34.4059115]`（經緯）。
2. 平面座標預期 x 約 **-194.586m**，z 約 **+985.935m**（glTF x東、y上、z南）。以 V06 已知 node `8255588823` 對照原座標 [87.2815,176.1121]，誤差約 0.002m。
3. Y **特意保留 null**。V11 腳本 `graded_rel_z/road_z` 已減去估計店區平台 `PAD=2.70m`。原 V06 Gate 的 +2.70m 並非已驗證的 Runtime 世界高程，不能盲目套用；須先取得 V06 原版地形、世界座標與垂直基準。
4. 已有原版 V11 GLB 的離線三維**候選檢視器**和 WebGL2 不可用時的七張真實 Blender 圖替代顯示，供候選審圖。完整檢視器、原版 GLB、母檔與七圖由 V13 對話獨立 ZIP 交付，不將大量 binary 直接提交本研究分支；本分支保持可交接的座標計算、CI 與手冊。

## 可重現水平門檻
```bash
mkdir -p outputs/halows-v13
python3 - <<'PY'
import sys,json,pathlib
sys.path.append("scripts/blender5")
from halows_site_v09_data import load_site_data
pathlib.Path("outputs/halows-v13/site_lock.json").write_text(
    json.dumps(load_site_data(),ensure_ascii=False,indent=2),encoding="utf-8")
PY
node scripts/research/halows_v13_geo_alignment.mjs
```

結果 `outputs/halows-v13/geo_alignment.json` 只承認平面定位成功、路權／垂直／瀏覽器／Android／人物碰撞皆未驗收。源鎖或 V06 anchor 不符就失敗，不得調寬門檻掩蓋來源差異。

## 後續必做（不可自行宣稱完成）
- 恢復真正的 V06 Runtime+Editable（不是 V05 替代母檔），比對網站最新工作樹 SHA、`world.json`、人物／單車與 GLB 資源。
- 對真正 V06 地形抽樣與 V11 PAD 取得**同一垂直基準**後，才產生 y 平移與交界連續掃掠。
- 渡船須核對現役線：尾道駅前～向島富浜、土堂～向島兼吉。福本渡船已於 2025/03 停航，不能當可搭乘航線。
- OSM V12 僅 4 ways / 39 nodes 的**局部中心線**；田尻西→南 66.5m 涉及 trunk 國道317，東 61.5m 為 tertiary；缺渡船→東西橋→Halows 真正道路資料、合法自行車藍線、店門與路緣切口。不能創造缺失可騎線、擅自跨接道路。
- 即使幾何、GLB 結構與 Blender 渲染成功，仍需真 Chromium WebGL2／Android 實際騎行、步行、牽車、碰撞、鏡頭驗收；WebGL2 不可用的圖片保底**不是**可玩 3D 驗收。

## 授權與官方參考
- © OpenStreetMap contributors，ODbL：https://www.openstreetmap.org/copyright
- GSI DEM5A 鎖定原資料詳 V09，20m 代表可讀子採樣而非新的 5m 測繪。
- Halows 既有店照：https://www.halows.com/stores/detail/77 （歷史照片僅作外觀參考；不複製為貼圖）。
- 島波海道官方安全資訊：https://www.jb-honshi.co.jp/english/shimanamicycling/howto/index02.html
- 尾道市渡船資訊：https://www.city.onomichi.hiroshima.jp/soshiki/32/65681.html
