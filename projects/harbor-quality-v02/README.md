# Harbor Quality v02｜角色建模升級與成熟引擎驗證

保留 Harbor Walk v0.1，新 asset ID：`harbor-courier-v02`。原創角色「林汐」採日常海港服裝：海綠外套、布領口與袖口、深色長褲、踝襪、鞋底與鞋帶、薄領巾、柔性郵包肩帶及分層棕色髮型。人體／短髮基底與 locomotion 來自 Quaternius CC0，服裝與配件是新製作的改作幾何，不宣稱全數從零建人體。

本版實際使用 Blender 4.3.2 與 **Godot 4.6.3**。Godot 原生 CharacterBody3D、SpringArm3D、AnimationTree / BlendSpace / TimeScale、碰撞、GUI 和 Web exporter 已加入工作流。Unreal Editor 不在本環境；UE 文件與匯入工作流程是交接候選，不是已驗證的 Unreal 遊戲。

## 直接操作預建 Web 版

Runtime ZIP 中包含 `web/`，不需安裝 Godot：

```sh
python START_V02.py
```

開啟 http://127.0.0.1:8130/ 。請用 HTTP，不要雙擊 file:// HTML。

- WASD 移動，Shift 跑步；按住滑鼠拖曳旋轉視角，滾輪拉遠近。
- E 與附近居民對話，Esc 關閉。
- Q 切換標準／省電畫質，V 切換角色近景，B 微笑表情。
- 1／2／3 播放工房 Idle／Walk／Run；按移動鍵回到操作。
- 阿澄提供悠閒路線與 60 秒快遞選擇。收集茶行、樹影、海風三枚印記，交給書店阿青；基本 150 點，快遞及時交付額外 50 點。

沒有聲音、手機觸控控制或實機 GPU 效能認證。角色與場景仍是品質候選，不等同參考遊戲的完成度。

## 在成熟引擎中編輯

以 Godot 4.6.3 開啟 `godot/project.godot`，主場景為 `main.tscn`。模型是匯入的真 GLB／Skeleton3D／AnimationPlayer；場景保留原生節點、光照、碰撞及批次幾何。`scripts/build_scene.gd` 能重建場景；手動修改前先另存場景，避免被重建器覆寫。

`assets/harbor-courier-v02.blend` 是可編輯母檔，GLB 是跨引擎交付，FBX 是 Unreal 匯入候選，`textures/` 有原創布料貼圖，其他貼圖同時內嵌於模型。配件按材質合批，可在 Blender 以 loose parts 分開編輯；生成腳本保留各原始零件名稱與參數。

## 重現角色與驗證

取得 `assets/source-lock.json` 所列免費 CC0 Standard 來源包，核對雜湊並解壓：

```sh
CC0_ROOT=/path/to/cc0 blender -b --factory-startup --python scripts/build_courier_v02.py
blender -b --factory-startup --python scripts/audit_motion.py
blender -b --factory-startup --python scripts/render_character.py
blender -b --factory-startup --python scripts/verify_fbx.py
python scripts/validate_glb.py assets
python scripts/check_asset.py
```

腳本輸出母檔、GLB、FBX、manifest、材質貼圖及檢查報告。鞋底檢查讀取真正蒙皮後的幾何，逐整數影格取樣；本版校正是每段動畫的固定垂直偏移，不是 Foot IK。

Godot 重建／匯出：

```sh
python scripts/bootstrap_godot_ci.py
python scripts/fetch_web_templates.py
python scripts/export_web.py --godot /absolute/path/to/godot
```

Windows 可指定已安裝的 Godot exe；bootstrap 腳本只下載 Linux CI binary。Web 模板使用官方固定版來源，按 HTTP Range 取得所需部分並核對成員 CRC，沒有冒稱已驗證整份 1.25GB archive 的 SHA。

真瀏覽器操作測試另需 Python Playwright、Chromium 與 Playwright FFmpeg；先啟動本地伺服器：

```sh
python -m pip install playwright
PLAYWRIGHT_BROWSERS_PATH=/path/to/cache python -m playwright install ffmpeg
CHROMIUM_PATH=/usr/bin/chromium PLAYWRIGHT_BROWSERS_PATH=/path/to/cache python scripts/browser_qa.py
```

## Unreal 與 GitHub

`unreal/HarborPilot.uproject`、`unreal/import_character.py`、`ci/harbor-unreal-v02.yml` 提供 UE5.6 匯入接點，需要已合法安裝 Unreal 的自管 Windows runner 與 `UE_EDITOR_CMD`。本環境沒有執行 Unreal，不提供原作解包模型，也沒有取得 Epic 憑證或再散布引擎。

`ci/harbor-godot-v02.yml` 使用 GitHub 託管 Ubuntu runner 驗證真 GLB、執行 Godot 匯入並產生 Web artifact；不部署網站。GitHub 執行結果與最後品質限制在 `docs/STATUS.md`。

授權見 `THIRD_PARTY_NOTICES.md`，接手規範見 `AGENTS.md`。
