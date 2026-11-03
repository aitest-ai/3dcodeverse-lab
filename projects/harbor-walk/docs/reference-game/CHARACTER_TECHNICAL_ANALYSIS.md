# 原作角色、骨架與材質研究

## 證據分級

**已由檔案驗證**表示可讀索引、檔案標頭或實際工具輸出所支持的範圍。**由畫面或名稱推測**不是解碼出的幾何或演算法。**尚待確認**不得改寫為已完成。原作 cooked 模型的壓縮 chunk 未成功解碼，因此此版沒有原作 mesh 拓樸、面數、骨數、權重或骨架尺寸報告。

## 角色組織

以下路徑可在 `evidence/retoc-paths.txt` 與原 `Manifest_UFSFiles_Win64.txt` 找到；內容仍在容器內：

| 可讀路徑（省略 `../../../GirlFishing/Content/`） | 證據與限制 |
|---|---|
| `xSeries/xModel/Ryotsu/SM_RyotsuFinal.uasset`、`SM_RyotsuFinal_Skeleton.uasset`、`SM_RyotsuFinal_PhysicsAsset.uasset` | 已驗證這些名稱與 chunk 存在；不能由此得出骨數、碰撞 primitive 或權重 |
| `xSeries/xModel/Reiko/SM_ReikoFinal.uasset`、`SM_ReikoFinal_PhysicsAsset.uasset` | 已驗證角色相關資產組織；未輸出或複用模型 |
| `xSeries/xModel/OL_Base/SM_OLFinal_Skeleton.uasset`、`OL_Base_Fat/SM_FatFinal_Skeleton.uasset` | 名稱顯示多體型骨架變體；是否同源、相容或重定向品質尚待確認 |
| `xSeries/xModel/Ai/SM_AiFinal_Skeleton.uasset`、`Oohara/SM_OoharaFinal_Skeleton.uasset` | 可證存在對應 skeletal 資產名稱，非取得骨架規格 |
| `xSeries/xModel/OL_Head1/h3.uasset`、`h6.uasset`、`h8.uasset`、`anime_character_heads_3d_model_basecolor.uasset` | 頭部子資產與貼圖名稱存在；模組化換頭是合理推測，並未解析連接方式 |

`tripo_mat_*` 名稱出現在部分材質／貼圖路徑，**名稱本身不能證明使用何種 AI 建模流程、來源授權或原作者**。

## 畫面觀察

使用者影片為 1920×1080、30 fps、126.084 秒（AV1 video / AAC audio）。本次依 0、15、30、45、60、75、90、105 秒接觸表觀察：

- 0 秒：第三人稱背後攝影機、室內走廊、前方居民與目標指示。主角比例偏誇張、制服輪廓清晰。
- 約 15 秒與 60 秒：近距離人物與目的地圖片選單；NPC 有不同髮型、身形及服裝。鼻子、髮絲輪廓及鞋履具有體積，但從影像不能量測拓樸或衣物厚度。
- 約 45 秒：可觀察 NPC 轉向與互動目標；約 75 秒出現較大姿態動作與畫面特效。
- 約 105 秒：命中特效／分數變化可見。顏色與材質風格化，陰影相對柔和；不能據此斷定使用特定 toon shader、描邊技術或後製管線。

沒有進行逐格足底追蹤、角色尺度重建或相機標定，因此不對腳滑量、關節角度或穿模率報數。影片不能替代原始 mesh 檢查。

## 骨架與動畫

已驗證的容器路徑包括：

- `RetargetAnim/RyotsuAnim/ABP_Unarmed_Ryotsu.uasset`
- `RetargetAnim/OoharaAnim/BS_Idle_Walk_Run.uasset`
- `RetargetAnim/OLFatAnim/MF_Unarmed_Walk_Bwd_Left.uasset`
- `RetargetAnim/OLAnim/MF_Unarmed_Jog_Left.uasset`
- `RetargetAnim/OLFatAnim/MM_Land.uasset`

這些名稱符合動畫藍圖、Idle/Walk/Run blend space、方向 locomotion 與落地動畫的常見 Unreal 組織。**尚未解碼**狀態轉移條件、blend 軸、root motion、Foot IK、表情、動畫重定向 solver、蒙皮權重與手持道具 socket。隨包附帶 Engine ControlRig/DeformerGraph 內容，也不能證明某個角色正在使用它們。

## 材質與渲染

Ryotsu 資料夾存在 `Ryotsu_basecolor`、`Ryotsu_normal`、`Ryotsu_roughness`、`Ryotsu_metallic` 的 `.uasset/.ubulk` 路徑，及 `MatInst_Ryotsu`。這支持 PBR 貼圖類別的組織，但未驗證每張圖的實際尺寸、通道內容或材質參數。

ShaderCodeLibrary 包含 `ShaderArchive-GirlFishing-PCD3D_SM5-PCD3D_SM5.ushaderbytecode` 與 SM6 等路徑。REA PE 匯入表確認 PE32+／AMD64 及 DXGI 等依賴；隨附 D3D12 runtime。這些證據不代表本次觀察到的遊戲必定以 DX12 執行，因為原 EXE 未被啟動。

## 我們的獨立實作

新角色「海風信使」使用合法 CC0 anatomy / hair / clothes / locomotion，另製原創郵包、肩帶、領巾、口袋、配色、Turn clip 與微笑 morph。沒有移植原作角色或動作。其 `.blend` 是 Blender 4.3.2 實際製作之母檔；不是聲稱取得原作 source 或免費 pack 的付費 `.blend`。

已測 GLB：65 根骨、17,925 weighted vertices、1 skin、七段具非靜態 channel 的動畫、1 morph target。檢驗細節在 `evidence/asset-deep-validation.json`。正面／側面／背面／臉部圖片在 `evidence/character/`。這仍是美術候選：肩部裸露接縫、領巾與肩帶的剛性外觀、衣袖與手臂的色彩一致性、走跑 foot slip 與全動畫穿模仍需改進／量測，沒有商用品質通過宣告。
