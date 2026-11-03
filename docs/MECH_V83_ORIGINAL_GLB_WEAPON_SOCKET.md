# 臺北機甲 v8.3｜原始 GLB 武器骨架接點與射線偏差（只讀診斷）

本 Draft PR 承接 v8.2 #122，建立以真正 Blender v5.0 `weapon_socket.R` 為依據的**可攜式診斷核心**。保留 v8.2 原始高品質機甲、敵機、OSM 城市及武器命中／傷害／側閃／三波防衛演算法。

## 交付

- `examples/threejs/mech-weapon-socket-v83.js` 是與使用者下載包內 `runtime/mech-weapon-socket-v83.js` **Git blob SHA1 完全一致**的原始碼：`a7d22c2da30ce3d87da5f88a1abbe257742a3828`。
- `tests/mecha/v83-weapon-socket.mjs` 驗證唯一骨架搜尋、姿勢後的 world pivot、本地端點校正、射線距離／角度、沒有預設假的砲口端點與受限隱私報告。
- 本輪完整**安全差分 ZIP**另於使用者對話交付；這個 GitHub 3dcodeverse-lab repo **不含完整 Windows 遊戲原始碼**。差分包含 `UPGRADE_V83.py`、`ROLLBACK_V83.py`、`INSTALL_V83_WINDOWS.cmd`、離線檢視頁 `qa/v83_weapon_socket_audit.html`、上輪安裝引用副本、Python/Node/Chromium 測試及 README。

## 正確定義

1. `weapon_socket.R` 是原始 Blender 骨架上的接點，不保證等於獨立主砲的真實炮管出口。**沒有經 Blender 精準校正的 muzzle tip，不自動修改光束起點。**
2. v8.3 對原本 `combat.fire(start, dir, heavy, charged)` 只插入不改傷害的診斷呼叫，確保參數、回傳與射線不變；診斷任何例外不會阻礙射擊。
3. 診斷手動開啟，最多 24 筆，不含世界位置、GPS、圖片、裝置資訊、帳號或絕對時間。
4. 在 Windows 已套用 v8.2 的完整遊戲包才可嘗試套用差分。安裝器會先從 v8.2 備份重建並核對原始碼、v8.2 HTML、原始 GLB 雜湊及唯一射擊／骨架插入點，失敗即拒絕修改；有獨立回退。

## 測試與未驗收

從 v8.3 **最終 ZIP 全新解壓**後，三組獨立測試成功（Node 模擬 rig math、Python 合成 v8.2 原始碼錨點／回退／中斷恢復、隔離 Chromium 用**合成測試 JSON**驗收 DOM）。ZIP 大小 49,283 bytes，SHA256 `b1ef27e70682374d5b6a8950b56604ccca7f0289be0b8f758ccb55c448eda389`，17 個項目，16/16 受管理檔案 SHA256 相符、CRC PASS。

**沒有完成**：在真正 Windows WebGPU 臺北遊戲上套用並遊玩、五分鐘三波防衛、真實 GPU FPS/VRAM、真正炮管出口視覺／骨架誤差、全動作穿模驗收。上述測試不可等同實機通過。

保持 Draft；Base = v8.2 分支，不合併 `main`、不更新公開站或覆寫原 ZIP。