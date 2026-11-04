# 來源盤點與採用界線

查核日：2026-11-04（臺灣）。獨立分支由 main `f088f0e584764b3fd37dc1bc0670df99313bec41` 開始；原工作目錄、main、原 PR、母檔與其他地圖不修改、不合併、不部署。

| 來源 | 已核對版本與狀態 | 本工作室採用 |
|---|---|---|
| PR #50 多樣化工作室 | Draft/open；`abb756d8cd9f92c5d559c048747ce15a0ebba35e`；D03/D06 0.1.0-gray.3，無衣鞋、無動畫；美術未核准 | 唯讀查核 ADOPTION/reference_lock；逐檔採用不依賴 Blender 的 GLB inspector（完整保留於 scripts/vendor），沒有把灰模當完整人物 |
| PR #137 Harbor | Draft/open；`8e877a07f19571436c2658a885db77206014a74c`；65 骨、7 原有片段、完整衣鞋、Blender 4.3.2 母檔；Godot 曾實跑 | 逐檔取用角色 BLEND/GLB、原生貼圖、CC0 notices 與原匯出/檢查腳本。保留 sources/harbor-v02；不整條合併 Godot/Unreal/遊戲網站。新介面獨立製作 |
| PR #39 NVIDIA | Draft/open；`424e7eda60d20f71990209a90c7c7a6c7a220724` | 查核文件及實驗界線。主要為合成 Nova77 測試，沒有真人 NVIDIA 推論、接地 IK、服裝碰撞及遊戲驗收；本版不採用其合成動畫，不宣稱自行訓練 |
| PR #48 V29 八人 | Draft/open；文件 `0cef2282394b911e61cb3cde169f31be0034af95`；實際建模 `1b1f3695abde627362f6cdd78031e442fbee9ea4` | 選 oldman 第二身形，保留原 BLEND/GLB/短姿態 GLB；其他七人不變。V29 八人是 you26/jie26/boss25/uncle24/bro27/cop28/oldman29/shui29 的混合版本，非八人一起重建完成 |
| PR #49 V30 | Draft/open；文件 `11cae1df15367cb5a41bdb6b3dc50d61fcc8e146`；建模 `293b92376c55b5e330e2aac7497055895f035921` | 最新是單肩毛巾；先前繞頸成功 CI 候選仍曾視覺拒收。只作來源參考，不取代已保留的 V29 與 V31，不把雕塑垂墜當物理布料 |
| PR #51 V31 | Draft/open；最新文件/診斷 HEAD `eafdaadae855b866c8c8f4f88c6526e2b484a11c`；實際返工 `8ebd82f908332e7519a9467b5f5d995445618704` | PR body 落後於實際 Actions：建模 run 41202687871 success；artifact 13043328209 51,110,007 bytes 已下載，CRC 與59檔 SHA核對通過。新衣襬下段有**刻意重建拓樸**，毛巾為180幀 Cloth 後靜態造型，非遊戲即時布料。另有最新診斷 run 41203672252 success。保存實際 report/provenance，尚未人工美術核准，**沒有列成工作室成品或替換 shui** |
| 基隆河 V110 | PR50 reference_lock/ADOPTION 記錄三份已交接包與來源 | 這次環境的 library-files、shared/downloads 沒有三包，未取到可再次核對的二進位。本版僅查核交接索引；已知胸口問題不能作合格基準 |
| 基隆河 V111 | 未取得可核對分支/commit/母檔/GLB/互動包 | PR/branch 搜尋 V111、keelung 及可取得檔案未找到；列缺口，不推論不存在，不退回 V103 |
| 彩虹橋走路/手肘/衣袖修正 | 未取得精確來源 | PR 搜尋彩虹橋、branch 搜尋 rainbow 未取得可核對產物；列缺口，不假稱已採用 |

## 本次重新取回與核對的資產

- oldman V29 artifact `13039030982` / run `41191249693`，ZIP SHA-256 `ccb9a2c819bca8cbd8c872965ae53b8e561ac6f19b3ded4053be28e13687c73b`，與 GitHub API digest 相同；ZIP CRC、原55項檔案 SHA 通過。本版只保留選定角色與相關來源，不混入拒收的其他角色候選。
- oldman V27 原始 source report 從 artifact `13035898672` 取回，含19筆 MHCLO/MHMAT 原始來源標頭。MRT T-shirt / wool pants 明列 CC0；MakeHuman 人體、眼睛、眉睫、牙舌、鞋與短髮的原 CC0 作者標頭保留。
- V31 artifact ZIP SHA-256 `c28032f1d9472fbc83e56003a37bdc2d95852beade9e336e025b678aac524092`，與 GitHub API digest 相同。report 原始資料保存在 evidence/upstream；大型候選仍可由固定 artifact 找回，未混入新角色匯出。
- GitHub CLI 對 Actions Azure redirect 的下載曾回403；改用已連接 GitHub 工具的 artifact 下載能力成功取回，再以同一代理正常下載檔案；未變更網路政策或憑證。

## 原始解析度與品質

Harbor 母檔中的7張實際來源影像為256×256（含原創織紋/眼圖）；oldman V29 保留13張512×512原始 packed 影像。本版逐位元組抽出，不再壓縮解析度，不假稱已取回歷代高解析度原圖。Harbor 原 source-lock 保留 CC0 pack 的 SHA，整個128MB人體包與15MB動畫包沒有一併取回；本版可直接由保留的可編輯母檔重建。若要回到 MPFB macro/MHCLO 或上游全解析度素材重新建人，仍須取回原始官方素材包與固定 MPFB 工具版本，不能把這個母檔流程說成全套原生建人環境已安裝。

選擇 Harbor 是因為來源、可編輯檔、衣鞋與動作完整，**不是它已通過高品質美術驗收**。目前可取得的這些人物都仍是候選。
