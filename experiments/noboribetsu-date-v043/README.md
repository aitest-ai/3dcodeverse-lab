# 登別伊達時代村 V043 R1｜四柱完整柱頂投影與木構件接合診斷

**獨立 QA / Inspector-only。** 直接從 V042 Draft PR #170 接續；不生成新的建築物 GLB，不修改 V039 G 完整園區、不變更碰撞、導航、網站或分享權限。保持 Draft，不合併、不部署。

## 為何從 V042 的中心距離改用整個柱頂
V042 已量過 4 根柱頂中心到最近 wood_lintel / wood_timber 三角面的距離，並發現中心垂直投影沒有命中。但「中心點沒有命中」不能推論整個柱頂沒有與木構件交疊。
V043 從封存的 H GLB 原始 wood_dark 兩三角面柱頂（P1 20/21、P2 32/33、P3 44/45、P4 56/57）擷取整片 0.150 × 0.200 的頂面，每片面積約 0.030 平方**模型**單位。逐一與 wood_lintel、wood_timber 的全部原始三角面計算投影到 XZ 平面的相交面積，以及精確的最短水平投影距離（Shapely）。另以 11×11 網格在整個頂面取樣 121 點，估計到原始木構件三角面的最短**3D 距離**。

| 柱頂 | lintel 最短 XZ 水平距離 | timber 最短 XZ 水平距離 | 11×11 近似 3D 最近值（lintel / timber） |
|---|---:|---:|---:|
| P1 左前 | 0.590 | 0.425 | 0.590 / 0.460 |
| P2 右前 | 0.590 | 0.425 | 0.590 / 0.460 |
| P3 左後 | 0.220 | 0.425 | 0.590 / 0.730 |
| P4 右後 | 0.220 | 0.425 | 0.590 / 0.730 |

**四柱 × 兩類木構件，共 8 組 XZ 投影重疊面積全部為 0。** P3/P4 在平面上距 lintel 較近，但因三維位置不同，3D 最近距離並沒有同樣減少。3D 取樣結果不是精確的全域 mesh-to-mesh 最近距離。

本檢查僅涵蓋兩個名稱特定的木構件 Mesh。木柱頂面與灰泥屋面模型內仍相隔約 0.05 單位，但不能把灰泥當作真實承重木樑。也不能從這個結果推論柱側面、其他隱藏結構或實際建築沒有支撐。**禁止把模型內的數字當成現場結構安全檢驗。**

## 真正完成的網頁工具
V043 由原 V042 Inspector.zip 直接乾淨重建，載入 3 份原始 G／F+G／H GLB（逐位元完全不變）。可單柱或四柱切換、比較 wood_lintel/wood_timber、看到 GLB 真三角面投影、柱頂外框、水平最近點、三維取樣最近點、11×11 點陣、暫時隱藏瓦片、四種固定鏡位及旋轉縮放，並可下載數據 JSON/CSV。所有彩線和標記只供診斷，**不是新建築構件**。

真 Chromium 144 + Xvfb + SwiftShader WebGL2：**3/3 原始 GLB 成功載入**，P1/P4、兩類木構、格點顯示、G/H 切換、隱藏屋瓦與固定攝影機通過。桌機 6 張真正截圖，430×932 行動 Chrome 模擬 1 張，0 JavaScript/console 錯誤。正式網站、Android 實機與 Blender 原生尚未驗收。

## 不可變資料與重播
唯一封存基底：Noboribetsu_Date_V042_R1_Inspector.zip，SHA256 `d6949e140f0763df1f2608ed5da6c48938192852878e52d18e121d69ac51d139`。
原版 17 個檔案中 **14 檔逐位元不變**，僅更新 app.js、index.html、style.css；另外新增診斷 JSON、CSV、README、品質契約、兩平台啟動腳本和 manifest，新版 **24 檔**。兩個空白工作目錄由未修改 V042 ZIP 重播 **24/24 SHA256 完全一致**。所有原始 GLB、Three.js vendor 與原有 V039 完整園區保持不變，ZIP CRC 通過。

獨立交付的 SourceQA.zip 存有完整可重跑 `audit_v043_footprint.py`（精確 Shapely 投影與 121 點三維取樣）、`replay_v043.py`、`qa_v043_source.py`、`qa_v043_webgl.py`、完整 app.js/index.html/style.css、7 張真 Chromium WebGL2 PNG，以及量測 CSV／JSON 和 SHA 契約。
本 GitHub 分支只保存不含私人場景素材的精確稽核演算法、交接和 QA 契約，不上傳原始 3D 模型或私人網站。

重播：`python source/replay_v043.py /private/Noboribetsu_Date_V042_R1_Inspector.zip /new/EMPTY_V043`，需 numpy/trimesh/shapely。網頁啟動：解壓 V043 Inspector.zip，在目錄內執行 `python -m http.server 8765`，以 Chrome/Edge 開啟 `http://127.0.0.1:8765/`；不能直接雙擊 file://。

## 交付 SHA256
- Inspector ZIP（24 files）：`23d23719fb7872f09f372c61796caffdfaa90c11667cfa7bc513f3c0fad67562`
- SourceQA ZIP（26 files）：`ccbef699745d2adbc3106733132dd27880606e2427260eb4c71d81cee27d8588`
- 實際 Chromium 四格 comparison PNG：`621ecd00db7a25372407c9071924600f8e09434c363d79c463ba9761a072b44b`
- 完全離線 slide Review HTML：`a774589e6ca39151160f481111eb62f4a638a44749b50206f9b053a4e1e0797b`

**限制**：沒有 Blender .blend/Cycles、Android 真機、正式私人 HTTPS/CDN、實地量測或結構安全確認。V044 可繼續檢查 wood_dark 及木柱側面與其他獨立構件的接合，不自動創造假想木梁。

KEEP DRAFT · NO MERGE · NO DEPLOY · NO PRIVATE HOST OVERWRITE.
