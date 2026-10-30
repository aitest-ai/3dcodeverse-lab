# 賽馬角色第一輪實測｜真正的 CC0 雙馬 GLB

日期：2026-10-30

## 已成功的產線（Blender 5.2.3）

來源一律是真正來自 Quaternius [Ultimate Animated Animals](https://quaternius.com/packs/ultimateanimatedanimals.html) 的 CC0 模型。Google Drive 官方發佈資料夾的單獨下載碰到存取次數限制，因此改從公開的 [PixelTriks 原始 Quaternius 模型下載頁](https://pixeltriks.com/browse?pack=quaternius-ultimate-animated-animals) 取得：

- https://pixeltriks.com/characters/animals/quaternius_Horse.gltf
- https://pixeltriks.com/characters/animals/quaternius_Horse_White.gltf

**此為作者原版兩匹馬，各自擁有原始網格與 13 段動畫；不是拿一匹改色，也不是第三方會變形的三動畫壓縮模型。**

實測完成的 [GitHub Actions #26](https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41001573577)：兩匹均匯入 Blender 5.2.3 LTS、保存 BLEND、GLB、六視角圖片與品質報告。

| 項目 | 深棕 Horse | Horse White |
| --- | --- | --- |
| 原始骨架 | 50 根 | 50 根 |
| 幾何頂點 | 約 4,442 | 約 4,442 |
| GLB | 892,560 bytes | 891,452 bytes |
| 匯出動畫 | 13 | 13 |
| 驗收 | Blender 模型、GLB skin、全部動畫、六視角 | 同左 |
| 目標使用 | 賽馬遊戲初期原型 | 賽馬遊戲初期原型 |

動畫含 `Attack_Headbutt`, `Attack_Kick`, `Death`, `Eating`, `Gallop`, `Gallop_Jump`, `Idle`, `Idle_2`, `Idle_Headlow`, `Idle_HitReact1`, `Idle_HitReact2`, `Jump_toIdle`, `Walk`。

## 避免前一輪失敗重現

- 先前從 `crisleyhguimaraes/space-ship` 取得 Quaternius／Poly Pizza CC0 馬，雖有 50 骨、3 clips，匯入 Blender 後卻出現**極長針狀變形**。解除 Meshopt 和 KHR mesh quantization 仍未改善，**不可將該版本當成合格成品**。
- 目標專案不應只檢查 `skins`／`animations` 數量，必須檢查 Blender 實際 3D 渲染、骨骼移動、四肢解剖，且驗收前不可聲稱可用。
- 前一輪 `racing-horses-12` 和 `racing-horses-15` 視覺失敗；使用 `racing-horses-26` 之後的原版。
- 版權：Quaternius 官方此 **2021 年 CC0 模型包**，不同於其他限制較多、未標 CC0 的素材。保留來源網頁與下載雜湊記錄。

## AI 工作流程

1. `python3 scripts/horses/fetch_horses.py`：只向公開原始地址下載 Horse / Horse_White，解析 GLTF 2.0，確認每隻 10+ clips 與 skins，寫 `source_manifest.json`。禁止任意追隨不明第三方網域或絕對路徑 sidecar。
2. `blender -b --python-exit-code 1 --python scripts/horses/build_horse_blender.py -- inputs/horses/Horse.gltf outputs/horse/Horse`：匯入、BLEND、GLB、真實圖片。
3. `python3 scripts/horses/validate_horse_glb.py outputs/horse/Horse`：再次確認 GLB 動畫沒有遺失、骨架蒙皮仍可用。
4. `python3 scripts/horses/make_horse_sheet.py outputs/horse/Horse`：製作六視角圖片。
5. `scripts/horses/qa_gallop.py`：獨立設定 Gallop，在 Blender 評估至少 2 個影格，確認真的有姿勢改變並保存截圖；此後仍要檢查蹄部滑動、四肢彎曲方向。
6. `examples/racing-horse/index.html`：從 `outputs/horse/demo` 載入兩匹馬的 GLB，選擇 Gallop／Walk／Idle，調整速度並可測試沿跑道運動。
7. 網頁本地測試需要 HTTP server（`python3 -m http.server 8000`），不要直接雙擊 HTML 用 `file://`，因 ES Modules/CORS 會出錯。

## 品質判定與下一階段

**目前模型屬低多邊形遊戲原型，並非寫實賽馬高模。** 完整賽馬系統仍要追加：

- 以真實馬匹照片查核頭型、頸長、肩胛、前膝、後跗關節、蹄形。
- 奔跑 gait cycle：四肢支撐／騰空時序、重心位移、腳蹄接地測試、動作循環無跳格。
- 賽馬比賽功能：每匹獨立編號、馬衣／蹄鐵、騎師骨架、馬鞍插槽、碰撞代理、坡道／彎道動作。
- 高品質版可以另以 <https://sketchfab.com/3d-models/horse-e62e8fae743b40b7b8c382ccca863725> 等合法下載的 CC BY 高模測試；不可繞過平台登入或假稱授權涵蓋第三方素材。
- 如果只是要高度寫實的付費或個人用角色，Warhorse Lite 提供高品質 2K PBR 模型，但僅有 Idle／Walk／Canter／Rear，缺 Gallop；授權禁止重新散布原素材，因此不能將其原始 GLB 提交到公開 repo。

本 PR 為 Draft，暫時不覆蓋 `main`，以方便用戶驗收。
