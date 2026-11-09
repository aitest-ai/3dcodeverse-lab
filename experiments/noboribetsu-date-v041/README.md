# 登別伊達時代村 V041 R1：屋頂與四根木柱頂部同步接合候選 H

此版延續 V040 Draft PR #162，屬獨立 QA / Inspector 候選。不要合併、部署或覆蓋 V039 完整園區及任何原始 GLB。

## 真正建模成果
以封存 V039 F+G GLB 為來源製作 H 副本：保留 F+G 已降低的灰泥屋面，再將原 wood_dark 的四根柱子上端 16 個共享頂點同步降低 0.225 模型單位。柱頂從 6.678521 降至 6.453521，灰泥屋面仍在 6.503520，柱頂相對屋面低約 0.0500。柱身側面與柱頂頂面仍連續，原木柱底部、其他 16 個 Mesh、材質、面索引、瓦片、碰撞全部不變。
新 H GLB SHA256：9d6ec28e7844c3b522b6b1453426334f36da580808ad78bd4bc3e7c5969463f4（1,208,064 bytes）。原始 G、F+G 和 V004 等 17 份 GLB 全部逐位元保留。H 是獨立檔，不會覆寫任何舊模型。

## 來源、乾淨重建及真實 WebGL2
唯一 V040 Inspector 基底 ZIP SHA256：800439290b4415deaf691d4e9e369b34a091573a8277be27a6051bd860fbc168。
原始 66 檔中 64 檔 SHA256 不變，只修改 app.js / index.html，新增 H GLB、README、Windows 啟動器、品質契約、幾何 QA 與完整性 manifest，V041 共 72 檔。由原始 ZIP 在兩個全新空目錄重建，72/72 SHA256 完全一致。
真 Chromium + Xvfb + ANGLE SwiftShader WebGL2：17/17 份 GLB 成功載入，桌機 3 視角 × G / F+G / H 共 9 張，柱頂診斷 1 張，430×932 Chrome 行動模擬 1 張，總計 11 張真畫面，沒有 JavaScript/console 例外。屋頂側緣 F+G 對 H 的像素差（max RGB channel >10）345，右側轉角 111，屋簷 77。測試只證明局部幾何差異和開關能運作，不代表實景美術已定稿。

## 明確限制
H 會移除 F+G 無意間露出的原始柱頂，但還沒有確認柱子頂端與其他獨立木樑、瓦片的全部接合關係；也沒有取得可量測高等學問所同棟建築正側面資料。因此工程 PASS、美術 / 現地精度 PENDING。**不要把 H 裝入完整園區 Runtime**；V039 G 仍是上一版已通過隔離完整 B 操作的保留基準。
目前執行環境無 Blender/bpy：沒有真正的 .blend / Cycles 成品。未測 Android 實體手機、私人 HTTPS/CDN / native WebCrypto 端到端或長時間 FPS。沒有更新原網站。

## 可重建交付及 SHA256
Inspector.zip 72 檔 SHA256：9561dcbdcb9fab6b173425eb2b0d809744a44882e41bd9018a8fedbb32417b87。
SourceQA.zip 20 檔 SHA256：30185986add7b5a2266e7f930405ec7e0a9cb84524f7f16f36a6de32f77d5d18。
完整 build_v041.py、qa_v041_browser.py、Blender native gate (未執行)、11 張真實 WebGL2 PNG、幾何 QA、可重播資產與報告均在私有 SourceQA.zip。此 GitHub 分支只保存契約與精確 H patch，不推送完整私有 GLB。
重建：python build_v041.py V040_Inspector.zip NEW_EMPTY_DIRECTORY
開啟檢視器：解壓後執行 START_V041_Windows.bat，或以 python -m http.server 8765 啟動並在 Chrome/Edge 開啟 http://localhost:8765/。不得使用 file://。
官方園區建築背景：https://edo-trip.jp/tw/about/ （不代表該棟的精確現地尺寸）。

KEEP DRAFT. NO MERGE. NO DEPLOY. NO SITE OVERWRITE.
