# v23｜北海道木雕熊：先確認輪廓，再雕木紋

**狀態：CANDIDATE / 未驗收。** 本次為獨立幾何實驗，絕不覆蓋 `models/hokkaido-bear/latest` 與 v22。

## 參考實物與風格邊界

- 北海道立北方民族博物館：https://hoppohm.org/object2/D12_11.htm
- 北海道立北方民族博物館木雕熊館藏報告：https://www.hoppohm.org/book/dayori/dayori109-120/dayori_117.pdf
- 八雲町官方木雕熊歷史：https://www.town.yakumo.lg.jp/uploaded/attachment/15093.pdf
- 旭川系實物「北人作」鮭熊：https://www.antique36gosen.com/onlineshop/item/bear/%E5%8C%97%E4%BA%BA%E4%BD%9C%E3%80%80%E9%AE%AD%E3%82%92%E3%81%8F%E3%82%8F%E3%81%88%E3%81%9F%E6%9C%A8%E5%BD%AB%E3%82%8A%E7%86%8A/

本實驗只借鑑實物照片的可觀察形態；不下載、擷取或挪用任何賣家 3D 模型。八雲系早期作品不以咬鮭魚為主要特徵，不能把所有北海道木雕熊說成同一種風格。

## v23 的優先規則（Shape First）

1. **熊的整體**：頭頸與厚肩自然連在一起；四腳踩在同一地面，避免圓柱靴筒和貼附葡萄形腳趾。
2. **嘴和魚的剖面**：先確認魚中央高點與低點分別靠近上、下顎，不只檢查魚心座標接近嘴巴；從 45° 和正面看到上下顎包住魚，不是魚橫擺在鼻子前。
3. **魚輪廓**：從魚嘴、鰓蓋、腹部、漸細尾柄到分叉尾鰭有清楚漸變，中央魚身有真正三維厚度，而不是矩形木板。
4. **魚鰭**：3D 網格連結魚身、沒有穿模或浮空；各部位隨魚中心線彎曲。
5. **表面**：現階段只用霧面素色材質，刻意不做濃重木紋。確認高模輪廓後才按解剖方向製作長短不規則的刀痕。
6. **反證**：四視角實際渲染若仍看起來像魚板或浮空咬合，停止修材質，重新建構咬合腔與魚身。

## 可驗證交付物

- `model.py`：完全新建的 Blender 幾何腳本，保留可重現性。
- `v23_highpoly_clay.glb`：真實輸出，不接受生圖假裝 GLB。
- `view_front_right_high.png`／`view_front.png`／`view_back_left_high.png`／`view_top.png`：實際 Blender Cycles 四視角。
- `shape_report.json` + `QA.json`：模型雜湊、網格數量、幾何與渲染檔檢查；所有藝術判斷標為 `UNREVIEWED`，不得自動核准。
- 前一輪 v22 已遭視覺審查退件，僅作對照基準。

## 品質閘門

數值與檔案正確不等於藝術完成。只有確實檢視多視角圖片、能清楚辨認咬合及木雕解剖、且平均達 4/5、每項至少 3/5、沒有 blocker/critical 問題，才可提出正式釋出。未達標，一律候選版。
