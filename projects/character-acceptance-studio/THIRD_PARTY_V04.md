# 模型庫 0.4.0：來源與授權

本階段只納入逐檔確認可修改與再散布的 CC0 素材。程式碼、第三方載入器與所有素材的授權分開記錄；「免費下載」、可觀看的 VRoid Hub 頁面與開源載入器本身均不等於該模型可再散布。沒有引用遊戲拆包、商業 VTuber 形象或未知權利模型。

| 類別 | 素材／作者 | 上游固定版本與授權依據 | 修改與可編輯來源 |
|---|---|---|---|
| 遊戲人物 | Knight、Barbarian、Mage、Rogue、Rogue_Hooded；Kay Lousberg | [原作者 GitHub](https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0/tree/672074b73ba276876a19e8816ecdc5241817ab47)，CC0；保留原 LICENSE.txt | 4 種人物＋1 兜帽外觀變體；GLB 位元組不變，每個 76 個原生片段。1024² 原貼圖。免費包不含原作者 .blend，本版提供 GLB 匯入的工作副本；沒有購買或取得 EXTRA／SOURCE 內容。 |
| 四足動物 | Cow、Bull、Alpaca、Deer、Stag、Donkey、ShibaInu、Husky、Fox、Wolf；Quaternius | [Ultimate Animated Animals](https://quaternius.com/packs/ultimateanimatedanimals.html) → [原作者 Drive](https://drive.google.com/drive/folders/1uJ3N5HfB7jKTseJUNQr3N4YaN0UuEtHk)，CC0；原 License.txt 與每檔 ID／修改時間已保存 | 原 .blend 與 .gltf 保留。只將 data URI glTF 無損封裝成 GLB；不改幾何、顏色、骨架、動作。原材質為色塊，沒有貼圖需要升降解析度。每隻 12 或 13 個原生片段。 |
| 動漫／VRM | Vita、Vivi、Victoria Rubin；pixiv Inc. 的 VRoid beta 範例設計 | [可下載 VRM 鏡像](https://github.com/madjin/vrm-samples/tree/e16eb187100149a315ad92c3c9968f1d5baa6c7d/vroid/beta)；三檔內嵌 meta 均 licenseName=CC0。原作者條款：[Vita／β3](https://vroid.pixiv.help/hc/en-us/articles/360014900113)、[Vivi／β2](https://vroid.pixiv.help/hc/en-us/articles/360014900273)、[Victoria／β4](https://vroid.pixiv.help/hc/en-us/articles/360014900233) | 取得管道為 madjin 的公開鏡像，不是假稱從官方取得母檔。檔內 author／version 欄空白，保留該缺口。原 VRM 容器完整不變；runtime model.glb 與原 .vrm 位元組一致，包含 VRM metadata、MToon、表情、SpringBone 資料。沒有 .vroid 母檔；Blender 為標準 glTF 匯入工作副本，不保證 VRM 語意往返。三者沒有動畫片段。 |
| 既有馬匹 | horse-brown、horse-white；Quaternius 原模型，aitest-ai 的材質／UV／PBR 衍生 | [專案既有 horses-v2.3.0 Release](https://github.com/aitest-ai/3dcodeverse-lab/releases/tag/horses-v2.3.0)；CC0，原 LICENSE_AND_SOURCE.md、registry、SHA256SUMS 保留且下載檔逐一核對 | 原 GLB、母檔及原解析度貼圖不變。每匹 13 片段。既有來源記錄的人工檢視不自動視作本模型庫重新驗收，物理步態未核准。 |

「532」是 **17 個資產內的片段項目總數**，包含同一 KayKit 動作集在不同人物的重複，並非 532 套獨立動作。20 個模型項目亦包括兜帽與兩種馬色，並非 20 種完全不同骨架或物種。

授權網頁擷取保存在 `sources-v04/license-evidence/`；來源檔的 SHA-256 在 `sources-v04/SOURCE_FILES.sha256`。每個 runtime 模型、母檔、貼圖與骨架設定的 SHA 分別保存在目錄、editor 報告、profile 與交付清單。

## 渲染程式

- Three.js r170（MIT），沿用 `web/vendor` 及其原授權檔。
- `@pixiv/three-vrm` 3.3.0（MIT）與同版子套件，原授權位於 `web-v04/vendor/THREE_VRM_LICENSE.txt`。以 esbuild 0.25.12 封裝，Three.js 作外部依賴；鎖檔在同目錄。VRM 外掛的 MIT 授權不替代模型的 CC0 證據。
- glTF 二進位檢查器沿用已盤點 PR #50 的 `scripts/vendor/inspect_glb.py`，原檔未更動。

## 未引用／後續擴充

Kenney 的 [Animated Characters](https://kenney.nl/assets/animated-characters-2) 系列已找到原作者頁面，尚未下載或完成逐檔檢查。Quaternius 的其他人物與農場包可沿用同樣接收流程。VRoid 新版 AvatarSample_A/B/C 的條件與舊版 CC0 不同，本次未引用。Blender Studio 等更精細人物需要另核對具體檔案、授權及取得方式；不將目錄連結算成已交付模型。
