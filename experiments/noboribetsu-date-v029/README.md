# 登別伊達時代村 V029 R1 — 可回退的屋簷與木作候選

基於 V028 Draft PR #126（獨立建築檢視器）及 V026 Draft PR #120（完整園區 Runtime）。維持 Draft，不合併、不部署、不更動正式網站。

## 本輪實際製作
使用原封 V026 Runtime ZIP SHA256 4e7436827c398689bc97906f268cbd49415ed2d08b2d612d868eb91d98e00167。
於高等學問所原始建築前新增約 19m 的屋簷下木樑、10 組不完全等距的支撐／柱樑接合細節及少量鐵件，4 Mesh、760 三角面、589,996 bytes 的獨立 GLB。
新 GLB SHA256 a3e148ed7a42c52c6740a8842e76c29e213bd3e04f10c4b6bd1523e11b65d78d。
原創程序化燻木與暖木 BaseColor／Roughness／Normal 紋理，不包含第三方照片。
正式 Runtime 只在 B 場景顯示，支援開關，原 V026 窗框不受影響。採原生 WebCrypto SHA256 fail-closed，不修改任何原有 GLB、屋頂輪廓、472 點路線、碰撞、角色控制或導引。
重要：這是作者美術估計，非現地測量或古建築結構認證。不要將「学問所寺子屋」外觀冒充「高等学問所」精確建築尺寸。

## 可重建與通過驗收
137 個原始 V026 Runtime 檔中 133 個雜湊完全相同，只有 app.js、index.html、qa.json、scene_view.json 四處更新；新增 README、GLB、JSON，V029 Runtime 合計 140 檔。獨立空目錄重播 140/140 SHA256 一致。
隔離 Chromium + Xvfb + ANGLE SwiftShader 真實 WebGL2：獨立檢視器六份 GLB 載入，屋簷/斜角/正面各開關兩張真截圖，JavaScript errors 0。
手機 430×932 Chromium emulation：真 WebGL2、斜角和 V029 開關通過（未測 Android 真機）。
完整園區真 Chromium SwiftShader WebGL2：B 場景載入成功、V029 開→關→開通過、V026 保持顯示、W 鍵移動約 1.2894m、JS errors 0。
隔離 QA 專用 digest adapter 和 state hook 不存在正式 Runtime；正式 HTTPS/CDN/登入、Android 實體裝置、長時間 FPS 未驗。

## Blender Native Gate
目前容器無 Blender/bpy，沒有產生 .blend 或 Cycles PNG。獨立 SourceQA ZIP 含 blender_native_v029.py，可在具備 Blender 4.x 以上的電腦，匯入五份既有 GLB 和新 GLB，產生可編輯 .blend 與 4 張 Cycles 同鏡位圖；實際執行前 gate 一律 PENDING。

## 各 ZIP（含全部真正來源與測試）的 SHA256
Runtime: a21beba4ba44ea03ed1f517eeea27e100a45917c6c10dcfd496bac892d9396bd
Inspector: df8cfef094b74311825f12fd874bc32282f6c4e5d1af8c6350478a24d44fcdc6
SourceQA: 34b2a46182563708239eea3d3d6efabde03b30145768441c9fb05b56a5a80c7e

Runtime.zip, Inspector.zip, SourceQA.zip, 六張 WebGL2 截圖、Comparison.png、Review.html、Delivery_Report.md 已獨立提供給使用者。GitHub 不上傳私有大型場景模型。
在 SourceQA 專案根目錄以 Python 執行 build_v029_asset.py、integrate_v029_runtime.py 和 qa_v029_source.py；V026 原始 Runtime ZIP SHA256 必須符合上述值。屋簷建築照片僅作類型參考，不是正交測繪。
官方建築背景：https://edo-trip.jp/tw/about/
商家街攝影參考：https://map.uu-hokkaido.jp/e/date-jidaimura/

保持 Draft，不自動合併、部署或改動分享權限。
