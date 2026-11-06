# Character Studio 0.15.0｜停步後再起步與行進轉向

本階段讓棕馬／白馬在瀏覽器中停止、保留世界位置與方向、再次起步，並排入 ±15° 行進轉向。前版 v14 的 18 段 GLB 動作、21 個 Blender actions、幾何、骨架、權重、原解析度貼圖完全保留；新增 3 段候選動作與相對應 root actions。兩色共用同一種身形，仍不是第二身形或人物服裝適配成果。

## 啟動與操作

從本階段 Draft PR 的成功 Actions artifact 下載 review ZIP，解開其中 Runtime 與 Sources 到同一目錄。執行：

```bash
python3 START_STUDIO_V15.py --open
```

Windows 可雙擊 `START_WINDOWS_V15.cmd`。預設 http://localhost:8808/web-v15/；只綁定 localhost，不更新網站。

1. 點棕馬／白馬卡片；載入時顯示進度，模型 SHA-256 不符會拒絕顯示並提供重試。
2. 點「進入控制模式」，再按「前進／再起步、排入停步、行進左轉／右轉」。B 使用新動作，A v14 沒有相對應片段，不提供虛構的前版比較。
3. 指令在完整步態／片段結束時執行。介面顯示目前片段、意圖、待轉方向與距銜接點時間。停步會清除待轉指令；停步期間再按前進會先完成停步，再進入 RestartWalk。最新左右轉向取代尚未執行的轉向。
4. 停下不歸零。只有「重設」、切換角色或模式才清除控制歷史與位置。拖曳時間可重播／預覽指令軌跡；倒回後發出新指令會刪除游標之後的舊指令。播放、0.1–2×、暫停、1/60 或 1/240 秒逐格均可用。
5. 「載入控制示範」提供 36 秒停步→停留→再起步→左轉→右轉→停步→再起步的指令歷史；按播放觀看。可切正面、側面、背面、前後蹄與關節近景；關閉跟隨可觀察世界路徑。
6. 單段動作可選 RestartWalk、WalkTurnLeft、WalkTurnRight。A/B 可比較原有 WalkWorld 等 18 段。新動作會自動切 B 單角色。

## 資產、授權、固定取用

- `library-v15/catalog.json`：A/B 路徑、來源、作者、版本、GLB／母檔／骨架設定完整 SHA-256。
- `library-v15/horse-{brown,white}-locomotion-review/0.1.0/`：GLB、完整 packed Blender 母檔、骨架 profile、adaptation、motion-audit、asset_manifest、report。
- `library-v14/horse-{brown,white}-walk-smooth-review/0.1.0/`：原封比較與直接重建輸入，不覆蓋。
- `motion-v15/`：可稽核 float32 原生 TRS 文字曲線與 SHA lock；三檔分開保存。鮮算原生解與固定曲線差異超過 1e-5 即拒絕重建。
- `config-v15/horses.lock.json`：固定 ID＋0.1.0＋模型 SHA。`THIRD_PARTY_V15.md` 與前階段 notices 保留 Quaternius CC0、aitest-ai 修改、Three.js 等來源與授權。原貼圖嵌入 GLB／packed 母檔，來源包內原檔保留。

```bash
python3 scripts/pin_horses_v15.py --id horse-brown-locomotion-review --version 0.1.0 --sha256 24b812bda86bcab93195d1d6537b492da4aa568075ec8261314647426f1a3632 --dest /new/review/horse --review-candidate --include-mother
```

拒絕已存在的目的目錄與不符的 ID／版本／SHA；此命令不會更新地圖。所有新動作皆待美術與遊戲驗收，尚未發布正式 Release。

## 原生編輯與可重現匯出

使用官方 Blender 5.2.3 LTS，CPU 背景執行，4 執行緒；未使用 GPU／GUI／付費模型或自行訓練。`AnimalArmature` 有 21 個 rig actions；`StudioTravelRoot_v11` 有 6 個對應 root actions，24 fps。選新動作時同時指定同名 `_Root` action。骨架仍是原生 50 骨，未搬入不相容骨架動作。glTF 前向 +Z；Blender 前向 −Y；原生 L 骨位於 +X，正 glTF Y yaw 朝原生左側。匯入其他引擎必須保留這個語意。

全新輸出目錄重建（先解開 Sources）：

```bash
STUDIO_V15_OUT=/absolute/new-output /path/to/blender -b -t 4 --python-exit-code 1 --python scripts/build_horses_v15.py
```

原生母檔另存後匯出新增三對動作（拒絕覆寫 output）：

```bash
/path/to/blender -b -t 4 --python-exit-code 1 --python scripts/export_horses_v15.py -- --id horse-brown-locomotion-review --mother /path/edited.blend --output /path/new-candidate.glb
```

此匯出器保護原有動作、幾何、rest pose、權重、材質、貼圖與父子變換；只允許新三對 rig/root 動作變更，時長保持原規格。修改後須另立候選版本、重新測接地／銜接／外觀。GLB 可逐位元重建；Blender 序列化檔案雜湊會依建置不同，以隨包 profile 的 SHA 為準。不要把 dense 曲線逐 key 重插或呼叫 `fc.update()`，會合併 0.01 frame 間距的 key。

## 驗收與已知限制

`evidence-v15/index.html` 收錄實際瀏覽器 298 張連續畫面、兩段轉向錄影、完整測量與來源；不是離線渲染。錄影由軟體繪圖產生，實際編碼時長、播放起訖另列，可能掉格／時間壓縮。

- 程式：來源 18 段與場景/BIN 前綴完全保留、固定版本、原生曲線／改壞幾何與舊 root 拒絕、ZIP CRC 與每檔 SHA、獨立乾淨重建。
- Blender：四個母檔冷開；B 27 actions；原有 21 actions、幾何與貼圖不變；21 個新動作時間點、全部 6548 身體頂點與瀏覽器比對。
- 瀏覽器：三新片段及 36 秒控制示範以 480 Hz 實際蒙皮取樣；四蹄接地、蹄面漂移、完整表面銜接、停留再起步位置、左右轉向、倒播重算、控制按鈕、錯誤與重試。
- 手機真機、硬體效能、人工自然度／美術、遊戲地圖、完整自碰撞與真實質量／地面力：**未測**。390px 桌面 viewport 不等於手機驗收。

目前只支援平地固定 0.8 m/s 行走及 ±15° 行進轉向。轉向片段長 5.833 秒，停步指令可能等待整段結束，再用 3.5 秒停下；不是緊急停步或任意相位融合。最小腿部伸展餘量約 1.91 mm（直走前版門檻 2 mm；本階段正餘量門檻 1.5 mm），未超伸但接近限制，不能擴大角度直接當成通用轉向。保留 20 mm 軀幹下移、3 mm 蹄面間隙；顯示比例不是生物尺寸認證。紫點是四個肩骨平均投影，不是物理重心。Idle 未新增呼吸；骨架姿勢自然度仍待人檢。

下一階段：優先以多視角人工檢查轉彎內外側腿、軀幹側向／尾部動作；再縮短指令等待，設計相位適配的方向與停止過渡。人物、衣服與真正第二身形保持獨立待辦，不以馬匹換色代替。
