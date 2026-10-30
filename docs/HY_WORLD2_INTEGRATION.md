# HY-World 2.0 ↔ 3DCodeVerse Lab：非破壞性匯入原型

> 狀態：已建立**檔案格式橋接 + 靜態預覽**原型；不是已完成 HY-World GPU 推論、不是模型品質驗收。
> 本功能與既有 Blender 5、機甲動畫 GLB 工作流程**分開**，不會修改正式模型。

## 為什麼要拆成兩條路？

| 上游輸出 | 真正的資料形式 | 我們的接法 | 注意 |
|---|---|---|---|
| `hyworld2/worldgen` 的 `render_results/global_mesh.ply` | 含面的三角網格 | Three.js PLY，或另外用 Blender 轉 GLB | 可能是全景初始幾何，不等於最終完整世界 |
| `hyworld2/worldrecon` 的 `gaussians.ply` | 3D Gaussian Splatting | Spark + Three.js | 不是可直接碰撞的三角網格 |
| `hyworld2/worldgen` 的 `ply/point_cloud_*.ply` 或 `.spz` | 3D Gaussian Splatting | Spark + Three.js | 大場景顯示需實測手機效能 |
| `hyworld2/worldrecon` 的 `points.ply` | 3D 點雲 | THREE.Points 預覽 | 無網格面、無物理碰撞 |
| 我們原有 `.glb` | glTF 2.0 | GLTFLoader | 可與現有 Blender 資產共存 |

**不能把 splat PLY 當作 mesh PLY 直接匯入 GLB。** 網格、3DGS、點雲需要不同載入器。
本工具讀取 PLY 標頭辨識資料型別；不執行模型推論，也不保證場景實際品質。

## 零 GPU 快速自測（無需真實 HY-World 權重）

本庫提供 **手工撰寫的八頂點測試方塊**，用來先驗證 PLY 格式辨識及 Three.js 載入路線。這個方塊不是 HY-World 的生成成果，也不代表其美術品質。

從本庫根目錄啟動 `python3 -m http.server 8000`，用瀏覽器開啟 `http://localhost:8000/examples/threejs/hyworld-viewer.html`，按預填測試方塊網址的「載入」，應可旋轉觀看方塊。若畫面空白，先查看瀏覽器 Console，並確認 WebGL2、模組 CDN 和本機靜態伺服器可用。

## 第一階段：先用現有 HY-World 輸出完成介面接線

把官方產生的檔案複製到安全工作資料夾（不要將權重或未經授權的資料提交 GitHub）：

```bash
python3 scripts/hyworld2/pack_world.py \
  --input /path/to/HY-World-2.0/output/gaussians.ply \
  --out examples/threejs/worlds/first-test \
  --asset-id first-test \
  --up-axis unknown
```

其他例子：

```bash
# 只要官方 WorldNav 階段已輸出 global_mesh.ply，即可先測三角網格的路線
python3 scripts/hyworld2/pack_world.py \
  --input /path/to/scene/render_results/global_mesh.ply \
  --out examples/threejs/worlds/initial-mesh \
  --asset-id initial-mesh
```

工具產生 `world_manifest.json` 與原始模型的**副本**；不會修改原始檔。將兩個檔案放在同一個公開可讀的靜態目錄。程式不會自動轉網格，因為那可能偽造碰撞面。

- `--up-axis` 可選 `Y`、`Z`、`unknown`；未知時**不自動旋轉**。
- `--meters-per-unit` 可指定來源座標單位對應幾公尺；缺乏比例測量時不要假設正確。
- 需要新的輸出資料夾，避免覆寫之前的場景。
- `collision_ready` 永遠標為 `false`，碰撞網格需另行驗證。

## 第二階段：瀏覽器預覽

採用 Spark 2.4 + Three.js（由官方 Spark 文件提供的 import map 範例）：

```bash
# 從本 repo 根目錄
python3 -m http.server 8000
```

開啟：

```
http://localhost:8000/examples/threejs/hyworld-viewer.html
```

在輸入框填入：

```
/examples/threejs/worlds/first-test/world_manifest.json
```

然後按「載入」。旋轉與縮放使用 OrbitControls。**這個檢視器不是第一人稱遊戲，亦沒有障礙物碰撞。**

在自己的 Three.js 程式中可使用：

```js
import { SparkRenderer } from "@sparkjsdev/spark";
import { loadHYWorld } from "./load-hy-world.js";

scene.add(new SparkRenderer({ renderer }));
const world = await loadHYWorld("/worlds/scene/world_manifest.json", scene);
// world.object：已加到 scene 的 3D 物件
// world.collisionReady === false
// 切換場景前 world.dispose()
```

安裝相容依賴：`npm install three @sparkjsdev/spark`。
需要跨域載入時，請確認有正確 CORS。**不要直接用 file:// 開啟 HTML。**
對於大型 splat，應先在桌面瀏覽器測試，再評估壓縮 SPZ、手機品質、LOD 與 VRAM。

## 第三階段：真正接上我們的 Blender／GLB 工作流

1. **如果是三角網格**：檢查 PLY 是否包含 face，再用 Blender 的 PLY 匯入功能（Blender 5 的 `bpy.ops.wm.ply_import`），手動檢查方向、比例、法線和拓樸；加入或重新建置碰撞網格後再匯出 GLB。
2. **如果是 Gaussian splats**：保留 .ply/.spz 進入 Spark（視覺層），另以重建輸出的深度／網格或人工建模建立碰撞層。不可用 splat 點位當作準確的物理表面。
3. **如果是實景地圖**：真實橋梁、建築及道路的座標需用測量或可信 GIS 資料校對；生成畫面不得視為真實地圖。

既有 `scripts/blender5/validate_glb.py` 只驗證 GLB，**不適用直接驗證 Gaussian PLY**。日後如從有面的 PLY 轉成 GLB，才使用該驗證器與視覺驗收。


## Blender 5.2 轉為 GLB（只支援真正有面的 PLY）

確認來源 PLY 含 face，並先量測來源軸向與比例，再在**已安裝 Blender 5.2 的電腦**執行：

```bash
blender -b --factory-startup --python scripts/blender5/hyworld_mesh_to_glb.py -- \\
  --input /path/to/scene/render_results/global_mesh.ply \\
  --out outputs/hyworld-test \\
  --asset-id hyworld-test --up-axis Z --meters-per-unit 1.0

python3 scripts/blender5/validate_glb.py outputs/hyworld-test
```

`--up-axis Z`、`--meters-per-unit 1.0` **只是命令格式範例，並非表示 HY-World 的輸出必定是 Z 軸朝上且單位為公尺**。未確認前不要當作實景場景使用。輸出的 GLB 經結構驗證後，仍須進行材質、尺度、碰撞和視覺檢核。這個腳本不接收 3DGS 或只有點的 PLY。

## 尚未完成的事情

- 未下載 HY-World 模型權重、未使用 CUDA GPU 跑 WorldMirror 或 WorldStereo。
- 未用實際 HY-World 匯出檔完成瀏覽器渲染驗收。
- 未校正相機 OpenCV → Three.js 的完整座標矩陣、比例與參考原點。
- 尚未建立 NavMesh、物理碰撞、第一人稱走路；Blender PLY → GLB 腳本已撰寫但尚未用真實輸出運行驗收。
- 本輪 CI 只進行 Python 單元測試與 JavaScript 語法檢查；**不是畫質測試**。

## 授權與資料治理

HY-World 2.0 採 Tencent HY-World 2.0 Community License，不是 MIT/Apache 授權，部分地區與用途受限（如 EU、UK、South Korea；使用輸出及訓練其他 AI 模型亦有限制）。每個輸入素材、生成結果及第三方程式都需個別確認權利。原始碼和模型權重不得直接複製到本庫。

官方文件：

- https://github.com/Tencent-Hunyuan/HY-World-2.0
- https://github.com/Tencent-Hunyuan/HY-World-2.0/blob/main/DOCUMENTATION.md
- https://github.com/Tencent-Hunyuan/HY-World-2.0/blob/main/hyworld2/worldgen/README.md
- https://github.com/Tencent-Hunyuan/HY-World-2.0/blob/main/License.txt
- https://sparkjs.dev/docs/loading-splats/
- https://github.com/sparkjsdev/spark （MIT）

## 驗收命令

```bash
python3 -m unittest discover -s tests -p 'test_hyworld2_bridge.py' -v
python3 -m py_compile scripts/hyworld2/pack_world.py scripts/blender5/hyworld_mesh_to_glb.py
node --input-type=module --check < examples/threejs/load-hy-world.js
```

以上測試在無 GPU 環境即可執行。下一階段需**真實上游輸出**與瀏覽器驗收。
