# 人物工作室：第一階段灰模檢視器

此頁呈現實際匯出的 D03／D06 GLB，用共同地面與鏡頭檢查身形、年齡感及無髮臉型。它是這次候選資產的獨立審查工具，並非完整遊戲或動作驗收結果。

## 本次範圍

- D03：24 歲、186 cm、高瘦青年；D06：73 歲、153 cm、較豐滿高齡女性。
- 兩份高品質 GLB 都完成位元組下載、SHA-256 校驗與材質準備後，才一起顯示。
- 使用 GLB 原有幾何與材質，不以假人佔位、不使用舊模型、不自動切換 LOD。
- 只平移到共用地面及左右位置（x = −0.68／+0.68 m），檢視器不縮放任一角色。
- 相同正交鏡頭顯示兩人。正／側／背按鈕讓角色各自在原地轉向，維持並列、共同投影尺度，避免側面視角時彼此遮擋。
- 青年／長者臉部近照使用相同的投影範圍。拖曳旋轉、滾輪／雙指縮放、方向鍵與 ＋／− 可操作鏡頭；Home 或「重設」回到共同正面。
- Stage 1 無髮、使用中性站姿，不建立 AnimationMixer，不產生或播放動畫。服裝、表情與動作需在後續階段分別驗收。

## 交付目錄

此儲存庫保存四個檢視器原始檔。打包時，將同一候選版本的模型與固定版 Three.js 放入下列相對位置：

```text
character-studio/
  index.html
  studio.js
  style.css
  README.md
  models/
    registry.json
    d03.glb
    d06.glb
  vendor/three-0.187.0/
    LICENSE
    build/three.module.js
    build/three.core.js
    examples/jsm/loaders/GLTFLoader.js
    examples/jsm/utils/BufferGeometryUtils.js
    examples/jsm/utils/SkeletonUtils.js
```

`three.module.js` 會載入 `three.core.js`；此固定 r187 的 `GLTFLoader.js` 會載入 `BufferGeometryUtils.js` 與 `SkeletonUtils.js`（已核對交接包中的實際 imports）。打包者應保留固定版本的相依檔案與 MIT 授權，不能只複製主模組。此頁不引用 CDN、外部字型或 OrbitControls。Three.js 官方來源：[mrdoob/three.js](https://github.com/mrdoob/three.js)，確切交付位元組應記錄於包內來源鎖定檔。

### registry.json

```json
{
  "schema_version": 1,
  "version": "0.1.0-candidate.1",
  "assets": [
    {
      "id": "d03",
      "label": "D03｜高瘦青年",
      "file": "d03.glb",
      "sha256": "替換成實際 GLB 的 64 字元 SHA-256",
      "height": 1.86,
      "version": "0.1.0-candidate.1",
      "bytes": 12345
    },
    {
      "id": "d06",
      "label": "D06｜較豐滿高齡女性",
      "file": "d06.glb",
      "sha256": "替換成實際 GLB 的 64 字元 SHA-256",
      "height": 1.53,
      "version": "0.1.0-candidate.1"
    }
  ]
}
```

`height` 單位為公尺；`bytes` 可省略，若提供則必須是實際檔案位元組數。其餘欄位除 `label` 外皆必填。範例中的雜湊與大小只是格式說明，不能直接用作登錄。登錄檔必須與 GLB 一同從已核對的版本產生，不能把舊檔雜湊換成新值以掩蓋版本問題。

檢視器會檢查 GLB 的實際世界高度。若與登錄高度差距超過 `max(1.5 cm, 1%)`，會停止載入並請修正輸出尺度，不會自動把人物拉高或縮小。此誤差容許來自表面細分與浮點數；不代表比例品質通過。

GLB 的 buffers／images 必須內嵌（bufferView 或 data URI），使外觀資源包含在同一個 SHA-256 內。外部檔案會明確拒絕。此審查包未設定 Draco／Meshopt／KTX2 解碼器；交付這次一般未壓縮 GLB 即可，不能為了這個檢視器丟失可編輯母檔或另做低品質模型。

## 執行

在 `character-studio` 目錄執行：

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

開啟 <http://localhost:8765/>。亦可使用 HTTPS 靜態主機。勿直接雙擊 HTML；瀏覽器模組載入、GLB 讀取及 SHA-256 WebCrypto 需要適當的來源與安全環境。`localhost` 可在不使用憑證的情況下提供本機安全環境。

下載進度來自 `ReadableStream` 實際收到的位元組。已知總長度時顯示已收／總量，未知時顯示已收位元組與不定進度，不捏造百分比。若任一模型失敗，完整視圖保持隱藏並提供同版本重試。WebGL 2、模組或雜湊校驗不可用時會說明原因。

## 驗證資料與只讀審查介面

預設收起的「驗證資料」會顯示資產版本、完整 SHA-256、實際高度、大小，以及此頁的連續量測。使用者可下載完整 JSON。資料只在瀏覽器本機生成，沒有傳送到分析服務。

- 暖機：先累積可見頁面 3 秒，再開始採樣。
- 樣本：`requestAnimationFrame` 的實際幀間隔，保留最近 1,800 筆與總樣本數；保留長幀，頁面在背景時不採樣。
- 統計：p50、p95、最大值、平均值、原始樣本、視角與時間戳記。
- 環境：瀏覽器 user agent、平台、WebGL renderer／vendor（若瀏覽器允許）、CSS 尺寸、實際像素比與繪圖緩衝區尺寸。
- 場景：Three.js 的 draw calls、triangles、幾何／貼圖計數。這些是目前完整審查場景的資料，包含工作室地面；不能當作每個角色單獨的繪製成本。
- 檢視器保留目前螢幕的像素比；沒有基於低 FPS 自動降低解析度、替換模型或啟用輕量模式。

`window.characterStudioReview` 是不可覆寫的只讀物件。取得的陣列與物件為凍結快照，不會公開可改寫模型或場景的引用：

```js
window.characterStudioReview.ready;        // boolean
window.characterStudioReview.status;       // loading | preparing | ready | error | unsupported
window.characterStudioReview.error;        // null 或原因字串
window.characterStudioReview.version;      // registry 候選版本
window.characterStudioReview.assets;       // SHA、大小、高度、匯入記錄
window.characterStudioReview.view;         // front | side | back | face-d03 | face-d06 | custom
window.characterStudioReview.measurements; // 量測快照；繪圖環境尚未建立時為 null
```

瀏覽器自動化可以等待 `ready === true`，或以 `status` 與 `error` 辨認失敗。成功僅表示這兩份 GLB 已完成校驗及繪製，並不等於臉型、自然度、服裝或動畫通過驗收。

## 實際瀏覽器驗收

需由交付者對真正的模型包執行並保存結果：

1. 確認兩個 GLB 一次出現、腳底同地面，186／153 cm 的身高差保留，沒有各自等高正規化。
2. 保存共同正／側／背與兩人無髮臉部近照的瀏覽器截圖；檢查輪廓、五官、眼球、陰影及可見表面瑕疵。
3. 操作拖曳、縮放與重設，確認鏡頭能恢復且角色幾何、比例、材質不變。
4. 模擬缺檔／錯誤雜湊，確認有明確原因、未顯示單一完成角色或替代人形，修復後可重試。
5. 暖機後確認可見頁面持續採樣，下載 JSON，記錄 renderer 與實際像素比。對軟體 GL 結果明確標註環境。

這些步驟是驗收方式，不是已完成測試的宣稱。執行結果應由交付報告另行記錄。

## 來源與限制

頁面的固定版本載入、真實進度、雜湊校驗及失敗重試概念沿用使用者提供的 V110 基隆河交接包經驗；此處重新實作為獨立人物審查介面，未複製或綁定地圖流程。角色 GLB、可編輯 Blender 母檔、原始 MPFB／MakeHuman 資產、授權及來源鎖定資料由主交付包管理，這四個網頁檔案不替代那些資料。

灰模採用共用工作室光源、地面與色調映射，並保留 GLB 材質參數。瀏覽器照明與 Blender 離線渲染設定不同，兩者必須各自看圖驗收。此頁沒有完整地圖場景、動畫、遊戲互動、Android 真機或 GPU 計時查詢；幀間隔受到 VSync、瀏覽器排程、螢幕解析度與硬體／軟體渲染的影響，不能直接推論手機是否跑得動。
