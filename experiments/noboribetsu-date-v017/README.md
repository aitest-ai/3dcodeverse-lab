# 登別伊達時代村 V017 R1｜商家門前步行淨空診斷

**本輪不是新建築或已驗收的店門通道。** 從 V016 凍結執行包取得既有 V004 商家街 route、walkable 三角面及 24 個 B-stage 模型碰撞障礙物，沿 s=82.877–130.0146m 每約 0.20m 取樣並扣除角色水平半徑 0.26m。

## 已完成的實體查核
- V004 路線中心線 237/237 取樣點落在原有可行走多邊形中；最小水平淨餘距 0.23203m，出現在 s≈89.8677m（高等學問所柱廊附近），縱坡最大 1.582%。
- 對每個中心點再取 7 個左右偏移位置，累計 1,659 個側向取樣，**沒有宣稱全部位置可走**。此為 2D 多邊形、模型障礙及角色半徑試算，未核實門檻高度、真實現場動線、動態障礙、室內或無障礙規範。
- B 精修場景新增 4 個可開關黃色環狀診斷標記；工具列「步行淨空診斷」預設關閉、不增加碰撞。保留 V016 四點基座診斷、V015 八處柱腳補強及 V011～V014 全部既有成果。
- 已真正透過隔離的 Chromium + SwiftShader 建立 WebGL2、解析完整 B 高品質場景，並觀察 V017 標記與按鈕 `false→true→false`。SHA adapter 僅在 QA Python 腳本中；正式 Runtime 仍使用 `crypto.subtle.digest`。
- 以未修改的 V016 Runtime ZIP 乾淨重建：新 V017 執行包 115/115 個檔案 SHA256 完全一致；原 V016 113 份檔案中 109 份不變，只更新 app.js、scene_view.json、index.html、qa.json，另加兩個新檔。

## 如何重播
1. 取得未修改的 `Noboribetsu_Date_V016_R1_Runtime.zip`。先核對 SHA256：`44f86918c5c548cf34fc28c7d38e4022dda7a65fbbaf145f99eb58a9c26dd3c9`。
2. 在新空白資料夾放置 V016 ZIP 與本包 `build_v017_clearance.py`、`integrate_v017.py` 等腳本，將原 ZIP 解壓至 `base/`。
3. 安裝 Python 套件 `numpy shapely trimesh matplotlib pillow`。先執行 `python build_v017_clearance.py`，再執行 `python integrate_v017.py`。
4. `python validate_v017.py` 需要完整隔離 WebGL2 QA 證據；若尚未執行，可先檢查原始 `V017_clearance_qa.json`、`node --check base/dist/app.js` 和重建檔案 SHA256。
5. 完整 Chrome WebGL2 測試可執行 `python qa_v017_webgl.py`（Linux 需 Xvfb、Playwright、Chromium 與 SwiftShader）。請勿將 Python QA 專用 SHA adapter 混入正式網站。

## 未驗收
真正 HTTPS top-level/native WebCrypto、私人網站 CDN/登入、Android 實體手機、Blender 原生 `.blend`、實景柱廊尺度及各店門檻與室內通行皆未完成。維持 Draft，不合併、不部署、不覆蓋 V016。