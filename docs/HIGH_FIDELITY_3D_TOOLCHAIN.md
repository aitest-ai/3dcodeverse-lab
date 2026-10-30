# 高品質、多物種 3D 建模工具鏈｜研究與整合規範

> 研究與來源查核：2026-10-30。**資源已編目 ≠ 套件已安裝 ≠ AI 已推論 ≠ 美術品質已驗收。**
>
> 本庫現有 Blender 5.2.3 + GitHub Actions 產生 GLB 的流程保持不變。新增工具預設只登錄 metadata；執行第三方 AI 生成需另外安排 CUDA GPU、安全性和授權檢查。

## 1. 為什麼單一「一鍵生 3D」不足以達到高品質

高品質分成五種相互獨立的要求：

- **外形**：多視角輪廓、形體比例、物種特徵、器物結構正確
- **網格**：關節位置的邊線流向／拓樸／物件分件合理，不只三角面數高
- **材質**：PBR 貼圖的 Base Color、Normal、Roughness、Metallic（必要時 Alpha、AO）對得上真實材質
- **動作**：骨架完整、蒙皮自然、足部著地、可用的動畫片段／表情
- **交付**：對齊公尺、glTF 2.0 GLB、LOD／壓縮／行動裝置效能、授權可追溯

例如：一張 AI 從正面圖片生出很漂亮的熊，背面可能失真、四足骨架不足、嘴部和肩胛骨動起來破形。光看一張渲染圖不能稱為遊戲可用。

## 2. 推薦的組合，不必強制同一工具處理所有角色

| 內容 | 優先的基底／幾何 | 精修、材質 | 骨架／動畫 | 常見風險 |
| --- | --- | --- | --- | --- |
| 真人／寫實人物 | MPFB 參數人體；搭配實際人體比例參考 | Blender 雕塑、寫實皮膚／眼睛；Poly Haven 照明 | MPFB 自帶骨架、Rigify／CloudRig（需測版本） | 顏面、手指、肩／髖變形；不應只用單張 AI 輸出直接動畫 |
| 風格化人物 | MPFB 或原創雕塑；TRELLIS.2 圖像轉 3D 做造型參考 | Blender 分件、重新拓樸與材質 | Rigify、CloudRig；人工調整表情 | AI 模型可能不具動畫級 Quad 拓樸 |
| 四足動物 | 正確的動物照片／多角度參考；TRELLIS.2 候選 | 雕塑與重拓樸；毛流／皮膚紋理，正常光照 | UniRig 初綁骨→人工調整脊椎／膝／尾，再建立步態 | UniRig 通用但不能保證物種解剖正確 |
| 木雕熊／博物館物件 | 參考真實照片／掃描資料；依輪廓 Blender 重建 | 木紋刻痕／高模轉法線貼圖、PBR | 通常不需骨架 | 不要把寫實生物的毛流當成雕刻木紋 |
| 硬表面機甲 | Blender 可參數化機械分件＋多角度設計圖；TRELLIS.2 輔助初稿 | 倒角／法線貼圖／磨損及金屬 PBR | 明確的機械鉸鏈、IK、碰撞代理 | 生成模型常把關節、護甲融在一起 |
| 校園／博物館建築 | 真實公開照片、可授權的測繪／掃描／自建幾何 | Poly Haven HDRI、PBR、LOD | 通常無需骨架 | 地理位置與真實樣貌要人工查核 |

## 3. 已查核的開放工具（依功能）

**幾何與外觀**

- [TRELLIS.2](https://github.com/microsoft/TRELLIS.2)：MIT 模型與程式，Linux + NVIDIA CUDA 24GB VRAM 以上為官方測試條件。圖片→高細節物件＋PBR；**不是自動完美綁骨工具**，有些相依套件另有授權。
- [Hunyuan3D 2.1](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1)：能做高品質幾何與 PBR；官方數值 10GB（形體）、21GB（材質）、約 29GB（整套）。採 **Tencent 自訂 Community License**，不是 MIT／Apache；授權範圍排除歐盟、英國和南韓等地區，使用與分發前先仔細審查。禁止將權重當成 CC0。
- [MPFB](https://extensions.blender.org/add-ons/mpfb/)：Blender 的完整人體基底、比例、服裝與骨架工具。外掛 GPLv3+，核心資產依 MakeHuman 採 CC0；2026-10 官方版本 2.0.18 標示 Blender 4.2+。
- [Smithsonian Open Access 3D](https://www.si.edu/openaccess/faq)：自然史標本、文物與動物相關靜態掃描；**僅指定 CC0 的單一作品才能當作自由素材**。高面數掃描通常需重新拓樸與減面。
- [Blender Studio Rain](https://studio.blender.org/characters/rain/v3/)：免費 CC-BY 專業人物綁骨參考，需標示作者；若 .blend 要執行嵌入 Python，先審查腳本。

**骨架、拓樸與材質**

- [UniRig](https://github.com/VAST-AI-Research/UniRig)：通用骨架預測與蒙皮；程式 MIT，CUDA 至少 8GB；模型權重和資料集需要分別確認。動物尾巴、翅膀、四足膝方向要驗證。
- [Blender Studio CloudRig](https://extensions.blender.org/add-ons/cloudrig/)：GPLv3+ 控制骨架；2026-10 官方列 Blender 5.0，**本庫 5.2 相容性尚未實測**。
- [Instant Meshes](https://github.com/wjakob/instant-meshes)：BSD-3-Clause、人工導向的四邊形重新拓樸，對高模或掃描特別有用。
- [Material Maker](https://github.com/RodZill4/material-maker)：MIT 開源 PBR 節點材質製作及貼圖繪製。
- [Poly Haven](https://polyhaven.com/)：CC0 HDRI、PBR、掃描道具。官方 API 免費但有獨立使用條款與識別要求。其 Blender **Online Asset Library** 2026-10 版需求 Blender 5.3+，不應當成已在本庫 5.2 安裝。
- [ambientCG](https://ambientcg.com/)：提供 CC0 為主的材質；實際素材仍需核對發佈頁資訊。
- [glTF-Transform](https://github.com/donmccurdy/glTF-Transform)／[Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator)：前者用 Node.js 做網頁模型／貼圖壓縮，後者用於規格級檢查。不等於美術驗收。

> 注意：某些網站把「原始碼開源」與「模型權重／生成內容可商用」混為一談。本專案**分別記錄程式授權、權重授權、素材授權與服務條款**。

## 4. 本次真正新增的可重複使用工具

| 檔案 | 已實作能力 | 限制 |
| --- | --- | --- |
| `resources/open_3d_tool_catalog.json` | 14 個資源、用途、硬體／授權、部署條件等機器可讀資訊 | 屬研究索引，不是套件安裝清單 |
| `scripts/assets/tool_catalog.py` | 可依類別、製作階段、GPU 條件篩選 | 不擅自下載外部程式 |
| `scripts/assets/polyhaven_search.py` | 透過官方 Poly Haven API 查找 CC0 物件／HDRI／材質的**中繼資料** | 不自動下載；請遵守 API ToS |
| `scripts/assets/glb_quality_report.py` | 統計三角面、UV、PBR、蒙皮、動畫、貼圖與效能警告 | 數字不是解剖學正確或美術品質證明 |
| `.github/workflows/open-3d-resources.yml` | 自動確認索引欄位、基本安全性與單元測試 | 不會替代 CUDA GPU 模型推論 |

### 範例指令（本機或 GitHub Actions）

```bash
# 找動物可用的骨架工具
python3 scripts/assets/tool_catalog.py --category animal --stage rigging

# 找不需 GPU 的人物基底
python3 scripts/assets/tool_catalog.py --category human --gpu cpu

# 真的查詢官方 Poly Haven API，只有名稱／來源／授權中繼資料
python3 scripts/assets/polyhaven_search.py stone --kind models --limit 5

# 完成 GLB 後，產生結構與網頁效能的品質報告
python3 scripts/assets/glb_quality_report.py outputs/mecha_blender5.glb \
  --kind mecha --target desktop --output outputs/quality_report.json
```

## 5. 可以做到高品質的完整產線（後續實作方向）

```text
需求＋真實多視角參考
  ├─ 人類 → MPFB／手工雕塑
  ├─ 動物 → 可信多視角／掃描／TRELLIS.2（另需 GPU）
  ├─ 機甲 → Blender 程序化精確分件／TRELLIS.2 草稿
  └─ 場景 → 授權可用的掃描／開放素材
       ↓
人工輪廓審查 → 高模精修 → 重拓樸（Instant Meshes／Blender）
       ↓
UV＋PBR（Poly Haven／Material Maker；來源授權記錄）
       ↓
綁骨（MPFB／CloudRig／UniRig 的 GPU 服務）／動畫
       ↓
Blender 5.2 CPU：GLB 匯出／三視角照片／數值驗收
       ↓
Khronos glTF Validator → glTF-Transform 優化與再驗證
       ↓
Three.js／Unity／Godot 等目標系統匯入實測
```

### 實際系統分工

- **GitHub Actions CPU**：程式建模、材質設定、GLB 匯出、圖片驗收、掃描網格品質、產出報告。
- **獨立 GPU 執行器**：TRELLIS.2／UniRig／Hunyuan3D 的推論；生成權重很大，避免加入 git，也不應假定 GitHub 的標準 runner 有 CUDA GPU。
- **人工驗收**：對照參考圖／真實解剖／機械運動／多視角畫面。高品質無法只用三角面數或一個 AI 分數判斷。
- **資產合約**：使用現有 `docs/AI_ASSET_PIPELINE.md` 的 `.blend`、`.glb`、`asset_manifest.json`、`validation.json`。另外存放創作者、來源網址及許可授權。

## 6. 下一步怎麼驗收真正的「高品質」

建議建立三個不同測試標的，而不是只測同一隻機甲：

1. **人類**：MPFB 生成人體＋手指、肩膀、臉部輪廓與表情（特寫驗收）。
2. **動物**：熊或犬的多角度模型＋四足關節、尾巴與跑步動作（側面及背面驗收）。
3. **機甲**：金屬／鉸鏈／倒角／PBR 磨損／分件輪廓，高模與遊戲低模分開交付。

每個測試物至少存正面、側面、背面、45 度四視圖，近拍關鍵部位，驗收文件記錄「觀察結果、錯誤、是否真的修復」，並針對手機 WebGL 檔案大小另測。這些測試尚未在本 PR 中執行，不可把資源索引建立視為高品質模型已完成。
