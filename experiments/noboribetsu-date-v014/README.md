# 登別伊達時代村 V014 — V004 中央石板設計候選

這一輪不是擴園或重建場景。以 V013 原 ZIP 為凍結來源，只在 V004 s=89.5–124.5m 內加入一小段 50 塊淺色中央石板設計研究，並提供真正遊戲中的開／關按鈕。

## 內容

- `build_v014.py`：只讀 V013 路線與 V004 原始石邊位置，新增 50 塊石板（100 面），不更動原有模型。
- `integrate_v014.py`：從 V013 完整執行包建立另一份 V014 runtime，防止覆蓋。
- `qa_v014_webgl.py`：隔離 Xvfb + Chromium 的實際 WebGL2 測試，僅 QA 使用測試專用 SHA 替身與鏡位，正式 Runtime 絕不包含。
- `V014_geometry_qa.json`, `V014_replay_qa.json`, `V014_Validation.json`：各自的檢查證據。
- `V014_V004_before_RealWebGL2.png`、`V014_V004_after_RealWebGL2.png`：相同鏡位真實渲染圖。

## 重建方式

1. 解壓 V013 Runtime ZIP 到新的 `v013` 資料夾（有 `dist`）。
2. 執行 `python build_v014.py v013 v014_center_stones.json`。
3. 執行 `python integrate_v014.py v013 v014 v014_center_stones.json`。
4. 在一般支援 WebGL2 的電腦，以本機 HTTP 伺服器提供 `v014/dist`（不要以 file:// 開啟）；於 B 場景中使用「中央石板候選」開關。

## 重要的真實性界線

- 實景照片只能支持「時代村某段商家街有中央淺色石板」的視覺特徵，不能核對本段確切位置或尺寸。此項是可拆除、可關閉的作者推估設計。
- 原道路 GLB、V011 地形補洞、V012/V013 路緣、A 骨架、231.5664m 路線及碰撞全部保留。
- Chromium 已完成真 WebGL2 渲染和畫面比較；實際私人站 HTTPS、Android 真機與 Blender-native 未驗。
- 只在隔離 QA 中使用 Python 獨立 SHA 核對後的測試替身；正式 Runtime 保留 WebCrypto 原生 SHA。