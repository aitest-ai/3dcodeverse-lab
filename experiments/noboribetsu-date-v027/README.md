# 登別伊達時代村 V027 R1｜建築比例與原生驗收（QA-only）

> **這是 QA-only 進度，不是新的建築模型或 Runtime。** 基底固定為 V026 Draft PR #120。保留所有 V002–V026 分支與完整 3D 場景，**不合併、不部署、不改分享設定**。

## 重新驗證的真實成果（2026-11-03）

使用獨立 Xvfb + Chromium ANGLE SwiftShader **真正 WebGL2**，直接讀取私有封存的 V026 完整 B 網頁：WebGL2 建立成功、B loaded=true、進場成功、V026 開→關→開及 V025 fallback 通過，W 鍵移動 1.26744m；測試程序 exit code 0，瀏覽器例外空。這次檢查是重新執行 V026 控制測試，**不是**從過去 V025 繼承驗收。正式站 HTTPS/CDN、Android 真機、長期 FPS、完整場景 A/B 截圖仍未驗。

隔離測試使用 QA 專用相機 hook、測試專用 SHA adapter；正式 Runtime 檔案沒有替換原生 WebCrypto。

## 幾何與封存證據
- V025 Runtime SHA256：`edad5d98c6632a7be7ae668cb80f6d6f2e4eb7f3f948507ce99e83f281bbc085`
- V026 Runtime SHA256：`4e7436827c398689bc97906f268cbd49415ed2d08b2d612d868eb91d98e00167`
- V026 SourceQA SHA256：`626c24d005c2192c984b2843d25c2253aed59dbc7602c56511ec1a768e0883f2`
- 134 → 137 檔；130 份不變、4 份原有介面接線變動、3 份新增（README、GLB、JSON）。
- V026 7 mesh／952 triangles，原 V025 5 mesh／792 triangles 的全部頂點、面索引一致。新增木框 112、陰影 48；沒有零面積三角面；原路線 472 點、CollisionWorld 不變。
- **模型量測**（不是現場尺寸）：該窗格外框 2.49m 寬，紙窗 1.988m 寬，紙窗寬度比例約 79.84%，模型外框高度約 2.959m。沒有足夠的精確現場高等學問所立面照片／圖面作比例認證。

## Blender Native Gate：PENDING

這次環境無 Blender / bpy 也無法下載安裝，**沒有生成 .blend 或任何 Cycles PNG**。交付 SourceQA ZIP（獨立私人檔）包含：
- `source/audit_v027.py`：檔案／模型頂點與幾何及比例稽核，錯版 fail closed
- `source/run_blender_v027.py` 與 `Run_V027_Native_Windows.bat`：在 Blender 4.5+ 電腦上實際跑 V026 Native Script，輸出 .blend、4 張 Cycles 與驗收 JSON 前才可改成 PASS
- 同鏡位 V025/V026 **前輪真實 WebGL2** 截圖、這次完整 B 操作 JSON／日誌、比例 JSON、反例驗收
- 獨立 HTML 比較頁與 PNG；都是審查證據，無新模型

GitHub 本 PR 只保存可公開驗收程式及來源契約，**不包含私有大型 Runtime/GLB**。下個實際建築重製階段需先補高等學問所可驗證的現場立面比例，不以其他園內照片替代實測。

**保持 Draft；勿合併或部署。**
