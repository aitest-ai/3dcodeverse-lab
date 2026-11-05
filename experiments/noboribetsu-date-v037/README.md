# 登別伊達時代村 V037 R1｜原始 V004 屋頂白帶「零幾何變動」材質候選

**獨立 QA／建築檢視器，不是完整園區 Runtime。** 基於 V036 Draft PR #146，不使用 V035 B 的屋面頂點下移方案，不修改 V031 完整遊戲，不更新正式網站；請保持 Draft、不合併、不部署。

## 真正建成的東西

V034–V036 的來源追查確認：原 `v004_merchant_facades.glb` 的 `plaster_offwhite` 第 8、9 號三角面（原 glTF 索引 `[3,7,6]` 與 `[3,6,2]`）為可見寬白帶的一部分。V035 B 下移頂點會破壞與側牆三條相鄰外緣的幾何連續。

這輪直接以原封 V004 GLB 為來源，**保留全部 17 個原始 mesh definition、全部 32 個灰泥網格頂點、48 個三角面及全部原有建築幾何與節點位置**。只將灰泥的 48 面拆成舊材質的 46 面與新材質的 2 面（增加一個 primitive，不新增屋面），保留其餘 16 組 Mesh 的原始定義與原始 BIN 的 **1,195,152 bytes 完整前綴**。

製作兩份全棟可切換的原創 GLB：
- **D｜淡暖灰**：`v037_v004_roof_cap_soft.glb`，1,221,288 bytes，SHA256 `fae86ba7a240cd19c99340be61953144f32856d594ce6ab68b1f9b4fb6e31112`。
- **E｜瓦片交界漸層灰**：`v037_v004_roof_cap_blend.glb`，1,223,176 bytes，SHA256 `ef38cdc679c70c01db01e3c69e420cd97205d10ae6bca43e15b3a5672b19ff03`。

貼圖由 Python/Pillow/NumPy 程序化繪製，不嵌入任何網路照片或第三方受限素材。D/E 與原 V004 互斥顯示，不會一層疊一層造成閃爍。原 V036 的屋頂／側面診斷控制全部保留，選回舊功能時自動還原原始 V004。

## 已完成的實測

- 從原封 `Noboribetsu_Date_V036_R1_Inspector.zip` SHA256 `fce794787e2b647972069aff5545a298859160663b4a014f7b7dd66f13198ce4` 在全新目錄乾淨重建，**53／53 檔案 SHA256 完全一致**。原 47 檔中 **45 檔逐位元不變**，僅更新 app.js/index.html 及新增 6 檔。
- GLB 精確檢查：兩個原始面索引、48 面重新組合、32 頂點、原 BIN 前綴、其他 16 Mesh 定義、17 節點配置全部吻合；**原幾何位移 = 0**，不引入 V035 B 的側牆邊界高差。
- 真 Chromium / Xvfb / ANGLE SwiftShader **WebGL2**：13/13 個 GLB 載入，三個固定鏡位（屋頂近景、側面、簷口）× 原版/D/E 共 **9 張實際畫面**；430×932 Chrome 手機**模擬** 1 張，0 JavaScript/console 錯誤，切換互斥與恢復 V036 既有模式通過。
- 屋頂近景同鏡位差異（最大 RGB 單通道差 >10）：D 只 **1 像素**，E 約 **46,216 像素**。這只代表色彩差異可被測得，**不是美術或實景相符分數**。
- **美術判定：D 太微弱；E 有可見調色，但缺少高等学問所同棟可量測的屋頂影像，兩者都未核可用於完整遊戲。** 沒有更新 V031 Runtime。

## 未通過的外部門檻

此執行環境仍沒有 Blender/bpy，所以沒有實際產生 `.blend` 或 Cycles 影像；SourceQA ZIP 內的 `blender_native_v037.py` 僅 source-ready。Android 真機、正式私人網站 HTTPS/CDN／登入、長期 FPS、同棟現地建築尺寸均未驗。

官方背景來源：https://edo-trip.jp/tw/about/；這只能說明園區採仙台藩相關江戶建築風格，不代表本棟屋頂精確尺寸。「高等学問所」與「学問所寺子屋」不能混用照片。

## 私人交付與可重播程式

獨立交付 `Noboribetsu_Date_V037_R1_Inspector.zip`（**53 檔，6,995,346 bytes，SHA256 `ff86ba6e7e64f69505aa5aa5d6cacfd2d73dba3da04e57043e67891fced2f453`**）與 `SourceQA.zip`（**26 檔，2,024,925 bytes，SHA256 `627a0c6a0289a2192c4a6fbb6732ebdafaeae44faeeb20ae13492af5e62ada5a`**），以及 9 張桌機 WebGL2、1 張手機模擬 PNG、Validation、前後比較 PNG、可離線拖曳的 Review.html、Delivery_Report.md。

**完整可重建 Python 程式不只 README：** SourceQA ZIP 內有 `source/build_v037.py`、`replay_v037.py`、`qa_v037_geometry.py`、`qa_v037_webgl.py`、`blender_native_v037.py`、`package_v037.py`，並含兩份產生的 GLB 與真實畫面證據。執行：
```bash
python source/build_v037.py /path/to/Noboribetsu_Date_V036_R1_Inspector.zip /new/EMPTY_V037_DIR
python source/qa_v037_geometry.py /new/EMPTY_V037_DIR /new/V037_geometry_QA.json
# 在有 Chromium + Xvfb + Playwright 的環境：
xvfb-run -a python source/qa_v037_webgl.py /new/EMPTY_V037_DIR /new/QA_EVIDENCE
# 需 Blender 原生環境才可以做 Native Gate：
blender -b --python source/blender_native_v037.py -- /new/EMPTY_V037_DIR /new/EMPTY_NATIVE
```

解壓 Inspector ZIP 後以 Python HTTP server 啟動（Windows 可執行 START_V037_Windows.bat），Chrome/Edge 開啟 `http://localhost:8765/`，**不能直接用 file:// 雙擊啟動**。

本 GitHub Draft 保存品質契約與可重用的來源驗證程式，私有完整 GLB 只在獨立交付的私人 ZIP 中，沒有把整座園區上傳。**KEEP DRAFT — NO MERGE / NO DEPLOY / NO HOST OVERWRITE.**
