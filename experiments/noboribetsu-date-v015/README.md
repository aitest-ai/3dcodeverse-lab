# 登別伊達時代村 V015｜V004 柱腳接地修正候選

本分支僅新增 `experiments/noboribetsu-date-v015/`，由 V014 Draft 工作分支延續，不覆寫 V002～V014，也不更新私人網站。

## 已完成
- 取用真正的 V004 facade/road GLB 和 V002 凍結地形，審核 V004 三棟商家建築 22 處柱腳。
- 發現 8 處懸空（門前地面差約 3.7～14.2cm），對高等學問所與北京亭新增 8 個獨立視覺接地支撐，96 個三角面，原模型未修改。
- 另外 4 處舊柱腳埋入地面超過 3.5cm，**本次沒有修復**，避免改動建築結構與碰撞；在 QA 中保留明確記錄。
- 在 B 精修模式加入「柱腳接地候選」開關；V014 的「中央石板候選」開關完整保留。
- V014 Runtime 111 個檔案中 107 個位元不變、4 個必要程式/設定改動，加上 1 個新 JSON，V015 共 112 個檔案。自原封存 ZIP 乾淨重建 **112/112 個 SHA-256 一致**。
- 原有高品質 B 模型、V011 地形補洞、V012～V013 路緣、路線及碰撞都未修改。

## 真實性界線
- Chromium/Xvfb/ANGLE SwiftShader 已成功建立 WebGL2，完整 B 場景載入成功，V015 度量資料顯示 8 處補強；但僅成功擷取補強前畫面，補強後的完整 WebGL2 擷取在慢速軟體渲染中逾時。
- VTK 的 GLB 同鏡位對照僅為診斷圖片，**不是** WebGL2 正式遊玩完成證據。
- 測試專用 SHA adapter **只存在 QA 腳本**，正式 Runtime 原生 crypto.subtle.digest 沒有被替換。
- 石質補強尺寸是依原模型幾何的視覺估計，非現地測量；Android 真機、私人網站 HTTPS/CDN/登入和 Blender Native .blend/Cycles 仍未驗。

## 重新建置
先將 V014 Runtime ZIP 解壓到空白工作資料夾的 `base/`，將 `scripts/build_v015.py` 和 `scripts/integrate_v015.py` 複製到與 `base/` 同層，設定 `NOBORIBETSU_V002_COMPLETE_ZIP` 指向原本 V002 Complete.zip，依序執行這兩個 Python 腳本。所有原資產都保留在使用者私人封存 ZIP，不放入公開 GitHub。

版本交付包保存在使用者私人 ChatGPT Library `/Noboribetsu_Date_V015_R1/`，包含完整 Runtime ZIP、SourceQA ZIP、獨立 GLB、同鏡位 VTK 比較與 SHA 清單。

**保持 Draft，不合併、不部署、不更改分享設定。**
