# AI × Blender 5 × GitHub → 可匯入遊戲的 3D 素材

這是一套 **跨 AI 模型共用的製作規範**。Copilot、ChatGPT、Claude、Codex 或其他可寫程式與使用 GitHub 的 AI 都能依照此規範工作。AI 必須真的擁有 GitHub／程式執行工具權限才可提交或執行；光貼上網址不代表有權限。

## 現有入口

- 儲存庫：https://github.com/aitest-ai/3dcodeverse-lab
- 人形機甲範例：`scripts/blender5/mecha_smoke.py`
- Blender 5.2.3 雲端流程：`.github/workflows/blender5-cloud.yml`
- 不依賴 Blender 的 GLB 驗證器：`scripts/blender5/validate_glb.py`
- Three.js 載入範例：`examples/threejs/load-animated-glb.js`

目前使用 Blender 5.2.3 LTS 的官方 Linux 版本，檔案 SHA-256 由官方清單核對。每次 GitHub Actions 開始才在臨時機器安裝 Blender，不是永久運行的桌面服務。

## 交付標準：請讓任何 AI 一律遵守

在 `scripts/blender5/` 放入新生成腳本，例：`river_robot.py`。腳本可直接 `bpy` 建模，也可以讀取經授權的外部素材。完成後在 `outputs/` 產生：

| 檔案 | 用途 | 必要 |
| --- | --- | --- |
| `<asset_id>.blend` | Blender 5 可編輯原始場景 | 是 |
| `<asset_id>.glb` | 網頁與遊戲引擎的正式交付品 | 是 |
| `asset_manifest.json` | 模型名稱、尺度、方向、動畫清單 | 是 |
| `report.json` | 建模／檢驗資訊、待驗證項目 | 是 |
| `validation.json` | 外部檢查器通過後產生 | 是 |
| `preview.png`、`preview.mp4` | 前／側／後視角及動作 | 建議 |

`asset_manifest.json` 的最低格式：

```json
{
  "schema_version": 1,
  "asset_id": "river_robot",
  "format": "glTF 2.0 GLB",
  "source": "original procedural Blender script",
  "unit": "meter",
  "coordinate_system": "Blender Z-up; glTF export converts to Y-up",
  "model_file": "river_robot.glb",
  "source_file": "river_robot.blend",
  "clips": ["Idle", "Run"],
  "min_animation_count": 2,
  "requirements": {
    "skins": true,
    "animated": true,
    "visual_review": true
  },
  "license_note": "Original geometry; list any external assets and licenses here."
}
```

- `asset_id` 與檔名只能使用安全英文數字、底線及連字號。模型需米制尺寸，進口系統再按場景縮放。
- 動畫每段使用可辨識名稱。範例機甲支援 `Idle`、`Run`、`Punch`、`Dodge`。
- 有骨架角色應提供 `skins`、`animations`；場景或靜態資產可將 `skins` 設為 `false`、`min_animation_count` 設為 0，`clips` 設為空陣列。
- GLB **自帶幾何、材質、骨架與動畫**，遊戲引擎載入不應還需要執行 Blender Python。
- 若素材來自網路，必須在說明及授權檔記錄來源、授權、作者、修改。不要把未知授權或付費素材推進公開儲存庫。

## AI 工作順序

1. 先確認使用者的目標平臺是 Three.js、Unity、Godot 或 Unreal，並釐清所需動作、面數、貼圖大小。
2. 閱讀本庫 `AGENTS.md`、本文件及既有範例，禁止臆測已有什麼工具或權限。
3. 建立新分支，不動既有的 `main` 成品，增加 `scripts/blender5/<asset_id>.py`。
4. 先用 Python 語法檢查；有 Blender 環境才執行建模。
5. 到 GitHub → Actions → **Blender 5.2 Cloud Mecha Test** → Run workflow。將 `scene_script` 設為新檔案路徑。**必須先讓該分支包含新檔案，並在 Actions 的分支選單指定該分支**。
6. 成功後檢查 `outputs/validation.json`，以及 `report.json`；到該次執行的 **Artifacts** 下載模型包（保留 14 天）。
7. 使用 Three.js 的 GLTFLoader 或目標遊戲引擎匯入 GLB，依動畫名稱播放，逐段檢查是否穿模、腳滑、關節過度扭曲、材質錯誤或掉幀。
8. 使用 Pull Request 告知修改、檢查紀錄、已知限制與畫面證據。沒有跑完前，不可宣稱「驗證完成」。

## 重要的真實性界線

- GitHub 提供版本管理及臨時運算；它不會替模型自動擁有軟體 GUI、GPU、Animatica 免費額度或第三方帳號權限。
- Choreographer 的 AI 生成若需登入／網路授權，與這個純 `bpy` 工作流程不同；不可直接聲稱 Choreographer 已參與動畫生成。
- `validate_glb.py` 確認容器、模型、動畫與骨架結構，不等於動作物理合理或美術高品質；必須檢視預覽並做遊戲內實測。
- 機甲 V3 目前使用「關鍵影格腳底高度修正」而不是完整 IK，仍要檢查中間影格的滑步。
- 不允許將機密、私有憑證或原本系統的內部資料傳給不具存取權的其他 AI。

## Web/Three.js 接入示例

先把從 Actions 下載的 `<asset_id>.glb` 複製到系統的 `public/models/`，再在已安裝 `three` 的 Vite/React/純 JavaScript ES Module 專案中：

```js
import { loadAnimatedGLB } from './load-animated-glb.js';

const bot = await loadAnimatedGLB('/models/river_robot.glb', scene);
bot.play('Idle');    // 名稱可用實際 GLB 的動畫名稱
function animate() {
  requestAnimationFrame(animate);
  bot.update(clock.getDelta());
  renderer.render(scene, camera);
}
animate();
```

`loadAnimatedGLB` 實作見 `examples/threejs/load-animated-glb.js`。它不取代原本系統的碰撞、遊戲邏輯或玩家控制。

## 可直接貼給其他 AI 的任務格式

> 請讀取 https://github.com/aitest-ai/3dcodeverse-lab 的 AGENTS.md 與 docs/AI_ASSET_PIPELINE.md，依 Blender 5.2.3 工作流程創作【角色／物件描述】，預期整合到【系統網址／repo】，需要【動作清單】；新建 scripts/blender5/<asset_id>.py，輸出可匯入的 .glb、.blend、asset_manifest.json、report.json，透過 GitHub Actions 驗證後提交 PR。必須保留現有程式，不得宣稱未執行的測試已成功。如果沒有 GitHub 權限，請先說明並提出 PR/Fork 或交付檔案的方法。



## 機甲 V4：逐影格動作品質報告與三視角預覽（待雲端實測）

本版新增了獨立的 `scripts/blender5/render_and_qa.py`，針對 `MechaRig`：

- 每段動畫檢查全部 48 格（4 段 × 48 格 × 左右腳 = 384 筆腳部量測）。
- 計算腳底最低位置 `sole_z_m`、膝蓋彎曲角度 `knee_flex_deg`、腳掌接觸地面時逐格位移 `stance_drift_m`。
- 產生 `outputs/motion_qa.json`，列出各動作的最小腳底高度、最大膝彎角度、最大逐格腳滑距離及警告。
- 每段動作輸出正面、側面、等角三個角度，合計 12 張 `outputs/previews/*.png`，並合成一張 `outputs/preview_contact_sheet.png`。

機甲程式的腳底高度修正已由原本 **每段 5 個指定影格** 改為 **每段 48 格全覆蓋**；但這只是姿態對地面高度的逐格補償，**不等於完整的雙腿 IK、重心動力學或零腳滑保證**。報告會把仍然滑動的距離直接量出來，供後續迭代。

預覽與品質報告是第二段 Blender 背景工作流程，在獨立開啟已產生的 `.blend` 後執行，不會把驗收地板或攝影機加入原本輸出的 GLB。自訂角色若不是 `MechaRig`，仍可先使用通用的 `validate_glb.py`；只有機甲範例會自動執行這份專用的逐格檢查。

### 如何使用成果

1. 點選該次成功的 GitHub Actions 執行。
2. 在 Artifacts 下載 `blender5-mecha-<run_number>`。
3. 先看 `preview_contact_sheet.png` 和 `motion_qa.json`，再使用 `.glb`。
4. 只有 GitHub Actions 顯示成功，且實際預覽合格，才能說 **Blender 成品完成驗收**。提交程式碼本身不是完成渲染。

