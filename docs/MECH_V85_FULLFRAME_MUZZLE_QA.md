# 臺北機甲 v8.5｜六段原始 NLA 動畫砲口逐格驗收

接續 v8.4 Draft PR #127。核心變更是對真正 Blender 候選母檔的唯讀驗證產線；不是再造低品質 GLB，也不是直接修改 combat.fire 或 OSM 建築碰撞。

原 V50 模型六段 NLA 軌道為 Idle、Run、Punch、Dodge、Fire、Hit，各 48 格；v8.4 MuzzleTip_R 標記沿用原 weapon_socket.R。程式在 REST 姿態找出 PrimaryCannon_energy_bore 真正端面頂點，在六段 NLA 單獨播放時逐格從 Blender evaluated depsgraph 讀取原砲管變形後的位置／方向，與附著在骨架的標記比對。完整 6×48=288 格。

幾何候選門檻：每格距離 <=25mm，方向角 <=9度。缺格、重複、異常頂點、非原始 NLA、錯誤綁骨或沒有原候選 GLB 皆須拒絕。不改原模型、模型骨架、敵機、武器傷害、控制器或原射線。

## 本 PR

- scripts/blender5/trajectory_math_v85.py：非 Blender 幾何計算核心。
- scripts/blender5/audit_animation_muzzle_v85.py：真正 Blender 5 + 候選 .blend 時的 288 格取樣報告生成器。
- examples/threejs/mech-animation-qa-v85.js：嚴格 JSON 格式和人工檢查報告驗證。
- tests/mecha/v85-trajectory.py 與 tests/mecha/v85-animation-qa.mjs，以及 Node22/Python3.11 CI。

另於對話交付完整安全工具包，含 Windows CMD、v8.4 舊來源參考、真正離線六圖頁、測試／manifest／詳細 README。ZIP SHA256: 65c18ae9a3e4c04b6f8b1e66b7a31ecc6b5f5f89b61204892b4516fe80a45dee；16 個項目、15 個檔案 SHA256 正確、ZIP CRC 正常。最終 ZIP 全新解壓 Python/Node 2 組通過；隔離 Chromium 使用明確的「合成測試 JSON」測試匯入、六圖、匯出和清除。直接 file:// 導覽於本測試環境被管理員阻擋。

## 無法宣稱

環境沒有 Blender 可執行檔，也沒有原始 mecha_v50.blend 和真正 v8.4 候選母檔；尚未真正載入／匯出新 GLB，未有 Windows WebGPU 真實臺北場景五分鐘遊玩、FPS/VRAM、動畫穿模或命中測試。CI 僅驗證純數學、格式及 Python 語法，不等於完整模型驗收。

保持 Draft；Base 是 v8.4 功能分支，而非 main。不合併其他 PR，不覆蓋舊版 ZIP，不更新公開臺北網站。
