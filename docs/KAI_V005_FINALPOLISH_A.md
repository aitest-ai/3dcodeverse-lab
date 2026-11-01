# 北海道開拓之村 V005 FinalPolish A｜Blender 回寫與跨 AI 交接

狀態：**runtime A 已由 Chromium/WebGL 驗證；Blender 母檔回寫流程已準備，但尚未在 GitHub Actions 取得 pinned source artifact 執行。**

範圍固定為 **14 舊島歌郵局 → 15 舊山本理髮店 → 16 舊渡邊商店**。本工作不新增第四棟。

## 已驗證的 A 參數

- V005 Blender 母檔 SHA-256：`7ead93b961f243c3521244a509e53546c73e27af4539a89a303a2e28c632ddbc`
- V005 baseline 環境 GLB SHA-256：`32ddd3721e75b95f54ade22304e4d383930e4411507b0858f7d957f7171462d4`
- FinalPolish A runtime GLB SHA-256：`752887763308bf71342b0d9ac292fc0f30ffa2e30d0ec6639e7373bb03cd5a55`
- 窗後暗面：`(0.055, 0.050, 0.044, 1.0)`
- 內框退縮面：`(0.070, 0.063, 0.052, 1.0)`
- 草緣：只處理 `V005 clustered grass 0..4` 靠街窄帶；runtime A 移除 547 / 56,769 個草三角片（約 0.96%）。

玻璃本體的 transmission／roughness 不變。沒有增加家具、房間、燈具或未確認室內內容。

## 絕對保護範圍

不得修改或刪除：

- 低石緣、郵局通路、郵筒及綠籬；
- 理髮店梯架、木桿、實景有依據的山牆斜撐；
- 理髮店已診斷並修補的上部雨遮左端側縫；
- 階梯、門檻、平台、屋簷／雨遮幾何；
- 非草物件 transform；
- 三棟室內格局。

## 為什麼來源檔不直接 commit 到 GitHub

`mainstreet-v005.blend` 約 456 MB，V005 baseline 環境 GLB 約 380 MB。它們不應以一般 GitHub contents commit 硬塞進 repository，也不應為了跑 workflow 改用低品質模型。

專用 workflow 因此使用**同一 repository 的 GitHub Actions artifact**作為來源傳遞層；原始來源仍由使用者的私人工作檔保存。

來源 artifact 必須包含：

```text
mainstreet-v005.blend
kaitaku-mainstreet-v005.glb
```

workflow 會先核對上列固定 SHA。任何不符都立即停止，不會套用 patch。

## 專用 workflow

`.github/workflows/kaitaku-v005-finalpolish-a.yml`

Push 只跑靜態語法／來源鎖檢查；**不會假裝 Blender 已執行**。

手動 `workflow_dispatch` 時需要：

- `source_artifact_run_id`：同一 repo 中保存 V005 pinned source artifact 的 workflow run ID。
- `source_artifact_name`：預設 `kaitaku-v005-source`。

完整執行後預期 artifact 包含：

```text
outputs/kaitaku-v005-finalpolish-a.blend
outputs/kaitaku-v005-finalpolish-a.glb
outputs/asset_manifest.json
outputs/report.json
outputs/validation.json
outputs/renders/01-mainstreet-overview.png
outputs/renders/02-shimauta-front.png
outputs/renders/03-shimauta-side-detail.png
outputs/renders/04-watanabe-front.png
outputs/renders/05-watanabe-side-detail.png
```

其中 GLB 是已驗證 FinalPolish A 的 deterministic runtime-equivalent GLB；`.blend` 是 Blender 正式回寫候選。**目前不宣稱 native Blender re-export 與 runtime GLB 完全 bytes 等價**，這要留到後續 export parity 驗證。

## 五個固定鏡位

沿用 V005 既有 offline inspection framing：

1. Mainstreet overview
2. Shimauta front
3. Shimauta side detail
4. Watanabe front
5. Watanabe side detail

使用原解析度材質，Cycles CPU，32 samples，不以縮圖、LOD 或舊模型替代。

## 尚未通過的項目

- GitHub Actions Blender 回寫：**等待 pinned source artifact，因此尚未執行。**
- Native Blender candidate → GLB export parity：未驗證。
- Android 真機：未測。
- 上述五張圖在 workflow 真的產出前不得寫成視覺驗收通過。

Runtime A 已有 Chromium/WebGL `ready` 與固定鏡位證據，但不能拿它冒充 Blender native offline render。
