# NVIDIA Body Pose → MPFB 53 骨 → Blender／GLB：第一輪驗證

## 完成範圍

這是**動作轉接技術驗證**，不是角色美術新版，也不是完成真人動作捕捉。

已在 GitHub Actions／Blender 5.2.3 LTS 真正執行：以原創 Nova-77 格式測試資料驅動現有 boss、jie，產出 .blend、動畫 .glb、實際渲染 PNG、檢查報告，並在新的 Blender 程序重新匯入檢查。

尚未執行：NVIDIA 雲端 API／真人影片辨識、Three.js／Unity 播放、腳底鎖定、衣服碰撞、完整手指與軸向扭轉。`live_nvidia_inference=false`、`art_approved=false` 不得改稱通過。

分支 `feat/nvidia-body-pose-retarget-poc` 從 main `f088f0e584764b3fd37dc1bc0670df99313bec41` 建立；不覆寫原檔，不合併其他角色、馬匹或機甲分支。

## 官方介面

NIM 1.0.0 使用 **gRPC + 77 關節 Nova**，不是 OpenAI 聊天 API，也不能沿用舊版 34 點索引。NIM 本身不做人物偵測與追蹤；除了影片，必須提供每一格人物框和穩定 tracking ID。輸出是 JSON Lines，官方客戶端要求副檔名 `.json`。

固定客戶端 `NVIDIA-Maxine/nim-clients@d02b7d57541b8598ac4c057947b10b2e42ccb1ee`。
官方來源（2026-10-31 查核）：
- https://build.nvidia.com/nvidia/body-pose/api
- https://docs.nvidia.com/nim/maxine/body-pose/1.0.0/basic-inference.html
- https://github.com/NVIDIA-Maxine/nim-clients/tree/d02b7d57541b8598ac4c057947b10b2e42ccb1ee/body-pose
- https://build.nvidia.com/nvidia/body-pose/modelcard

Build function ID `254b3621-bb66-4b7b-9c89-621c352b4d91`；端點 `grpc.nvcf.nvidia.com:443`。已核對文件，**未用金鑰呼叫**。官方改版後先審查結構，不能靜默切換。

## 現有角色骨架

實際下載 V17 四角 GLB：boss／jie／uncle／you 都是 1 skin、53 骨、0 段既有動畫。身體各有 10 個臉部 morph targets，衣髮、眉毛、睫毛、牙齒等另有變形。不能把「有表情變形」寫成「52 個 ARKit 全套已驗證」。

來源 run `41138623403`；artifact `13018220793`，名稱 `taiwan-v17-four-real-MPFB-knitted-layer-PILOT`。
來源 ZIP SHA-256：`6e4471392173f308bf7a8db10469cf507c7788747dff873a91fe13c80972997c`。
預定 2026-11-13 到期；CI 目前仍依賴該 artifact。到期後應換成授權與 SHA 明確的固定測試資產，不能悄悄下載別版。本次未發布新的永久角色 Release。

V18 曾對同一 game53 骨架做抬手、彎腰、跨步。本輪 V17 GLB 只是隔離測試夾具，**不取代最新角色分支**；正式製作優先使用 .blend 原始檔。

| 目標骨頭 | Nova 關節段 |
|---|---|
| pelvis | 0→1 |
| spine_01／02／03 | 1→2／2→3／3→4 |
| neck_01／head | 4→6／6→7 |
| clavicle_l／r | 11→12／39→40 |
| upperarm_l／r | 12→13／40→41 |
| lowerarm_l／r | 13→14／41→42 |
| thigh_l／r | 67→68／72→73 |
| calf_l／r | 68→69／73→74 |
| foot_l／r | 69→70／74→75 |
| ball_l／r | 70→71／75→76 |
| Root | 關節 0 相對參考影格的位移 |

共 **20 根旋轉骨 + Root 位移**；另 32 根（雙手掌與 30 根手指）不新增獨立動作，但仍隨父骨運動。臉部 shape keys 保留，不做表情辨識。這個 profile 僅接受 game53，機甲需要另一份 profile，馬與熊不能套人體對照。

## 轉接原則與限制

真人影片 + 人物框 → 官方 gRPC（尚待實接）→ Nova77 JSONL → 格式與品質檢查 → 參考姿勢校正 → FK 動作 → GLB → 結構檢查與 Blender 重匯入 → 影片／腳滑／穿模／引擎人工驗收。

相機 `[x,y,z]` 轉 Blender `[x,z,-y]`。原角色骨長、rest pose、頂點、權重與 shape-key 座標都有前後雜湊比對，來源檔 SHA 必須不變。

第一輪使用**關節位置推算方向**，以校正影格與目標 rest pose 對齊，再轉成角色局部旋轉。不直接複製 NVIDIA quaternion；軸向扭轉仍是近似，完整 local-quaternion／rest-frame 解算尚未完成。

校正影格應刻意拍攝與角色原姿勢對應的姿勢，不能隨意用跳舞第一格當零點。短暫低可信度可保持前格，超限即停止；骨盆失效、缺格、人物 ID 消失或重複、34 點、非有限數與錯誤 quaternion 皆停止，不補造長段動作。

Root 保留模式是相機相對位移，不能保證固定世界中的移動距離。未實作腳底鎖定或衣服碰撞。

## 已完成的測量

Smoke run `41146700110`，commit `7068e154c69bae1328fbbc9c805d3e91345379b7` 已通過 18 項資料測試與兩角 Blender／GLB 往返。新增影片預檢另有 7 項單元測試。

| 指標 | boss | jie |
|---|---:|---:|
| 影格／fps | 61／30 | 61／30 |
| 骨頭數 | 53 | 53 |
| 左手相對 Root 最大位移 | 0.327200 m | 0.397619 m |
| 右手相對 Root 最大位移 | 0 | 0.000000030 m |
| Root 位移 | 0（原地） | 0.190152 m（保留） |
| 重匯入最大關節誤差 | 0.0000005003 m | 0.0000003843 m |
| 比較樣本 | 305 | 305 |

極小誤差是**動畫匯出再讀回的保存誤差，不是 NVIDIA 捕捉精度**。原創合成資料只有抬左臂與人工側向位移，不是步行或腳底接觸測試。61 格、30fps 的時間跨度是 2 秒。

四角只確認骨架結構，真正動畫往返是 boss、jie。來源沒有既有動畫；已有多段動畫的保留路徑有防護但**尚未以多動畫夾具驗證**，往返檢查器遇到多 action 會要求明確指定。

## 程式與輸出

- `scripts/body_pose/pose_io.py`：嚴格 Nova77 與 GLB accessor 驗證。
- `capture_nvidia.py`：明確授權才呼叫，影片／人物框預檢、收據及金鑰遮蔽。
- `retarget_blender.py`：game53 動作轉接、合成測試、渲染與匯出。
- `verify_blender.py`：新 Blender 程序重匯入，逐格比對實際關節。
- `run_smoke.py`：兩角整合測試，另呼叫專案原本 `scripts/blender5/validate_glb.py`。
- `.github/workflows/nvidia-body-pose-poc.yml`：獨立 CI，無金鑰、不送真人影片。

每角輸出 `.blend`、`.glb`、`asset_manifest.json`、`report.json`、`validation.json`、`pose_validation.json`、`roundtrip.json`、三張渲染 PNG。validation 是專案原檢查器，pose_validation 是詳細檢查；較早 run2 尚無 pose_validation 的另存檔。

### 離線重現

repo 根目錄需有 Blender 5.2.3，`input` 放原始 V17 四角 GLB（可有子目錄）；Actions 已下載。

```bash
python3 -m unittest discover -s scripts/body_pose -p 'test_*.py' -v
python3 scripts/body_pose/run_smoke.py --input input --output outputs/body_pose
```

只測一角：

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python scripts/body_pose/retarget_blender.py -- \
  --asset input/boss_v17_ponytail01.glb \
  --output outputs/body_pose_manual --fixture --root-motion in-place --render
```

### 真人影片實接（尚未執行）

先用**同意上傳的成人**、單人固定鏡頭、手腳不出框的 5～10 秒短片。先維持對應角色的 A-pose，再單獨抬左手、放下、抬右手。避免多人、移動鏡頭、跳躍或打架。

準備 Python 3.10～3.12、FFmpeg／ffprobe：

```bash
git clone https://github.com/NVIDIA-Maxine/nim-clients.git .deps/nvidia-clients
git -C .deps/nvidia-clients checkout d02b7d57541b8598ac4c057947b10b2e42ccb1ee
python3 -m venv .venv-pose
source .venv-pose/bin/activate
python -m pip install -r .deps/nvidia-clients/body-pose/requirements.txt

# 去音軌、固定30fps、另存；HDR需先正確轉SDR，不是只改pix_fmt。
ffmpeg -n -i input.mov -an -vf fps=30 -c:v libx264 -pix_fmt yuv420p \
  -movflags +faststart clip_cfr.mp4

# bash隱藏輸入，勿貼到聊天／程式／提交紀錄。
read -rsp 'NVIDIA API key: ' NVIDIA_API_KEY; echo
export NVIDIA_API_KEY
python scripts/body_pose/capture_nvidia.py \
  --client-root .deps/nvidia-clients --video clip_cfr.mp4 \
  --bbox tracked_boxes.txt --track-id 1 \
  --output outputs/capture_001 --confirm-upload
unset NVIDIA_API_KEY

blender -b --factory-startup --python-exit-code 1 \
  --python scripts/body_pose/retarget_blender.py -- \
  --asset input/boss_v17_ponytail01.glb --pose outputs/capture_001/pose.json \
  --fps 30 --track-id 1 --calibration-frame 0 \
  --root-motion in-place --output outputs/capture_001_boss --render
```

人物框首行是人數，之後每格 `frame_id tracking_id x y width height`。本輪未安裝通用人物偵測器。單人固定鏡頭的管線試跑可用 `--single-person-full-frame` 取代 `--bbox`；全畫面框不是精準人物框，不能當模型準確率評測。

本試作額外限制 30 秒、60fps、50,000,000 bytes、H.264／yuv420p／SDR；30秒／60fps 是本專案保守限制，不是官方全域上限。API 不自動重試。

收據只表示請求是否收到結構完整回覆，不等於動作品質。轉接報告仍保守標記未獨立驗證，需對照收據、原影片、骨架疊圖與 GLB。

## 隱私與授權

先閱讀 NVIDIA 試用條款，確認真人同意，不拿學生或研究原始影像作首輪範例。沒有 `--confirm-upload` 不送出；CI 不讀 Secret、不自動上傳影片。

原角色素材沿用原專案授權。NVIDIA 客戶端 MIT 不代表模型權重、服務或真人影片都是 MIT；附官方程式與圖示時保留 LICENSE。

下一個品質門檻：真人→疊圖正確→左右與時間同步→GLB→腳滑與衣服穿模→遊戲引擎。全部完成前不宣稱 production-ready。
